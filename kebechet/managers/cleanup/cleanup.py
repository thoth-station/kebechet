#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2021 Tlegen Kamidollayev
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

"""Removes unused libraries from requirements files."""

import logging
import typing

from kebechet.managers.manager import ManagerBase
from kebechet.utils import cloned_repo

import toml

_LOGGER = logging.getLogger(__name__)

class CleanupManager(ManagerBase):
    """Manager to check whether all the packages defined in requirements are used. If not removes unused ones from requirements files."""

    #adopted from pipfile_requirements/pipfile_requirements.py

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

    def run(self) -> typing.Optional[dict]:
        """Check packages usage and remove from requirements if not used."""
        return None
