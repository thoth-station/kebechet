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

"""A variety of functions to be used in version manager with no home in particular."""


from datetime import datetime
from typing import Callable, Optional, Dict, List, Any
import os
import re
import logging

from git import Repo
from thoth.glyph import generate_log, MLModel, Format

from . import constants

_get_new_version = constants._get_new_version
_LOGGER = logging.getLogger(__name__)


def _adjust_version_file(file_path: str, update_function: Callable) -> Optional[tuple]:
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

            new_version = update_function(old_version)
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


def _prev_release_tag(repo: Repo, old_version: str) -> Optional[str]:
    tags = repo.git.tag().splitlines()

    for tag in tags:
        if old_version == tag or re.match(f"v?{old_version}", tag):
            return tag
    else:
        return None


def _write_to_changelog(changelog, new_version):
    _LOGGER.info("Adding changelog to the CHANGELOG.md file")
    file_mode = "r+" if os.path.exists("CHANGELOG.md") else "w+"
    with open("CHANGELOG.md", file_mode) as changelog_file:
        lines = changelog_file.readlines()
        changelog_file.seek(0, 0)
        if len(lines) > 0 and lines[0].startswith(
            "# "
        ):  # checking if title its a title of type "# Title"
            changelog_file.write(lines[0])
            changelog_file.write(
                f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
            )
            changelog_file.write("\n".join(changelog) + "\n")
            changelog_file.write("".join(lines[1:]))
        elif (
            len(lines) > 1 and lines[1][0] == "="
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


def _compute_changelog(
    repo: Repo,
    old_version: str,
    new_version: str,
    changelog_smart: bool,
    changelog_classifier: str,
    changelog_format: str,
    prev_release_tag: Optional[str] = None,
    version_file: bool = False,
) -> List[str]:
    """Compute changelog for the given repo.

    If version file is used, add changelog to the version file and add changes to git.
    """
    _LOGGER.info(
        "Computing changelog for new release from version %r to version %r",
        old_version,
        new_version,
    )

    if not prev_release_tag:
        _LOGGER.info(
            "Old version was not found in the git tag history, assuming initial release"
        )
        # Use the initial commit if this the previous tag was not found - this
        # can be in case of the very first release.
        old_versions = repo.git.rev_list("HEAD", max_parents=0).split()
        old_version = old_versions[-1]
    else:
        old_version = prev_release_tag

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
        file_mode = "r+" if os.path.exists("CHANGELOG.md") else "w+"
        with open("CHANGELOG.md", file_mode) as changelog_file:
            lines = changelog_file.readlines()
            changelog_file.seek(0, 0)
            if len(lines) > 0 and lines[0].startswith(
                "# "
            ):  # checking if title its a title of type "# Title"
                changelog_file.write(lines[0])
                changelog_file.write(
                    f"\n## Release {new_version} ({datetime.now().replace(microsecond=0).isoformat()})\n"
                )
                changelog_file.write("\n".join(changelog) + "\n")
                changelog_file.write("".join(lines[1:]))
            elif (
                len(lines) > 1 and lines[1][0] == "="
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


def _is_merge_event(payload: Dict[str, Any]):
    if payload["service_type"] != "GITHUB":
        raise NotImplementedError(
            "This function only works for GitHub payloads at this time."
        )
    if (
        payload["event"] == "pull_request"
        and payload["raw_payload"]["payload"]["action"] == "closed"
    ):
        return payload["raw_payload"]["payload"]["pull_request"]["merged"]


def _pr_id_from_webhook(payload: Dict[str, Any]):
    return payload["raw_payload"]["payload"]["number"]
