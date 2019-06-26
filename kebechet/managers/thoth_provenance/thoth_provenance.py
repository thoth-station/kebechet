#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019 Kevin Postlethwait
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

"""Consume Thoth Output for Kebechet auto-dependency management."""

import hashlib
import os
import logging
import json
import typing
import pprint

from thamos import lib
import git

from kebechet.exception import DependencyManagementError
from kebechet.exception import InternalError
from kebechet.exception import PipenvError
from kebechet.managers.manager import ManagerBase
from kebechet.source_management import Issue
from kebechet.source_management import MergeRequest
from kebechet.utils import cloned_repo


_LOGGER = logging.getLogger(__name__)

_BRANCH_NAME = "kebechet_thoth"


class ThothProvenanceManager(ManagerBase):
    """Manage source issues of dependencies."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothProvenance manager."""
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    def run(self, labels: list):
        """Run the provenance check bot."""
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            if not (os.path.isfile("Pipfile") and os.path.isfile("Pipfile.lock")):
                _LOGGER.warning("Pipfile or Pipfile.lock is missing from repo, opening issue")
                self.sm.open_issue_if_not_exist(
                    "Missing pipenv files",
                    lambda: "Check your repository to make sure Pipfile and Pipfile.lock exist.",
                    labels=labels
                )
                return False
        lib.provenance_check_here(nowait=True, origin=(self.service_url + self.slug))
        return True
