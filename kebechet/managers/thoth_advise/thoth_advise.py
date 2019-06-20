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

_BRANCH_NAME = "kebechet_thoth"


class ThothAdviseManager(ManagerBase):
    """Manage updates of dependencies using Thoth."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothAdvise manager."""
        # TODO: What needs to be changed for event driven Kebechet??
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    def _construct_branch_name(self) -> str:
        """Construct branch name for the updated dependency."""
        return f"{_BRANCH_NAME}-{self.sha}"

    def _git_push(
        self, commit_msg: str, branch_name: str, files: list, force_push: bool = False
    ) -> None:
        """Perform git push after adding files and giving a commit message."""
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    def _open_merge_request(
        self, branch_name: str, labels: list, files: list
    ) -> typing.Optional[int]:
        """Open a pull/merge request for dependency update."""
        commit_msg = "Auto generated update"
        body = "Pipfile.lock updated by kebechet-thoth manager"

        # Delete branch if it didn't change Pipfile.lock
        diff = self.repo.git.diff("master", files)
        if diff == "":
            return

        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        LOGGER_.info('Pushing changes')
        self._git_push(":pushpin: " + commit_msg, branch_name, files, force_push=True)

        # Check if the merge request already exists
        for mr in self._cached_merge_requests:
            if mr.head_branch_name == branch_name:
                LOGGER_.info('Merge request already exists, updating...')
                return

        LOGGER_.info('Opening merge request')
        merge_request = self.sm.open_merge_request(
            commit_msg, branch_name, body, labels
        )
        return merge_request

    @staticmethod
    def _write_advise(adv_results: list):
        lock_info = adv_results[0]["report"][0][1]["requirements_locked"]
        with open("Pipfile.lock", "w+") as f:
            LOGGER_.info('Writing to Pipfile.lock')
            LOGGER_.debug(f"{json.dumps(lock_info)}")
            f.write(json.dumps(lock_info))
        return

    def _issue_advise_error(self, adv_results: list, labels: list):
        """Create an issue if advise fails."""
        error_info = adv_results[0]["report"][0][0][0]
        justification = error_info["justification"]
        type_ = error_info["type"]
        LOGGER_.warning('Error type: {type_}')
        checksum = hashlib.md5(justification.encode("utf-8")).hexdigest()[:10]
        LOGGER_.info('Creating issue')
        self.sm.open_issue_if_not_exist(
            f"{checksum}-{type_}: Automated kebechet thoth-advise Issue",
            lambda: justification,
            labels=labels,
        )

    def run(self, labels: list):
        """Run Thoth Advising Bot."""
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            branch_name = self._construct_branch_name()
            branch = self.repo.git.checkout("-B", branch_name)
            self._cached_merge_requests = self.sm.repository.merge_requests
            if os.path.isfile("Pipfile"):
                res = lib.advise_here()
                for i in range(1, 11):
                    if res is not None:
                        break
                    LOGGER_.info(f"Advising failed, retrying ({i}/10)")
                    res = lib.advise_here(force=True)

                if res is None:
                    LOGGER_.error("Advising failed")
                    return False
                LOGGER_.debug(f"{json.dumps(res)}")

                if res[1] is False:
                    LOGGER_.info('Advise succeeded')
                    self._write_advise(res)
                    self._open_merge_request(branch_name, ["bot"], ["Pipfile.lock"])
                    return True
                else:
                    LOGGER_.warning('Found error while running adviser... Creating issue')
                    self._issue_advise_error(res, labels)
                    return False
