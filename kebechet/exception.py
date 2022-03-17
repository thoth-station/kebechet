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

"""Exceptions and errors that can be found in Kebechet."""

from delegator import Command


class KebechetException(Exception):
    """A base class for Kebechet exception hierarchy."""


class ConfigurationError(KebechetException):
    """Raised on error in configuration file."""


class PipenvError(KebechetException):
    """Raised on missing/invalid Pipenv or Pipenv.lock file."""

    def __init__(self, command: Command, *args, **kwargs):
        """Asssign values for exception so that they can be used in issue reports automatically."""
        self.command = command.cmd
        self.stdout = command.out
        self.stderr = command.err
        self.raw_command = command
        super().__init__(*args)

    def char_limit_dict(self, char_limit: int):
        """Return command, stdout, and stderr in a dictionary with a maximum num. of characters allocated."""
        to_ret = {}
        attrs = [
            (len(self.command), "command", self.command),
            (len(self.stdout), "stdout", self.stdout),
            (len(self.stderr), "stderr", self.stderr),
        ]
        attrs.sort()  # sorted according to string length, ensures largest attrs get highest char limit
        individual_char_limit = int(char_limit / len(attrs))
        for i in range(len(attrs)):
            curr = attrs[i]
            if curr[0] < individual_char_limit:
                to_ret[curr[1]] = curr[2]

                # distribute remaining limit, the max is to avoid divide by 0 on the final iteration
                individual_char_limit += int(
                    (individual_char_limit - curr[0]) / max(1, len(attrs) - i - 1)
                )
            else:
                to_ret[curr[1]] = curr[2][: individual_char_limit - 3] + "..."

        return to_ret


class InternalError(KebechetException):
    """Raised for internal errors, should not occur for end-user."""


class PullRequestError(KebechetException):
    """Raised in case of failed pull request."""


class WebhookPayloadError(KebechetException):
    """An exception raised if there is an error if the webhook passed cannot be parsed as a json.

    Generally the payload is empty or not of proper json format.
    """


class CannotFetchPRError(KebechetException):
    """An exception raised if there OGR cannot fetch the PR's for a repo.

    Generally the token is invalid or doesn't have access to the repo.
    """


class CannotFetchBranchesError(KebechetException):
    """An exception raised if there OGR cannot fetch the repo branches.

    Generally the token is invalid or doesn't have access to the repo.
    """


class CreatePRError(KebechetException):
    """An exception raised if there OGR cannot create an PR.

    Generally the token is invalid or doesn't have access to the repo.
    """
