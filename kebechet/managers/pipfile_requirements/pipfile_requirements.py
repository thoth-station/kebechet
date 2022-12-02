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

import logging
import tempfile
from typing import Optional

from kebechet.managers.manager import ManagerBase
from kebechet.utils import cloned_repo

from pipenv.vendor.requirementslib.models.pipfile import Pipfile
from pipenv.vendor.requirementslib.models.lockfile import Lockfile

from github.GithubException import UnknownObjectException

_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "merge_request"]


class PipfileRequirementsManager(ManagerBase):
    """Keep requirements.txt in sync with Pipfile or Pipfile.lock."""

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

    def _remote_reqs_txt_eql_new_reqs(
        self, requirements: list, ref: Optional[str] = None
    ) -> bool:
        ref = self.project.default_branch if ref is None else ref
        try:
            file_contents = self.project.get_file_content(
                path="requirements.txt", ref=ref
            )
            remote_reqs_txt = file_contents.splitlines()
        except (FileNotFoundError, UnknownObjectException):
            return False

        return sorted(requirements) == sorted(remote_reqs_txt)

    def run(self, lockfile: bool = False) -> None:  # type: ignore
        """Keep your requirements.txt in sync with Pipfile/Pipfile.lock."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "PipfileRequirementsManager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        if lockfile:
            try:
                file_contents = self.project.get_file_content("Pipfile.lock")
            except FileNotFoundError:
                self._create_missing_pipenv_files_issue("Pipfile.lock")
                return
        else:
            try:
                file_contents = self.project.get_file_content("Pipfile")
            except FileNotFoundError:
                self._create_missing_pipenv_files_issue("Pipfile")
                return

        tmp = tempfile.NamedTemporaryFile()
        with open(tmp.name, "w") as f:
            f.write(file_contents)

        if lockfile:
            requirements = sorted(
                [r.as_line() for r in Lockfile.load(tmp.name).requirements]
            )
        else:
            requirements = sorted(
                [r.as_line() for r in Pipfile.load(tmp.name).requirements]
            )

        branch_name = "kebechet-pipfile-requirements-sync"

        if self._remote_reqs_txt_eql_new_reqs(requirements=requirements):
            _LOGGER.info("Requirements in requirements.txt are up to date")
            for pr in self.get_prs_by_branch(branch_name):
                pr.comment("requirements.txt up to date")
                pr.close()
            with cloned_repo(self) as repo:
                self.repo = repo
                self.delete_remote_branch(f"origin/{branch_name}")
                self.repo = None
            return

        if self._remote_reqs_txt_eql_new_reqs(
            requirements=requirements, ref=branch_name
        ):
            _LOGGER.info("requirements in PR are up to date")
            return

        with cloned_repo(self, depth=1) as repo:
            self.repo = repo
            with open("requirements.txt", "w") as requirements_file:
                requirements_file.write("\n".join(requirements))
                requirements_file.write("\n")

            self._git_commit_push(
                commit_msg="Update requirements.txt respecting requirements in {}".format(
                    "Pipfile" if not lockfile else "Pipfile.lock"
                ),
                branch_name=branch_name,
                files=["requirements.txt"],
                force_push=True,
            )
            if not self.get_prs_by_branch(branch_name):
                self.create_pr(
                    title=f"Syncing requirements.txt using {'Pipfile.lock' if lockfile else 'Pipfile'}",
                    body="Automatic update of requirements.txt content.",
                    source_branch=branch_name,
                    target_branch=self.project.default_branch,
                )
