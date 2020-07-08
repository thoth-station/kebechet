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
from kebechet.utils import construct_raw_file_url
from kebechet.utils import cloned_repo

import requests
import toml

_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "merge_request"]


class PipfileRequirementsManager(ManagerBase):
    """Keep requirements.txt in sync with Pipfile or Pipfile.lock."""

    @staticmethod
    def get_pipfile_requirements(content_str: str) -> typing.Set[str]:
        """Parse Pipfile file and gather requirements, respect version specifications listed."""
        content = toml.loads(content_str)

        requirements = set()
        for package_name, entry in content["packages"].items():
            if not isinstance(entry, str):
                # e.g. using git, ...
                raise ValueError(
                    "Package {} does not use pinned version: {}".format(
                        package_name, entry
                    )
                )

            package_version = entry if entry != "*" else ""
            requirements.add(f"{package_name}{package_version}")

        return requirements

    @staticmethod
    def get_pipfile_lock_requirements(content_str: str) -> typing.Set[str]:
        """Parse Pipfile.lock and gather pinned down requirements."""
        content = json.loads(content_str)

        requirements = set()
        for package_name, package_version in content.items():
            if not isinstance(package_version, str):
                # e.g. using git, ...
                raise ValueError(
                    "Unsupported version entry for {}: {!r}".format(
                        package_name, package_version
                    )
                )

            specifier = package_version if package_version != "*" else ""
            requirements.add(f"{package_name}{specifier}")

        return requirements

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
        file_url = construct_raw_file_url(
            self.service_url, self.slug, file_name, self.service_type
        )

        _LOGGER.debug("Downloading %r from %r", file_name, file_url)
        # TODO: propagate tls_verify for internal GitLab instances here and bellow as well
        response = requests.get(file_url)
        response.raise_for_status()
        pipfile_content = (
            sorted(self.get_pipfile_lock_requirements(response.text))
            if lockfile
            else sorted(self.get_pipfile_requirements(response.text))
        )

        file_url = construct_raw_file_url(
            self.service_url, self.slug, "requirements.txt", self.service_type
        )
        _LOGGER.debug("Downloading requirements.txt from %r", file_url)
        response = requests.get(file_url)
        if response.status_code == 404:
            # If the requirements.txt file does not exist, create it.
            requirements_txt_content = []
        else:
            response.raise_for_status()
            requirements_txt_content = sorted(response.text.splitlines())

        if pipfile_content == requirements_txt_content:
            _LOGGER.info("Requirements in requirements.txt are up to date")
            # TODO: delete branch if already exists
            return

        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            with open("requirements.txt", "w") as requirements_file:
                requirements_file.write("\n".join(pipfile_content))
                requirements_file.write("\n")

            branch_name = "pipfile-requirements-sync"
            repo.git.checkout(b=branch_name)
            repo.index.add(["requirements.txt"])
            repo.index.commit(
                "Update requirements.txt respecting requirements in {}".format(
                    "Pipfile" if not lockfile else "Pipfile.lock"
                )
            )
            repo.remote().push(branch_name)
