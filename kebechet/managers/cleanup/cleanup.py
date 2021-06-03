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

"""Removes unused libraries from requirements files."""

import logging
import typing

from kebechet.managers.manager import ManagerBase
from kebechet.utils imoprt cloned_repo

_LOGGER = logging.getLogger(__name__)

class CleanupManager(ManagerBase):
    """Manager to check whether all the packages defined in requirements are used. If not removes unused ones from requirements files."""
    
    def run(self) -> typing.Optional[dict]: 
        """Check packages usage and remove from requirements if not used."""
        return None
