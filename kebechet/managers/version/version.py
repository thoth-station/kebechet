#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019 Fridolin Pokorny
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
    "new calendar release": lambda _: datetime.utcnow().strftime("%Y.%m.%d"),
    "new major release": semver.bump_major,
    "new minor release": semver.bump_minor,
    "new patch release": semver.bump_patch,
    "new pre-release": semver.bump_prerelease,
    "new build release": semver.bump_build,
}


class VersionError(Exception):
    """An exception raised on invalid version provided or found in the repo."""


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    def _adjust_version_file(self, file_path: str, issue: Issue) -> typing.Optional[tuple]:
        """Adjust version in the given file, return signalizes whether the return value indicates change in file."""
        with open(file_path, 'r') as input_file:
            content = input_file.read().splitlines()

        changed = False
        new_version = None
        old_version = None
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

        return new_version, old_version

    def _adjust_version_in_sources(self, repo: Repo, labels: list, issue: Issue) -> typing.Optional[tuple]:
        """Walk through the directory structure and try to adjust version identifier in sources."""
        adjusted = []
        for root, _, files in os.walk('./'):
            for file_name in files:
                if file_name in ('setup.py', '__init__.py', 'version.py'):
                    file_path = os.path.join(root, file_name)
                    adjusted_version = self._adjust_version_file(file_path, issue)
                    if adjusted_version:
                        repo.git.add(file_path)
                        adjusted.append((file_path, adjusted_version[0], adjusted_version[1]))

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

        # Return old and new version identifier.
        return adjusted[0][1], adjusted[0][2]

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
        handler = _RELEASE_TITLES.get(issue_title.lower())
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
        issue_title = issue_title.lower()
        return _RELEASE_TITLES.get(issue_title) is not None \
            or issue_title.endswith(_DIRECT_VERSION_TITLE) and len(issue_title.split(' ')) == 2

    @staticmethod
    def _compute_changelog(repo: Repo, old_version: str, new_version: str,
                           version_file: bool = False) -> typing.List[str]:
        """Compute changelog for the given repo.

        If version file is used, add changelog to the version file and add changes to git.
        """
        _LOGGER.debug("Computing changelog for new release from version %r to version %r", old_version, new_version)
        if old_version not in repo.git.tag().splitlines():
            _LOGGER.debug("Old version was not found in the git tag history, assuming initial release")
            # Use the initial commit if this the previous tag was not found - this
            # can be in case of the very first release.
            old_version = repo.git.rev_list('HEAD', max_parents=0)

        changelog = repo.git.log(f'{old_version}..HEAD', no_merges=True, format='* %s').splitlines()
        if version_file:
            # TODO: We should prepend changes instead of appending them.
            _LOGGER.info("Adding changelog to the CHANGELOG.md file")
            with open('CHANGELOG.md', 'a') as changelog_file:
                changelog_file.write(
                    f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
                )
                changelog_file.write('\n'.join(changelog))
                changelog_file.write('\n')
            repo.git.add('CHANGELOG.md')

        _LOGGER.debug("Computed changelog has %d entries", len(changelog))
        return changelog

    @staticmethod
    def _construct_pr_body(issue: Issue, changelog: str) -> str:
        """Construct body of the opened pull request with version update."""
        # Copy body from the original issue, this is helpful in case of
        # instrumenting CI (e.g. Depends-On in case of Zuul) so automatic
        # merges are perfomed as desired.
        body = ''
        if issue.description:
            body = issue.description + '\n\n'

        body += 'Related: #' + str(issue.number) + '\n\nChangelog:\n' + '\n'.join(changelog)
        return body

    def run(self, maintainers: list = None, assignees: list = None,
            labels: list = None, changelog_file: bool = False) -> None:
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
                if assignees:
                    try:
                        self.sm.assign(issue, assignees)
                    except Exception:
                        _LOGGER.exception(f"Failed to assign {assignees} to issue #{issue.number}")
                        issue.add_comment("Unable to assign provided assignees, please check bot configuration.")

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
                    version_identifier, old_version = self._adjust_version_in_sources(repo, labels, issue)
                except VersionError as exc:
                    _LOGGER.exception("Failed to adjust version information in sources")
                    issue.add_comment(str(exc))
                    issue.close()
                    raise

                if not version_identifier:
                    _LOGGER.error("Giving up with automated release")
                    return

                changelog = self._compute_changelog(
                    repo, old_version, version_identifier, version_file=changelog_file
                )
                branch_name = 'v' + version_identifier
                repo.git.checkout('HEAD', b=branch_name)
                message = _VERSION_PULL_REQUEST_NAME.format(version_identifier)
                repo.index.commit(message)
                # If this PR already exists, this will fail.
                repo.remote().push(branch_name)

                request = self.sm.open_merge_request(
                    message,
                    branch_name,
                    body=self._construct_pr_body(issue, changelog),
                    labels=labels
                )

                _LOGGER.info(
                    f"Opened merge request with {request.number} for new release of {self.slug} "
                    f"in version {version_identifier}"
                )

        for reported_issue in reported_issues:
            reported_issue.add_comment("Closing as this issue is no longer relevant.")
            reported_issue.close()
