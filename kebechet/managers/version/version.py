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

"""Automatically issue a new PR with adjusted version for Python projects."""

import logging

from kebechet.utils import cloned_repo
from kebechet.managers.manager import ManagerBase

_LOGGER = logging.getLogger(__name__)
_VERSION_REQUEST_ISSUE = ' release'
_VERSION_PULL_REQUEST_NAME = 'Release of version {}'


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    def _adjust_version_in_sources(self, version_identifier: str):
        # TODO: Implement
        return

    def run(self, labels: list = None) -> None:
        """Check issues for new issue request, if a request exists, issue a new PR with adjusted version in sources."""
        for issue in self.sm.repository.issues:
            issue_title = issue.title.strip()

            if not issue_title.endswith(_VERSION_REQUEST_ISSUE):
                continue

            parts = issue_title.split(' ')
            if len(parts) != 2:
                continue

            _LOGGER.info(f"Found an issue which requests new version release with number: {issue.number}")
            # The first part is our version, the second is the 'release' keyword.
            version_identifier = parts[0]
            branch_name = 'v' + version_identifier

            with cloned_repo(self.service_url, self.slug) as repo:
                self._adjust_version_in_sources(version_identifier)

                repo.git.checkout('HEAD', b=branch_name)
                repo.git.tag(version_identifier)
                message = _VERSION_PULL_REQUEST_NAME.format(version_identifier)
                repo.index.commit(message)
                # If this PR already exists, this will fail.
                repo.remote().push(version_identifier)

                request = self.sm.open_merge_request(message, branch_name, body='', labels=labels)

                _LOGGER.info(
                    f"Opened merge request with {request.number} for new release of {self.slug} "
                    f"in version {version_identifier}"
                )
