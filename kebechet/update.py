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

import os
import logging
import toml
import json
from itertools import chain
from tempfile import TemporaryDirectory

import git
from pipenv.core import do_install as pipenv_install

from .exception import PipenvError
from .exception import InternalError
from .utils import cwd

_LOGGER = logging.getLogger(__name__)


def _get_dependency_version(repo: git.Repo, dependency: str) -> str:
    pipfile_lock_path = os.path.join(repo.working_dir, 'Pipfile.lock')
    try:
        with open(pipfile_lock_path) as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile.lock file: {str(exc)}") from exc

    version = pipfile_lock_content['default'].get(dependency, {}).get('version')
    if not version:
        # Fallback to dev dependencies
        version = pipfile_lock_content['develop'].get(dependency, {}).get('version')

    if not version:
        raise InternalError(f"Failed to retrieve version information for dependency {dependency}")

    return version


def _get_direct_dependencies(repo: git.Repo) -> tuple:
    """Get all direct dependencies stated in the Pipfile file."""
    pipfile_path = os.path.join(repo.working_dir, 'Pipfile')
    try:
        pipfile_content = toml.load(pipfile_path)
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile: {str(exc)}") from exc

    default = list(pipfile_content['packages'].keys())
    develop = list(pipfile_content['dev-packages'].keys())

    return default, develop


def _create_update(repo: git.repo, dependency: str, is_dev: bool=False) -> tuple:
    old_version = _get_dependency_version(repo, dependency)
    pipenv_install(dependency, selective_upgrade=True, keep_outdated=True, dev=is_dev, three=True)
    new_version = _get_dependency_version(repo, dependency)

    if old_version != new_version:
        branch_name = f'kebechet-update-{new_version}'
        repo.git.checkout('HEAD', b=branch_name)
        repo.index.add(['Pipfile.lock'])
        repo.index.commit(f"Update of dependency {dependency} from {old_version} to {new_version}")
        repo.remote().push(branch_name)
        # TODO: we should probably recover from failures so next rounds will work as expected
        repo.git.checkout('master')

    return old_version, new_version


def update(slug: str) -> list:
    """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
    result = []

    with TemporaryDirectory() as repo_path, cwd(repo_path):
        repo_url = f'git@github.com:{slug}.git'
        _LOGGER.debug(f"Cloning repository {repo_url} to {repo_path}")
        repo = git.Repo.clone_from(repo_url, repo_path, branch='master')

        _LOGGER.debug("Retrieving direct dependencies stated in Pipfile")
        default, develop = _get_direct_dependencies(repo)

        default, develop = ((dep, False) for dep in default), ((dep, True) for dep in develop)
        for dependency, is_dev in chain(default, develop):
            try:
                _LOGGER.debug(f"Creating update for dependency {dependency} in repo {slug}")
                versions = _create_update(repo, dependency, is_dev=is_dev)
                if versions:
                    result.append({dependency: versions})
            except Exception as exc:
                _LOGGER.exception(f"Failed to create update for dependency {dependency}: {str(exc)}")

    return result
