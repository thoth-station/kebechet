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

"""Manages the 'approved' label."""

import logging
import typing

from kebechet.utils import cloned_repo

from .manager import Manager


_LOGGER = logging.getLogger(__name__)


class ApprovelManager(Manager):
    """Manager for adding or removing the 'approved' label of Merge/Pull Requests."""

    def run(self, mr_url: str) -> typing.Optional[dict]:
        """Add or remove the 'approved' label of the given Merge/Pull Request."""
        pass
