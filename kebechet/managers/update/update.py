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
from functools import partial

import git

from kebechet.exception import DependencyManagementError
from kebechet.exception import InternalError
from kebechet.exception import PipenvError
from kebechet.managers.manager import ManagerBase
from kebechet.source_management import Issue
from kebechet.source_management import MergeRequest
from kebechet.utils import cloned_repo

from .messages import ISSUE_CLOSE_COMMENT
from .messages import ISSUE_COMMENT_UPDATE_ALL
from .messages import ISSUE_INITIAL_LOCK
from .messages import ISSUE_NO_DEPENDENCY_MANAGEMENT
from .messages import ISSUE_PIPENV_UPDATE_ALL
from .messages import ISSUE_REPLICATE_ENV

_LOGGER = logging.getLogger(__name__)
_RE_VERSION_DELIMITER = re.compile('(==|===|<=|>=|~=|!=|<|>|\\[)')

_ISSUE_UPDATE_ALL_NAME = "Failed to update dependencies to their latest version"
_ISSUE_INITIAL_LOCK_NAME = "Failed to perform initial lock of software stack"
_ISSUE_REPLICATE_ENV_NAME = "Failed to replicate environment for updates"
_ISSUE_NO_DEPENDENCY_NAME = "No dependency management found"

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.


class UpdateManager(ManagerBase):
    """Manage updates of dependencies."""

    def __init__(self, *args, **kwargs):
        """Initialize update manager."""
        self._repo = None
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    @property
    def repo(self):
        """Get repository on which we work on."""
        return self._repo

    @repo.setter
    def repo(self, repo: git.Repo):
        """Set repository information and all derived information needed."""
        self._repo = repo
        self.slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    @staticmethod
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

    @staticmethod
    def _get_direct_dependencies() -> tuple:
        """Get all direct dependencies stated in the Pipfile file."""
        try:
            pipfile_content = toml.load('Pipfile')
        except Exception as exc:
            # TODO: open a PR to fix this
            raise DependencyManagementError(f"Failed to load Pipfile: {str(exc)}") from exc

        default = list(package_name.lower() for package_name in pipfile_content['packages'].keys())
        develop = list(package_name.lower() for package_name in pipfile_content['dev-packages'].keys())

        return default, develop

    @staticmethod
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

    @staticmethod
    def _get_all_packages_versions() -> dict:
        """Parse Pipfile.lock file and retrieve all packages in the corresponding locked versions."""
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

    @classmethod
    def _get_direct_dependencies_version(cls) -> dict:
        """Get versions of all direct dependencies based on the currently present Pipfile.lock."""
        default, develop = cls._get_direct_dependencies()

        result = {}
        default, develop = ((dep, False)
                            for dep in default), ((dep, True) for dep in develop)
        for dependency, is_dev in chain(default, develop):
            version = cls._get_dependency_version(dependency, is_dev=is_dev)
            result[dependency] = {'version': version, 'dev': is_dev}

        return result

    @staticmethod
    def _get_requirements_txt_dependencies() -> dict:
        """Gather dependencies from requirements.txt file, our requirements.txt holds fully pinned down stack."""
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

    @staticmethod
    def _construct_branch_name(package_name: str, new_package_version: str) -> str:
        """Construct branch name for the updated dependency."""
        return f'kebechet-{package_name}-{new_package_version}'

    def _open_merge_request_update(self, dependency: str, old_version: str, new_version: str,
                                   labels: list, files: list, merge_request: MergeRequest) -> typing.Optional[int]:
        """Open a pull/merge request for dependency update."""
        branch_name = self._construct_branch_name(dependency, new_version)
        commit_msg = f"Automatic update of dependency {dependency} from {old_version} to {new_version}"

        # If we have already an update for this package we simple issue git
        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        self._git_push(commit_msg, branch_name, files, force_push=True)

        if not merge_request:
            _LOGGER.info(f"Creating a pull request to update {dependency} from version {old_version} to {new_version}")
            body = f'Dependency {dependency} was used in version {old_version}, ' \
                   f'but the current latest version is {new_version}.'
            merge_request = self.sm.open_merge_request(commit_msg, branch_name, body, labels)
            return merge_request

        _LOGGER.info(f"Pull request #{merge_request.number} to update {dependency} from "
                     f"version {old_version} to {new_version} updated")
        merge_request.add_comment(f"Pull request has been rebased on top of the current master with SHA {self.sha}")
        return merge_request

    def _should_update(self, package_name, new_package_version) -> tuple:
        """Check whether the given update was already proposed as a pull request."""
        branch_name = self._construct_branch_name(package_name, new_package_version)
        response = {mr for mr in self._cached_merge_requests
                    if mr.head_branch_name == branch_name and mr.state in ('opened', 'open')}

        if len(response) == 0:
            _LOGGER.debug(f"No pull request was found for update of {package_name} to version {new_package_version}")
            return None, True
        elif len(response) == 1:
            response = list(response)[0]
            commits = response.commits
            if len(commits) != 1:
                _LOGGER.info("Update of package {package_name} to version {new_package_version} will not be issued,"
                             "the pull request as additional commits (by a maintaner?)")
                return response, False

            pr_number = response.number
            if self.sha != commits[0].parent.sha:
                _LOGGER.debug(f"Found already existing  pull request #{pr_number} for old master "
                              f"branch {commits[0].parent.sha[:7]!r} updating pull request based on "
                              f"branch {branch_name!r} for the current master branch {self.sha[:7]!r}")
                return response, True
            else:
                _LOGGER.debug(f"Found already existing  pull request #{pr_number} for the current master "
                              f"branch {self.sha[:7]!r}, not updating pull request")
                return response, False
        else:
            raise InternalError(f"Multiple ({len(response)}) pull requests with same "
                                f"branch name {branch_name!r} opened.")

    def _git_push(self, commit_msg: str, branch_name: str, files: list, force_push: bool = False) -> None:
        """Perform git push after adding files and giving a commit message."""
        self.repo.git.checkout('HEAD', b=branch_name)
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    def _get_all_outdated(self, old_direct_dependencies: dict) -> dict:
        """Get all outdated packages based on Pipfile.lock."""
        new_direct_dependencies = self._get_direct_dependencies_version()

        result = {}
        for package_name in old_direct_dependencies.keys():
            if old_direct_dependencies[package_name]['version'] \
                    != new_direct_dependencies.get(package_name, {}).get('version'):
                old_version = old_direct_dependencies[package_name]['version']
                new_version = new_direct_dependencies.get(package_name, {}).get('version')
                is_dev = old_direct_dependencies[package_name]['dev']

                _LOGGER.debug(f"Found new update for {package_name}: {old_version} -> {new_version} (dev: {is_dev})")
                result[package_name] = {
                    'dev': is_dev,  # This should not change
                    'old_version': old_version,
                    'new_version': new_version
                }

        return result

    @classmethod
    def _pipenv_lock_requirements(cls) -> None:
        """Perform pipenv lock into requirements.txt file."""
        result = cls.run_pipenv('pipenv lock -r ')
        with open('requirements.txt', 'w') as requirements_file:
            requirements_file.write(result)

    def _create_update(self, dependency: str, package_version: str, old_version: str,
                       is_dev: bool = False, labels: list = None, old_environment: dict = None,
                       merge_request: MergeRequest = None, pipenv_used: bool = True) -> typing.Union[tuple, None]:
        """Create an update for the given dependency when dependencies are managed by Pipenv.

        The old environment is set to a non None value only if we are operating on requirements.{in,txt}. It keeps
        information of packages that were present in the old environment so we can selectively change versions in the
        already existing requirements.txt or add packages that were introduced as a transitive dependency.
        """
        cmd = f'pipenv install {dependency}=={package_version} --keep-outdated'
        if is_dev:
            cmd += ' --dev'
        self.run_pipenv(cmd)
        if pipenv_used:
            # Discard changes by pipenv made in Pipfile (dependency lock) as it affects hashes computed for
            # Pipfile.lock. We don't do `pipenv update` as in some cases pipenv does not update dependencies at all.
            self.repo.git.checkout('--', 'Pipfile')
        self.run_pipenv('pipenv lock --keep-outdated')

        if not old_environment:
            merge_request = self._open_merge_request_update(
                dependency, old_version, package_version, labels, ['Pipfile.lock'], merge_request
            )
            return old_version, package_version, merge_request.number

        # For requirements.txt scenario we need to propagate all changes (updates of transitive dependencies)
        # into requirements.txt file
        self._pipenv_lock_requirements()
        merge_request = self._open_merge_request_update(
            dependency, old_version, package_version, labels, ['requirements.txt'], merge_request
        )
        return old_version, package_version, merge_request.number

    @classmethod
    def _replicate_old_environment(cls) -> None:
        """Replicate old environment based on its specification - packages in specific versions."""
        _LOGGER.info("Replicating old environment for incremental update")
        cls.run_pipenv('pipenv sync --dev')

    @classmethod
    def _create_pipenv_environment(cls) -> None:
        """Create a pipenv environment - Pipfile and Pipfile.lock from requirements.in file."""
        if not os.path.isfile('requirements.in'):
            raise DependencyManagementError(
                "No dependency management found in the repo - no Pipfile nor requirements.in"
            )

        _LOGGER.info("Installing dependencies from requirements.in")
        cls.run_pipenv('pipenv install -r requirements.in')

    def _create_initial_lock(self, labels: list, pipenv_used: bool) -> bool:
        """Perform initial requirements lock into requirements.txt file."""
        # We use lock_func to optimize run - it will be called only if actual locking needs to be performed.
        if not pipenv_used and not os.path.isfile('requirements.txt'):
            _LOGGER.info("Initial lock based on requirements.in will be done")
            lock_func = self._pipenv_lock_requirements
        elif pipenv_used and not os.path.isfile('Pipfile.lock'):
            _LOGGER.info("Initial lock based on Pipfile will be done")
            lock_func = partial(self.run_pipenv, 'pipenv lock')
        else:
            return False

        branch_name = "kebechet-initial-lock"
        request = {mr for mr in self.sm.repository.merge_requests
                   if mr.head_branch_name == branch_name and mr.state in ('opened', 'open')}
        files = ['requirements.txt' if not pipenv_used else 'Pipfile.lock']

        commit_msg = "Initial dependency lock"
        if len(request) == 0:
            lock_func()
            self._git_push(commit_msg, branch_name, files)
            request = self.sm.open_merge_request(commit_msg, branch_name, body='', labels=labels)
            _LOGGER.info(f"Initial dependency lock present in PR #{request.number}")
        elif len(request) == 1:
            request = list(request)[0]
            commits = request.commits

            if len(request.commits) != 1:
                _LOGGER.info("There have been done changes in the original pull request (multiple commits found), "
                             "aborting doing changes to the adjusted opened pull request")
                return False

            if self.sha != commits[0].parent.sha:
                lock_func()
                self._git_push(commit_msg, branch_name, files, force_push=True)
                request.add_comment(f"Pull request has been rebased on top of the current master with SHA {self.sha}")
            else:
                _LOGGER.info(f"Pull request #{request.number} is up to date for the current master branch")
        else:
            raise DependencyManagementError(
                f"Found two or more pull requests for initial requirements lock for branch {branch_name}"
            )

        return True

    @classmethod
    def _pipenv_update_all(cls):
        """Update all dependencies to their latest version."""
        _LOGGER.info("Updating all dependencies to their latest version")
        cls.run_pipenv('pipenv update --dev')
        cls.run_pipenv('pipenv lock')

    def _add_refresh_comment(self, exc: PipenvError, issue: Issue) -> typing.Optional[str]:
        """Create a refresh comment to an issue if the given master has some changes."""
        if self.sha in issue.description:
            _LOGGER.debug("No need to update refresh comment, the issue is up to date")
            return

        for issue_comment in issue.comments:
            if self.sha in issue_comment.body:
                _LOGGER.debug(f"No need to update refresh comment, comment for the current "
                              f"master {self.sha[:7]!r} found in a comment")
                break
        else:
            return ISSUE_COMMENT_UPDATE_ALL.format(
                sha=self.sha,
                slug=self.slug,
                environment_details=self.get_environment_details(),
                dependency_graph=self.get_dependency_graph(graceful=True),
                **exc.__dict__
            )

    def _relock_all(self, exc: PipenvError, labels: list) -> None:
        """Re-lock all dependencies given the Pipfile."""
        issue = self.sm.open_issue_if_not_exist(
            _ISSUE_REPLICATE_ENV_NAME,
            lambda: ISSUE_REPLICATE_ENV.format(
                **exc.__dict__,
                sha=self.sha,
                slug=self.slug,
                environment_details=self.get_environment_details()
            ),
            refresh_comment=partial(self._add_refresh_comment, exc),
            labels=labels
        )

        self._pipenv_update_all()
        commit_msg = "Automatic dependency re-locking"
        branch_name = "kebechet-dependency-relock"
        self._git_push(commit_msg, branch_name, ['Pipfile.lock'])
        pr_id = self.sm.open_merge_request(commit_msg, branch_name, f"Fixes: #{issue.number}", labels)
        _LOGGER.info(f"Issued automatic dependency re-locking in PR #{pr_id} to fix issue #{issue.number}")

    def _delete_old_branches(self, outdated: dict) -> None:
        """Delete old kebechet branches from the remote repository."""
        branches = {
            entry['name']
            for entry in self.sm.list_branches()
            if entry['name'].startswith('kebechet-')
        }
        for package_name, info in outdated.items():
            # Do not remove active branches - branches we issued PRs in.
            branch_name = self._construct_branch_name(package_name, info['new_version'])
            try:
                branches.remove(branch_name)
            except KeyError:
                # e.g. if there was an issue with PR opening.
                pass

        for branch_name in branches:
            _LOGGER.debug(f"Deleting old branch {branch_name}")
            try:
                self.sm.delete_branch(branch_name)
            except Exception:
                _LOGGER.exception(f"Failed to delete inactive branch {branch_name}")

    def _do_update(self, labels: list, pipenv_used: bool = False) -> dict:
        """Update dependencies based on management used."""
        close_initial_lock_issue = partial(
            self.sm.close_issue_if_exists,
            _ISSUE_INITIAL_LOCK_NAME,
            comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha)
        )

        # Check for first time (initial) locks first.
        try:
            if self._create_initial_lock(labels, pipenv_used):
                close_initial_lock_issue()
                return {}
        except PipenvError as exc:
            _LOGGER.exception("Failed to perform initial dependency lock")
            self.sm.open_issue_if_not_exist(
                _ISSUE_INITIAL_LOCK_NAME,
                body=lambda: ISSUE_INITIAL_LOCK.format(
                    sha=self.sha,
                    slug=self.slug,
                    file='requirements.in' if not pipenv_used else 'Pipfile',
                    environment_details=self.get_environment_details(),
                    **exc.__dict__
                ),
                refresh_comment=partial(self._add_refresh_comment, exc),
                labels=labels
            )
            raise

        close_initial_lock_issue()

        if pipenv_used:
            old_environment = self._get_all_packages_versions()
            old_direct_dependencies_version = self._get_direct_dependencies_version()
            try:
                self._pipenv_update_all()
            except PipenvError as exc:
                _LOGGER.warning("Failed to update dependencies to their latest version, reporting issue")
                self.sm.open_issue_if_not_exist(
                    _ISSUE_UPDATE_ALL_NAME,
                    body=lambda: ISSUE_PIPENV_UPDATE_ALL.format(
                        sha=self.sha,
                        slug=self.slug,
                        environment_details=self.get_environment_details(),
                        dependency_graph=self.get_dependency_graph(graceful=True),
                        **exc.__dict__
                    ),
                    refresh_comment=partial(self._add_refresh_comment, exc),
                    labels=labels
                )
                return {}
            else:
                # We were able to update all, close reported issue if any.
                self.sm.close_issue_if_exists(_ISSUE_UPDATE_ALL_NAME, comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha))
        else:  # requirements.txt
            old_environment = self._get_requirements_txt_dependencies()
            direct_dependencies = self._get_direct_dependencies_requirements()
            old_direct_dependencies_version = {k: v for k, v in old_environment.items() if k in direct_dependencies}

        outdated = self._get_all_outdated(old_direct_dependencies_version)
        _LOGGER.info(f"Outdated: {outdated}")

        # Undo changes made to Pipfile.lock by _pipenv_update_all.
        self.repo.head.reset(index=True, working_tree=True)

        result = {}
        if outdated:
            # Do API calls only once, cache results.
            self._cached_merge_requests = self.sm.repository.merge_requests

        for package_name in outdated.keys():
            # As an optimization, first check if the given PR is already present.
            new_version = outdated[package_name]['new_version']
            old_version = outdated[package_name]['old_version']

            merge_request, should_update = self._should_update(package_name, new_version)
            if not should_update:
                _LOGGER.info(f"Skipping update creation for {package_name} from version {old_version} to "
                             f"{new_version} as the given update already exists in PR #{merge_request.number}")
                continue

            try:
                self._replicate_old_environment()
            except PipenvError as exc:
                # There has been an error in locking dependencies. This can be due to a missing dependency or simply
                # currently locked dependencies are not correct. Try to issue a pull request that would fix
                # that. We know that update all works, use update.
                _LOGGER.warning("Failed to replicate old environment, re-locking all dependencies")
                self._relock_all(exc, labels)
                return {}

            is_dev = outdated[package_name]['dev']
            try:
                _LOGGER.info(f"Creating update of dependency {package_name} in repo {self.slug} (devel: {is_dev})")
                versions = self._create_update(
                    package_name, new_version, old_version,
                    is_dev=is_dev,
                    labels=labels,
                    old_environment=old_environment if not pipenv_used else None,
                    merge_request=merge_request,
                    pipenv_used=pipenv_used
                )
                if versions:
                    result[package_name] = versions
            except Exception as exc:
                _LOGGER.exception(f"Failed to create update for dependency {package_name}: {str(exc)}")
            finally:
                self.repo.head.reset(index=True, working_tree=True)
                self.repo.git.checkout('master')

        # We know that locking was done correctly - if the issue is still open, close it. The issue
        # should be automatically closed by merging the generated PR.
        self.sm.close_issue_if_exists(
            _ISSUE_REPLICATE_ENV_NAME,
            comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha)
        )

        self._delete_old_branches(outdated)
        return result

    def run(self, labels: list) -> typing.Optional[dict]:
        """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
        # We will keep venv in the project itself - we have permissions in the cloned repo.
        os.environ['PIPENV_VENV_IN_PROJECT'] = '1'

        with cloned_repo(self.service_url, self.slug) as repo:
            # Make repo available in the instance.
            self.repo = repo

            close_no_management_issue = partial(
                self.sm.close_issue_if_exists,
                _ISSUE_NO_DEPENDENCY_NAME,
                comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha)
            )

            if os.path.isfile('Pipfile'):
                _LOGGER.info("Using Pipfile for dependency management")
                close_no_management_issue()
                result = self._do_update(labels, pipenv_used=True)
            elif os.path.isfile('requirements.in'):
                self._create_pipenv_environment()
                _LOGGER.info("Using requirements.in for dependency management")
                close_no_management_issue()
                result = self._do_update(labels, pipenv_used=False)
            else:
                _LOGGER.warning("No dependency management found")
                self.sm.open_issue_if_not_exist(
                    _ISSUE_NO_DEPENDENCY_NAME,
                    lambda: ISSUE_NO_DEPENDENCY_MANAGEMENT,
                    labels=labels
                )
                return {}

            return result
