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

"""Report information about repository and Kebechet itself."""

import logging
import typing

from kebechet.managers.manager import ManagerBase
from kebechet.utils import cloned_repo

from .messages import INFO_REPORT

_INFO_ISSUE_NAME = 'Kebechet info'

_LOGGER = logging.getLogger(__name__)


class InfoManager(ManagerBase):
    """Manager for submitting information about running Kebechet instance."""

    def run(self) -> typing.Optional[dict]:
        """Check for info issue and close it with a report."""
        issue = self.sm.get_issue(_INFO_ISSUE_NAME)
        if not issue:
            _LOGGER.info("No issue to report to, exiting")
            return

        _LOGGER.info(f"Found issue {_INFO_ISSUE_NAME}, generating report")
        with cloned_repo(self.service_url, self.slug) as repo:
            # We could optimize this as the get_issue() does API calls as well. Keep it this simple now.
            self.sm.close_issue_if_exists(
                _INFO_ISSUE_NAME,
                INFO_REPORT.format(
                    sha=repo.head.commit.hexsha,
                    slug=self.slug,
                    environment_details=self.get_environment_details(),
                    dependency_graph=self.get_dependency_graph(graceful=True),
                )
            )
