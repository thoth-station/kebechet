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

"""Common GitHub operations."""

# TODO: replace this with a lib that also covers GitLab.

import logging
import typing

import requests

from .config import config
from .exception import PullRequestError

_LOGGER = logging.getLogger(__name__)


def github_create_pr(slug: str, title: str, body: str, source_branch: str) -> int:
    """Create a GitHub pull request with the given dependency update."""
    url = f'https://api.github.com/repos/{slug}/pulls'
    response = requests.post(
        url,
        headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {config.github_token}'
        },
        json={
            'title': title,
            'body': body,
            'head': source_branch,
            'base': 'master',
            'maintainer_can_modify': True
        }
    )
    try:
        response.raise_for_status()
    except Exception as exc:
        raise PullRequestError(f"Failed to create a pull request: {response.text}") from exc

    _LOGGER.info(f"Newly created pull request #{response.json()['number']} "
                 f"available at {response.json()['html_url']}")
    return response.json()['number']


def github_add_labels(slug: str, issue_id: int, labels: list) -> None:
    """All a list of labels to an Issue."""
    url = f'https://api.github.com/repos/{slug}/issues/{issue_id}/labels'
    response = requests.post(
        url,
        headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {config.github_token}'
        },
        json=labels
    )
    response.raise_for_status()


def github_list_pull_requests(slug: str, head: str = None) -> list:
    """List GitHub pull requests.

    Optionally you can specify head to be used as a filter.
    """
    params = {}
    if head:
        params['head'] = head

    response = requests.get(
        f'https://api.github.com/repos/{slug}/pulls',
        params=params,
        headers={f'Authorization': f'token {config.github_token}'}
    )
    response.raise_for_status()
    # TODO: pagination?
    return response.json()


def github_list_issues(slug: str) -> list:
    """List GitHub issues."""
    # This will list open pull requests (see state parameter in docs)- that is what we want.
    response = requests.get(
        f'https://api.github.com/repos/{slug}/issues',
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    # TODO: pagination?
    return response.json()


def github_open_issue(slug: str, title: str, body: str, labels: list = None) -> dict:
    """Open an issue on GitHub."""
    response = requests.post(
        f'https://api.github.com/repos/{slug}/issues',
        json={
            'title': title,
            'body': body,
            'labels': labels
        },
        headers={f'authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    return response.json()


def github_get_issue(slug: str, issue_id: int) -> dict:
    """Get the given issue."""
    response = requests.get(
        f'https://api.github.com/repos/{slug}/issues/{issue_id}',
        headers={f'authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    return response.json()


def github_add_comment(slug: str, issue_id: int, comment_body: str, force_add: bool = False) -> typing.Optional[dict]:
    """Add a comment to GitHub issue.

    The comment will be added only if label 'silent-bot' is not set - this behaviour can be suppressed
    with `force_add` set to True.
    """
    if not force_add:
        issue = github_get_issue(slug, issue_id)
        for label in issue['labels']:
            if label['name'] == 'silent-bot':
                # We should be quiet.
                return None

    response = requests.post(
        f'https://api.github.com/repos/{slug}/issues/{issue_id}/comments',
        json={'body': comment_body},
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    return response.json()


def github_list_issue_comments(slug: str, issue_id: int) -> list:
    """List comments for the given GitHub issue."""
    response = requests.get(
        f'https://api.github.com/repos/{slug}/issues/{issue_id}/comments',
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    # TODO: pagination
    return response.json()


def github_close_issue(slug: str, issue_id: int) -> dict:
    """Close the given GitHub issue."""
    response = requests.patch(
        f'https://api.github.com/repos/{slug}/issues/{issue_id}',
        json={'state': 'closed'},
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    return response.json()


def github_delete_branch(slug: str, branch: str) -> None:
    """Delete the given branch from remote repository."""
    response = requests.delete(
        f'https://api.github.com/repos/{slug}/git/refs/heads/{branch}',
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    # GitHub returns an empty string, noting to return.


def github_get_branches(slug: str) -> list:
    """Get listing of all branches available on remote repository."""
    response = requests.get(
        f'https://api.github.com/repos/{slug}/branches',
        headers={f'Authorization': f'token {config.github_token}'}
    )

    response.raise_for_status()
    # TODO: pagination
    return response.json()
