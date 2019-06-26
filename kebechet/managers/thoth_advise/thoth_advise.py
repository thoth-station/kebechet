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


class ThothAdviseManager(ManagerBase):
    """Manage updates of dependencies using Thoth."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothAdvise manager."""
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    def run(self, labels: list):
        """Run Thoth Advising Bot."""
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            if not os.path.isfile("Pipfile"):
                _LOGGER.warning("Pipfile not found in repo... Creating issue")
                self.sm.open_issue_if_not_exist(
                    "Missing Pipfile",
                    lambda: "Check your repository to make sure Pipfile exists",
                    labels=labels
                )
                return False

            lib.advise_here(nowait=True, origin=(f"{self.service_url}/{self.slug}))
            return True
