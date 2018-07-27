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
import typing

from git import Repo
from IGitt.Interfaces.Issue import Issue
import yaml
import semver
from datetime import datetime

from kebechet.utils import cloned_repo
from kebechet.managers.manager import ManagerBase


_LOGGER = logging.getLogger(__name__)
_VERSION_PULL_REQUEST_NAME = 'Release of version {}'
_NO_VERSION_FOUND_ISSUE_NAME = f"No version identifier found in sources to perform a release"
_MULTIPLE_VERSIONS_FOUND_ISSUE_NAME = f"Multiple version identifiers found in sources to perform a new release"
_NO_MAINTAINERS_ERROR = "No release maintainers stated for this repository"
_DIRECT_VERSION_TITLE = ' release'
_RELEASE_TITLES = {
    "New calendar release": lambda _: datetime.utcnow().strftime("%y.%m.%d"),
    "New major release": semver.bump_major,
    "New minor release": semver.bump_minor,
    "New patch release": semver.bump_patch,
    "New pre-release": semver.bump_prerelease,
    "New build release": semver.bump_build,
}


class VersionError(Exception):
    """An exception raised on invalid version provided or found in the repo."""


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    def _adjust_version_file(self, file_path: str, issue: Issue) -> typing.Optional[str]:
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

                old_version = parts[1][1:-1]  # Remove ' and " in string representation.
                _LOGGER.info("Old version found in sources: %s", old_version)

                new_version = self._get_new_version(issue.title.strip(), old_version)
                _LOGGER.info("Computed new version: %s", new_version)

                content[idx] = f'__version__ = "{new_version}"'
                changed = True

        if not changed:
            return None

        # Apply changes.
        with open(file_path, 'w') as output_file:
            output_file.write("\n".join(content))
            # Add new line at the of file explicitly.
            output_file.write("\n")

        return new_version

    def _adjust_version_in_sources(self, repo: Repo, labels: list, issue: Issue) -> typing.Optional[str]:
        """Walk through the directory structure and try to adjust version identifier in sources."""
        adjusted = []
        for root, _, files in os.walk('./'):
            for file_name in files:
                if file_name in ('setup.py', '__init__.py', 'version.py'):
                    file_path = os.path.join(root, file_name)
                    new_version = self._adjust_version_file(file_path, issue)
                    if new_version:
                        repo.git.add(file_path)
                        adjusted.append((file_path, new_version))

        if len(adjusted) == 0:
            error_msg = _NO_VERSION_FOUND_ISSUE_NAME
            _LOGGER.warning(error_msg)
            self.sm.open_issue_if_not_exist(
                error_msg,
                lambda: "Automated version release cannot be performed.\nRelated: #" + str(issue.number),
                labels
            )

        if len(adjusted) > 1:
            error_msg = _MULTIPLE_VERSIONS_FOUND_ISSUE_NAME
            _LOGGER.warning(error_msg)
            self.sm.open_issue_if_not_exist(
                error_msg,
                lambda x: "Automated version release cannot be performed.\nRelated: #" + str(issue.number),
                labels
            )

        # Return version identifier.
        return adjusted[0][1]

    def _get_maintainers(self, labels: list = None) -> list:
        """Get maintainers based on configuration.

        Maintainers can be either stated in the configuration or in the OWNERS file in the repo itself.
        """
        try:
            with open('OWNERS', 'r') as owners_file:
                owners = yaml.load(owners_file)
            maintainers = list(map(str, owners['maintainers']))
        except (FileNotFoundError, KeyError, ValueError, yaml.ParseError):
            _LOGGER.exception("Failed to load maintainers file")
            self.sm.open_issue_if_not_exist(
                _NO_MAINTAINERS_ERROR,
                lambda: "This repository is not correctly setup for automated version releases. "
                        "Please revisit bot configuration.",
                labels=labels
            )
            return []

        self.sm.close_issue_if_exists(_NO_MAINTAINERS_ERROR, "No longer relevant for the current bot setup.")
        return maintainers

    @staticmethod
    def _get_new_version(issue_title: str, current_version: str) -> typing.Optional[str]:
        """Get next version based on user request."""
        handler = _RELEASE_TITLES.get(issue_title)
        if handler:
            try:
                return handler(current_version)
            except ValueError as exc:  # Semver raises ValueError when version cannot be parsed.
                raise VersionError(f"Wrong version specifier found in sources: {str(exc)}") from exc

        if issue_title.endswith(_DIRECT_VERSION_TITLE):  # a specific release
            parts = issue_title.split(' ')
            if len(parts) == 2:
                return parts[0]

        return None

    @staticmethod
    def _is_release_request(issue_title):
        """Check for possible candidate for a version bump."""
        return _RELEASE_TITLES.get(issue_title) is not None \
            or issue_title.endswith(_DIRECT_VERSION_TITLE) and len(issue_title.split(' ')) == 2

    def run(self, maintainers: list = None, labels: list = None) -> None:
        """Check issues for new issue request, if a request exists, issue a new PR with adjusted version in sources."""
        reported_issues = []
        for issue in self.sm.repository.issues:
            issue_title = issue.title.strip()

            if issue_title.startswith((_NO_VERSION_FOUND_ISSUE_NAME, _MULTIPLE_VERSIONS_FOUND_ISSUE_NAME)):
                # Reported issues that should be closed on success version change.
                reported_issues.append(issue)

            # This is an optimization not to clone repo each time.
            if not self._is_release_request(issue_title):
                continue

            _LOGGER.info(
                "Found an issue #%s which is a candidate for request of new version release: %s",
                issue.number, issue.title
            )

            with cloned_repo(self.service_url, self.slug) as repo:
                maintainers = maintainers or self._get_maintainers(labels)
                if issue.author.username not in maintainers:
                    issue.add_comment(
                        f"Sorry, @{issue.author.username} but you are not stated in maintainers section for "
                        f"this project. Maintainers are @" + ', @'.join(maintainers)
                        if maintainers else "Sorry, no maintainers configured."
                    )
                    issue.close()
                    # Next issue.
                    continue

                try:
                    version_identifier = self._adjust_version_in_sources(repo, labels, issue)
                except VersionError as exc:
                    _LOGGER.exception("Failed to adjust version information in sources")
                    issue.add_comment(str(exc))
                    issue.close()
                    raise

                if not version_identifier:
                    _LOGGER.error("Giving up with automated release")
                    return

                branch_name = 'v' + version_identifier
                repo.git.checkout('HEAD', b=branch_name)
                message = _VERSION_PULL_REQUEST_NAME.format(version_identifier)
                repo.index.commit(message)
                repo.git.tag(version_identifier)
                # If this PR already exists, this will fail.
                repo.remote().push(branch_name)
                repo.remote().push(tags=True)

                request = self.sm.open_merge_request(
                    message,
                    branch_name,
                    body='Fixes: #' + str(issue.number),
                    labels=labels
                )

                _LOGGER.info(
                    f"Opened merge request with {request.number} for new release of {self.slug} "
                    f"in version {version_identifier}"
                )

        for reported_issue in reported_issues:
            reported_issue.add_comment("Closing as this issue is no longer relevant.")
            reported_issue.close()
