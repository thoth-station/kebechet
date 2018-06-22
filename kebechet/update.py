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

"""The real stuff."""

import os
import logging
import toml
import re
import json
import typing
from itertools import chain
from tempfile import TemporaryDirectory

import delegator
import git
import requests

from .config import config
from .exception import PipenvError
from .exception import DependencyManagementError
from .exception import InternalError
from .github import github_create_pr
from .github import github_add_labels
from .utils import cwd


_LOGGER = logging.getLogger(__name__)
# Ignore PycodestyleBear
_RE_VERSION_DELIMITER = re.compile('(==|===|<=|>=|~=|!=|<|>|\[)')

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.


def _get_dependency_version(dependency: str, is_dev: bool) -> str:
    """Get version of the given dependency from Pipfile.lock."""
    try:
        with open('Pipfile.lock') as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        raise PipenvError(
            f"Failed to load Pipfile.lock file: {str(exc)}") from exc

    version = pipfile_lock_content['develop' if is_dev else 'default'].get(
        dependency, {}).get('version')
    if not version:
        raise InternalError(
            f"Failed to retrieve version information for dependency {dependency}, (dev: {is_dev})")

    return version[len('=='):]


def _get_direct_dependencies() -> tuple:
    """Get all direct dependencies stated in the Pipfile file."""
    try:
        pipfile_content = toml.load('Pipfile')
    except Exception as exc:
        raise PipenvError(f"Failed to load Pipfile: {str(exc)}") from exc

    default = list(package_name.lower()
                   for package_name in pipfile_content['packages'].keys())
    develop = list(package_name.lower()
                   for package_name in pipfile_content['dev-packages'].keys())

    return default, develop


def _get_direct_dependencies_requirements() -> set:
    """Get all direct dependencies based on requirements.in file and generated Pipfile.lock from it."""
    with open('requirements.in') as requirements_in_file:
        content = requirements_in_file.read()

    direct_dependencies = set()
    for line in content.splitlines():
        if line.strip().startswith('#'):
            continue

        # TODO: we could reuse pip or pipenv functionality here to parse file.
        package_name = _RE_VERSION_DELIMITER.split(line)[0]
        direct_dependencies.add(package_name.lower())

    return direct_dependencies


def _get_all_packages_versions() -> dict:
    """Parse Pipfile.lock file and retrieve all packages in the corresponding version to which they were locked to."""
    try:
        with open('Pipfile.lock') as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        raise PipenvError(
            f"Failed to load Pipfile.lock file: {str(exc)}") from exc

    result = {}
    for package_name, package_info in pipfile_lock_content['default'].items():
        result[package_name.lower()] = {
            'dev': False,
            'version': package_info['version'][len('=='):]
        }

    for package_name, package_info in pipfile_lock_content['develop'].items():
        result[package_name.lower()] = {
            'dev': False,
            'version': package_info['version'][len('=='):]
        }

    return result


def _get_direct_dependencies_version() -> dict:
    """Get versions of all direct dependencies based on the currently present Pipfile.lock."""
    default, develop = _get_direct_dependencies()

    result = {}
    default, develop = ((dep, False)
                        for dep in default), ((dep, True) for dep in develop)
    for dependency, is_dev in chain(default, develop):
        version = _get_dependency_version(dependency, is_dev=is_dev)
        result[dependency] = {'version': version, 'dev': is_dev}

    return result


def _get_requirements_txt_dependencies() -> dict:
    """Gather dependencies from requirements.txt file, we assume requirements.txt holds fully pinned down stack."""
    result = {}

    with open('requirements.txt', 'r') as requirements_file:
        content = requirements_file.read()

    for line in content.splitlines():
        if line.strip().startswith(('#', '-')):
            continue

        package_and_version = line.split('==', maxsplit=1)
        if len(package_and_version) != 2:
            raise DependencyManagementError(f"File requirements.txt does not state fully locked "
                                            f"dependencies: {line!r} is not fully qualified dependency")
        package_name, package_version = package_and_version
        result[package_name] = {
            # FIXME: tabs?
            'version': package_version.split(r' ', maxsplit=1)[0],
            'dev': False
        }

    return result


def _open_pull_request_update(repo: git.Repo, dependency: str,
                              old_version: str, new_version: str,
                              labels: list, files: list) -> typing.Optional[int]:
    """Open a pull request for dependency update."""
    if not config.github_token:
        _LOGGER.info(
            "Skipping automated pull requests opening - no GitHub OAuth token provided")
        return None

    _LOGGER.info(
        f"Creating a pull request to update {dependency} from version {old_version} to {new_version}")
    branch_name = f'kebechet-{dependency}-{new_version}'
    commit_msg = f"Automatic update of dependency {dependency} from {old_version} to {new_version}"
    pr_body = f'Dependency {dependency} was used in version {old_version}, ' \
              f'but the current latest version is {new_version}.'

    slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]
    owner, repo_name = slug.split('/', maxsplit=1)
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}/pulls',
        params={'head': f'{owner}:{branch_name}'},
        headers={f'Authorization': f'token {config.github_token}'}
    )
    response.raise_for_status()
    response = response.json()

    if len(response) == 0:
        # We don't have update for this package yet, open a PR for it.
        _git_push(repo, commit_msg, branch_name, files)
        return _open_pull_request(repo, commit_msg, branch_name, pr_body, labels)
    elif len(response) == 1:
        # We have already an update for this package - check whether the opened pull request is pull request matching
        # the current master. If not, rebase it to the current master. To avoid merge conflicts, we simple issue git
        # push force to the update branch.
        base_sha = response[0]['base']['sha']
        pr_number = response[0]['number']
        if repo.head.commit.hexsha != base_sha:
            _LOGGER.info(f"Found already existing  pull request #{pr_number} for old master branch {base_sha[:7]!r} "
                         f"updating pull request based on branch {branch_name!r} for the "
                         f"current master branch {repo.head.commit.hexsha[:7]!r}")
            _git_push(repo, commit_msg, branch_name, files, force_push=True)
            # Return PR number directly
            return response[0]['number']
        else:
            _LOGGER.info(f"Found already existing  pull request #{pr_number} for the current master "
                         f"branch {repo.head.commit.hexsha[:7]!r}, "
                         f"not updating pull request")
    else:
        InternalError("Multiple pull requests with same branch name opened.")


def _git_push(repo: git.Repo, commit_msg: str, branch_name: str, files: list, force_push: bool = False) -> None:
    """Perform git push after adding files and giving a commit message."""
    repo.git.checkout('HEAD', b=branch_name)
    repo.index.add(files)
    repo.index.commit(commit_msg)
    repo.remote().push(branch_name, force=force_push)


def _open_pull_request(repo: git.Repo, commit_msg: str, branch_name: str, pr_body: str,
                       labels: list) -> typing.Optional[int]:
    """Open a pull request for the given branch."""
    slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]
    try:
        pr_id = github_create_pr(slug, commit_msg, pr_body, branch_name)
        if labels:
            _LOGGER.debug(
                f"Adding labels to newly created PR #{pr_id}: {labels}")
            github_add_labels(slug, pr_id, labels)
    finally:
        repo.git.checkout('master')

    return pr_id


def _get_all_outdated(old_direct_dependencies: dict) -> dict:
    """Get all outdated packages based on Pipfile.lock."""
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

            _LOGGER.debug(
                f"Found new update for {package_name}: {old_version} -> {new_version} (dev: {is_dev})")
            result[package_name] = {
                'dev': is_dev,  # This should not change
                'old_version': old_version,
                'new_version': new_version
            }

    return result


def _pipenv_lock_requirements() -> None:
    """Perform pipenv lock into requirements.txt file."""
    result = delegator.run('pipenv lock -r ')
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(f"Pipenv lock failed: {result.out}")

    with open('requirements.txt', 'w') as requirements_file:
        requirements_file.write(result.out)


def _create_update(repo: git.Repo, dependency: str, package_version: str, old_version: str,
                   is_dev: bool = False, labels: list = None,
                   old_environment: dict = None) -> typing.Union[tuple, None]:
    """Create an update for the given dependency when dependencies are managed by Pipenv.

    The old environment is set to a non None value only if we are operating on requirements.{in,txt}. It keeps
    information of packages that were present in the old environment so we can selectively change versions in the
    already existing requirements.txt or add packages that were introduced as a transitive dependency.
    """
    pipenv_opts = ['install',
                   f"{dependency}=={package_version}", '--keep-outdated']
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

    if not old_environment:
        pr_id = _open_pull_request_update(
            repo, dependency, old_version, package_version, labels, ['Pipfile.lock'])
        return old_version, package_version, pr_id

    # For requirements.txt scenario we need to propagate all changes (updates of transitive dependencies)
    # into requirements.txt file
    _pipenv_lock_requirements()
    pr_id = _open_pull_request_update(
        repo, dependency, old_version, package_version, labels, ['requirements.txt'])
    return old_version, package_version, pr_id


def _replicate_old_environment(repo: git.Repo, old_environment: dict) -> None:
    """Replicate old environment based on its specification - packages in specific versions."""
    # TODO: pipenv sync?
    _LOGGER.info("Replicating old environment for incremental update")

    dev_packages = []
    default_packages = []
    for package_name in old_environment.keys():
        if old_environment[package_name]['dev']:
            dev_packages.append(
                f"{package_name}=={old_environment[package_name]['version']}")
        else:
            default_packages.append(
                f"{package_name}=={old_environment[package_name]['version']}")

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


def _create_pipenv_environment():
    """Create a pipenv environment - Pipfile and Pipfile.lock from requirements.in file."""
    if not os.path.isfile('requirements.in'):
        raise DependencyManagementError(
            "No dependency management found in the repo (no Pipfile nor requirments.in)")

    _LOGGER.debug("Installing dependencies from requirements.in")
    result = delegator.run('pipenv install -r requirements.in --pre')
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(
            f"Pipenv failed to install dependencies from requirements.in: {result.out}")


def _create_initial_lock_requirements(repo: git.Repo, labels) -> list:
    """Perform initial requirements lock into requirements.txt file."""
    _pipenv_lock_requirements()
    pr_id = _open_pull_request(
        repo,
        "Initial dependency lock", 'kebechet-initial-lock',
        "Initially lock all packages stated in requirements.in file in requirements.txt",
        labels,
        ['requirements.txt']
    )

    packages = _get_all_packages_versions()

    # Be compatible with return value of update().
    return [(p, None, e['version'], pr_id) for p, e in packages.items()]


def _do_update(repo: git.Repo, labels: list, pipenv_used: bool = False) -> list:
    """Update dependencies based on management used."""
    if not pipenv_used and not os.path.isfile('requirements.txt'):
        # First time lock, open a PR
        _LOGGER.info("Initial requirements.lock will be done")
        return _create_initial_lock_requirements(repo, labels)

    if pipenv_used:
        old_environment = _get_all_packages_versions()
        old_direct_dependencies_version = _get_direct_dependencies_version()
    else:
        old_environment = _get_requirements_txt_dependencies()
        direct_dependencies = _get_direct_dependencies_requirements()
        old_direct_dependencies_version = {
            k: v for k, v in old_environment.items() if k in direct_dependencies}

    outdated = _get_all_outdated(old_direct_dependencies_version)
    _LOGGER.info(f"Outdated: {outdated}")

    result = []
    slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]
    for package_name in outdated.keys():
        _replicate_old_environment(repo, old_environment)

        is_dev = outdated[package_name]['dev']
        try:
            _LOGGER.info(
                f"Creating update of dependency {package_name} in repo {slug} (devel: {is_dev})")
            versions = _create_update(
                repo, package_name,
                outdated[package_name]['new_version'], outdated[package_name]['old_version'],
                is_dev=is_dev, labels=labels, old_environment=old_environment if not pipenv_used else None
            )
            if versions:
                result.append({package_name: versions})
        except Exception as exc:
            _LOGGER.exception(
                f"Failed to create update for dependency {package_name}: {str(exc)}")

    return result


def update(slug: str, labels: list) -> list:
    """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
    os.environ['PIPENV_VENV_IN_PROJECT'] = '1'

    with TemporaryDirectory() as repo_path:
        with cwd(repo_path):
            repo_url = f'git@github.com:{slug}.git'
            _LOGGER.info(f"Cloning repository {repo_url} to {repo_path}")
            repo = git.Repo.clone_from(
                repo_url, repo_path, branch='master', depth=1)

            if os.path.isfile('Pipfile'):
                _LOGGER.info("Using Pipfile for dependency management")
                return _do_update(repo, labels, pipenv_used=True)
            elif os.path.isfile('requirements.in'):
                _create_pipenv_environment()
                _LOGGER.info("Using requirments.in for dependency management")
                return _do_update(repo, labels, pipenv_used=False)
            else:
                raise DependencyManagementError("There was found an issue in your dependency "
                                                "management - there was not found Pipfile nor requirements.in")
