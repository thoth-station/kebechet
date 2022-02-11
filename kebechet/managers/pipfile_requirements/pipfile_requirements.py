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

"""Keep your requirements.txt files in sync with Pipfile or Pipfile.lock files."""

import json
import logging
import typing

from kebechet.managers.manager import ManagerBase
from kebechet.managers.exceptions import ManagerFailedException
from kebechet.utils import cloned_repo

import toml
from github.GithubException import UnknownObjectException

_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "merge_request"]


class PipfileRequirementsManager(ManagerBase):
    """Keep requirements.txt in sync with Pipfile or Pipfile.lock."""

    def get_pipfile_requirements(self, content_str: str) -> typing.Set[str]:
        """Parse Pipfile file and gather requirements, respect version specifications listed."""
        content = toml.loads(content_str)

        requirements = set()
        for package_name, entry in content["packages"].items():
            if not isinstance(entry, str) or (
                isinstance(entry, dict) and "version" not in entry
            ):
                # e.g. using git, ...
                issue_title = f"No pinned version for {package_name}"
                body = f"Package {package_name} does not use pinned version in Pipfile: {entry}"
                if self.get_issue_by_title(issue_title) is None:
                    self.project.create_issue(
                        title=issue_title,
                        body=body,
                    )
                raise ManagerFailedException(body)

            package_version = entry if entry != "*" else ""
            requirements.add(f"{package_name}{package_version}")

        return requirements

    def get_pipfile_lock_requirements(self, content_str: str) -> typing.Set[str]:
        """Parse Pipfile.lock and gather pinned down requirements."""
        content = json.loads(content_str)

        requirements = set()
        for package_name, package_version in content.items():
            if not isinstance(package_version, str):
                # e.g. using git, ...
                issue_title = f"Unsupported version entry for {package_name}"
                body = f"Unsupported version entry for {package_name} in Pipfile.lock: {package_version}"
                if self.get_issue_by_title(issue_title) is None:
                    self.project.create_issue(
                        title=issue_title,
                        body=body,
                    )
                raise ManagerFailedException(body)

            specifier = package_version if package_version != "*" else ""
            requirements.add(f"{package_name}{specifier}")

        return requirements

    def _create_missing_pipenv_files_issue(self, file_name):
        issue_title = (
            f"Kebechet Pipfile Requirements Manager: no {file_name} found in repo"
        )
        body = f"""Kebechet pipfile_requirements manager is installed but no
        `{file_name}` was found in this repository.

        `{file_name}` is required by the pipfile_requirements manager in its
        current configuration (as specified in `.thoth.yaml`).

        Either remove this manager from `.thoth.yaml`, adjust its configuration,
        or update the repository to meet the requirements.

        Reference: see the documentation for
        [pipfile_requirements](https://thoth-station.ninja/docs/developers/kebechet/managers/pipfile_requirements.html).
        """
        issue = self.get_issue_by_title(issue_title)
        if issue:
            return
        self.project.create_issue(title=issue_title, body=body)

    def run(self, lockfile: bool = False) -> None:  # type: ignore
        """Keep your requirements.txt in sync with Pipfile/Pipfile.lock."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "PipfileRequirementsManager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        file_name = "Pipfile.lock" if lockfile else "Pipfile"

        try:
            file_contents = self.project.get_file_content(file_name)
        except FileNotFoundError:
            self._create_missing_pipenv_files_issue(file_name)
            return

        pipfile_content = (
            sorted(self.get_pipfile_lock_requirements(file_contents))
            if lockfile
            else sorted(self.get_pipfile_requirements(file_contents))
        )

        try:
            file_contents = self.project.get_file_content("requirements.txt")
            requirements_txt_content = sorted(file_contents.splitlines())
        except (FileNotFoundError, UnknownObjectException):
            requirements_txt_content = (
                []
            )  # requirements.txt file has not been created so the manager will create it

        if pipfile_content == requirements_txt_content:
            _LOGGER.info("Requirements in requirements.txt are up to date")
            # TODO: delete branch if already exists
            return

        with cloned_repo(self, depth=1) as repo:
            with open("requirements.txt", "w") as requirements_file:
                requirements_file.write("\n".join(pipfile_content))
                requirements_file.write("\n")

            branch_name = "kebechet-pipfile-requirements-sync"
            repo.git.checkout(b=branch_name)
            repo.index.add(["requirements.txt"])
            repo.index.commit(
                "Update requirements.txt respecting requirements in {}".format(
                    "Pipfile" if not lockfile else "Pipfile.lock"
                )
            )
            repo.remote().push(branch_name)
