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
