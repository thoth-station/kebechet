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

"""Exceptions and errors that can be found in Kebechet."""


class KebechetException(Exception):
    """A base class for Kebechet exception hierarchy."""


class ConfigurationError(KebechetException):
    """Raised on error in configuration file."""


class PipenvError(KebechetException):
    """Raised on missing/invalid Pipenv or Pipenv.lock file."""


class InternalError(KebechetException):
    """Raised for internal errors, should not occur for end-user."""


class PullRequestError(KebechetException):
    """Raised in case of failed pull request."""


class DependencyManagementError(KebechetException):
    """
    An exception raised if there is an error in dependency management in the repo.

    This errors are usually wrong or missing Pipfile, Pipfile.lock, requirments.in or requirments.txt.
    """
