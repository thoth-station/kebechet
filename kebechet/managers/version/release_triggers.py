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

import toml
from ogr.abstract import Issue, PullRequest
from kebechet.utils import get_issue_by_title
from kebechet.managers.manager import ManagerBase

from . import constants
from .exceptions import VersionError
from .messages import (
    RELEASE_TAG_MISSING_WARNING,
    ISSUE_BODY_NO_VERSION_IDENTIFIER_FOUND,
    UNABLE_TO_UPDATE_VERSION_ERROR,
)

_LOGGER = logging.getLogger(__name__)


class BaseTrigger:
    """Base class for triggers of new version releases."""

    def adjust_version_toml_file(self, file_path: str) -> Optional[tuple]:
        """Adjust version in the toml file, return signalizes whether the return value indicates change in file."""
        with open(file_path, "r") as f:
            toml_content = toml.loads(f.read())
        project = toml_content.get("project", {})
        old_version = project.get("version")
        if old_version:
            try:
                new_version = self.get_new_version(old_version)
            except VersionError as e:
                raise VersionError(
                    UNABLE_TO_UPDATE_VERSION_ERROR.format(
                        file_path=file_path,
                        line_num=1,
                        old_version=old_version,
                        reason=str(e),
                        environment_details=ManagerBase.get_environment_details(),
                    )
                ) from e
            _LOGGER.info("Computed new version: %s", new_version)
            toml_content["project"]["version"] = new_version
            with open(file_path, "w") as output_file:
                output_file.write(toml.dumps(toml_content))
            return new_version, old_version
        return None

    def adjust_version_file(self, file_path: str) -> Optional[tuple]:
        """Adjust version in the given file, return signalizes whether the return value indicates change in file."""
        changed = False
        old_version = None
        with open(file_path, "r") as input_file:
            content = input_file.read().splitlines()
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

                try:
                    new_version = self.get_new_version(old_version)
                except VersionError as e:
                    raise VersionError(
                        UNABLE_TO_UPDATE_VERSION_ERROR.format(
                            file_path=file_path,
                            line_num=idx + 1,
                            old_version=old_version,
                            reason=str(e),
                            environment_details=ManagerBase.get_environment_details(),
                        )
                    ) from e
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
        for root, dirs, files in os.walk("./"):
            dirs[:] = [
                d for d in dirs if not d[0] == "."
            ]  # remove hidden dirs (done in place to remove from walk)
            if "tests" in dirs:
                dirs.remove("tests")
            files = [f for f in files if not f[0] == "."]  # remove hidden files
            files_dict = {
                "setup.py": self.adjust_version_file,
                "__init__.py": self.adjust_version_file,
                "__about__.py": self.adjust_version_file,
                "version.py": self.adjust_version_file,
                "app.py": self.adjust_version_file,
                "wsgi.py": self.adjust_version_file,
                "pyproject.toml": self.adjust_version_toml_file,
            }
            for file_name in files:
                if file_name in files_dict:
                    func_to_call = files_dict[file_name]
                    adjusted_version = func_to_call(os.path.join(root, file_name))
                    if adjusted_version:
                        adjusted.append(
                            (
                                os.path.join(root, file_name),
                                adjusted_version[0],
                                adjusted_version[1],
                            )
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
        truncated_changelog = changelog[: constants._MAX_CHANGELOG_SIZE]
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
        if len(changelog) > constants._MAX_CHANGELOG_SIZE:
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
                f"The version found in sources is not a valid SemVer string: `{old_version}`"
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
                body=ISSUE_BODY_NO_VERSION_IDENTIFIER_FOUND.format(
                    github_id=self.pull_request.id
                ),
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
                f"The version found in sources is not a valid SemVer string: `{old_version}`"
            ) from e

    def _get_pr_greeting(self) -> str:
        greeting = f"Hey, @{self.issue.author}!\n\n"

        if self.issue.title.lower == self._TITLE2UPDATE_INDEX[3]:  # patch
            return f"{greeting}Opening this PR to fix the last release.\n"
        elif self.issue.title.lower == self._TITLE2UPDATE_INDEX[2]:  # minor
            return f"{greeting}Opening this PR to create a release in a backwards compatible manner.\n"
        elif self.issue.title.lower == self._TITLE2UPDATE_INDEX[1]:  # major
            return f"{greeting}Your possible backwards incompatible changes will be released by this PR.\n"
        else:  # default
            return f"{greeting}Creating requested release.\n"

    def construct_pr_body(self, changelog: List[str], has_prev_release: bool) -> str:
        """Construct body of the opened pull request with version update."""
        # Copy body from the original issue, this is helpful in case of
        # instrumenting CI (e.g. Depends-On in case of Zuul) so automatic
        # merges are perfomed as desired.
        body = self._get_pr_greeting()
        truncated_changelog = changelog[: constants._MAX_CHANGELOG_SIZE]
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
        if len(changelog) > constants._MAX_CHANGELOG_SIZE:
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
                body=ISSUE_BODY_NO_VERSION_IDENTIFIER_FOUND.format(
                    github_id=self.issue.id
                ),
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
