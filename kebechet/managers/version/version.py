#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020, 2021 Fridolin Pokorny, Kevin Postlethwait
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

"""Automatically issue a new PR with adjusted version for Python projects."""

import logging
from typing import List, Tuple

import yaml
from github.GithubException import GithubException

from kebechet.utils import cloned_repo, get_issue_by_title
from kebechet.managers.manager import ManagerBase
from kebechet.managers.exceptions import ManagerFailedException
from thoth.glyph import MLModel, Format, ThothGlyphException

from .release_triggers import (
    ReleasePRlabels,
    ReleaseIssue,
    ReleaseLabelConfig,
    BaseTrigger,
)
from .exceptions import NoChangesException, VersionError, NotATriggerException
from . import constants
from . import utils
from . import messages

_LOGGER = logging.getLogger(__name__)
_VERSION_PULL_REQUEST_NAME = "Release of version {}"
_NO_VERSION_FOUND_ISSUE_NAME = (
    "No version identifier found in sources to perform a release"
)
_MULTIPLE_VERSIONS_FOUND_ISSUE_NAME = (
    "Multiple version identifiers found in sources to perform a new release."
)
_MULTIPLE_VERSIONS_FOUND_ISSUE_BODY = "Please have only one version string, to facilitate automated releases.\
         Multiple version strings found in these files - "
_NO_MAINTAINERS_ERROR = "No release maintainers stated for this repository"
_BODY_TRUNCATED = "The changelog body was truncated, please check CHANGELOG.md for the complete changelog."
_DIRECT_VERSION_TITLE = " release"
# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["issues", "issue", "pull_request"]
# Maximum number of log messages in a single release. Set due to ultrahook limits.
_MAX_CHANELOG_SIZE = 300


class VersionManager(ManagerBase):
    """Automatic version management for Python projects."""

    # Previous release tag present
    _PREV_RELEASE_TAG = False

    def _get_maintainers(self) -> list:
        """Get maintainers based on configuration.

        Maintainers can be either stated in the configuration or in the OWNERS file in the repo itself.
        """
        try:
            owners = yaml.safe_load(self.project.get_file_content("OWNERS"))
            maintainers = list(map(str, owners.get("approvers") or []))
        except (FileNotFoundError, KeyError, ValueError, yaml.YAMLError):
            _LOGGER.exception("Failed to load maintainers file")
            issue = self.get_issue_by_title(_NO_MAINTAINERS_ERROR)
            if issue is None:
                self.project.create_issue(
                    title=_NO_MAINTAINERS_ERROR,
                    body="This repository is not correctly setup for automated version releases.",
                    labels=self.labels,
                )
            else:
                issue.comment("Please revisit bot configuration.")
            return []

        self.close_issue_and_comment(
            _NO_MAINTAINERS_ERROR, "No longer relevant for the current bot setup."
        )
        return maintainers

    def _trigger_update_files(self, trigger: BaseTrigger):
        if not trigger.is_trigger():
            raise NotATriggerException
        adjusted = trigger.adjust_version_in_sources(labels=self.labels)
        if len(adjusted) == 0:
            trigger.open_no_files_adjusted_issue(labels=self.labels)
            raise ManagerFailedException("No version files adjusted.")
        if len(adjusted) > 1:
            trigger.open_many_files_adjusted_issue(
                adjusted_files=[i[0] for i in adjusted], labels=self.labels
            )
            raise ManagerFailedException("More than one file adjusted.")
        return adjusted[0]

    def _branch_and_update_vers_and_changelog(
        self,
        trigger: BaseTrigger,
        changelog_smart: bool,
        changelog_classifier: str,
        changelog_format: str,
        changelog_file: bool,
    ) -> Tuple[str, str, List[str], bool]:
        with cloned_repo(self) as repo:
            res = self._trigger_update_files(trigger)
            version_file, new_version, old_version = res
            repo.git.add(version_file)
            prev_release = utils._prev_release_tag(repo, old_version)
            changelog = utils._compute_changelog(
                repo=repo,
                old_version=old_version,
                new_version=new_version,
                changelog_smart=changelog_smart,
                changelog_classifier=changelog_classifier,
                changelog_format=changelog_format,
                prev_release_tag=prev_release,
            )

            if not changelog:
                raise NoChangesException("No changes found.")

            if changelog_file:
                utils._write_to_changelog(changelog, new_version)
                repo.git.add("CHANGELOG.md")

            branch_name = "v" + new_version
            repo.git.checkout("HEAD", b=branch_name)
            message = constants._VERSION_PULL_REQUEST_NAME.format(new_version)
            repo.index.commit(message)
            repo.remote().push(branch_name)
            return branch_name, new_version, changelog, bool(prev_release)

    def _create_pr_for_trigger_release(
        self,
        trigger: BaseTrigger,
        changelog: List[str],
        branch_name: str,
        new_version: str,
        has_prev_release: bool,
    ):
        message = constants._VERSION_PULL_REQUEST_NAME.format(new_version)
        try:
            # If this PR already exists, this will fail.
            pr = self.project.create_pr(
                title=message,
                body=trigger.construct_pr_body(
                    changelog=changelog, has_prev_release=has_prev_release
                ),
                target_branch=self.project.default_branch,
                source_branch=branch_name,
            )
        except GithubException as ghub_exc:
            errors = ghub_exc.data.get("errors", [])  # type: ignore
            for e in errors:
                if isinstance(e, dict) and "pull request already exists" in e.get(
                    "message", ""
                ):
                    _LOGGER.warning("Attempted to open another PR for current branch.")
                    return
            else:
                raise ghub_exc

        pr.add_label(*self.labels)
        _LOGGER.info(
            f"Opened merge request with {pr.id} for new release of {self.slug} "
            f"in version {new_version}"
        )

    def run(  # type: ignore
        self,
        maintainers: list = None,
        assignees: list = None,
        labels: List[str] = [],
        changelog_file: bool = False,
        changelog_smart: bool = False,
        changelog_classifier: str = MLModel.DEFAULT.name,
        changelog_format: str = Format.DEFAULT.name,
        pr_releases: bool = True,
        release_label_config: dict = dict(),
    ) -> None:
        """Check issues for new issue request, if a request exists, issue a new PR with adjusted version in sources."""
        self.labels = labels
        if self.parsed_payload:
            event_type = self.parsed_payload.get("event")
            if event_type not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "Version Manager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return

        trigger: BaseTrigger

        if (
            self.parsed_payload
            and utils._is_merge_event(self.parsed_payload)
            and utils._is_release_version_pr(self.parsed_payload)
        ):
            tag_version = utils._get_version(self.parsed_payload)
            with cloned_repo(self) as repo:
                _LOGGER.info(f"Creating Tag of version {tag_version}")
                _LOGGER.info(
                    repo.git.execute(
                        [
                            "git",
                            "tag",
                            f"{tag_version}",
                            f"{utils._get_merge_commit_sha(self.parsed_payload)}",
                        ]
                    )
                )
                _LOGGER.info(
                    repo.git.execute(
                        ["git", "push", "origin", f"refs/tags/{tag_version}"]
                    )
                )
                try:
                    # Branch name is same as tag version
                    _LOGGER.info(f"Deleting branch {tag_version}")
                    repo.git.execute(
                        [
                            "git",
                            "push",
                            "origin",
                            "-d",
                            f"refs/heads/{tag_version}",
                        ]
                    )

                except Exception:
                    _LOGGER.exception(f"Failed to delete branch {tag_version}")
                    self.pr_comment(
                        utils._pr_id_from_webhook(self.parsed_payload),
                        body=f"Failed to delete branch {tag_version} , due to permissions issue",
                    )

            return
        if (
            pr_releases
            and self.parsed_payload
            and utils._is_merge_event(self.parsed_payload)
        ):
            trigger_pr = self.project.get_pr(
                utils._pr_id_from_webhook(self.parsed_payload)
            )
            try:
                label_config = ReleaseLabelConfig.from_dict(release_label_config)
            except ValueError as exc:
                _LOGGER.warning(constants._INVALID_LABEL_CONFIG_ISSUE_NAME)
                i = get_issue_by_title(
                    self.project, constants._INVALID_LABEL_CONFIG_ISSUE_NAME
                )
                if i is None:
                    self.project.create_issue(
                        title=constants._INVALID_LABEL_CONFIG_ISSUE_NAME,
                        body=messages.RELEASE_LABEL_CONFIG_INVALID,
                        labels=labels,
                    )
                raise ManagerFailedException from exc
            trigger = ReleasePRlabels(label_config, trigger_pr)
            try:
                (
                    branch_name,
                    new_version,
                    changelog,
                    has_prev_release,
                ) = self._branch_and_update_vers_and_changelog(
                    trigger=trigger,
                    changelog_smart=changelog_smart,
                    changelog_classifier=changelog_classifier,
                    changelog_format=changelog_format,
                    changelog_file=changelog_file,
                )
            except (ThothGlyphException, VersionError) as exc:
                if isinstance(exc, ThothGlyphException):
                    _LOGGER.exception("Failed to generate smart release log.")
                    trigger_pr.comment(str(exc))
                    raise ManagerFailedException from exc
                elif isinstance(exc, VersionError):
                    _LOGGER.exception(
                        "Failed to adjust version information in sources."
                    )
                    trigger_pr.comment(str(exc))
                    raise ManagerFailedException from exc

            self._create_pr_for_trigger_release(
                trigger=trigger,
                changelog=changelog,
                branch_name=branch_name,
                new_version=new_version,
                has_prev_release=has_prev_release,
            )

        reported_issues = []
        version_update_complete = False
        for issue in self.project.get_issue_list():
            issue_title = issue.title.strip()

            if issue_title.startswith(
                (
                    constants._NO_VERSION_FOUND_ISSUE_NAME,
                    constants._MULTIPLE_VERSIONS_FOUND_ISSUE_NAME,
                )
            ):
                # Reported issues that should be closed on success version change.
                reported_issues.append(issue)

            trigger = ReleaseIssue(issue)
            if not trigger.is_trigger():
                continue
            elif version_update_complete:
                reported_issues.append(
                    issue
                )  # will close duplicate version release issues
                continue  # skip so that we don't open two PRs for same branch

            if assignees:
                try:
                    issue.add_assignee(*assignees)
                except Exception:
                    _LOGGER.exception(
                        f"Failed to assign {assignees} to issue #{issue.id}"
                    )
                    issue.comment(
                        "Unable to assign provided assignees, please check bot configuration."
                    )

            maintainers = maintainers or self._get_maintainers()
            if issue.author.lower() not in (m.lower() for m in maintainers):
                issue.comment(
                    f"Sorry, @{issue.author} but you are not stated in maintainers section for "
                    f"this project. Maintainers are @" + ", @".join(maintainers)
                    if maintainers
                    else "Sorry, no maintainers configured."
                )
                issue.close()
                # Next issue.
                continue

            _LOGGER.info(
                "Found an issue #%s which is a candidate for request of new version release: %s",
                issue.id,
                issue.title,
            )

            try:
                (
                    branch_name,
                    new_version,
                    changelog,
                    has_prev_release,
                ) = self._branch_and_update_vers_and_changelog(
                    trigger=trigger,
                    changelog_smart=changelog_smart,
                    changelog_classifier=changelog_classifier,
                    changelog_format=changelog_format,
                    changelog_file=changelog_file,
                )
            except (NoChangesException, ThothGlyphException, VersionError) as exc:
                if isinstance(exc, NoChangesException):
                    message = f"Closing the issue as there is no changelog between the new release of {self.slug}."
                    _LOGGER.info(message)
                    issue.comment(message)
                    issue.close()
                    return
                elif isinstance(exc, ThothGlyphException):
                    _LOGGER.exception("Failed to generate smart release log")
                    issue.comment(str(exc))
                    issue.close()
                    raise ManagerFailedException from exc
                elif isinstance(exc, VersionError):
                    _LOGGER.exception("Failed to adjust version information in sources")
                    issue.comment(str(exc))
                    issue.close()
                    raise ManagerFailedException from exc

            self._create_pr_for_trigger_release(
                trigger=trigger,
                changelog=changelog,
                branch_name=branch_name,
                new_version=new_version,
                has_prev_release=has_prev_release,
            )
            version_update_complete = (
                True  # do not create multiple PRs if multiple release issues exist
            )

        for reported_issue in reported_issues:
            reported_issue.comment("Closing as this issue is no longer relevant.")
            reported_issue.close()
