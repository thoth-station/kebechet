from behave import *
from ogr.services.github import GithubProject
from kebechet import managers
from kebechet.managers.version.release_triggers import ReleaseIssue
import behave
import git
import os
import requests
import time

from data import merged_pr_webhook

ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


def create_file_for_changelog(context):
    "create a file so that changelog will not be empty when computed"
    with open("/tmp/keb_integration/new_file.txt", "w+") as f:
        f.write("hello world")
    context.repo.git.add("new_file.txt")
    context.repo.index.commit("new file added")
    context.repo.remote().push(context.project.default_branch)


def merge_pr(context, pr_number):
    # https://docs.github.com/en/rest/reference/pulls#merge-a-pull-request
    headers = {"Authorization": f"token {ACCESS_TOKEN}"}
    r = requests.put(
        f"https://api.github.com/repos/{context.project.full_repo_name}/pulls/{pr_number}/merge",
        headers=headers,
    )
    r.raise_for_status()


@given("a repository with a minor update issue and a new file")
def step_impl(context):
    create_file_for_changelog(context)

    # 2 is the index of the minor issue
    context.project.create_issue(title=ReleaseIssue._TITLE2UPDATE_INDEX[2], body="")


@when("Kebechet version manager is run")
def step_impl(context):
    version_manager = managers.VersionManager(
        slug=context.project.full_repo_name,
        service=context.ogr_service,
        service_type="github",
    )
    version_manager.run(labels=["bot"])


@then("pull request is opened with updated version string")
def step_impl(context):
    new_version = f"0.1.0"
    version_file: str = context.project.get_file_content(
        "version.py", ref=f"v{new_version}"
    )
    assert new_version in version_file


@given("a pull request is merged with a new file")
def step_impl(context):
    with open("/tmp/keb_integration/new_file.txt", "w+") as f:
        f.write("hello world")
    context.repo.git.checkout("-b", "new_file")
    context.repo.git.add("new_file.txt")
    context.repo.index.commit("new file added")
    context.repo.remote().push("new_file")
    pr = context.project.create_pr(
        title="a",
        body="n",
        target_branch=context.project.default_branch,
        source_branch="new_file",
    )
    pr.add_label("minor-release")
    merge_pr(context, 1)


@when(
    "kebechet receives webhook corresponding to a merged PR with minor-release label set"
)
def step_impl(context):
    version_manager = managers.VersionManager(
        slug=context.project.full_repo_name,
        service=context.ogr_service,
        service_type="github",
        parsed_payload=merged_pr_webhook,
    )
    version_manager.run(labels=["bot"])
