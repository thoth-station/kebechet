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

"""Exceptions to be used throughout the Kebechet version manager."""

from kebechet.managers.exceptions import ManagerFailedException


class VersionError(Exception):
    """An exception raised on invalid version provided or found in the repo."""


class NoChangesException(Exception):
    """An exception raised if list of changes is found to be empty after being computed."""


class NotATriggerException(ManagerFailedException):
    """An exception that to be raised if is_trigger() is False."""
