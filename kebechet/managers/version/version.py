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

"""Automatically issue a new PR with adjusted version for Python projects."""

import os
import re
import typing

import logging

from git import Repo
from ogr.abstract import Issue
import yaml
import semver
from datetime import datetime
from github.GithubException import GithubException

from kebechet.utils import cloned_repo
from kebechet.managers.manager import ManagerBase
from thoth.glyph import generate_log
from thoth.glyph import MLModel
from thoth.glyph import Format
from thoth.glyph import ThothGlyphException
from .messages import RELEASE_TAG_MISSING_WARNING

_LOGGER = logging.getLogger(__name__)
_VERSION_PULL_REQUEST_NAME = "Release of version {}"
_NO_VERSION_FOUND_ISSUE_NAME = (
    "No version identifier found in sources to perform a release"
)
_MULTIPLE_VERSIONS_FOUND_ISSUE_NAME = (
    "Multiple version identifiers found in sources to perform a new release."
)
_MULTIPLE_VERSIONS_FOUND_ISSUE_BODY = "Please have only one version string, to facilitate automated releases.\
         Multiple version strings found in these files - "
_NO_MAINTAINERS_ERROR = "No release maintainers stated for this repository"
_BODY_TRUNCATED = "The changelog body was truncated, please check CHANGELOG.md for the complete changelog."
_DIRECT_VERSION_TITLE = " release"
_RELEASE_TITLES = {
    "new calendar release": lambda _: datetime.utcnow().strftime("%Y.%m.%d"),
    "new major release": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).bump_major(),
    "new minor release": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).bump_minor(),
    "new patch release": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).bump_patch(),
    "new pre-release": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).bump_prerelease(),
    "new build release": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).bump_build(),
    "finalize version": lambda current_version: semver.VersionInfo.parse(
        current_version
    ).finalize_version(),
}


# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["issues", "issue"]
# Maximum number of log messages in a single release. Set due to ultrahook limits.
_MAX_CHANELOG_SIZE = 300


class VersionError(Exception):
    """An exception raised on invalid version provided or found in the repo."""


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    # Previous release tag present
    _PREV_RELEASE_TAG = False

    def _adjust_version_file(
        self, file_path: str, issue: Issue
    ) -> typing.Optional[tuple]:
        """Adjust version in the given file, return signalizes whether the return value indicates change in file."""
        with open(file_path, "r") as input_file:
            content = input_file.read().splitlines()

        changed = False
        new_version = None
        old_version = None
        for idx, line in enumerate(content):
            if line.startswith("__version__ = "):
                parts = line.split(" = ", maxsplit=1)
                if len(parts) != 2:
                    _LOGGER.warning(
                        "Found '__version__' identifier but unable to parse old version, skipping: %r",
                        line,
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
        with open(file_path, "w") as output_file:
            output_file.write("\n".join(content))
            # Add new line at the of file explicitly.
            output_file.write("\n")

        return new_version, old_version

    def _adjust_version_in_sources(
        self, repo: Repo, labels: typing.Optional[list], issue: Issue
    ) -> typing.Optional[tuple]:
        """Walk through the directory structure and try to adjust version identifier in sources."""
        adjusted = []
        for root, _, files in os.walk("./"):
            for file_name in files:
                if file_name in (
                    "setup.py",
                    "__init__.py",
                    "__about__.py",
                    "version.py",
                    "app.py",
                    "wsgi.py",
                ):
                    file_path = os.path.join(root, file_name)
                    adjusted_version = self._adjust_version_file(file_path, issue)
                    if adjusted_version:
                        repo.git.add(file_path)
                        adjusted.append(
                            (file_path, adjusted_version[0], adjusted_version[1])
                        )

        if len(adjusted) == 0:
            error_msg = _NO_VERSION_FOUND_ISSUE_NAME
            _LOGGER.warning(error_msg)
            i = self.get_issue_by_title(error_msg)
            if i is None:
                self.project.create_issue(
                    title=error_msg,
                    body=f"Automated version release cannot be performed.\nRelated: #{issue.id}",
                    labels=labels,
                )
            return None

        if len(adjusted) > 1:
            error_msg = _MULTIPLE_VERSIONS_FOUND_ISSUE_NAME
            file_locations = [loc for loc, _, _ in adjusted]
            _LOGGER.warning(error_msg)
            _issue_body = (
                _MULTIPLE_VERSIONS_FOUND_ISSUE_BODY
                + "\n`"
                + ", ".join(file_locations)
                + "`"
            )
            i = self.get_issue_by_title(error_msg)
            if i is None:
                self.project.create_issue(
                    title=error_msg,
                    body=f"{_issue_body}\nRelated: #{issue.id}",
                    labels=labels,
                )
            return None

        # Return old and new version identifier.
        return adjusted[0][1], adjusted[0][2]

    def _get_maintainers(self, labels: list = None) -> list:
        """Get maintainers based on configuration.

        Maintainers can be either stated in the configuration or in the OWNERS file in the repo itself.
        """
        try:
            with open("OWNERS", "r") as owners_file:
                owners = yaml.safe_load(owners_file)
            maintainers = list(map(str, owners.get("maintainers") or []))
        except (FileNotFoundError, KeyError, ValueError, yaml.YAMLError):
            _LOGGER.exception("Failed to load maintainers file")
            issue = self.get_issue_by_title(_NO_MAINTAINERS_ERROR)
            if issue is None:
                self.project.create_issue(
                    title=_NO_MAINTAINERS_ERROR,
                    body="This repository is not correctly setup for automated version releases.",
                    labels=labels,
                )
            else:
                issue.comment("Please revisit bot configuration.")
            return []

        self.close_issue_and_comment(
            _NO_MAINTAINERS_ERROR, "No longer relevant for the current bot setup."
        )
        return maintainers

    @staticmethod
    def _get_new_version(
        issue_title: str, current_version: str
    ) -> typing.Optional[str]:
        """Get next version based on user request."""
        issue_title = issue_title.lower()

        handler = _RELEASE_TITLES.get(issue_title)
        if handler:
            try:
                return str(handler(current_version))
            except ValueError as exc:  # Semver raises ValueError when version cannot be parsed.
                raise VersionError(
                    f"Wrong version specifier found in sources: `{current_version}`"
                ) from exc

        if issue_title.endswith(_DIRECT_VERSION_TITLE):  # a specific release
            parts = issue_title.split(" ")
            if len(parts) == 2:
                return parts[0]

        return None

    @staticmethod
    def _is_release_request(issue_title):
        """Check for possible candidate for a version bump."""
        issue_title = issue_title.lower()
        return (
            _RELEASE_TITLES.get(issue_title) is not None
            or issue_title.endswith(_DIRECT_VERSION_TITLE)
            and len(issue_title.split(" ")) == 2
        )

    @classmethod
    def _compute_changelog(
        cls,
        repo: Repo,
        old_version: str,
        new_version: str,
        changelog_smart: bool,
        changelog_classifier: str,
        changelog_format: str,
        version_file: bool = False,
    ) -> typing.List[str]:
        """Compute changelog for the given repo.

        If version file is used, add changelog to the version file and add changes to git.
        """
        _LOGGER.info(
            "Computing changelog for new release from version %r to version %r",
            old_version,
            new_version,
        )
        tags = repo.git.tag().splitlines()

        for tag in tags:
            if old_version == tag or re.match(f"v?{old_version}", tag):
                old_version = tag
                cls._PREV_RELEASE_TAG = True
                break

        if not cls._PREV_RELEASE_TAG:
            _LOGGER.info(
                "Old version was not found in the git tag history, assuming initial release"
            )
            # Use the initial commit if this the previous tag was not found - this
            # can be in case of the very first release.
            old_versions = repo.git.rev_list("HEAD", max_parents=0).split()
            old_version = old_versions[-1]

        _LOGGER.info("Smart Log : %s", str(changelog_smart))

        if changelog_smart:
            _LOGGER.info("Classifier : %s", changelog_classifier)
            _LOGGER.info("Format : %s", changelog_format)
            changelog = repo.git.log(
                f"{old_version}..HEAD", no_merges=True, format="%s"
            ).splitlines()
            changelog = generate_log(
                changelog,
                Format.by_name(changelog_format),
                MLModel.by_name(changelog_classifier),
            )
        else:
            changelog = repo.git.log(
                f"{old_version}..HEAD", no_merges=True, format="* %s"
            ).splitlines()

        if version_file:
            _LOGGER.info("Adding changelog to the CHANGELOG.md file")
            with open("CHANGELOG.md", "w+") as changelog_file:
                lines = changelog_file.readlines()
                changelog_file.seek(0, 0)
                if lines[0].startswith(
                    "# "
                ):  # checking if title its a title of type "# Title"
                    changelog_file.write(lines[0])
                    changelog_file.write(
                        f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
                    )
                    changelog_file.write("\n".join(changelog) + "\n")
                    changelog_file.write("".join(lines[1:]))
                elif (
                    lines[1][0] == "="
                ):  # Checking if its a title of type "Title \n ===="
                    changelog_file.write(lines[0] + lines[1])
                    changelog_file.write(
                        f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
                    )
                    changelog_file.write("\n".join(changelog) + "\n")
                    changelog_file.write("".join(lines[2:]))
                else:  # No title
                    changelog_file.write(
                        f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
                    )
                    changelog_file.write("\n".join(changelog) + "\n")
                    changelog_file.write("".join(lines))

            repo.git.add("CHANGELOG.md")

        _LOGGER.info("Computed changelog has %d entries", len(changelog))
        return changelog

    @staticmethod
    def _adjust_pr_body(issue: Issue) -> str:
        if not issue.description:
            return ""

        result = "\n".join(issue.description.splitlines())
        result = result.replace(
            "Hey, Kebechet!\n\nCreate a new patch release, please.",
            f"Hey, @{issue.author}!\n\nOpening this PR to fix the last release.",
        )

        result = result.replace(
            "Hey, Kebechet!\n\nCreate a new minor release, please.",
            f"Hey, @{issue.author}!\n\nOpening this PR to create a release in a backwards compatible manner.",
        )

        return result.replace(
            "Hey, Kebechet!\n\nCreate a new major release, please.",
            f"Hey, @{issue.author}!\n\nYour possible backwards incompatible changes will be released by this PR.",
        )

    @classmethod
    def _construct_pr_body(cls, issue: Issue, changelog: typing.List[str]) -> str:
        """Construct body of the opened pull request with version update."""
        # Copy body from the original issue, this is helpful in case of
        # instrumenting CI (e.g. Depends-On in case of Zuul) so automatic
        # merges are perfomed as desired.
        body = cls._adjust_pr_body(issue)
        truncated_changelog = changelog[:_MAX_CHANELOG_SIZE]
        if not cls._PREV_RELEASE_TAG:
            body = body + "\n" + RELEASE_TAG_MISSING_WARNING
        body += (
            "\n\nCloses: #"
            + str(issue.id)
            + "\n\n```"
            + "\n\nChangelog:\n"
            + "\n".join(truncated_changelog)
            + "\n```"
        )
        if len(changelog) > _MAX_CHANELOG_SIZE:
            body += "\n" + _BODY_TRUNCATED
        return body

    def run(  # type: ignore
        self,
        maintainers: list = None,
        assignees: list = None,
        labels: list = None,
        changelog_file: bool = False,
        changelog_smart: bool = False,
        changelog_classifier: str = MLModel.DEFAULT.name,
        changelog_format: str = Format.DEFAULT.name,
    ) -> None:
        """Check issues for new issue request, if a request exists, issue a new PR with adjusted version in sources."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "Version Manager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        reported_issues = []
        for issue in self.project.get_issue_list():
            issue_title = issue.title.strip()

            if issue_title.startswith(
                (_NO_VERSION_FOUND_ISSUE_NAME, _MULTIPLE_VERSIONS_FOUND_ISSUE_NAME)
            ):
                # Reported issues that should be closed on success version change.
                reported_issues.append(issue)

            # This is an optimization not to clone repo each time.
            if not self._is_release_request(issue_title):
                continue

            _LOGGER.info(
                "Found an issue #%s which is a candidate for request of new version release: %s",
                issue.id,
                issue.title,
            )

            with cloned_repo(self) as repo:
                if assignees:
                    try:
                        issue.add_assignee(*assignees)
                    except Exception:
                        _LOGGER.exception(
                            f"Failed to assign {assignees} to issue #{issue.id}"
                        )
                        issue.comment(
                            "Unable to assign provided assignees, please check bot configuration."
                        )

                maintainers = maintainers or self._get_maintainers(labels)
                if issue.author.lower() not in (m.lower() for m in maintainers):
                    issue.comment(
                        f"Sorry, @{issue.author} but you are not stated in maintainers section for "
                        f"this project. Maintainers are @" + ", @".join(maintainers)
                        if maintainers
                        else "Sorry, no maintainers configured."
                    )
                    issue.close()
                    # Next issue.
                    continue

                try:
                    v_info = self._adjust_version_in_sources(repo, labels, issue)
                    if v_info is None:
                        return

                except VersionError as exc:
                    _LOGGER.exception("Failed to adjust version information in sources")
                    issue.comment(str(exc))
                    issue.close()
                    raise

                version_identifier, old_version = v_info

                if not version_identifier:
                    _LOGGER.error("Giving up with automated release")
                    return

                try:
                    changelog = self._compute_changelog(
                        repo,
                        old_version,
                        version_identifier,
                        changelog_smart,
                        changelog_classifier,
                        changelog_format,
                        version_file=changelog_file,
                    )
                except ThothGlyphException as exc:
                    _LOGGER.exception("Failed to generate smart release log")
                    issue.comment(str(exc))
                    issue.close()
                    return

                # If an issue exists, we close it as there is no change to source code.
                if not changelog:
                    message = f"Closing the issue as there is no changelog between the new release of {self.slug}."
                    _LOGGER.info(message)
                    issue.comment(message)
                    issue.close()
                    return

                branch_name = "v" + version_identifier
                repo.git.checkout("HEAD", b=branch_name)
                message = _VERSION_PULL_REQUEST_NAME.format(version_identifier)
                repo.index.commit(message)

                repo.remote().push(branch_name)

                try:
                    # If this PR already exists, this will fail.

                    pr = self.project.create_pr(
                        title=message,
                        body=self._construct_pr_body(issue, changelog),
                        target_branch=self.project.default_branch,
                        source_branch=branch_name,
                    )
                except GithubException as ghub_exc:
                    errors = ghub_exc.data.get("errors", [])  # type: ignore
                    for e in errors:
                        if isinstance(
                            e, dict
                        ) and "pull request already exists" in e.get("message", ""):
                            _LOGGER.warning(
                                "Attempted to open another PR for current branch."
                            )
                            return
                    else:
                        raise ghub_exc

                pr.add_label(*labels)

                _LOGGER.info(
                    f"Opened merge request with {pr.id} for new release of {self.slug} "
                    f"in version {version_identifier}"
                )

        for reported_issue in reported_issues:
            reported_issue.comment("Closing as this issue is no longer relevant.")
            reported_issue.close()
