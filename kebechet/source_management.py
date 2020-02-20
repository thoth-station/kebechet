#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Sai Sankar Gochhayat, Fridolin Pokorny
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

from ogr.services.github import GithubService
from ogr.services.gitlab import GitlabService

from .enums import ServiceType
from ogr.abstract import Issue
from ogr.abstract import PullRequest
from .exception import CannotFetchPRError
from .exception import CannotFetchBranchesError
from .exception import CreatePRError
import json

_LOGGER = logging.getLogger(__name__)
BASE_URL = {"github": "https://api.github.com", "gitlab": "https://gitlab.com//api/v4"}


class SourceManagement:
    """Abstract source code management services like GitHub and GitLab."""

    def __init__(
        self, service_type: ServiceType, service_url: str, token: str, slug: str
    ):
        """Initialize source code management tools abstraction.

        Note that we are using OGR for calls. OGR keeps URL to services in its global context per GitHub/GitLab.
        This is global context is initialized in the manager with a hope to fix this behavior for our needs.
        """
        self.service_type = service_type
        self.slug = slug
        self.service_url = service_url
        self.token = token
        self.namespace, self.repo = slug.rsplit("/", 1)

        if self.service_type == ServiceType.GITHUB:
            self.service = GithubService(self.token)
            self.repository = self.service.get_project(
                repo=self.repo, namespace=self.namespace
            )
        elif self.service_type == ServiceType.GITLAB:
            self.service = GitlabService(self.token)
            self.repository = self.service.get_project(
                repo=self.repo, namespace=self.namespace
            )
        else:
            raise NotImplementedError

    def get_issue(self, title: str) -> Issue:
        """Retrieve issue with the given title."""
        for issue in self.repository.get_issue_list():
            if issue._raw_issue.title == title:
                return issue

        return None

    def open_issue_if_not_exist(
        self,
        title: str,
        body: typing.Callable,
        refresh_comment: typing.Callable = None,
        labels: list = None,
    ) -> Issue:
        """Open the given issue if does not exist already (as opened)."""
        _LOGGER.debug(f"Reporting issue {title!r}")
        issue = self.get_issue(title)
        if issue:
            _LOGGER.info(
                f"Issue already noted on upstream with title #{issue._raw_issue.title}"
            )
            if not refresh_comment:
                return issue

            comment_body = refresh_comment(issue)
            if comment_body:
                issue.comment(comment_body)
                _LOGGER.info(
                    f"Added refresh comment to issue with title #{issue._raw_issue.title}"
                )
            else:
                _LOGGER.debug(f"Refresh comment not added")
        else:
            issue = self.repository.create_issue(title, body())
            issue.add_label(*set(labels or []))
            _LOGGER.info(f"Reported issue {title!r} with id #{issue.id}")

        return issue

    def close_issue_if_exists(self, title: str, comment: str = None):
        """Close the given issue (referenced by its title) and close it with a comment."""
        issue = self.get_issue(title)
        if not issue:
            _LOGGER.debug(f"Issue {title!r} not found, not closing it")
            return

        issue.comment(comment)
        issue.close()

    def _github_assign(self, issue: Issue, assignees: typing.List[str]) -> None:
        """Assign the given users to a particular issue."""
        data = {"assignees": assignees}
        response = requests.Session().post(
            f"{BASE_URL['github']}/repos/{self.slug}/issues/{issue.id}/assignees",
            headers={f"Authorization": f"token {self.token}"},
            json=data,
        )

        response.raise_for_status()

    def _gitlab_fetch_userid(self, usernames: typing.List[str]) -> typing.List[int]:
        """Method fetches the corresponding user ids for usernames."""
        user_ids = []
        for username in usernames:
            response = requests.Session().get(
                f"{BASE_URL['gitlab']}/users?username={username}",
                headers={f"Authorization": f"token {self.token}"},
            )
            res = json.loads(response.text)
            userid = res.pop().get("id")
            if userid:
                user_ids.append(userid)
        return user_ids

    def _gitlab_assign(self, issue: Issue, assignees: typing.List[str]) -> None:
        """Assign the given users to a particular issue. Gitlab assignee id's are different from username."""
        assignees = self._gitlab_fetch_userid(assignees)
        data = {"assignees": assignees}
        response = requests.Session().put(
            f"{BASE_URL['gitlab']}/repos/{self.slug}/issues/{issue.id}/assignees",
            headers={f"Authorization": f"token {self.token}"},
            json=data,
        )

        response.raise_for_status()

    def assign(self, issue: Issue, assignees: typing.List[str]) -> None:
        """Assign users (by their accounts) to the given issue."""
        # Replace with OGR methods, when implemented in OGR.
        if self.service_type == ServiceType.GITHUB:
            self._github_assign(issue, assignees)
        elif self.service_type == ServiceType.GITLAB:
            self._gitlab_assign(issue, assignees)
        else:
            raise NotImplementedError

    def open_merge_request(
        self, commit_msg: str, branch_name: str, body: str, labels: list
    ) -> PullRequest:
        """Open a merge request for the given branch."""
        try:
            merge_request = self.repository.create_pr(
                commit_msg, body, "master", branch_name
            )
            merge_request.add_label(*labels)

        except Exception as exc:
            raise CreatePRError(f"Failed to create a pull request: {exc}")
        else:
            _LOGGER.info(
                f"Newly created pull request #{merge_request.id} available at {merge_request.url}"
            )
            return merge_request

    def _github_delete_branch(self, branch: str) -> None:
        """Delete the given branch from remote repository."""
        response = requests.Session().delete(
            f"{BASE_URL['github']}/repos/{self.slug}/git/refs/heads/{branch}",
            headers={f"Authorization": f"token {self.token}"},
        )

        response.raise_for_status()
        # GitHub returns an empty string, noting to return.

    def _gitlab_delete_branch(self, branch: str) -> None:
        """Delete the given branch from remote repository."""
        response = requests.Session().delete(
            f"{BASE_URL['gitlab']}/projects/{quote_plus(self.slug)}/repository/branches/{branch}",
            params={"private_token": self.token},
        )
        response.raise_for_status()

    def list_branches(self) -> set:
        """Get branches available on remote."""
        try:
            branches = self.repository.get_branches()
        except Exception as exc:
            raise CannotFetchBranchesError(f"Cannot fetch branches. Error is: {exc}")
        else:
            return branches

    def get_prs(self) -> list:
        """Get all the open PR objects as a list for a repo."""
        try:
            prs = self.repository.get_pr_list()
        except Exception as exc:
            raise CannotFetchPRError(f"Cannot fetch PR's. Error is - {exc}")
        else:
            return prs

    def delete_branch(self, branch_name: str) -> None:
        """Delete the given branch from remote."""
        # TODO: remove this logic once OGR will support branch operations
        if self.service_type == ServiceType.GITHUB:
            return self._github_delete_branch(branch_name)
        elif self.service_type == ServiceType.GITLAB:
            return self._gitlab_delete_branch(branch_name)
        else:
            raise NotImplementedError
