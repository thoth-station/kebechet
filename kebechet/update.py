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

"""Dependency update management logic."""

import os
import logging
import toml
import re
import json
import typing
from itertools import chain
import platform
from tempfile import TemporaryDirectory
from functools import partial

import delegator
import git
import kebechet

from .exception import PipenvError
from .exception import DependencyManagementError
from .exception import InternalError
from .github import github_create_pr
from .github import github_add_comment
from .github import github_add_labels
from .github import github_list_pull_requests
from .github import github_list_issues
from .github import github_list_issue_comments
from .github import github_open_issue
from .github import github_close_issue
from .github import github_delete_branch
from .github import github_get_branches
from .messages import ISSUE_PIPENV_UPDATE_ALL
from .messages import ISSUE_COMMENT_UPDATE_ALL
from .messages import ISSUE_INITIAL_LOCK
from .messages import ISSUE_CLOSE_COMMENT
from .messages import ISSUE_NO_DEPENDENCY_MANAGEMENT
from .messages import ISSUE_REPLICATE_ENV
from .utils import cwd


_LOGGER = logging.getLogger(__name__)
_RE_VERSION_DELIMITER = re.compile('(==|===|<=|>=|~=|!=|<|>|\\[)')

_ISSUE_UPDATE_ALL_NAME = "Failed to update dependencies to their latest version"
_ISSUE_INITIAL_LOCK_NAME = "Failed to perform initial lock of software stack"
_ISSUE_REPLICATE_ENV_NAME = "Failed to replicate environment for updates"
_ISSUE_NO_DEPENDENCY_NAME = "No dependency management found"

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.


def _run_pipenv(cmd: str):
    """Run pipenv, raise :ref:kebechet.exception.PipenvError on any error holding all the ingormation."""
    _LOGGER.debug(f"Running pipenv command {cmd!r}")
    result = delegator.run(cmd)
    if result.return_code != 0:
        _LOGGER.error(result.err)
        raise PipenvError(result)

    return result.out


def _get_environment_details() -> str:
    try:
        pipenv_version = _run_pipenv('pipenv --version')
    except PipenvError as exc:
        pipenv_version = f"Failed to obtain pipenv version:\n{exc.stderr}"

    return f"""
Kebechet version: {kebechet.__version__}
Python version: {platform.python_version()}
Platform: {platform.platform()}
pipenv version: {pipenv_version}
"""


def _get_dependency_graph(graceful: bool = False):
    try:
        _run_pipenv('pipenv install --dev --skip-lock')
        return _run_pipenv('pipenv graph')
    except PipenvError as exc:
        if not graceful:
            raise
        return f"Unable to obtain dependency graph:\n\n{exc.stderr}"


def _get_dependency_version(dependency: str, is_dev: bool) -> str:
    """Get version of the given dependency from Pipfile.lock."""
    try:
        with open('Pipfile.lock') as pipfile_lock:
            pipfile_lock_content = json.load(pipfile_lock)
    except Exception as exc:
        # TODO: open a PR to fix this
        raise DependencyManagementError(f"Failed to load Pipfile.lock file: {str(exc)}") from exc

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
        # TODO: open a PR to fix this
        raise DependencyManagementError(f"Failed to load Pipfile: {str(exc)}") from exc

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
        # TODO: open a PR to fix this
        raise DependencyManagementError(f"Failed to load Pipfile.lock file: {str(exc)}") from exc

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


def _construct_branch_name(package_name: str, new_package_version: str) -> str:
    """Construct branch name for the updated dependency."""
    return f'kebechet-{package_name}-{new_package_version}'


def _open_pull_request_update(repo: git.Repo, dependency: str,
                              old_version: str, new_version: str,
                              labels: list, files: list, pr_number: int) -> typing.Optional[int]:
    """Open a pull request for dependency update."""
    branch_name = _construct_branch_name(dependency, new_version)
    commit_msg = f"Automatic update of dependency {dependency} from {old_version} to {new_version}"

    # If we have already an update for this package we simple issue git
    # push force always to keep branch up2date with the recent master and avoid merge conflicts.
    _git_push(repo, commit_msg, branch_name, files, force_push=True)

    if pr_number < 0:
        _LOGGER.info(f"Creating a pull request to update {dependency} from version {old_version} to {new_version}")
        pr_body = f'Dependency {dependency} was used in version {old_version}, ' \
                  f'but the current latest version is {new_version}.'
        pr_id = _open_pull_request(repo, commit_msg, branch_name, pr_body, labels)
        return pr_id

    _LOGGER.info(f"Pull request #{pr_number} to update {dependency} from "
                 f"version {old_version} to {new_version} updated")
    github_add_comment(
        _get_slug(repo),
        pr_number,
        f"Pull request has been rebased on top of the current master with SHA {repo.head.commit.hexsha}"
    )
    return pr_number


def _get_issue(repo, title: str) -> typing.Optional[dict]:
    """Retrieve issue with the given title."""
    slug = _get_slug(repo)
    for issue in github_list_issues(slug):
        if issue['title'] == title:
            return issue

    return None


def _open_issue_if_not_exist(repo: git.Repo, title: str, body: typing.Callable,
                             refresh_comment: typing.Callable = None, labels: list = None) -> typing.Optional[int]:
    """Open the given issue if does not exist already (as opened)."""
    slug = _get_slug(repo)

    _LOGGER.debug(f"Reporting issue {title!r}")
    issue = _get_issue(repo, title)
    if issue:
        _LOGGER.info(f"Issue already noted on upstream with id #{issue['number']}")
        if not refresh_comment:
            return None

        comment_body = refresh_comment(repo, issue)
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


def _close_issue_if_exists(repo: git.Repo, title: str, comment: str = None):
    issue = _get_issue(repo, title)
    if not issue:
        _LOGGER.debug(f"Issue {title!r} not found, not closing it")
        return

    slug = _get_slug(repo)
    github_add_comment(slug, issue['number'], comment, force_add=True)
    github_close_issue(slug, issue['number'])


def _get_slug(repo: git.Repo) -> str:
    """Get slug (org/repo) for a repo."""
    return repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]


def _should_update(repo: git.Repo, package_name, new_package_version) -> tuple:
    """Check whether the given update was already proposed as a pull request."""
    slug = _get_slug(repo)
    owner, repo_name = slug.split('/', maxsplit=1)
    branch_name = _construct_branch_name(package_name, new_package_version)
    response = github_list_pull_requests(slug, head=f'{owner}:{branch_name}')

    if len(response) == 0:
        _LOGGER.debug(f"No pull request was found for update of {package_name} to version {new_package_version}")
        return -1, True
    elif len(response) == 1:
        base_sha = response[0]['base']['sha']
        pr_number = response[0]['number']
        if repo.head.commit.hexsha != base_sha:
            _LOGGER.debug(f"Found already existing  pull request #{pr_number} for old master branch {base_sha[:7]!r} "
                          f"updating pull request based on branch {branch_name!r} for the "
                          f"current master branch {repo.head.commit.hexsha[:7]!r}")
            return response[0]['number'], True
        else:
            _LOGGER.debug(f"Found already existing  pull request #{pr_number} for the current master "
                          f"branch {repo.head.commit.hexsha[:7]!r}, "
                          f"not updating pull request")
            return response[0]['number'], False
    else:
        raise InternalError(f"Multiple ({len(response)}) pull requests with same branch name {branch_name!r} opened.")


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
    new_direct_dependencies = _get_direct_dependencies_version()

    result = {}
    for package_name in old_direct_dependencies.keys():
        if old_direct_dependencies[package_name]['version'] \
                != new_direct_dependencies.get(package_name, {}).get('version'):
            old_version = old_direct_dependencies[package_name]['version']
            new_version = new_direct_dependencies.get(package_name, {}).get('version')
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
    result = _run_pipenv('pipenv lock -r ')
    with open('requirements.txt', 'w') as requirements_file:
        requirements_file.write(result)


def _create_update(repo: git.Repo, dependency: str, package_version: str, old_version: str,
                   is_dev: bool = False, labels: list = None,
                   old_environment: dict = None, pr_number: int = False) -> typing.Union[tuple, None]:
    """Create an update for the given dependency when dependencies are managed by Pipenv.

    The old environment is set to a non None value only if we are operating on requirements.{in,txt}. It keeps
    information of packages that were present in the old environment so we can selectively change versions in the
    already existing requirements.txt or add packages that were introduced as a transitive dependency.
    """
    cmd = f'pipenv install {dependency}=={package_version} --keep-outdated'
    if is_dev:
        cmd += ' --dev'
    _run_pipenv(cmd)
    _run_pipenv('pipenv lock --keep-outdated')

    if not old_environment:
        pr_id = _open_pull_request_update(
            repo, dependency, old_version, package_version, labels, ['Pipfile.lock'], pr_number)
        return old_version, package_version, pr_id

    # For requirements.txt scenario we need to propagate all changes (updates of transitive dependencies)
    # into requirements.txt file
    _pipenv_lock_requirements()
    pr_id = _open_pull_request_update(
        repo, dependency, old_version, package_version, labels, ['requirements.txt'], pr_number)
    return old_version, package_version, pr_id


def _replicate_old_environment() -> None:
    """Replicate old environment based on its specification - packages in specific versions."""
    _LOGGER.info("Replicating old environment for incremental update")
    _run_pipenv('pipenv sync --dev')


def _create_pipenv_environment() -> None:
    """Create a pipenv environment - Pipfile and Pipfile.lock from requirements.in file."""
    if not os.path.isfile('requirements.in'):
        raise DependencyManagementError("No dependency management found in the repo (no Pipfile nor requirements.in)")

    _LOGGER.debug("Installing dependencies from requirements.in")
    _run_pipenv('pipenv install -r requirements.in')


def _create_initial_lock(repo: git.Repo, labels: list, pipenv_used: bool) -> bool:
    """Perform initial requirements lock into requirements.txt file."""
    # We use lock_func to optimize run - it will be called only if actual locking needs to be performed.
    if not pipenv_used and not os.path.isfile('requirements.txt'):
        _LOGGER.info("Initial lock based on requirements.in will be done")
        lock_func = _pipenv_lock_requirements
    elif pipenv_used and not os.path.isfile('Pipfile.lock'):
        _LOGGER.info("Initial lock based on Pipfile will be done")
        lock_func = partial(_run_pipenv, 'pipenv lock')
    else:
        return False

    branch_name = "kebechet-initial-lock"
    slug = _get_slug(repo)
    owner, repo_name = slug.split('/', maxsplit=1)
    response = github_list_pull_requests(slug, head=f'{owner}:{branch_name}')
    files = ['requirements.txt' if not pipenv_used else 'Pipfile.lock']

    commit_msg = "Initial dependency lock"
    if len(response) == 0:
        lock_func()
        _git_push(repo, commit_msg, branch_name, files)
        pr_id = _open_pull_request(repo, commit_msg, branch_name, pr_body='', labels=labels)
        _LOGGER.info(f"Initial dependency lock present in PR #{pr_id}")
    elif len(response) == 1:
        base_sha = response[0]['base']['sha']
        pr_number = response[0]['number']
        if repo.head.commit.hexsha != base_sha:
            lock_func()
            _git_push(repo, commit_msg, branch_name, files, force_push=True)
            github_add_comment(
                _get_slug(repo),
                pr_number,
                f"Pull request has been rebased on top of the current master with SHA {repo.head.commit.hexsha}"
            )
        else:
            _LOGGER.info(f"Pull request #{pr_number} is up to date for the current master branch")
    else:
        raise DependencyManagementError(f"Found two pull requests for initial "
                                        f"requirements lock for branch {branch_name}")

    return True


def _pipenv_update_all():
    """Update all dependencies to their latest version."""
    _LOGGER.info("Updating all dependencies to their latest version")
    _run_pipenv('pipenv update --dev')
    _run_pipenv('pipenv lock')


def _add_refresh_comment(exc: PipenvError, repo: git.Repo, issue: dict) -> typing.Optional[str]:
    """Create a refresh comment to an issue if the given master has some changes."""
    slug = _get_slug(repo)
    sha = repo.head.commit.hexsha

    if sha in issue['body']:
        _LOGGER.debug("No need to update refresh comment, the issue is up to date")
        return

    for issue_comment in github_list_issue_comments(slug, issue['number']):
        if sha in issue_comment['body']:
            _LOGGER.debug(f"No need to update refresh comment, comment for the current "
                          f"master {sha[:7]!r} found in a comment")
            break
    else:
        return ISSUE_COMMENT_UPDATE_ALL.format(
            sha=repo.head.commit.hexsha,
            slug=_get_slug(repo),
            environment_details=_get_environment_details(),
            dependency_graph=_get_dependency_graph(graceful=True),
            **exc.__dict__
        )


def _relock_all(repo: git.Repo, exc: PipenvError, labels: list) -> None:
    """Re-lock all dependencies given the Pipfile."""
    issue_id = _open_issue_if_not_exist(
        repo,
        _ISSUE_REPLICATE_ENV_NAME,
        lambda: ISSUE_REPLICATE_ENV.format(
            **exc.__dict__, sha=repo.head.commit.hexsha,
            slug=_get_slug(repo),
            environment_details=_get_environment_details()
        ),
        refresh_comment=partial(_add_refresh_comment, exc),
        labels=labels
    )

    _pipenv_update_all()
    commit_msg = "Automatic dependency re-locking"
    branch_name = "kebechet-dependency-relock"
    _git_push(repo, commit_msg, branch_name, ['Pipfile.lock'])
    pr_id = _open_pull_request(
        repo,
        commit_msg,
        branch_name,
        f"Fixes: #{issue_id}",
        labels,
    )

    _LOGGER.info(f"Issued automatic dependency re-locking in PR #{pr_id} to fix issue #{issue_id}")


def _delete_old_branches(slug: str, outdated: dict) -> None:
    """Delete old kebechet branches from the remote repository."""
    branches = {entry['name'] for entry in github_get_branches(slug) if entry['name'].startswith('kebechet-')}
    for package_name, info in outdated.items():
        # Do not remove active branches - branches we issued PRs in.
        branch_name = _construct_branch_name(package_name, info['new_version'])
        try:
            branches.remove(branch_name)
        except KeyError:
            # e.g. if there was an issue with PR opening.
            pass

    for branch_name in branches:
        _LOGGER.debug(f"Deleting old branch {branch_name}")
        try:
            github_delete_branch(slug, branch_name)
        except Exception:
            _LOGGER.exception(f"Failed to delete inactive branch {branch_name}")


def _do_update(repo: git.Repo, labels: list, pipenv_used: bool = False) -> dict:
    """Update dependencies based on management used."""
    # Check for first time (initial) locks first.
    try:
        if _create_initial_lock(repo, labels, pipenv_used):
            return {}
    except PipenvError as exc:
        _LOGGER.exception("Failed to perform initial dependency lock")
        _open_issue_if_not_exist(
            repo,
            _ISSUE_INITIAL_LOCK_NAME,
            body=lambda: ISSUE_INITIAL_LOCK.format(
                sha=repo.head.commit.hexsha,
                slug=_get_slug(repo),
                file='requirements.in' if not pipenv_used else 'Pipfile',
                environment_details=_get_environment_details(),
                **exc.__dict__
            ),
            refresh_comment=partial(_add_refresh_comment, exc),
            labels=labels
        )
        raise
    else:
        _close_issue_if_exists(
            repo,
            _ISSUE_INITIAL_LOCK_NAME,
            comment=ISSUE_CLOSE_COMMENT.format(sha=repo.head.commit.hexsha)
        )

    if pipenv_used:
        old_environment = _get_all_packages_versions()
        old_direct_dependencies_version = _get_direct_dependencies_version()
        try:
            _pipenv_update_all()
        except PipenvError as exc:
            _LOGGER.warning("Failed to update dependencies to their latest version, reporting issue")
            _open_issue_if_not_exist(
                repo,
                _ISSUE_UPDATE_ALL_NAME,
                body=lambda: ISSUE_PIPENV_UPDATE_ALL.format(
                    sha=repo.head.commit.hexsha,
                    slug=_get_slug(repo),
                    environment_details=_get_environment_details(),
                    dependency_graph=_get_dependency_graph(graceful=True),
                    **exc.__dict__
                ),
                refresh_comment=partial(_add_refresh_comment, exc),
                labels=labels
            )
            return {}
        else:
            # We were able to update all, close reported issue if any.
            _close_issue_if_exists(
                repo,
                _ISSUE_UPDATE_ALL_NAME,
                comment=ISSUE_CLOSE_COMMENT.format(sha=repo.head.commit.hexsha)
            )
    else:  # requirements.txt
        old_environment = _get_requirements_txt_dependencies()
        direct_dependencies = _get_direct_dependencies_requirements()
        old_direct_dependencies_version = {k: v for k, v in old_environment.items() if k in direct_dependencies}

    outdated = _get_all_outdated(old_direct_dependencies_version)
    _LOGGER.info(f"Outdated: {outdated}")

    # Undo changes made to Pipfile.lock by _pipenv_update_all.
    repo.head.reset(index=True, working_tree=True)

    result = {}
    slug = _get_slug(repo)
    for package_name in outdated.keys():
        # As an optimization, first check if the given PR is already present.
        new_version = outdated[package_name]['new_version']
        old_version = outdated[package_name]['old_version']

        pr_number, should_update = _should_update(repo, package_name, new_version)
        if not should_update:
            _LOGGER.info(f"Skipping update creation for {package_name} from version {old_version} to "
                         f"{new_version} as the given update already exists in PR #{pr_number}")
            continue

        try:
            _replicate_old_environment()
        except PipenvError as exc:
            # There has been an error in locking dependencies. This can be due to a missing dependency or simply
            # currently locked dependencies are not correct. Try to issue a pull request that would fix that. We know
            # that update all works, use update.
            _LOGGER.warning("Failed to replicate old environment, re-locking all dependencies")
            _relock_all(repo, exc, labels)
            return {}

        is_dev = outdated[package_name]['dev']
        try:
            _LOGGER.info(f"Creating update of dependency {package_name} in repo {slug} (devel: {is_dev})")
            versions = _create_update(
                repo, package_name, new_version, old_version,
                is_dev=is_dev,
                labels=labels,
                old_environment=old_environment if not pipenv_used else None,
                pr_number=pr_number
            )
            if versions:
                result[package_name] = versions
        except Exception as exc:
            _LOGGER.exception(f"Failed to create update for dependency {package_name}: {str(exc)}")
        finally:
            repo.head.reset(index=True, working_tree=True)

    # We know that locking was done correctly - if the issue is still open, close it. The issue
    # should be automatically closed by merging the generated PR.
    _close_issue_if_exists(
        repo,
        _ISSUE_REPLICATE_ENV_NAME,
        comment=ISSUE_CLOSE_COMMENT.format(sha=repo.head.commit.hexsha)
    )

    _delete_old_branches(slug, outdated)
    return result


def update(slug: str, labels: list) -> dict:
    """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
    os.environ['PIPENV_VENV_IN_PROJECT'] = '1'

    with TemporaryDirectory() as repo_path, cwd(repo_path):
        repo_url = f'git@github.com:{slug}.git'
        _LOGGER.info(f"Cloning repository {repo_url} to {repo_path}")
        repo = git.Repo.clone_from(
            repo_url, repo_path, branch='master', depth=1)

        close_no_management_issue = partial(
            _close_issue_if_exists,
            repo,
            _ISSUE_NO_DEPENDENCY_NAME,
            comment=ISSUE_CLOSE_COMMENT.format(sha=repo.head.commit.hexsha)
        )

        if os.path.isfile('Pipfile'):
            _LOGGER.info("Using Pipfile for dependency management")
            close_no_management_issue()
            result = _do_update(repo, labels, pipenv_used=True)
        elif os.path.isfile('requirements.in'):
            _create_pipenv_environment()
            _LOGGER.info("Using requirments.in for dependency management")
            result = _do_update(repo, labels, pipenv_used=False)
        else:
            _LOGGER.warning("No dependency management found")
            _open_issue_if_not_exist(
                repo,
                _ISSUE_NO_DEPENDENCY_NAME,
                lambda: ISSUE_NO_DEPENDENCY_MANAGEMENT,
                labels=labels
            )
            return {}

        return result
