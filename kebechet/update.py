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
import typing
from itertools import chain
from tempfile import TemporaryDirectory

import git
import delegator

from .config import config
from .exception import PipenvError
from .exception import InternalError
from .github import github_create_pr
from .github import github_add_labels
from .utils import cwd

_LOGGER = logging.getLogger(__name__)

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.

def _get_dependency_version(dependency: str, is_dev: bool) -> str:
    """Get version of the given dependency from Pipfile.lock."""
    try:
        with open('Pipfile.lock') as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile.lock file: {str(exc)}") from exc

    if is_dev:
        version = pipfile_lock_content['develop'].get(dependency, {}).get('version')
    else:
        version = pipfile_lock_content['default'].get(dependency, {}).get('version')

    if not version:
        raise InternalError(f"Failed to retrieve version information for dependency {dependency}, (dev: {is_dev})")

    return version[len('=='):]


def _get_direct_dependencies() -> tuple:
    """Get all direct dependencies stated in the Pipfile file."""
    try:
        pipfile_content = toml.load('Pipfile')
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile: {str(exc)}") from exc

    default = list(pipfile_content['packages'].keys())
    develop = list(pipfile_content['dev-packages'].keys())

    return default, develop


def _get_all_packages_versions() -> dict:
    try:
        with open('Pipfile.lock') as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile.lock file: {str(exc)}") from exc

    result = {}
    for package_name, package_info in pipfile_lock_content['default'].items():
        result[package_name] = {
            'dev': False,
            'version': package_info['version'][len('=='):]
        }

    for package_name, package_info in pipfile_lock_content['develop'].items():
        result[package_name] = {
            'dev': False,
            'version': package_info['version'][len('=='):]
        }

    return result


def _get_direct_dependencies_version() -> dict:
    """Get versions of all direct dependencies."""
    default, develop = _get_direct_dependencies()

    result = {}
    default, develop = ((dep, False) for dep in default), ((dep, True) for dep in develop)
    for dependency, is_dev in chain(default, develop):
        version = _get_dependency_version(dependency, is_dev=is_dev)
        result[dependency] = {'version': version, 'dev': is_dev}

    return result


def _get_all_outdated() -> dict:
    """Get all outdated packages based on Pipfile.lock"""
    old_direct_dependencies = _get_direct_dependencies_version()

    # We need to install environment first as this command is the first command run.
    result = delegator.run('pipenv install --dev')
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv install failed: {result.out}")

    new_direct_dependencies = _get_direct_dependencies_version()

    result = {}
    for package_name in old_direct_dependencies.keys():
        if old_direct_dependencies[package_name]['version'] != new_direct_dependencies[package_name]['version']:
            old_version = old_direct_dependencies[package_name]['version']
            new_version = new_direct_dependencies[package_name]['version']
            is_dev = old_direct_dependencies[package_name]['dev']

            _LOGGER.debug(f"Found new update for {package_name}: {old_version} -> {new_version} (dev: {is_dev})")
            result[package_name] = {
                'dev': is_dev,  # This should not change
                'old_version': old_version,
                'new_version': new_version
            }

    return result


def _create_update(repo: git.Repo, dependency: str, package_version: str,
                   is_dev: bool=False, labels: list=None) -> typing.Union[tuple, None]:
    """Create an update for the given dependency, if an update is possible."""
    old_version = _get_dependency_version(dependency, is_dev)

    pipenv_opts = ['install', f"{dependency}=={package_version}", '--keep-outdated']
    if is_dev:
        pipenv_opts.append('--dev')

    result = delegator.run('pipenv ' + ' '.join(pipenv_opts))
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv install failed: {result.out}")

    pipenv_opts = ['lock', '--keep-outdated']
    result = delegator.run('pipenv ' + ' '.join(pipenv_opts))
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv lock failed: {result.out}")

    new_version = _get_dependency_version(dependency, is_dev)
    _LOGGER.info(f"Creating a pull request to update {dependency} from version {old_version} to {new_version}")
    branch_name = f'kebechet-{dependency}-{new_version}'
    repo.git.checkout('HEAD', b=branch_name)
    repo.index.add(['Pipfile.lock'])
    commit_msg = f"Automatic update of dependency {dependency} from {old_version} to {new_version}"
    repo.index.commit(commit_msg)
    repo.remote().push(branch_name)

    if not config.github_token:
        _LOGGER.info("Skipping automated pull requests opening - no GitHub OAuth token provided")
        return old_version, new_version, None

    slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]
    try:
        pr_body = f'Dependency {dependency} was used in version {old_version}, ' \
                  f'but the current latest version is {new_version}.'
        pr_id = github_create_pr(slug, commit_msg, pr_body, branch_name)
        if labels:
            _LOGGER.debug(f"Adding labels to newly created PR #{pr_id}: {labels}")
            github_add_labels(slug, pr_id, labels)
    finally:
        # TODO: we should probably be more strict with failures if any and fully recover here to a working master
        repo.git.checkout('master')

    return old_version, new_version, pr_id


def _replicate_old_environment(repo, outdated: dict) -> None:
    # TODO: pipenv sync?
    _LOGGER.info("Replicating old environment for incremental update")
    dev_packages = []
    default_packages = []
    for package_name in outdated.keys():
        if outdated[package_name]['dev']:
            dev_packages.append(f"{package_name}=={outdated[package_name]['version']}")
        else:
            default_packages.append(f"{package_name}=={outdated[package_name]['version']}")

    result = delegator.run('pipenv install ' + ' '.join(default_packages))
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv install failed: {result.out}")

    result = delegator.run('pipenv install --dev ' + ' '.join(dev_packages))
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv install failed: {result.out}")

    result = delegator.run('pipenv lock')
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv lock failed: {result.out}")

    # Discard changes made to Pipenv by pipenv itself. We will open one pull request per update.
    repo.head.reset(index=True, working_tree=True)


def update(slug: str, labels: list) -> list:
    """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
    result = []
    os.environ['PIPENV_VENV_IN_PROJECT'] = '1'

    with TemporaryDirectory() as repo_path:
        with cwd(repo_path):
            repo_url = f'git@github.com:{slug}.git'
            _LOGGER.info(f"Cloning repository {repo_url} to {repo_path}")
            repo = git.Repo.clone_from(repo_url, repo_path, branch='master', depth=1)

            old_environment = _get_all_packages_versions()
            outdated = _get_all_outdated()
            _LOGGER.info(f"Outdated: {outdated}")

            for package_name in outdated.keys():
                _replicate_old_environment(repo, old_environment)

                is_dev = outdated[package_name]['dev']
                try:
                    _LOGGER.info(f"Creating update of dependency {package_name} in repo {slug} (devel: {is_dev})")
                    versions = _create_update(repo, package_name, outdated[package_name]['new_version'],
                                              is_dev=is_dev, labels=labels)
                    if versions:
                        result.append({package_name: versions})
                except Exception as exc:
                    _LOGGER.exception(f"Failed to create update for dependency {package_name}: {str(exc)}")

    return result

