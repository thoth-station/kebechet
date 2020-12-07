#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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

import kebechet
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
from kebechet.managers.manager import ManagerBase, refresh_repo_url
from thoth.sourcemanagement import Issue
from thoth.sourcemanagement import PullRequest
from thoth.sourcemanagement import PRStatus
from kebechet.utils import cloned_repo

from .messages import ISSUE_CLOSE_COMMENT
from .messages import ISSUE_COMMENT_UPDATE_ALL
from .messages import ISSUE_INITIAL_LOCK
from .messages import ISSUE_NO_DEPENDENCY_MANAGEMENT
from .messages import ISSUE_PIPENV_UPDATE_ALL
from .messages import ISSUE_REPLICATE_ENV
from .messages import ISSUE_UNSUPPORTED_PACKAGE
from .messages import UPDATE_MESSAGE_BODY
from kebechet.utils import construct_raw_file_url

_LOGGER = logging.getLogger(__name__)
_RE_VERSION_DELIMITER = re.compile("(==|===|<=|>=|~=|!=|<|>|\\[)")

_ISSUE_UPDATE_ALL_NAME = "Failed to update dependencies to their latest version"
_ISSUE_INITIAL_LOCK_NAME = "Failed to perform initial lock of software stack"
_ISSUE_REPLICATE_ENV_NAME = "Failed to replicate environment for updates"
_ISSUE_NO_DEPENDENCY_NAME = "No dependency management found"
_ISSUE_UNSUPPORTED_PACKAGE = (
    "Application cannot be managed by Kebechet due to Git package"
)
_ISSUE_MANUAL_UPDATE = "Kebechet update"

_UPDATE_BRANCH_NAME = "kebechet-automatic-update"

# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "issues", "issue", "merge_request"]

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

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    @staticmethod
    def _get_dependency_version(dependency: str, is_dev: bool) -> str:
        """Get version of the given dependency from Pipfile.lock."""
        try:
            with open("Pipfile.lock") as pipfile_lock:
                pipfile_lock_content = json.load(pipfile_lock)
        except Exception as exc:
            # TODO: open a PR to fix this
            raise DependencyManagementError(
                f"Failed to load Pipfile.lock file: {str(exc)}"
            ) from exc

        # We look for normalized dependency in Pipfile.lock.
        normalized_dependency = re.sub(r"[-_.]+", "-", dependency).lower()
        version = (
            pipfile_lock_content["develop" if is_dev else "default"]
            .get(normalized_dependency, {})
            .get("version")
        )
        # if not kept as normaized depedency in Pipfile.lock.
        version = (
            pipfile_lock_content["develop" if is_dev else "default"]
            .get(dependency, {})
            .get("version")
        )
        if not version:
            raise InternalError(
                f"Failed to retrieve version information for dependency {dependency}, (dev: {is_dev})"
            )

        return version[len("==") :]

    @staticmethod
    def _get_direct_dependencies() -> tuple:
        """Get all direct dependencies stated in the Pipfile file."""
        try:
            pipfile_content = toml.load("Pipfile")
        except Exception as exc:
            # TODO: open a PR to fix this
            raise DependencyManagementError(
                f"Failed to load Pipfile: {str(exc)}"
            ) from exc

        default = list(
            package_name.lower() for package_name in pipfile_content["packages"].keys()
        )
        develop = list(
            package_name.lower()
            for package_name in pipfile_content.get("dev-packages", {}).keys()
        )

        return default, develop

    @staticmethod
    def _get_direct_dependencies_requirements(req_dev: bool) -> set:
        """Gather all direct dependencies.

        Get all direct dependencies based on either requirements.in or requirements-dev.in file
        and generated Pipfile.lock from it.
        """
        input_file = "requirements-dev.in" if req_dev else "requirements.in"
        with open(input_file, "r") as requirements_in_file:
            content = requirements_in_file.read()

        direct_dependencies = set()
        for line in content.splitlines():
            if line.strip().startswith("#"):
                continue

            # TODO: we could reuse pip or pipenv functionality here to parse file.
            package_name = _RE_VERSION_DELIMITER.split(line)[0]
            direct_dependencies.add(package_name.lower())

        return direct_dependencies

    def _get_all_packages_versions(self) -> dict:
        """Parse Pipfile.lock file and retrieve all packages in the corresponding locked versions."""
        try:
            with open("Pipfile.lock") as pipfile_lock:
                pipfile_lock_content = json.load(pipfile_lock)
        except Exception as exc:
            # TODO: open a PR to fix this
            raise DependencyManagementError(
                f"Failed to load Pipfile.lock file: {str(exc)}"
            ) from exc

        result = {}

        for package_name, package_info in pipfile_lock_content["default"].items():
            if "git" in package_info:
                self._create_unsupported_package_issue(package_name)
                raise DependencyManagementError(
                    "Failed to find version in package that uses git source."
                )
            result[package_name.lower()] = {
                "dev": False,
                "version": package_info["version"][len("==") :],
            }

        for package_name, package_info in pipfile_lock_content["develop"].items():
            if "git" in package_info:
                self._create_unsupported_package_issue(package_name)
                raise DependencyManagementError(
                    "Failed to find version in package that uses git source."
                )
            result[package_name.lower()] = {
                "dev": False,
                "version": package_info["version"][len("==") :],
            }
        # Close git as a source issues.
        self.sm.close_issue_if_exists(
            _ISSUE_UNSUPPORTED_PACKAGE,
            f"Issue closed as no packages use git as a \
                    source anymore. Related SHA - {self.sha}",
        )
        return result

    def _create_unsupported_package_issue(self, package_name):
        """Create an issue as Kebechet doesn't support packages with git as source."""
        _LOGGER.info("Key Errror encountered, due package source being git.")
        pip_url = construct_raw_file_url(
            self.service_url, self.slug, "Pipfile", self.service_type
        )
        piplock_url = construct_raw_file_url(
            self.service_url, self.slug, "Pipfile.lock", self.service_type
        )
        self.sm.open_issue_if_not_exist(
            _ISSUE_UNSUPPORTED_PACKAGE,
            lambda: ISSUE_UNSUPPORTED_PACKAGE.format(
                sha=self.sha,
                package=package_name,
                pip_url=pip_url,
                piplock_url=piplock_url,
                environment_details=self.get_environment_details(),
            ),
        )

    @classmethod
    def _get_direct_dependencies_version(cls) -> dict:
        """Get versions of all direct dependencies based on the currently present Pipfile.lock."""
        default, develop = cls._get_direct_dependencies()

        result = {}
        default, develop = (
            ((dep, False) for dep in default),
            ((dep, True) for dep in develop),
        )
        for dependency, is_dev in chain(default, develop):
            version = cls._get_dependency_version(dependency, is_dev=is_dev)
            result[dependency] = {"version": version, "dev": is_dev}

        return result

    @staticmethod
    def _get_requirements_txt_dependencies(req_dev: bool) -> dict:
        """Gather dependencies from fully pinned down stack.

        Gather dependencies from either requirements.txt or requirements-dev.txt file,
        our requirements.txt and requirements-dev.txt holds fully pinned down stack.
        """
        result = {}
        input_file = "requirements-dev.txt" if req_dev else "requirements.txt"
        with open(input_file, "r") as requirements_file:
            content = requirements_file.read()

        for line in content.splitlines():
            line = line.strip()

            if line.startswith(("#", "-")) or not line:
                continue

            package_and_version = line.split("==", maxsplit=1)
            if len(package_and_version) != 2:
                raise DependencyManagementError(
                    f"File {input_file} does not state fully locked "
                    f"dependencies: {line!r} is not fully qualified dependency"
                )
            package_name, package_version = package_and_version
            result[package_name] = {
                # FIXME: tabs?
                "version": package_version.split(r" ", maxsplit=1)[0],
                "dev": False,
            }

        return result

    @staticmethod
    def _construct_branch_name(package_name: str, new_package_version: str) -> str:
        """Construct branch name for the updated dependency."""
        return f"kebechet-{package_name}-{new_package_version}"

    def _open_merge_request_update(
        self,
        body: str,
        labels: typing.Optional[list],
        files: list,
        merge_request: PullRequest,
    ) -> typing.Optional[int]:
        """Open a pull/merge request for dependency update."""
        branch_name = _UPDATE_BRANCH_NAME
        commit_msg = "Automatic update of dependencies by kebechet."

        # If we have already an update for this package we simple issue git
        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        self._git_push(":arrow_up: " + commit_msg, branch_name, files, force_push=True)

        if not merge_request:
            _LOGGER.info("Creating a new pull request to update dependencies.")
            merge_request = self.sm.open_merge_request(
                commit_msg, branch_name, body, labels
            )
            return merge_request

        _LOGGER.info(
            f"Pull request #{merge_request.id} to update dependencies has been updated."
        )
        merge_request.comment(
            f"Pull request has been rebased on top of the current master with SHA {self.sha}"
        )
        return merge_request

    def _should_update(self) -> tuple:
        """Check whether the given update was already proposed as a pull request."""
        branch_name = _UPDATE_BRANCH_NAME
        response = {
            mr
            for mr in self._cached_merge_requests
            if mr.source_branch == branch_name and mr.status == PRStatus.open
        }

        if len(response) == 0:
            _LOGGER.debug("No pull request was found for automatic update.")
            return None, True
        elif len(response) == 1:
            response = list(response)[0]
            commits = response.get_all_commits()  # type: ignore
            if len(commits) != 1:
                _LOGGER.info(
                    "Automatic update will not be issued,"
                    "the pull request as additional commits (by a maintaner?)"
                )
                return response, False

            pr_number = response.id  # type: ignore
            if self.sha != commits[0]:
                _LOGGER.debug(
                    f"Found already existing  pull request #{pr_number} for old master "
                    f"branch {commits[0][:7]!r} updating pull request based on "
                    f"branch {branch_name!r} for the current master branch {self.sha[:7]!r}"
                )
                return response, True
            else:
                _LOGGER.debug(
                    f"Found already existing  pull request #{pr_number} for the current master "
                    f"branch {self.sha[:7]!r}, not updating pull request"
                )
                return response, False
        else:
            raise InternalError(
                f"Multiple ({len(response)}) pull requests with same "
                f"branch name {branch_name!r} opened."
            )

    @refresh_repo_url
    def _git_push(
        self, commit_msg: str, branch_name: str, files: list, force_push: bool = False
    ) -> None:
        """Perform git push after adding files and giving a commit message."""
        self.repo.git.checkout("HEAD", b=branch_name)
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    def _get_all_outdated(self, old_direct_dependencies: dict) -> dict:
        """Get all outdated packages based on Pipfile.lock."""
        new_direct_dependencies = self._get_direct_dependencies_version()

        result = {}
        for package_name in old_direct_dependencies.keys():
            if old_direct_dependencies[package_name][
                "version"
            ] != new_direct_dependencies.get(package_name, {}).get("version"):
                old_version = old_direct_dependencies[package_name]["version"]
                new_version = new_direct_dependencies.get(package_name, {}).get(
                    "version"
                )
                is_dev = old_direct_dependencies[package_name]["dev"]

                _LOGGER.debug(
                    f"Found new update for {package_name}: {old_version} -> {new_version} (dev: {is_dev})"
                )
                result[package_name] = {
                    "dev": is_dev,  # This should not change
                    "old_version": old_version,
                    "new_version": new_version,
                }

        return result

    @classmethod
    def _pipenv_lock_requirements(cls, output_file: str) -> None:
        """Perform pipenv lock into requirements.txt or requirements-dev.txt file."""
        result = cls.run_pipenv("pipenv lock -r ")
        with open(output_file, "w") as requirements_file:
            # Remove markers from requirements file.
            for line in result.splitlines():
                parts = line.split(" ; ", maxsplit=1)
                requirements_file.write(parts[0])

    def _create_update(
        self,
        body: str,
        is_dev: bool = False,
        labels: list = None,
        old_environment: dict = None,
        merge_request: PullRequest = None,
        pipenv_used: bool = True,
        req_dev: bool = False,
    ) -> str:
        """Create an update for the given dependency when dependencies are managed by Pipenv.

        The old environment is set to a non None value only if we are operating on requirements.{in,txt}. It keeps
        information of packages that were present in the old environment so we can selectively change versions in the
        already existing requirements.txt or add packages that were introduced as a transitive dependency.
        """
        if not old_environment:
            merge_request = self._open_merge_request_update(
                body, labels, ["Pipfile.lock"], merge_request
            )
            return merge_request.id  # type: ignore

        # For either requirements.txt  or requirements-dev.text scenario we need to propagate all changes
        # (updates of transitive dependencies) into requirements.txt or requirements-dev file
        output_file = "requirements-dev.txt" if req_dev else "requirements.txt"
        self._pipenv_lock_requirements(output_file)
        merge_request = self._open_merge_request_update(
            body, labels, [output_file], merge_request
        )
        return merge_request.id  # type: ignore

    @classmethod
    def _replicate_old_environment(cls) -> None:
        """Replicate old environment based on its specification - packages in specific versions."""
        _LOGGER.info("Replicating old environment for incremental update")
        cls.run_pipenv("pipenv sync --dev")

    @classmethod
    def _create_pipenv_environment(cls, input_file: str) -> None:
        """Create a pipenv environment - Pipfile and Pipfile.lock from requirements.in or requirements-dev.in file."""
        if os.path.isfile(input_file) and input_file == "requirements.in":
            _LOGGER.info(f"Installing dependencies from {input_file}")
            cls.run_pipenv(f"pipenv install -r {input_file}")
        elif os.path.isfile(input_file) and input_file == "requirements-dev.in":
            _LOGGER.info(f"Installing dependencies from {input_file}")
            cls.run_pipenv(f"pipenv install -r {input_file} --dev")
        else:
            raise DependencyManagementError(
                "No dependency management found in the repo - no Pipfile nor requirements.in nor requirements-dev.in"
            )

    def _get_prs(self, source_branch_name: str) -> set:
        """Get pull requests with source branch name."""
        return {
            mr
            for mr in self.sm.get_prs()
            if mr.source_branch == source_branch_name and mr.status == PRStatus.open
        }

    def _create_initial_lock(
        self, labels: list, pipenv_used: bool, req_dev: bool
    ) -> bool:
        """Perform initial requirements lock into requirements.txt file."""
        # We use lock_func to optimize run - it will be called only if actual locking needs to be performed.
        if not pipenv_used and not os.path.isfile("requirements.txt") and not req_dev:
            _LOGGER.info("Initial lock based on requirements.in will be done")
            lock_func = partial(self._pipenv_lock_requirements, "requirements.txt")
        elif not pipenv_used and not os.path.isfile("requirements-dev.txt") and req_dev:
            _LOGGER.info("Initial lock based on requirements-dev.in will be done")
            lock_func = partial(self._pipenv_lock_requirements, "requirements-dev.txt")
        elif pipenv_used and not os.path.isfile("Pipfile.lock"):
            _LOGGER.info("Initial lock based on Pipfile will be done")
            lock_func = partial(self.run_pipenv, "pipenv lock")
        else:
            return False

        branch_name = "kebechet-initial-lock"
        request = self._get_prs(source_branch_name=branch_name)

        if req_dev and not pipenv_used:
            files = ["requirements-dev.txt"]
        elif not req_dev and not pipenv_used:
            files = ["requirements.txt"]
        else:
            files = ["Pipfile.lock"]

        commit_msg = "Initial dependency lock"
        if len(request) == 0:
            lock_func()
            self._git_push(commit_msg, branch_name, files)
            request = self.sm.open_merge_request(
                commit_msg, branch_name, body="", labels=labels
            )
            _LOGGER.info(
                f"Initial dependency lock present in PR #{request.id}"  # type: ignore
            )
        elif len(request) == 1:
            request = list(request)[0]
            commits = request.get_all_commits()  # type: ignore

            if len(commits) != 1:
                _LOGGER.info(
                    "There have been done changes in the original pull request (multiple commits found), "
                    "aborting doing changes to the adjusted opened pull request"
                )
                return False

            if self.sha != commits[0]:
                lock_func()
                self._git_push(commit_msg, branch_name, files, force_push=True)
                request.comment(  # type: ignore
                    f"Pull request has been rebased on top of the current master with SHA {self.sha}"
                )
            else:
                _LOGGER.info(
                    f"Pull request #{request.id} is up to date for the current master branch"  # type: ignore
                )
        else:
            raise DependencyManagementError(
                f"Found two or more pull requests for initial requirements lock for branch {branch_name}"
            )

        return True

    @classmethod
    def _pipenv_update_all(cls):
        """Update all dependencies to their latest version."""
        _LOGGER.info("Updating all dependencies to their latest version")
        cls.run_pipenv("pipenv update --dev")
        cls.run_pipenv("pipenv lock")
        return None

    def _add_refresh_comment(
        self, exc: PipenvError, issue: Issue
    ) -> typing.Optional[str]:
        """Create a refresh comment to an issue if the given master has some changes."""
        if self.sha in issue.description:
            _LOGGER.debug("No need to update refresh comment, the issue is up to date")
            return None

        for issue_comment in issue.get_comments():
            if self.sha in issue_comment.body:
                _LOGGER.debug(
                    f"No need to update refresh comment, comment for the current "
                    f"master {self.sha[:7]!r} found in a comment"
                )
                break
        else:
            return ISSUE_COMMENT_UPDATE_ALL.format(
                sha=self.sha,
                slug=self.slug,
                environment_details=self.get_environment_details(),
                dependency_graph=self.get_dependency_graph(graceful=True),
                **exc.__dict__,
            )
        return None

    def _relock_all(self, exc: PipenvError, labels: list) -> None:
        """Re-lock all dependencies given the Pipfile."""
        pip_url = construct_raw_file_url(
            self.service_url, self.slug, "Pipfile", self.service_type
        )
        piplock_url = construct_raw_file_url(
            self.service_url, self.slug, "Pipfile.lock", self.service_type
        )
        issue = self.sm.open_issue_if_not_exist(
            _ISSUE_REPLICATE_ENV_NAME,
            lambda: ISSUE_REPLICATE_ENV.format(
                **exc.__dict__,
                sha=self.sha,
                pip_url=pip_url,
                piplock_url=piplock_url,
                environment_details=self.get_environment_details(),
            ),
            refresh_comment=partial(self._add_refresh_comment, exc),
            labels=labels,
        )

        self._pipenv_update_all()
        commit_msg = "Automatic dependency re-locking"
        branch_name = "kebechet-dependency-relock"

        existing_prs = self._get_prs(branch_name)
        if len(existing_prs) == 1:
            pr = list(existing_prs)[0]
            commits = pr.get_all_commits()
            if len(commits) != 1:
                pr.comment(
                    "There have been done changes in the original pull request (multiple commits found), "
                    "aborting doing changes to the modified opened pull request"
                )
                return None
            if self.sha != commits[0]:
                self._git_push(
                    ":pushpin: " + commit_msg,
                    branch_name,
                    ["Pipfile.lock"],
                    force_push=True,
                )
                pr.comment(
                    f"Pull request has been rebased on top of the current master with SHA {self.sha}"
                )
        elif len(existing_prs) == 0:
            # Default case
            self._git_push(":pushpin: " + commit_msg, branch_name, ["Pipfile.lock"])
            pr_id = self.sm.open_merge_request(
                commit_msg, branch_name, f"Fixes: #{issue.id}", labels
            )
            _LOGGER.info(
                f"Issued automatic dependency re-locking in PR #{pr_id} to fix issue #{issue.id}"
            )
        else:
            raise DependencyManagementError(
                f"Found two or more pull requests for automatic relock for branch {branch_name}"
            )

    def _delete_old_branches(self, outdated: dict) -> None:
        """Delete old kebechet branches from the remote repository."""
        branches = {
            entry for entry in self.sm.list_branches() if entry.startswith("kebechet-")
        }
        for package_name, info in outdated.items():
            # Do not remove active branches - branches we issued PRs in.
            branch_name = self._construct_branch_name(package_name, info["new_version"])
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

    def _generate_update_body(self, outdated: dict) -> str:
        kebechet_version = kebechet.__version__
        package_name_rows = ""
        for package in outdated.keys():
            details = outdated[package]
            old_version, new_version, is_dev = (
                details.get("old_version"),
                details.get("new_version"),
                details.get("dev"),
            )
            package_name_rows += f"**{package}**|{old_version}|{new_version}|{is_dev}\n"
        body = UPDATE_MESSAGE_BODY.format(
            package_name_rows=package_name_rows, kebechet_version=kebechet_version
        )
        return body

    def _do_update(
        self, labels: list, pipenv_used: bool = False, req_dev: bool = False
    ) -> dict:
        """Update dependencies based on management used."""
        close_initial_lock_issue = partial(
            self.sm.close_issue_if_exists,
            _ISSUE_INITIAL_LOCK_NAME,
            comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha),
        )

        # Check for first time (initial) locks first.
        try:
            if self._create_initial_lock(labels, pipenv_used, req_dev):
                close_initial_lock_issue()
                return {}
        except PipenvError as exc:
            _LOGGER.exception("Failed to perform initial dependency lock")
            file_name = (
                "requirements.txt"
                if not req_dev
                else "requirements-dev.txt"
                if not pipenv_used
                else "Pipfile"
            )
            file_url = construct_raw_file_url(
                self.service_url, self.slug, file_name, self.service_type
            )
            self.sm.open_issue_if_not_exist(
                _ISSUE_INITIAL_LOCK_NAME,
                body=lambda: ISSUE_INITIAL_LOCK.format(
                    sha=self.sha,
                    url=file_url,
                    file=file_name,
                    environment_details=self.get_environment_details(),
                    **exc.__dict__,  # noqa F821
                ),
                refresh_comment=partial(self._add_refresh_comment, exc),
                labels=labels,
            )
            raise

        close_initial_lock_issue()

        if pipenv_used:
            old_environment = self._get_all_packages_versions()
            old_direct_dependencies_version = self._get_direct_dependencies_version()
            try:
                self._pipenv_update_all()
            except PipenvError as exc:
                _LOGGER.warning(
                    "Failed to update dependencies to their latest version, reporting issue"
                )
                pip_url = construct_raw_file_url(
                    self.service_url, self.slug, "Pipfile", self.service_type
                )
                piplock_url = construct_raw_file_url(
                    self.service_url, self.slug, "Pipfile.lock", self.service_type
                )
                self.sm.open_issue_if_not_exist(
                    _ISSUE_UPDATE_ALL_NAME,
                    body=lambda: ISSUE_PIPENV_UPDATE_ALL.format(
                        sha=self.sha,
                        pip_url=pip_url,
                        piplock_url=piplock_url,
                        environment_details=self.get_environment_details(),
                        dependency_graph=self.get_dependency_graph(graceful=True),
                        **exc.__dict__,  # noqa F821
                    ),
                    refresh_comment=partial(self._add_refresh_comment, exc),
                    labels=labels,
                )
                return {}
            else:
                # We were able to update all, close reported issue if any.
                self.sm.close_issue_if_exists(
                    _ISSUE_UPDATE_ALL_NAME,
                    comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha),
                )
        else:  # either requirements.txt or requirements-dev.txt
            old_environment = self._get_requirements_txt_dependencies(req_dev)
            direct_dependencies = self._get_direct_dependencies_requirements(req_dev)
            old_direct_dependencies_version = {
                k: v for k, v in old_environment.items() if k in direct_dependencies
            }

        outdated = self._get_all_outdated(old_direct_dependencies_version)
        _LOGGER.info(f"Outdated: {outdated}")

        # Undo changes made to Pipfile.lock by _pipenv_update_all. # Disabled for now.
        # self.repo.head.reset(index=True, working_tree=True)

        result = {}
        if outdated:
            # Do API calls only once, cache results.
            self._cached_merge_requests = self.sm.get_prs()
            body = self._generate_update_body(outdated)
            merge_request, should_update = self._should_update()
            if not should_update:
                _LOGGER.info(
                    f"Skipping update creation as the given update already exists in PR #{merge_request.id}"
                )
            try:
                versions = self._create_update(
                    body=body,
                    labels=labels,
                    old_environment=old_environment if not pipenv_used else None,
                    merge_request=merge_request,
                    pipenv_used=pipenv_used,
                    req_dev=req_dev,
                )
                if versions:
                    result["merge request id"] = versions  # return the merge request id
            except Exception as exc:
                _LOGGER.exception(
                    f"Failed to create update for current master {self.sha}: {str(exc)}"
                )
        return result

    def run(self, labels: list) -> typing.Optional[dict]:
        """Create a pull request for each and every direct dependency in the given org/repo (slug)."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "Update Manager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return None

        # We will keep venv in the project itself - we have permissions in the cloned repo.
        os.environ["PIPENV_VENV_IN_PROJECT"] = "1"

        with cloned_repo(self, depth=1) as repo:
            # Make repo available in the instance.
            self.repo = repo

            close_no_management_issue = partial(
                self.sm.close_issue_if_exists,
                _ISSUE_NO_DEPENDENCY_NAME,
                comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha),
            )

            close_manual_update_issue = partial(
                self.sm.close_issue_if_exists,
                _ISSUE_MANUAL_UPDATE,
                comment=ISSUE_CLOSE_COMMENT.format(sha=self.sha),
            )

            if os.path.isfile("Pipfile"):
                _LOGGER.info("Using Pipfile for dependency management")
                close_no_management_issue()
                result = self._do_update(labels, pipenv_used=True, req_dev=False)
                close_manual_update_issue()
            elif os.path.isfile("requirements.in"):
                self._create_pipenv_environment(input_file="requirements.in")
                _LOGGER.info("Using requirements.in for dependency management")
                close_no_management_issue()
                result = self._do_update(labels, pipenv_used=False, req_dev=False)
                if os.path.isfile("requirements-dev.in"):
                    self._create_pipenv_environment(input_file="requirements-dev.in")
                    _LOGGER.info("Using requirements-dev.in for dependency management")
                    close_no_management_issue()
                    result = self._do_update(labels, pipenv_used=False, req_dev=True)
                close_manual_update_issue()
            else:
                _LOGGER.warning("No dependency management found")
                self.sm.open_issue_if_not_exist(
                    _ISSUE_NO_DEPENDENCY_NAME,
                    lambda: ISSUE_NO_DEPENDENCY_MANAGEMENT,
                    labels=labels,
                )
                return {}

            return result
