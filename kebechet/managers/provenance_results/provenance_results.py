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


class ProvenanceResultsManager(ManagerBase):
    """Manage source issues of dependencies."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothProvenance manager."""
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    def _issue_provenance_error(self, prov_results: list, labels: list):
        error_info = prov_results[0]
        text_block = ""

        for err in error_info:
            _LOGGER.info(f"{err['id']}: {err['package_name']} {err['package_version']}")
            text_block = (
                text_block
                + f"## {err['type']}: {err['id']} - {err['package_name']}:{err['package_version']}\n"
                + f"**Justification: {err['justification']}**\n"
                + f"#### source: \n {pprint.pformat(err['source'])}\n"
                + f"#### lock_info:\n {pprint.pformat(err['package_locked'])}"
            )

        checksum = hashlib.md5(text_block.encode("utf-8")).hexdigest()[:10]

        self.sm.open_issue_if_not_exist(
            f"{checksum} - {len(error_info)}: Automated kebechet thoth-provenance Issue",
            lambda: text_block,
            labels=labels,
        )

    def run(self, analysis_id: str, labels: list):
        """Run the provenance check bot."""
        res = lib.get_analysis_results(analysis_id)
        if res is None:
            _LOGGER.error("Provenance check failed on server side, contact the maintainer")
            return
        if res[1] is False:
            _LOGGER.info("Provenance check found problems, creating issue...")
            self._issue_provenance_error(res, labels)
            return False
        else:
            _LOGGER.info("Provenance check found no problems, carry on coding :)")
            return True
