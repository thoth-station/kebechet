#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2021 Kevin Postlethwait
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

"""Util functions for update manager."""

import git
from ogr.abstract import PullRequest


def _pull_remote_branch_to_local(repo: git.Repo, branch_name: str):
    original_branch = repo.active_branch.name
    repo.git.checkout(branch_name)
    repo.git.pull()
    repo.git.checkout(original_branch)


def num_commits_behind(repo: git.Repo, target_branch: str, source_branch: str) -> int:
    """Count how many commits source branch is behind target branch."""
    _pull_remote_branch_to_local(
        repo=repo, branch_name=source_branch
    )  # otherwise the ref cannot be found
    commit_dif_count = repo.git.rev_list(
        f"{target_branch}...{source_branch}", left_right=True, count=True
    ).split("\t")
    return int(commit_dif_count[0])


def rebase_pr_branch_and_comment(
    repo: git.Repo, pr: PullRequest, close_on_failure: bool = True
):
    """Rebase PR on top of target branch."""
    num_behind = num_commits_behind(
        repo=repo, target_branch=pr.target_branch, source_branch=pr.source_branch
    )
    if num_behind == 0:
        return None  # pr is directly on top of target_branch
    cur_branch = repo.active_branch.name
    try:
        repo.git.checkout(pr.source_branch)
        repo.git.rebase(pr.target_branch)
        repo.git.push("origin", pr.source_branch, force=True)
        pr.comment(f"Rebased PR on top of {pr.target_branch}")
    except git.GitCommandError as exc:
        if close_on_failure:
            pr.comment(f"Failed to rebase PR on top of {pr.target_branch}.")
            pr.close()
        else:
            raise exc
    finally:
        repo.git.checkout(cur_branch)
