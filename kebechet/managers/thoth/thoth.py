#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019 Fridolin Pokorny
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

"""Dependency update management logic."""

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

from .messages import ISSUE_CLOSE_COMMENT
from .messages import ISSUE_COMMENT_UPDATE_ALL
from .messages import ISSUE_INITIAL_LOCK
from .messages import ISSUE_NO_DEPENDENCY_MANAGEMENT
from .messages import ISSUE_PIPENV_UPDATE_ALL
from .messages import ISSUE_REPLICATE_ENV

_LOGGER = logging.getLogger(__name__)
_RE_VERSION_DELIMITER = re.compile('(==|===|<=|>=|~=|!=|<|>|\\[)')

_ISSUE_UPDATE_ALL_NAME = "Failed to update dependencies to their latest version"
_ISSUE_INITIAL_LOCK_NAME = "Failed to perform initial lock of software stack"
_ISSUE_REPLICATE_ENV_NAME = "Failed to replicate environment for updates"
_ISSUE_NO_DEPENDENCY_NAME = "No dependency management found"

_BRANCH_NAME = "kebechet_thoth"

# Note: We cannot use pipenv as a library (at least not now - version 2018.05.18) - there is a need to call it
# as a subprocess as pipenv keeps path to the virtual environment in the global context that is not
# updated on subsequent calls.


class ThothManager(ManagerBase):
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
        commit_msg = f"Test"
        body = "BODY"

        # If we have already an update for this package we simple issue git
        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        self._git_push(":pushpin: " + commit_msg, branch_name, files, force_push=True)
        merge_request = self.sm.open_merge_request(commit_msg, branch_name, body, labels)
        return merge_request

    def _advise_wrap(self):
        with open("Pipfile", "r") as pipfile:            
            res = lib.advise(pipfile.read(), "")
            print(res)
            pip_info = res[0]["report"][0][1]["requirements"]
            lock_info = res[0]["report"][0][1]["requirements_locked"]
        return res
    
    def _advise_and_write(self):
        res = self._advise_wrap()

        pip_info = res[0]["report"][0][1]["requirements"]
        lock_info = res[0]["report"][0][1]["requirements_locked"]
        with open("Pipfile", "w+") as f:
            f.write("[dev-packages]\n")
            for entry in pip_info["dev-packages"]:
                f.write("{} = \"{}\"\n".format(entry, pip_info["dev-packages"][entry]))

                f.write("\n[packages]\n")
                for entry in pip_info["packages"]:
                    f.write("{} = \"{}\"\n".format(entry, pip_info["packages"][entry]))
            
                f.write("\n[requires]\n")
                for entry in pip_info["requires"]:
                    f.write("{} = \"{}\"\n".format(entry, pip_info["requires"][entry]))
                        
                for index in pip_info["source"]:
                    f.write("\n[[source]]\n")
                    for entry in index:
                        if entry == "verify_ssl":
                            f.write("{} = {}\n".format(entry, str(index[entry]).lower()))
                        else:
                            f.write("{} = \"{}\"\n".format(entry, index[entry]))

        with open("Pipfile.lock", "w+") as f:
            f.write(json.dumps(lock_info))

        return


    def run(self, labels: list):
        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            self.repo = repo
            branch_name = self._construct_branch_name()
            branch = self.repo.git.checkout('-b', branch_name)
            # TODO: _advise_and_write
            # TODO: push _BRANCH_NAME
            # TODO: generate pull request if diff master Pipfile.lock and _BRANCH_NAME Pipfile.lock (git diff master _BRANCH_NAME)
            if os.path.isfile('Pipfile'):
                self._advise_and_write()
                self._open_merge_request(branch_name, ['bot'], ["Pipfile.lock"])
