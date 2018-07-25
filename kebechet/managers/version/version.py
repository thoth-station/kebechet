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

"""Automatically issue a new PR with adjusted version for Python projects."""

import os
import logging

from kebechet.utils import cloned_repo
from kebechet.managers.manager import ManagerBase

from git import Repo
from IGitt.Interfaces.Issue import Issue

_LOGGER = logging.getLogger(__name__)
_VERSION_REQUEST_ISSUE = ' release'
_VERSION_PULL_REQUEST_NAME = 'Release of version {}'


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    @staticmethod
    def _adjust_version_file(file_path: str, new_version: str):
        """Adjust version in the given file, return signalizes whether the return value indicates change in file."""
        with open(file_path, 'r') as input_file:
            content = input_file.read().splitlines()

        changed = False
        for idx, line in enumerate(content):
            if line.startswith('__version__ = '):
                parts = line.split(' = ', maxsplit=1)
                if len(parts) != 2:
                    _LOGGER.warning(
                        "Found '__version__' identifier but unable to parse old version, skipping: %r", line
                    )
                    continue

                old_version = parts[1]
                _LOGGER.info("Old version found in sources: %r", old_version)

                content[idx] = f'__version__ = "{new_version}"'
                changed = True

        if not changed:
            return False

        # Apply changes.
        with open(file_path, 'w') as output_file:
            output_file.write("\n".join(content))
            # Add new line at the of file explicitly.
            output_file.write("\n")

        return True

    def _adjust_version_in_sources(self, repo: Repo, new_version: str, labels: list, issue: Issue):
        """Walk through the directory structure and try to adjust version identifier in sources."""
        adjusted_count = 0
        for root, _, files in os.walk('./'):
            for file_name in files:
                if file_name in ('setup.py', '__init__.py'):
                    file_path = os.path.join(root, file_name)
                    adjusted = self._adjust_version_file(file_path, new_version)
                    if adjusted:
                        repo.git.add(file_path[len(os.getcwd()):])
                        adjusted_count += 1

        if adjusted_count == 0:
            error_msg = f"No version identifier found in sources to release {new_version}"
            _LOGGER.warning(error_msg)
            self.sm.open_issue_if_not_exist(
                error_msg,
                lambda x: "Automated version release cannot be performed.\nRelated: #" + str(issue.number),
                labels
            )

        if adjusted_count > 1:
            error_msg = f"Multiple version identifiers found in sources to release {new_version}"
            _LOGGER.warning(error_msg)
            self.sm.open_issue_if_not_exist(
                error_msg,
                lambda x: "Automated version release cannot be performed.\nRelated: #" + str(issue.number),
                labels
            )

        return adjusted_count == 1

    def run(self, labels: list = None) -> None:
        """Check issues for new issue request, if a request exists, issue a new PR with adjusted version in sources."""
        for issue in self.sm.repository.issues:
            issue_title = issue.title.strip()

            if not issue_title.endswith(_VERSION_REQUEST_ISSUE):
                continue

            parts = issue_title.split(' ')
            if len(parts) != 2:
                continue

            _LOGGER.info(f"Found an issue which requests new version release with number: {issue.number}")
            # The first part is our version, the second is the 'release' keyword.
            version_identifier = parts[0]
            branch_name = 'v' + version_identifier

            with cloned_repo(self.service_url, self.slug) as repo:
                if not self._adjust_version_in_sources(version_identifier, labels, issue):
                    _LOGGER.error("Giving up with automated release")
                    return

                repo.git.checkout('HEAD', b=branch_name)
                repo.git.tag(version_identifier)
                message = _VERSION_PULL_REQUEST_NAME.format(version_identifier)
                repo.index.commit(message)
                # If this PR already exists, this will fail.
                repo.remote().push(version_identifier)

                request = self.sm.open_merge_request(message, branch_name, body='', labels=labels)

                _LOGGER.info(
                    f"Opened merge request with {request.number} for new release of {self.slug} "
                    f"in version {version_identifier}"
                )
