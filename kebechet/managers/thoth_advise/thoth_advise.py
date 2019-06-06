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


class ThothAdviseManager(ManagerBase):
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
        self.slug = repo.remote().url.split(':', maxsplit=1)[1][:-len('.git')]

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    # TODO: determine how branch name will be constructed
    def _construct_branch_name(self) -> str:
        """Construct branch name for the updated dependency."""
        return f"{_BRANCH_NAME}-{self.sha}"

    
    def _git_push(self, commit_msg: str, branch_name: str, files: list, force_push: bool = False) -> None:
        """Perform git push after adding files and giving a commit message."""
        #  self.repo.git.checkout('HEAD', b=branch_name)
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    
    def _open_merge_request(self, branch_name: str, labels: list, files: list) -> typing.Optional[int]:
        """Open a pull/merge request for dependency update."""
        commit_msg = "Auto generated update"
        body = "Pipfile.lock updated by kebechet-thoth manager"

        # Delete branch if it didn't change Pipfile.lock
        diff = self.repo.git.diff('master', files)
        if diff == "":
            return
        
        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        self._git_push(":pushpin: " + commit_msg, branch_name, files, force_push=True)
        
        for mr in self._cached_merge_requests:
            if mr.head_branch_name == branch_name:
                return
        
        merge_request = self.sm.open_merge_request(commit_msg, branch_name, body, labels)
        return merge_request

    @staticmethod
    def _write_advise(adv_results: list):
        lock_info = adv_results[0]["report"][0][1]["requirements_locked"]
        with open("Pipfile.lock", "w+") as f:
            f.write(json.dumps(lock_info))
        return

    def _issue_advise_error(self, adv_results: list, labels: list):
        error_info = adv_results[0]["report"][0][0][0]
        justification = error_info["justification"]
        type_ = error_info["type"]
        checksum = hashlib.md5(justification.encode('utf-8')).hexdigest()[:10]
        self.sm.open_issue_if_not_exist(
            f"{checksum}-{type_}: Automated kebechet thoth-advise Issue",
            lambda: justification,
            labels
        )

    def run(self, labels: list):
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            branch_name = self._construct_branch_name()
            branch = self.repo.git.checkout('-B', branch_name)
            self._cached_merge_requests = self.sm.repository.merge_requests
            if os.path.isfile('Pipfile'):
                res = lib.advise_here()
                print(res)
                if res[1] == False:
                    self._write_advise(res)
                    self._open_merge_request(branch_name, ['bot'], ["Pipfile.lock"])
                else:
                    self._issue_advise_error(res, labels)
