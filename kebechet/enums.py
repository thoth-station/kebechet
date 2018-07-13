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

"""Enumerations used in Kebechet."""

from enum import Enum
from enum import auto


class ServiceType(Enum):
    """A service Kebechet talks to."""

    GITHUB = auto()
    GITLAB = auto()

    @classmethod
    def by_name(cls, name: str):
        """Get service type by its name."""
        # Use GitHub by default.
        if name is None:
            return cls.GITHUB

        name = name.lower()

        if name == 'github':
            return cls.GITHUB
        elif name == 'gitlab':
            return cls.GITLAB
        else:
            raise NotImplementedError(f"Unsupported service {name!r}, available ones are 'github' and 'gitlab'")
