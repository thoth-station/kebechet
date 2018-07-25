#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Abstract calls to GitHub and GitLab APIs."""

import logging
import typing

import requests
from urllib.parse import quote_plus

from IGitt.Interfaces import Issue
from IGitt.Interfaces import MergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.GitLab import GitLabPrivateToken
import IGitt.GitLab

from .enums import ServiceType


_LOGGER = logging.getLogger(__name__)


class SourceManagement:
    """Abstract source code management services like GitHub and GitLab."""

    def __init__(self, service_type: ServiceType, service_url: str, token: str, slug: str):
        """Initialize source code management tools abstraction.

        Note that we are using IGitt for calls. IGitt keeps URL to services in its global context per GitHub/GitLab.
        This is global context is initialized in the manager with a hope to fix this behavior for our needs.
        """
        self.service_type = service_type
        self.slug = slug
        self.service_url = service_url
        self.token = token

        if self.service_type == ServiceType.GITHUB:
            self.repository = GitHubRepository(token=GitHubToken(token), repository=slug)
        elif self.service_type == ServiceType.GITLAB:
            self.repository = GitLabRepository(token=GitLabPrivateToken(token), repository=slug)
        else:
            raise NotImplementedError

    def get_issue(self, title: str) -> Issue:
        """Retrieve issue with the given title."""
        for issue in self.repository.issues:
            if issue.title == title:
                return issue

        return None

    def open_issue_if_not_exist(self, title: str, body: typing.Callable,
                                refresh_comment: typing.Callable = None, labels: list = None) -> Issue:
        """Open the given issue if does not exist already (as opened)."""
        _LOGGER.debug(f"Reporting issue {title!r}")
        issue = self.get_issue(title)
        if issue:
            _LOGGER.info(f"Issue already noted on upstream with id #{issue.number}")
            if not refresh_comment:
                return None

            comment_body = refresh_comment(issue)
            if comment_body:
                issue.add_comment(comment_body)
                _LOGGER.info(f"Added refresh comment to issue #{issue.number}")
            else:
                _LOGGER.debug(f"Refresh comment not added")
        else:
            issue = self.repository.create_issue(title, body())
            issue.labels = set(labels or [])
            _LOGGER.info(f"Reported issue {title!r} with id #{issue.number}")
            return issue

        return None

    def close_issue_if_exists(self, title: str, comment: str = None):
        """Close the given issue (referenced by its title) and close it with a comment."""
        issue = self.get_issue(title)
        if not issue:
            _LOGGER.debug(f"Issue {title!r} not found, not closing it")
            return

        issue.add_comment(comment)
        issue.close()

    def _github_open_merge_request(self, commit_msg, body, branch_name) -> GitHubMergeRequest:
        """Create a GitHub pull request with the given dependency update."""
        url = f'{IGitt.GitHub.BASE_URL}/repos/{self.slug}/pulls'
        response = requests.Session().post(
            url,
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {self.token}'
            },
            json={
                'title': commit_msg,
                'body': body,
                'head': branch_name,
                'base': 'master',
                'maintainer_can_modify': True
            }
        )
        try:
            response.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Failed to create a pull request: {response.text}") from exc

        mr_number = response.json()['number']
        _LOGGER.info(f"Newly created pull request #{mr_number} available at {response.json()['html_url']}")
        return GitHubMergeRequest.from_data(
            response.json(), token=GitHubToken(self.token), repository=self.slug, number=mr_number
        )

    def _gitlab_open_merge_request(self, commit_msg, body, branch_name) -> GitLabMergeRequest:
        url = f'{IGitt.GitLab.BASE_URL}/projects/{quote_plus(self.slug)}/merge_requests'
        # Use Session as these calls are mocked based on tls_verify configuration.
        response = requests.Session().post(
            url,
            params={'private_token': self.token},
            json={
                'title': commit_msg,
                'description': body,
                'source_branch': branch_name,
                'target_branch': 'master',
                'allow_collaboration': True
            }
        )
        try:
            response.raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"Failed to create a pull request: {response.text}") from exc

        mr_number = response.json()['iid']
        _LOGGER.info(f"Newly created pull request #{mr_number} available at {response.json()['web_url']}")
        return GitLabMergeRequest.from_data(
            response.json(), token=GitLabPrivateToken(self.token), repository=self.slug, number=mr_number
        )

    def open_merge_request(self, commit_msg: str, branch_name: str, body: str, labels: list) -> MergeRequest:
        """Open a merge request for the given branch."""
        if self.service_type == ServiceType.GITHUB:
            merge_request = self._github_open_merge_request(commit_msg, body, branch_name)
        elif self.service_type == ServiceType.GITLAB:
            merge_request = self._gitlab_open_merge_request(commit_msg, body, branch_name)
        else:
            raise NotImplementedError

        merge_request.labels = set(labels or [])
        return merge_request

    def _github_delete_branch(self, branch: str) -> None:
        """Delete the given branch from remote repository."""
        response = requests.Session().delete(
            f'{IGitt.GitHub.BASE_URL}/repos/{self.slug}/git/refs/heads/{branch}',
            headers={f'Authorization': f'token {self.token}'},
        )

        response.raise_for_status()
        # GitHub returns an empty string, noting to return.

    def _gitlab_delete_branch(self, branch: str) -> None:
        """Delete the given branch from remote repository."""
        response = requests.Session().delete(
            f'{IGitt.GitLab.BASE_URL}/projects/{quote_plus(self.slug)}/repository/branches/{branch}',
            params={'private_token': self.token},
        )
        response.raise_for_status()

    def _github_list_branches(self) -> typing.Set[str]:
        """Get listing of all branches available on the remote GitHub repository."""
        response = requests.Session().get(
            f'{IGitt.GitHub.BASE_URL}/repos/{self.slug}/branches',
            headers={f'Authorization': f'token {self.token}'},
        )

        response.raise_for_status()
        # TODO: pagination?
        return response.json()

    def _gitlab_list_branches(self) -> typing.Set[str]:
        """Get listing of all branches available on the remote GitLab repository."""
        response = requests.Session().get(
            f"{IGitt.GitLab.BASE_URL}/projects/{quote_plus(self.slug)}/repository/branches",
            params={'private_token': self.token},
        )

        response.raise_for_status()
        # TODO: pagination?
        return response.json()

    def list_branches(self) -> set:
        """Get branches available on remote."""
        # TODO: remove this logic once IGitt will support branch operations
        if self.service_type == ServiceType.GITHUB:
            return self._github_list_branches()
        elif self.service_type == ServiceType.GITLAB:
            return self._gitlab_list_branches()
        else:
            raise NotImplementedError

    def delete_branch(self, branch_name: str) -> None:
        """Delete the given branch from remote."""
        # TODO: remove this logic once IGitt will support branch operations
        if self.service_type == ServiceType.GITHUB:
            return self._github_delete_branch(branch_name)
        elif self.service_type == ServiceType.GITLAB:
            return self._gitlab_delete_branch(branch_name)
        else:
            raise NotImplementedError
