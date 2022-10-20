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

"""Constants used for Kebechet version manager."""

from functools import partial
import semver
from datetime import datetime
import typing

from .exceptions import VersionError

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
_INVALID_LABEL_CONFIG_ISSUE_NAME = (
    ".thoth.yaml PR label release configuration is invalid"
)

# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["issues", "issue"]
# Maximum number of log messages in a single release. Set due to ultrahook limits.
_MAX_CHANGELOG_SIZE = 300


def _get_new_version(
    handler: typing.Callable, current_version: str
) -> typing.Optional[str]:
    """Get next version based on user request."""
    try:
        return str(handler(current_version))
    except ValueError as exc:  # Semver raises ValueError when version cannot be parsed.
        raise VersionError(
            f"Wrong version specifier found in sources: `{current_version}`"
        ) from exc


VERSION_UPDATE_LOOKUP_TABLE = [
    partial(
        _get_new_version, lambda _: datetime.utcnow().strftime("%Y.%m.%d")
    ),  # 0, calendar
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).bump_major()
    ),  # 1, major
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).bump_minor()
    ),  # 2, minor
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).bump_patch()
    ),  # 3, patch
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).bump_prerelease()
    ),  # 4, pre
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).bump_build()
    ),  # 5, build
    partial(
        _get_new_version, lambda v: semver.VersionInfo.parse(v).finalize_version()
    ),  # 6, finalize
]
