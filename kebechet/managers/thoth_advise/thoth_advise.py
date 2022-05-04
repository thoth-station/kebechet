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

import logging
import json
import typing
import yaml
import os

from thamos import lib
from thamos.exceptions import ConfigurationError as ThothConfigurationError

import git  # noqa F401

from kebechet.managers.exceptions import DependencyManagementError  # noqa F401
from kebechet.exception import InternalError  # noqa F401
from kebechet.exception import PipenvError  # noqa F401
from kebechet.utils import cloned_repo
from kebechet.managers.manager import ManagerBase
from thoth.common import ThothAdviserIntegrationEnum, cwd
from thoth.common.enums import InternalTriggerEnum
from thoth.python.exceptions import FileLoadError
from ogr.abstract import Issue, PullRequest

from .messages import (
    DEFAULT_PR_BODY,
    MISSING_PACKAGE_PR_BODY,
    MISSING_PACKAGE_VERSION_PR_BODY,
    NEW_RELEASE_PR_BODY,
    NEW_CVE_PR_BODY,
    HASH_MISMATCH_PR_BODY,
    ADVISE_ACTION_NOT_PERMITTED,
)
from .messages import (
    MISSING_PACKAGE_ISSUE_BODY,
    HASH_MISMATCH_ISSUE_BODY,
    NEW_CVE_ISSUE_BODY,
    MISSING_PACKAGE_VERSION_ISSUE_BODY,
)

_BRANCH_NAME = "kebechet-thoth"
_LOGGER = logging.getLogger(__name__)
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["push", "issues", "issue", "merge_request"]

ADVISE_ISSUE_TITLE = "Kebechet Advise"

STARTED_ADVISE_COMMENT = "Started advise for {env}: analysis id = {analysis_id}, to get current status, click [here](\
    https://{host}/api/v1/advise/python/{analysis_id})"
STARTED_COMMENT_STARTS_WITH = STARTED_ADVISE_COMMENT[
    : STARTED_ADVISE_COMMENT.index("{env}")
]
STARTED_ADVISE_REGEX = r"^Started advise for ([\w\-]*): "

ADVISE_RESULT_PREFIX = "Result for {env}: "
SUCCESSFUL_ADVISE_COMMENT = ADVISE_RESULT_PREFIX + "Finished advise.\n\n"
SUCCESSFUL_ADVISE_REGEX = r"^Result for ([\w\-]*): Finished"
ERROR_ADVISE_REGEX = r"^Result for ([\w\-]*): Error"

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


APP_NAME = f'{os.getenv("GITHUB_APP_NAME", "khebhut").lower()}[bot]'


def _runtime_env_name_from_advise_response(response: dict):
    return response["result"]["parameters"]["project"]["runtime_environment"]["name"]


class ThothAdviseManager(ManagerBase):
    """Manage updates of dependencies using Thoth."""

    def __init__(self, *args, **kwargs):
        """Initialize ThothAdvise manager."""
        # We do API calls once for merge requests and we cache them for later use.
        self._cached_merge_requests = None
        self._issue_list = None

        self._tracking_issue = None  # if a Kebechet Advise issue is found it will be commented on to track progress
        super().__init__(*args, **kwargs)

    @property
    def sha(self):
        """Get SHA of the current head commit."""
        return self.repo.head.commit.hexsha

    def _construct_branch_name(self, analysis_id: str) -> str:
        """Construct branch name for the updated dependency."""
        return f"{_BRANCH_NAME}-{analysis_id[:15]}"

    def _git_push(
        self, commit_msg: str, branch_name: str, files: list, force_push: bool = False
    ) -> None:
        """Perform git push after adding files and giving a commit message."""
        self.repo.index.add(files)
        self.repo.index.commit(commit_msg)
        self.repo.remote().push(branch_name, force=force_push)

    def _open_merge_request(
        self, branch_name: str, labels: list, files: list, metadata: dict
    ) -> typing.Optional[PullRequest]:
        """Open a pull/merge request for dependency update."""
        commit_msg = "Auto generated update"

        if self._metadata_indicates_internal_trigger():
            body = _INTERNAL_TRIGGER_PR_BODY_LOOKUP[
                self.metadata["message_justification"]  # type: ignore
            ].format(
                package=self.metadata.get("package_name"),  # type: ignore
                version=self.metadata.get("package_version"),  # type: ignore
                index=self.metadata.get("package_index"),  # type: ignore
                document_id=metadata["document_id"],
            )
        else:
            body = DEFAULT_PR_BODY.format(document_id=metadata["document_id"])

        with open(".thoth.yaml", "r") as f:
            thoth_config = yaml.safe_load(f)
        overlays_dir = thoth_config.get("overlays_dir")

        full_name = (
            f"{overlays_dir}/{self.runtime_environment}"
            if overlays_dir
            else self.runtime_environment
        )

        body = f"# Automatic Update of {full_name} runtime-environment\n" + body

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
                mr.body = body
                return mr

        _LOGGER.info("Opening merge request")
        pr = self.create_pr(
            title=commit_msg,
            body=body,
            target_branch=self.project.default_branch,
            source_branch=branch_name,
        )
        pr.add_label(*labels)

        return pr

    def _write_advise(self, adv_results: dict):
        with open(".thoth.yaml", "r") as f:
            thoth_config = yaml.safe_load(f)
        overlays_dir = thoth_config.get("overlays_dir")
        requirements_lock = adv_results["result"]["report"]["products"][0]["project"][
            "requirements_locked"
        ]
        requirements = adv_results["result"]["parameters"]["project"]["requirements"]
        requirements_format = adv_results["result"]["parameters"]["requirements_format"]
        if overlays_dir:
            with cwd(f"{overlays_dir}/{self.runtime_environment}"):
                lib.write_files(
                    requirements=requirements,
                    requirements_lock=requirements_lock,
                    requirements_format=requirements_format,
                )
        else:
            lib.write_files(
                requirements=requirements,
                requirements_lock=requirements_lock,
                requirements_format=requirements_format,
            )

    def _act_on_advise_error(self, adv_results: dict):
        """Create an issue if advise fails."""
        _LOGGER.debug(json.dumps(adv_results))
        textblock = ""
        document_id = adv_results["metadata"]["document_id"]

        textblock = (
            textblock
            + "## Error:"
            + adv_results["result"]["error_msg"]
            + f"**runtime_environment**: {self.runtime_environment}\n"
            + "## Justification**:\n"
            + f"for more information please see https://thoth-station.ninja/search/advise/{document_id}/summary"
        )

        if self._tracking_issue:
            comment = (
                SUCCESSFUL_ADVISE_COMMENT.format(env=self.runtime_environment)
                + f"Adviser failed\n{textblock}"
            )
            self._tracking_issue.comment(comment)

    def _get_users_with_permission(self) -> typing.List[str]:
        try:
            with open("OWNERS", "r") as owners_file:
                owners = yaml.safe_load(owners_file)
            return list(map(str, owners.get("approvers") or [])) + [APP_NAME]
        except FileNotFoundError:
            return list(self.project.who_can_merge_pr()) + [APP_NAME]

    def _close_advise_issues4users_lacking_perms(self):
        permitted_users = self._get_users_with_permission()
        copy_of_issue_list = (
            self._issue_list.copy()
        )  # so we don't mess with iteration by removing items
        for issue in self._issue_list:
            if (
                issue.title == ADVISE_ISSUE_TITLE
                and issue.author.lower() not in permitted_users
            ):
                issue.comment(
                    ADVISE_ACTION_NOT_PERMITTED.format(
                        author=issue.author, permitted_users=", ".join(permitted_users)
                    )
                )
                issue.close()
                copy_of_issue_list.remove(issue)
        self._issue_list = copy_of_issue_list

    def _advise_issue_is_fresh(self, issue: Issue):
        return not issue.get_comments(author=APP_NAME)

    def _close_all_but_oldest_issue(self) -> typing.Optional[Issue]:
        oldest = None
        to_close: typing.List[Issue] = []
        for issue in self._issue_list:
            if issue.title == ADVISE_ISSUE_TITLE:
                if oldest is None:
                    oldest = issue
                elif oldest.created > issue.created:
                    to_close.append(oldest)
                    oldest = issue
                else:
                    to_close.append(issue)

        for issue in to_close:
            issue.comment(
                f"Older Kebechet Advise found that is still in progress, see #{oldest.id}"  # type: ignore
            )
            issue.close()
            self._issue_list.remove(issue)

        return oldest

    def _metadata_indicates_internal_trigger(self) -> bool:
        return bool(self.metadata and self.metadata.get("message_justification"))

    def run(self, labels: list, analysis_id=None):
        """Run Thoth Advising Bot."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "ThothAdviseManager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        self._issue_list = self.project.get_issue_list()
        self._close_advise_issues4users_lacking_perms()
        self._tracking_issue = self._close_all_but_oldest_issue()
        runtime_environments: typing.List[typing.Tuple[str, Issue]]

        if analysis_id is None:
            if self._tracking_issue is None:
                _LOGGER.debug("No issue found to start advises for.")
                return
            elif not self._advise_issue_is_fresh(self._tracking_issue):
                _LOGGER.debug(
                    "Issue has already been acted on by Kebechet and is still 'in progress'"
                )
                return

            with cloned_repo(self, self.project.default_branch, depth=1) as repo:
                self.repo = repo

                with open(".thoth.yaml", "r") as f:
                    thoth_config = yaml.safe_load(f)

                if thoth_config.get("overlays_dir"):
                    runtime_environments = [
                        e["name"] for e in thoth_config["runtime_environments"]
                    ]
                    for e in thoth_config["runtime_environments"]:
                        runtime_environments.append(e["name"])
                else:
                    runtime_environments = [
                        thoth_config["runtime_environments"][0]["name"]
                    ]

                for e in runtime_environments:
                    try:
                        analysis_id = lib.advise_here(
                            nowait=True,
                            origin=(f"{self.service_url}/{self.slug}"),
                            source_type=ThothAdviserIntegrationEnum.KEBECHET,
                            kebechet_metadata=self.metadata,
                            runtime_environment_name=e,
                        )
                        self._tracking_issue.comment(
                            STARTED_ADVISE_COMMENT.format(
                                analysis_id=analysis_id,
                                env=e,
                                host=thoth_config["host"],
                            )
                        )
                    except (FileLoadError, ThothConfigurationError) as exc:
                        if isinstance(exc, FileLoadError):
                            self._tracking_issue.comment(
                                f"""Result for {e}: Error advising, no requirements found.

                                If this project does not use requirements.txt or Pipfile then remove thoth-advise
                                manager from your .thoth.yaml configuration."""
                            )
                        elif isinstance(exc, ThothConfigurationError):
                            self._tracking_issue.comment(
                                f"""Result for {e}: Error advising, configuration error found in .thoth.yaml. The
                                following exception was caught when submitting:

                                ```
                                {exc}
                                ```"""
                            )
                            # open issue
                            # comment on advise issue with issue id
                        return False
            return True
        else:
            with cloned_repo(self, self.project.default_branch, depth=1) as repo:
                self.repo = repo
                _LOGGER.info("Using analysis results from %s", analysis_id)
                res = lib.get_analysis_results(analysis_id)
                if self._metadata_indicates_internal_trigger():
                    self._tracking_issue = None  # internal trigger advise results should not be tracked by issue
                branch_name = self._construct_branch_name(analysis_id)
                branch = self.repo.git.checkout("-B", branch_name)  # noqa F841
                self._cached_merge_requests = self.project.get_pr_list()

                if res is None:
                    _LOGGER.error(
                        "Advise failed on server side, contact the maintainer"
                    )
                    return False
                _LOGGER.debug(json.dumps(res))

                self.runtime_environment = _runtime_env_name_from_advise_response(
                    res[0]
                )
                to_ret = False
                if res[1] is False:
                    _LOGGER.info("Advise succeeded")
                    self._write_advise(res[0])
                    opened_merge = self._open_merge_request(
                        branch_name, labels, ["Pipfile.lock"], res[0].get("metadata")
                    )
                    if opened_merge and self._tracking_issue:
                        comment = (
                            SUCCESSFUL_ADVISE_COMMENT.format(
                                env=self.runtime_environment
                            )
                            + f"Opened merge request, see: #{opened_merge.id}"
                        )
                        self._tracking_issue.comment(comment)
                    elif self._tracking_issue:
                        comment = (
                            SUCCESSFUL_ADVISE_COMMENT.format(
                                env=self.runtime_environment
                            )
                            + "Dependencies for this runtime environment are already up to date :)."
                        )
                        self._tracking_issue.comment(comment)
                    to_ret = True
                else:
                    _LOGGER.warning(
                        "Found error while running adviser... Creating issue"
                    )
                    self._act_on_advise_error(res)
                if self._tracking_issue:
                    to_open = len(
                        self._tracking_issue.get_comments(
                            filter_regex=STARTED_ADVISE_REGEX,
                            author=APP_NAME,
                        )
                    )
                    finished = len(
                        self._tracking_issue.get_comments(
                            filter_regex=SUCCESSFUL_ADVISE_REGEX,
                            author=APP_NAME,
                        )
                    )
                    errors = len(
                        self._tracking_issue.get_comments(
                            filter_regex=ERROR_ADVISE_REGEX,
                            author=APP_NAME,
                        )
                    )
                    if to_open - finished == 0:
                        if errors > 0:
                            comment = f"""All advises complete, but leaving issue open because {errors} could not be
                            successfully submitted and may require user action."""
                        else:
                            self._tracking_issue.comment(
                                "Finished advising for all environments."
                            )
                            self._tracking_issue.close()
                return to_ret
