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
# TODO: replace calls to a lib that abstracts APIs of github/gitlab

import logging
import typing

from .github import github_add_comment
from .github import github_add_labels
from .github import github_close_issue
from .github import github_create_pr
from .github import github_delete_branch
from .github import github_list_branches
from .github import github_list_issue_comments
from .github import github_list_issues
from .github import github_list_pull_requests
from .github import github_open_issue


_LOGGER = logging.getLogger(__name__)


def get_issue(slug: str, title: str) -> typing.Optional[dict]:
    """Retrieve issue with the given title."""
    for issue in github_list_issues(slug):
        if issue['title'] == title:
            return issue

    return None


def open_issue_if_not_exist(slug: str, title: str, body: typing.Callable,
                            refresh_comment: typing.Callable = None, labels: list = None) -> typing.Optional[int]:
    """Open the given issue if does not exist already (as opened)."""
    _LOGGER.debug(f"Reporting issue {title!r}")
    issue = get_issue(slug, title)
    if issue:
        _LOGGER.info(f"Issue already noted on upstream with id #{issue['number']}")
        if not refresh_comment:
            return None

        comment_body = refresh_comment(issue)
        if comment_body:
            github_add_comment(slug, issue['number'], comment_body)
            _LOGGER.info(f"Added refresh comment to issue #{issue['number']}")
        else:
            _LOGGER.debug(f"Refresh comment not added")
    else:
        issue_id = github_open_issue(slug, title, body(), labels)['number']
        _LOGGER.info(f"Reported issue {title!r} with id #{issue_id}")
        return issue_id

    return None


def close_issue_if_exists(slug: str, title: str, comment: str = None):
    """Close the given issue (referenced by its title) and close it with a comment."""
    issue = get_issue(slug, title)
    if not issue:
        _LOGGER.debug(f"Issue {title!r} not found, not closing it")
        return

    github_add_comment(slug, issue['number'], comment, force_add=True)
    github_close_issue(slug, issue['number'])


def open_pull_request(slug: str, commit_msg: str, branch_name: str, pr_body: str, labels: list) -> int:
    """Open a pull request for the given branch."""
    pr_id = github_create_pr(slug, commit_msg, pr_body, branch_name)
    if labels:
        _LOGGER.debug(f"Adding labels to newly created PR #{pr_id}: {labels}")
        github_add_labels(slug, pr_id, labels)

    return pr_id


def add_comment(slug: str, number: int, comment: str) -> None:
    """Add a comment to an issue or pull request."""
    github_add_comment(slug, number, comment)


def list_pull_requests(slug: str, head: str = None) -> list:
    """List pull requests available."""
    return github_list_pull_requests(slug, head=head)


def list_issue_comments(slug: str, issue_number: int) -> list:
    """List comments added to an issue."""
    return github_list_issue_comments(slug, issue_number)


def list_branches(slug: str) -> list:
    """Get branches available on remote."""
    return github_list_branches(slug)


def delete_branch(slug: str, branch_name: str) -> None:
    """Delete the given branch from remote."""
    return github_delete_branch(slug, branch_name)
