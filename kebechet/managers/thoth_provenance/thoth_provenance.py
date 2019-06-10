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

"""Consume Thoth Output for Kebechet auto-dependency management"""

import hashlib
import os
import logging
import toml
import re
import json
import typing
from itertools import chain
from functools import partial
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

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.


class ThothProvenanceManager(ManagerBase):
    """Manage updates of dependencies."""

    def __init__(self, *args, **kwargs):
        """Initialize update manager."""
        self._repo = None
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    @property
    def repo(self):
        """Get repository on which we work on."""
        return self._repo

    @repo.setter
    def repo(self, repo: git.Repo):
        """Set repository information and all derived information needed."""
        self._repo = repo
        self.slug = repo.remote().url.split(":", maxsplit=1)[1][: -len(".git")]

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    def _issue_provenance_error(self, prov_results: list, labels: list):
        error_info = prov_results[0]
        text_block = ""
        # XXX: Does not have any real values
        for err in error_info:
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

    def run(self, labels: list):
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            if os.path.isfile("Pipfile") and os.path.isfile("Pipfile.lock"):
                with open("Pipfile", "r") as pipfile, open(
                    "Pipfile.lock", "r"
                ) as piplock:
                    res = lib.provenance_check(pipfile.read(), piplock.read())
                print(res)
                if res != None and res[1] == False:
                    self._issue_provenance_error(res, labels)
