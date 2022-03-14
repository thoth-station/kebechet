#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2021 Kevin Postlethwait
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

"""Release triggers which result in new version released on GitHub."""

from typing import List, Optional, Any, Dict, Tuple
import logging
import os
import json

from ogr.abstract import Issue, PullRequest
from kebechet.utils import get_issue_by_title

from . import constants
from .exceptions import VersionError
from .messages import RELEASE_TAG_MISSING_WARNING

_LOGGER = logging.getLogger(__name__)


class BaseTrigger:
    """Base class for triggers of new version releases."""

    def adjust_version_file(self, file_path: str) -> Optional[tuple]:
        """Adjust version in the given file, return signalizes whether the return value indicates change in file."""
        with open(file_path, "r") as input_file:
            content = input_file.read().splitlines()

        changed = False
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

                new_version = self.get_new_version(old_version)
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

    def adjust_version_in_sources(
        self, labels: Optional[list]
    ) -> List[Tuple[str, str, str]]:
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
                    adjusted_version = self.adjust_version_file(file_path)
                    if adjusted_version:
                        adjusted.append(
                            (file_path, adjusted_version[0], adjusted_version[1])
                        )
        return adjusted

    def construct_pr_body(self, changelog: List[str], has_prev_release: bool):
        """Construct PR body for trigger."""
        raise NotImplementedError

    def is_trigger(self):
        """Check if trigger content makes object a trigger candidate."""
        raise NotImplementedError

    def get_new_version(self, old_version):
        """Update old version string."""
        raise NotImplementedError

    def open_many_files_adjusted_issue(
        self, adjusted_files: List[str], labels: List[str]
    ):
        """Open issue if multiple files are changed when updating version."""
        raise NotImplementedError

    def open_no_files_adjusted_issue(self, labels):
        """Open issue if no files are changed when updating version."""
        raise NotImplementedError


class ReleaseLabelConfig:
    """Configuration for getting update function from pull request labels."""

    def __init__(
        self,
        calendar: List[str] = ["calendar-release"],
        major: List[str] = ["major-release"],
        minor: List[str] = ["minor-release"],
        patch: List[str] = ["patch-release"],
        pre: List[str] = ["pre-release"],
        build: List[str] = ["build-release"],
        finalize: List[str] = [
            "finalize-version",
        ],
    ):
        """Initialize new instance of ReleaseLabelConfig."""
        self.update_lookup: Dict[str, int] = dict()

        def _set_all_to_value(d: dict, array: List[Any], v: Any) -> None:
            for i in array:
                if d.get(i):
                    raise ValueError(
                        "Duplicate label found for multiple release types."
                    )
                d[i] = v

        _set_all_to_value(self.update_lookup, calendar, 0)
        _set_all_to_value(self.update_lookup, major, 1)
        _set_all_to_value(self.update_lookup, minor, 2)
        _set_all_to_value(self.update_lookup, patch, 3)
        _set_all_to_value(self.update_lookup, pre, 4)
        _set_all_to_value(self.update_lookup, build, 5)
        _set_all_to_value(self.update_lookup, finalize, 6)

    @classmethod
    def from_dict(cls, attributes: dict):
        """Create instance of ReleaseLabelConfig from a dictionary.

        Args:
            attributes (Dict[str, List[str]]): values to be passed to __init__

        Raises:
            TypeError: unexpected keyword argument

        Returns:
            ReleaseLabelConfig: new instance from passed args
        """
        return cls(**attributes)

    @classmethod
    def from_json(cls, json_string: str):
        """Create instance of ReleaseLabelConfig from a json string.

        Args:
            json_string (str): json string which fits valid format for ReleaseLabelConfig
                i.e.: {"calendar": [...], "major": [...], ...}

        Raises:
            json.decoder.JSONDecodeError: for invalid json input
            TypeError: unexpected keyword argument

        Returns:
            ReleaseLabelConfig: new instance from parsed json
        """
        return cls.from_dict(json.loads(json_string))

    def get_index(self, label: str) -> Optional[int]:
        """Given a label, get the index of the update function.

        Args:
            label (str): pull request label

        Returns:
            Optional[int]: returns index of update function, see constants.VERSION_UPDATE_LOOKUP_TABLE
        """
        return self.update_lookup.get(label)

    def index_from_label_list(self, label_list: List[str]) -> Optional[int]:
        """Given a list of labels, return the index of the corresponding update function.

        Args:
            label_list (List[str]): list of labels set on a PR

        Raises:
            ValueError: if multiple labels correspond to entries in configuration

        Returns:
            Optional[int]: returns index of update function, see constants.VERSION_UPDATE_LOOKUP_TABLE
        """
        v = None
        for label in label_list:
            cur_v = self.update_lookup.get(label)
            if cur_v is not None:
                if v is not None:
                    raise ValueError("Multiple valid label values present.")
                v = cur_v
        return v


class ReleasePRlabels(BaseTrigger):
    """Trigger when PR is merged with certain labels set."""

    def __init__(
        self,
        label_config: ReleaseLabelConfig,
        pull_request: PullRequest,
    ):
        """Create new ReleasePR trigger."""
        self.label_config = label_config
        self.pull_request = pull_request

    def is_trigger(self) -> bool:
        """Return whether or not this object is a valid trigger for a new version.

        Returns:
            bool
        """
        list_of_labels = [lbl.name for lbl in self.pull_request.labels]
        return self.label_config.index_from_label_list(list_of_labels) is not None

    def construct_pr_body(self, changelog: List[str], has_prev_release: bool):
        """Construct body of the opened pull request with version update.

        Args:
            changelog (List[str]): List of individual changes based off of commits
            has_prev_release (bool): Whether or not the was a previous tag for the repository

        Returns:
            (str): The PR containing the new version string's body.
        """
        body = ""
        truncated_changelog = changelog[: constants._MAX_CHANELOG_SIZE]
        if not has_prev_release:
            body = body + "\n" + RELEASE_TAG_MISSING_WARNING
        body += (
            "\n\nFrom: #"
            + str(self.pull_request.id)
            + "\n\n```"
            + "\n\nChangelog:\n"
            + "\n".join(truncated_changelog)
            + "\n```"
        )
        if len(changelog) > constants._MAX_CHANELOG_SIZE:
            body += "\n" + constants._BODY_TRUNCATED
        return body

    def get_new_version(self, old_version):
        """Update the passed version using requested update type in the title.

        Args:
            old_version (str): base version which will be incremented by the update

        Raises:
            ValueError: none of the labels in this PR are supported based on configuration
            kebechet.managers.version.exceptions.VersionError: Wrong version specifier found in sources: {old_version}

        Returns:
            str: The computed version
        """
        label_list = [lbl.name for lbl in self.pull_request.labels]
        index = self.label_config.index_from_label_list(label_list)
        if index is None:
            raise ValueError("No supported labels found.")
        update_function = constants.VERSION_UPDATE_LOOKUP_TABLE[
            self.label_config.index_from_label_list(label_list)
        ]
        try:
            return update_function(old_version)
        except ValueError as e:  # Semver raises ValueError when version cannot be parsed.
            raise VersionError(
                f"Wrong version specifier found in sources: `{old_version}`"
            ) from e

    def open_no_files_adjusted_issue(self, labels: List[str]):
        """Open issue if no files are changed when updating version.

        Args:
            labels (List[str]): labels to apply to the issue

        Returns:
            None
        """
        error_msg = constants._NO_VERSION_FOUND_ISSUE_NAME
        _LOGGER.warning(error_msg)
        i = get_issue_by_title(self.pull_request.source_project, error_msg)
        if i is None:
            self.pull_request.source_project.create_issue(
                title=error_msg,
                body=f"Automated version release cannot be performed.\nRelated: #{self.pull_request.id}",
                labels=labels,
            )

    def open_many_files_adjusted_issue(
        self, adjusted_files: List[str], labels: List[str]
    ):
        """Open issue if multiple files are changed when updating version.

        Args:
            adjusted_files (List[str]): a list of files that were updated
            labels (List[str]): labels to apply to the issue

        Returns:
            None
        """
        error_msg = constants._MULTIPLE_VERSIONS_FOUND_ISSUE_NAME
        _LOGGER.warning(error_msg)
        _issue_body = (
            constants._MULTIPLE_VERSIONS_FOUND_ISSUE_BODY
            + "\n`"
            + ", ".join(adjusted_files)
            + "`"
        )
        i = get_issue_by_title(self.pull_request.source_project, error_msg)
        if i is None:
            self.pull_request.source_project.create_issue(
                title=error_msg,
                body=f"{_issue_body}\nRelated: #{self.pull_request.id}",
                labels=labels,
            )


class ReleaseIssue(BaseTrigger):
    """Representation of a git issue as a release trigger."""

    _TITLE2UPDATE_INDEX = [
        "new calendar release",  # index 0
        "new major release",  # index 1
        "new minor release",  # index 2
        "new patch release",  # index 3
        "new pre-release",  # index 4
        "new build release",  # index 5
        "finalize version",  # index 6
    ]

    def __init__(self, issue: Issue):
        """Create new release issue trigger."""
        self.issue = issue

    def _is_fresh(self):
        return len(self.issue.get_comments()) == 0

    def is_trigger(self) -> bool:
        """Return whether or not this object is a valid trigger for a new version.

        Returns:
            bool
        """
        t = self.issue.title.lower()
        return (
            t in self._TITLE2UPDATE_INDEX
            or (t.endswith(constants._DIRECT_VERSION_TITLE) and len(t.split(" ")) == 2)
            and self._is_fresh()
        )

    def get_new_version(self, old_version):
        """Update the passed version using requested update type in the title.

        Args:
            old_version (str): base version which will be incremented by the update

        Raises:
            ValueError: {self.issue.title} issue title not supported
            kebechet.managers.version.exceptions.VersionError: Wrong version specifier found in sources: {old_version}

        Returns:
            str: The computed version
        """
        t = self.issue.title.lower()

        if t.endswith(constants._DIRECT_VERSION_TITLE):  # a specific release
            parts = t.split(" ")
            if len(parts) == 2:
                return parts[0]

        try:
            update_function = constants.VERSION_UPDATE_LOOKUP_TABLE[
                self._TITLE2UPDATE_INDEX.index(t)
            ]
        except ValueError as e:
            raise ValueError(f"{t} issue title not supported.") from e

        try:
            return update_function(old_version)
        except ValueError as e:  # Semver raises ValueError when version cannot be parsed.
            raise VersionError(
                f"Wrong version specifier found in sources: `{old_version}`"
            ) from e

    def _adjust_pr_body(self) -> str:
        if not self.issue.description:
            return ""

        result = "\n".join(self.issue.description.splitlines())
        result = result.replace(
            "Hey, Kebechet!\n\nCreate a new patch release, please.",
            f"Hey, @{self.issue.author}!\n\nOpening this PR to fix the last release.",
        )

        result = result.replace(
            "Hey, Kebechet!\n\nCreate a new minor release, please.",
            f"Hey, @{self.issue.author}!\n\nOpening this PR to create a release in a backwards compatible manner.",
        )

        return result.replace(
            "Hey, Kebechet!\n\nCreate a new major release, please.",
            f"Hey, @{self.issue.author}!\n\nYour possible backwards incompatible changes will be released by this PR.",
        )

    def construct_pr_body(self, changelog: List[str], has_prev_release: bool) -> str:
        """Construct body of the opened pull request with version update."""
        # Copy body from the original issue, this is helpful in case of
        # instrumenting CI (e.g. Depends-On in case of Zuul) so automatic
        # merges are perfomed as desired.
        body = self._adjust_pr_body()
        truncated_changelog = changelog[: constants._MAX_CHANELOG_SIZE]
        if not has_prev_release:
            body = body + "\n" + RELEASE_TAG_MISSING_WARNING
        body += (
            "\n\nCloses: #"
            + str(self.issue.id)
            + "\n\n```"
            + "\n\nChangelog:\n"
            + "\n".join(truncated_changelog)
            + "\n```"
        )
        if len(changelog) > constants._MAX_CHANELOG_SIZE:
            body += "\n" + constants._BODY_TRUNCATED
        return body

    def open_no_files_adjusted_issue(self, labels) -> None:
        """Open issue if no files are changed when updating version.

        Args:
            labels (List[str]): labels to apply to the issue

        Returns:
            None
        """
        error_msg = constants._NO_VERSION_FOUND_ISSUE_NAME
        _LOGGER.warning(error_msg)
        i = get_issue_by_title(self.issue.project, error_msg)
        if i is None:
            self.issue.project.create_issue(
                title=error_msg,
                body=f"Automated version release cannot be performed.\nRelated: #{self.issue.id}",
                labels=labels,
            )

    def open_many_files_adjusted_issue(
        self,
        adjusted_files: List[str],
        labels: List[str],
    ) -> None:
        """Open issue if multiple files are changed when updating version.

        Args:
            adjusted_files (List[str]): a list of files that were updated
            labels (List[str]): labels to apply to the issue

        Returns:
            None
        """
        error_msg = constants._MULTIPLE_VERSIONS_FOUND_ISSUE_NAME
        _LOGGER.warning(error_msg)
        _issue_body = (
            constants._MULTIPLE_VERSIONS_FOUND_ISSUE_BODY
            + "\n`"
            + ", ".join(adjusted_files)
            + "`"
        )
        i = get_issue_by_title(self.issue.project, error_msg)
        if i is None:
            self.issue.project.create_issue(
                title=error_msg,
                body=f"{_issue_body}\nRelated: #{self.issue.id}",
                labels=labels,
            )
