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
from kebechet.utils import cloned_repo
from kebechet.managers import ManagerBase
from thoth.common import ThothAdviserIntegrationEnum
from thoth.common.enums import InternalTriggerEnum

from .messages import (
    DEFAULT_PR_BODY,
    MISSING_PACKAGE_PR_BODY,
    MISSING_PACKAGE_VERSION_PR_BODY,
    NEW_RELEASE_PR_BODY,
    NEW_CVE_PR_BODY,
    HASH_MISMATCH_PR_BODY,
)
from .messages import (
    MISSING_PACKAGE_ISSUE_BODY,
    HASH_MISMATCH_ISSUE_BODY,
    NEW_CVE_ISSUE_BODY,
    MISSING_PACKAGE_VERSION_ISSUE_BODY,
)

_BRANCH_NAME = "kebechet_thoth"
_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "issues", "issue", "merge_request"]


_INTERNAL_TRIGGER_PR_BODY_LOOKUP = {
    InternalTriggerEnum.CVE.value: NEW_CVE_PR_BODY,
    InternalTriggerEnum.HASH_MISMATCH.value: HASH_MISMATCH_PR_BODY,
    InternalTriggerEnum.MISSING_PACKAGE.value: MISSING_PACKAGE_PR_BODY,
    InternalTriggerEnum.MISSING_VERSION.value: MISSING_PACKAGE_VERSION_PR_BODY,
    InternalTriggerEnum.NEW_RELEASE.value: NEW_RELEASE_PR_BODY,
}

_INTERNAL_TRIGGER_ISSUE_BODY_LOOKUP = {
    InternalTriggerEnum.CVE.value: NEW_CVE_ISSUE_BODY,
    InternalTriggerEnum.HASH_MISMATCH.value: HASH_MISMATCH_ISSUE_BODY,
    InternalTriggerEnum.MISSING_PACKAGE.value: MISSING_PACKAGE_ISSUE_BODY,
    InternalTriggerEnum.MISSING_VERSION.value: MISSING_PACKAGE_VERSION_ISSUE_BODY,
}


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

    def _git_push(
        self, commit_msg: str, branch_name: str, files: list, force_push: bool = False
    ) -> None:
        """Perform git push after adding files and giving a commit message."""
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    def _open_merge_request(
        self, branch_name: str, labels: list, files: list, metadata: dict
    ) -> typing.Optional[int]:
        """Open a pull/merge request for dependency update."""
        commit_msg = "Auto generated update"

        kebechet_metadata = metadata.get(
            "kebechet_metadata"
        )  # type: typing.Optional[dict]
        if kebechet_metadata is not None and kebechet_metadata.get(
            "message_justification"
        ):
            body = _INTERNAL_TRIGGER_PR_BODY_LOOKUP[
                kebechet_metadata.get("message_justification")
            ].format(
                package=kebechet_metadata.get("package_name"),
                version=kebechet_metadata.get("package_version"),
                index=kebechet_metadata.get("package_index"),
            )
        else:
            body = DEFAULT_PR_BODY

        # Delete branch if it didn't change Pipfile.lock
        diff = self.repo.git.diff(self.project.default_branch, files)
        if diff == "":
            _LOGGER.info("No changes necessary, exiting...")
            return None

        # push force always to keep branch up2date with the recent branch HEAD and avoid merge conflicts.
        _LOGGER.info("Pushing changes")
        self._git_push(":pushpin: " + commit_msg, branch_name, files, force_push=True)

        # Check if the merge request already exists
        for mr in self._cached_merge_requests:
            if mr.source_branch == branch_name:
                _LOGGER.info("Merge request already exists, updating...")
                return None

        _LOGGER.info("Opening merge request")
        pr = self.project.create_pr(
            title=commit_msg,
            body=body,
            target_branch=self.project.default_branch,
            source_branch=branch_name,
        )
        pr.add_label(*labels)

        return pr

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

            kebechet_metadata = adv_results[0]["metadata"].get("kebechet_metadata")

            if (
                kebechet_metadata is not None
                and kebechet_metadata.get("message_justification") is not None
            ):
                internal_trigger_info = _INTERNAL_TRIGGER_ISSUE_BODY_LOOKUP[
                    kebechet_metadata["message_justification"]
                ].format(
                    package=kebechet_metadata.get("package_name"),
                    version=kebechet_metadata.get("package_version"),
                    index=kebechet_metadata.get("package_index"),
                )
            else:
                internal_trigger_info = ""

            textblock = (
                textblock
                + f"## Error type: {type_}\n"
                + f"**Justification**: {justification}\n"
                + internal_trigger_info
            )

        checksum = hashlib.md5(textblock.encode("utf-8")).hexdigest()[:10]
        issue_title = f"{checksum} - Automated kebechet thoth-advise Issue"
        issue = self.get_issue_by_title(issue_title)
        if not issue:
            _LOGGER.info("Creating issue")
            self.project.create_issue(
                title=issue_title,
                body=textblock,
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
                    issue = self.get_issue_by_title("Missing Pipfile")
                    if not issue:
                        self.project.create_issue(
                            title="Missing Pipfile",
                            body="Check your repository to make sure Pipfile exists",
                            labels=labels,
                        )

                    return False

                lib.advise_here(
                    nowait=True,
                    origin=(f"{self.service_url}/{self.slug}"),
                    source_type=ThothAdviserIntegrationEnum.KEBECHET,
                    kebechet_metadata=self.metadata,
                )
            return True
        else:
            with cloned_repo(self, depth=1) as repo:
                self.repo = repo
                _LOGGER.info("Using analysis results from %s", analysis_id)
                res = lib.get_analysis_results(analysis_id)
                branch_name = self._construct_branch_name()
                branch = self.repo.git.checkout("-B", branch_name)  # noqa F841
                self._cached_merge_requests = self.project.get_pr_list()

                if res is None:
                    _LOGGER.error(
                        "Advise failed on server side, contact the maintainer"
                    )
                    return False
                _LOGGER.debug(json.dumps(res))

                if res[1] is False:
                    _LOGGER.info("Advise succeeded")
                    self._write_advise(res)
                    self._open_merge_request(
                        branch_name, labels, ["Pipfile.lock"], res[0].get("metadata")
                    )
                    return True
                else:
                    _LOGGER.warning(
                        "Found error while running adviser... Creating issue"
                    )
                    self._issue_advise_error(res, labels)
                    return False
