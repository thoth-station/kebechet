#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Kevin Postlethwait
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

import git  # noqa F401

from kebechet.exception import DependencyManagementError  # noqa F401
from kebechet.exception import InternalError  # noqa F401
from kebechet.exception import PipenvError  # noqa F401
from kebechet.managers.manager import ManagerBase, refresh_repo_url
from thoth.sourcemanagement.sourcemanagement import Issue  # noqa F401
from thoth.sourcemanagement.sourcemanagement import PullRequest  # noqa F401
from kebechet.utils import cloned_repo
from thoth.common import ThothAdviserIntegrationEnum

_BRANCH_NAME = "kebechet_thoth"
_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "issues", "issue", "merge_request"]


class ThothAdviseManager(ManagerBase):
    """Manage updates of dependencies using Thoth."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothAdvise manager."""
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        super().__init__(*args, **kwargs)

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    def _construct_branch_name(self) -> str:
        """Construct branch name for the updated dependency."""
        return f"{_BRANCH_NAME}-{self.sha[:10]}"

    @refresh_repo_url
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
            _LOGGER.info("No changes necessary, exiting...")
            return None

        # push force always to keep branch up2date with the recent master and avoid merge conflicts.
        _LOGGER.info("Pushing changes")
        self._git_push(":pushpin: " + commit_msg, branch_name, files, force_push=True)

        # Check if the merge request already exists
        for mr in self._cached_merge_requests:
            if mr.source_branch == branch_name:
                _LOGGER.info("Merge request already exists, updating...")
                return None

        _LOGGER.info("Opening merge request")
        merge_request = self.sm.open_merge_request(
            commit_msg, branch_name, body, labels
        )
        return merge_request

    @staticmethod
    def _write_advise(adv_results: list):
        lock_info = adv_results[0]["report"][0][1]["requirements_locked"]
        with open("Pipfile.lock", "w+") as f:
            _LOGGER.info("Writing to Pipfile.lock")
            _LOGGER.debug(f"{json.dumps(lock_info)}")
            f.write(json.dumps(lock_info))

    def _issue_advise_error(self, adv_results: list, labels: list):
        """Create an issue if advise fails."""
        _LOGGER.debug(json.dumps(adv_results))
        textblock = ""
        errors = adv_results[0]["report"][0][0]
        for error in errors:
            justification = error["justification"]
            type_ = error["type"]
            _LOGGER.info(f"Error type: {type_}")
            textblock = (
                textblock
                + f"## Error type: {type_}\n"
                + f"**Justification**: {justification}\n"
            )

        checksum = hashlib.md5(textblock.encode("utf-8")).hexdigest()[:10]
        _LOGGER.info("Creating issue")
        self.sm.open_issue_if_not_exist(
            f"{checksum} - Automated kebechet thoth-advise Issue",
            lambda: textblock,
            labels=labels,
        )

    def run(self, labels: list, analysis_id=None):
        """Run Thoth Advising Bot."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "ThothAdviseManager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        if analysis_id is None:
            with cloned_repo(self, depth=1) as repo:
                self.repo = repo
                if not os.path.isfile("Pipfile"):
                    _LOGGER.warning("Pipfile not found in repo... Creating issue")
                    self.sm.open_issue_if_not_exist(
                        "Missing Pipfile",
                        lambda: "Check your repository to make sure Pipfile exists",
                        labels=labels,
                    )
                    return False

                lib.advise_here(
                    nowait=True,
                    origin=(f"{self.service_url}/{self.slug}"),
                    source_type=ThothAdviserIntegrationEnum.KEBECHET,
                )
            return True
        else:
            with cloned_repo(self, depth=1) as repo:
                self.repo = repo
                _LOGGER.info("Using analysis results from %s", analysis_id)
                res = lib.get_analysis_results(analysis_id)
                branch_name = self._construct_branch_name()
                branch = self.repo.git.checkout("-B", branch_name)  # noqa F841
                self._cached_merge_requests = self.sm.repository.get_pr_list()

                if res is None:
                    _LOGGER.error(
                        "Advise failed on server side, contact the maintainer"
                    )
                    return False
                _LOGGER.debug(json.dumps(res))

                if res[1] is False:
                    _LOGGER.info("Advise succeeded")
                    self._write_advise(res)
                    self._open_merge_request(branch_name, labels, ["Pipfile.lock"])
                    return True
                else:
                    _LOGGER.warning(
                        "Found error while running adviser... Creating issue"
                    )
                    self._issue_advise_error(res, labels)
                    return False
