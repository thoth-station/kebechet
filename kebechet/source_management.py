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

from IGitt.Interfaces import Issue
from IGitt.Interfaces import MergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GL_INSTANCE_URL
from IGitt.GitLab import BASE_URL as GL_BASE_URL
from IGitt.GitHub import GH_INSTANCE_URL
from IGitt.GitHub import BASE_URL as GH_BASE_URL

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
            self.repository = GitLabRepository(token=GitLabOAuthToken(token), repository=slug)
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
            _LOGGER.info(f"Issue already noted on upstream with id #{issue['number']}")
            if not refresh_comment:
                return None

            comment_body = refresh_comment(issue)
            if comment_body:
                issue.add_comment(comment_body)
                _LOGGER.info(f"Added refresh comment to issue #{issue['number']}")
            else:
                _LOGGER.debug(f"Refresh comment not added")
        else:
            issue = self.repository.create_issue(title, body())
            issue.labels = set(labels)
            _LOGGER.info(f"Reported issue {title!r} with id #{issue.number}")
            return issue

        return None

    def close_issue_if_exists(self, title: str, comment: str = None):
        """Close the given issue (referenced by its title) and close it with a comment."""
        issue = self.get_issue(title)
        if not issue:
            _LOGGER.debug(f"Issue {title!r} not found, not closing it")
            return

        if self.service_type == ServiceType.GITHUB:
            issue.add_comment(comment)
            issue.close()
        else:
            raise NotImplementedError

    def _github_open_merge_request(self, commit_msg, body, branch_name) -> GitHubMergeRequest:
        """Create a GitHub pull request with the given dependency update."""
        url = GH_BASE_URL + f'/repos/{self.slug}/pulls'
        response = requests.post(
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

        _LOGGER.info(f"Newly created pull request #{response.json()['number']} "
                     f"available at {response.json()['html_url']}")
        return GitHubMergeRequest.from_data(response.json())

    def _gitlab_open_merge_request(self, commit_msg, pr_body, branch_name) -> GitLabMergeRequest:
        raise NotImplementedError

    def open_merge_request(self, commit_msg: str, branch_name: str, pr_body: str, labels: list) -> MergeRequest:
        """Open a merge request for the given branch."""
        if self.service_type == ServiceType.GITHUB:
            merge_request = self._github_open_merge_request(commit_msg, pr_body, branch_name)
        elif self.service_type == ServiceType.GITLAB:
            merge_request = self._gitlab_open_merge_request(commit_msg, pr_body, branch_name)
        else:
            raise NotImplementedError

        merge_request.labels = set(labels)
        return merge_request

    def _github_delete_branch(self, branch: str) -> None:
        """Delete the given branch from remote repository."""
        response = requests.delete(
            f'https://api.github.com/repos/{self.slug}/git/refs/heads/{branch}',
            headers={f'Authorization': f'token {config.github_token}'}
        )

        response.raise_for_status()
        # GitHub returns an empty string, noting to return.

    def _github_list_branches(self) -> typing.List[str]:
        """Get listing of all branches available on remote repository."""
        response = requests.get(
            f'https://api.github.com/repos/{self.slug}/branches',
            headers={f'Authorization': f'token {self.token}'}
        )

        response.raise_for_status()
        # TODO: pagination
        return response.json()

    def list_branches(self) -> list:
        """Get branches available on remote."""
        if self.service_type == ServiceType.GITHUB:
            return self._github_list_branches()
        else:
            raise NotImplementedError

    def delete_branch(self, branch_name: str) -> None:
        """Delete the given branch from remote."""
        if self.service_type == ServiceType.GITHUB:
            return self._github_delete_branch(branch_name)
        else:
            raise NotImplementedError
