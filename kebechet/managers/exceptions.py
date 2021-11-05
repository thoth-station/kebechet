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

"""Exceptions used by the update manager."""


class ManagerFailedException(Exception):
    """Used to explicitly fail managers without opening issues."""


class DependencyManagementError(ManagerFailedException):
    """An exception raised if there is an error in dependency management in the repo.

    This errors are usually wrong or missing Pipfile, Pipfile.lock, requirments.in or requirments.txt.
    """
