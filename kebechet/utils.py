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

"""Just some utility methods."""


import os
import logging
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from urllib.parse import urljoin

import git

from .enums import ServiceType

_LOGGER = logging.getLogger(__name__)


@contextmanager
def cwd(path: str):
    """Change working directory in a push-pop manner with context manager."""
    previous_dir = os.getcwd()
    try:
        os.chdir(path)
        yield previous_dir
    finally:
        os.chdir(previous_dir)


@contextmanager
def cloned_repo(service_url: str, slug: str):
    """Clone the given Git repository and cd into it."""
    if service_url.startswith('https://'):
        service_url = service_url[len('https://'):]
    elif service_url.startswith('http://'):
        service_url = service_url[len('http://'):]
    else:
        # This is mostly internal error - we require service URL to have protocol explicitly set
        raise NotImplementedError

    repo_url = f'git@{service_url}:{slug}.git'
    with TemporaryDirectory() as repo_path, cwd(repo_path):
        _LOGGER.info(f"Cloning repository {repo_url} to {repo_path}")
        repo = git.Repo.clone_from(repo_url, repo_path, branch='master', depth=1)
        repo.config_writer().set_value(
            'user', 'name', os.getenv('KEBECHET_GIT_NAME', 'Kebechet')
        ).release()
        repo.config_writer().set_value(
            'user', 'email', os.getenv('KEBECHET_GIT_EMAIL', 'noreply+kebechet@redhat.com')
        ).release()
        yield repo


def construct_raw_file_url(service_url: str, slug: str, file_name: str,
                           service_type: ServiceType, branch: str = None) -> str:
    """Get URL to a raw file - useful for downloads of content."""
    branch = branch or 'master'
    if service_type == ServiceType.GITHUB:
        # TODO self hosted GitHub?
        url = f'https://raw.githubusercontent.com/{slug}/{branch}/{file_name}'
    elif service_type == ServiceType.GITLAB:
        url = urljoin(service_url, f'{slug}/raw/{branch}/{file_name}')
    else:
        raise NotImplementedError

    return url
