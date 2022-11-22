#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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

"""Common and useful utilities for managers."""

import logging
import platform
import typing
import git
import os
from typing import Dict, List, Optional
from functools import partial

import delegator
import kebechet

from kebechet.exception import PipenvError
from ogr.services.base import BaseGitService
from ogr.abstract import Issue, PullRequest, PRStatus

from kebechet import utils

_LOGGER = logging.getLogger(__name__)


class ManagerBase:
    """A base class for manager instances holding common and useful utilities."""

    def __init__(
        self,
        slug: str,
        service: BaseGitService,
        service_type: str,
        parsed_payload: Optional[dict] = None,
        metadata: Optional[dict] = None,
        runtime_environments: List[str] = None,
    ):
        """Initialize manager instance for talking to services."""
        self.service_url: str = service.instance_url  # type: ignore
        self.slug = slug
        self.service_type = service_type
        # Parsed payload structure can be accessed in payload_parser.py
        self.parsed_payload = None
        if parsed_payload:
            self.parsed_payload = parsed_payload
        self.owner, self.repo_name = self.slug.split("/", maxsplit=1)
        self.installation = False
        if os.getenv("GITHUB_PRIVATE_KEY_PATH") and os.getenv("GITHUB_APP_ID"):
            self.installation = True  # Authenticate as github app.

        self.service = service
        self.project = service.get_project(namespace=self.owner, repo=self.repo_name)
        self._repo: git.Repo = None
        self.metadata = metadata
        self.runtime_environments = runtime_environments

    @property
    def repo(self):
        """Get repository on which we work on."""
        return self._repo

    @repo.setter
    def repo(self, repo: git.Repo):
        """Set repository information and all derived information needed."""
        self._repo = repo

    @classmethod
    def get_environment_details(
        cls, as_dict=False
    ) -> typing.Union[str, typing.Dict[str, str]]:
        """Get details for environment in which Kebechet runs."""
        try:
            pipenv_version = cls.run_pipenv("pipenv --version")
        except PipenvError as exc:
            pipenv_version = f"Failed to obtain pipenv version:\n{exc.stderr}"

        return (
            f"""
Kebechet version: {kebechet.__version__}
Python version: {platform.python_version()}
Platform: {platform.platform()}
pipenv version: {pipenv_version}
"""
            if not as_dict
            else {
                "kebechet_version": kebechet.__version__,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "pipenv_version": pipenv_version,
            }
        )

    @staticmethod
    def run_pipenv(cmd: str):
        """Run pipenv, raise :ref:kebechet.exception.PipenvError on any error holding all the information."""
        _LOGGER.debug(f"Running pipenv command {cmd!r}")
        result = delegator.run(cmd)
        if result.return_code != 0:
            _LOGGER.warning(result.err)
            raise PipenvError(result)

        return result.out

    @classmethod
    def get_dependency_graph(cls, graceful: bool = False):
        """Get dependency graph of the project."""
        try:
            cls.run_pipenv(
                "pipenv sync --dev"
            )  # use sync so that deps are from Pipfile.lock
            return cls.run_pipenv("pipenv graph")
        except PipenvError as exc:
            if not graceful:
                raise
            return f"Unable to obtain dependency graph:\n\n{exc.stderr}"

    def get_issue_by_title(self, title: str) -> Optional[Issue]:
        """Get an ogr.Issue object with a matching title."""
        return utils.get_issue_by_title(self.project, title)

    def get_prs_by_branch(self, branch: str, status=PRStatus.open) -> List[PullRequest]:
        """Get a list of ogr.PullRequest objects which are using the supplied branch name."""
        to_ret = []
        self.project.get_pr_list
        for pr in self.project.get_pr_list(status=status):
            if pr.source_branch == branch:
                to_ret.append(pr)
        return to_ret

    def delete_remote_branch(self, branch: str):
        """Delete a remote branch without using pure git."""
        remote = self.repo.remote()
        for repo_branch in self.repo.references:
            if branch == repo_branch.name:
                remote.push(refspec=(f":{repo_branch.remote_head}"))

    def close_issue_and_comment(self, title: str, comment: str):
        """Comment and close an issue if it exists."""
        issue = self.get_issue_by_title(title)

        if issue is None:
            _LOGGER.debug(f"Issue {title} not found, not closing.")
            return
        issue.comment(comment)
        issue.close()

    def create_pr(self, title: str, body: str, source_branch: str, target_branch: str):
        """Create a PR but defaults to opening PR within a fork rather than on parent fork."""
        return self.project.create_pr(
            title=title,
            body=body + f"\n<details>"
            f"<summary>Environment details</summary>"
            f"\n{self.get_environment_details()}\n</details>",
            target_branch=target_branch,
            source_branch=source_branch,
            fork_username=self.project.namespace if self.project.is_fork else None,
        )

    def _git_commit_push(
        self, commit_msg: str, branch_name: str, files: list, force_push: bool = False
    ) -> None:
        """Perform git push after adding files and giving a commit message."""
        cur_branch = self.repo.active_branch
        self.repo.git.checkout("HEAD", b=branch_name)
        try:
            self.repo.git.add(files)
            self.repo.git.commit(f"--message='{commit_msg}'", "--signoff")
            self.repo.remote().push(branch_name, force=force_push).raise_if_error()
        finally:  # always revert to original
            self.repo.git.checkout(
                cur_branch
            )  # maybe turn into context manager in the future `with_branch(branch_name)`

    def pr_comment(self, id: int, body: str):
        """Comment on the PR."""
        pr = self.project.get_pr(id)
        pr.comment(body=body)

    def run(self, labels: list) -> typing.Optional[dict]:
        """Run the given manager implementation."""
        raise NotImplementedError

    @staticmethod
    def create_github_body(
        template: str,
        required_info: Dict[str, str] = {},
        optional_info: Dict[str, str] = {},
    ) -> str:
        """Create a github issue body from a template respecting github character limit."""
        partial_format = partial(template.format, **required_info)

        req_info_len = sum(len(s) for s in required_info.values())

        # final len(body) < 65536 because len(body) includes {{format}} strings which are replaced
        optional_data_lim = (
            65536 - len(template) - req_info_len
        )  # 65536 is the github character limit

        opt_info_list = [(k, v) for k, v in optional_info.items()]
        opt_info_list = sorted(
            opt_info_list, key=lambda x: len(x[1])
        )  # sort so smallest items are truncated first

        for i in range(len(opt_info_list)):
            item_limit = int(optional_data_lim / (len(optional_info) - i))
            optional_info[opt_info_list[i][0]] = opt_info_list[i][1][:item_limit]
            optional_data_lim -= len(opt_info_list[i][1][:item_limit])

        return partial_format(**optional_info)
