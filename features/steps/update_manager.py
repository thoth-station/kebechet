from behave import *
import toml
import json
from kebechet import managers
from github import Repository, PaginatedList, PullRequest
from ogr.services.github import GithubProject, GithubPullRequest


@given(
    "repository with a `click` version (==1.0.0) older than defined constraint (<=2.0.0)"
)
def step_impl(context):
    # template repository has out of date click by default
    # TD: assert specified version and installed version are the same
    pipfile = context.project.get_file_content("Pipfile")
    pip_dict = toml.loads(pipfile)
    assert pip_dict["packages"]["click"] == "<=2.0.0"
    pipfilelock = context.project.get_file_content("Pipfile.lock")
    piplock_dict = json.loads(pipfilelock)
    assert piplock_dict["default"]["click"]["version"].startswith("==1.")


@when("update manager is run")
def step_impl(context):
    update_manager = managers.UpdateManager(
        slug=context.project.full_repo_name,
        service=context.ogr_service,
        service_type="github",
    )
    update_manager.run(labels=["bot"])


@then("PR is opened with `click==2.0` in Pipfile.lock")
def step_impl(context):
    prs = context.project.get_pr_list()
    assert len(prs) == 1
    pipfilelock = context.project.get_file_content(
        "Pipfile.lock", "kebechet-automatic-update-rhel-8"
    )
    piplock_dict = json.loads(pipfilelock)
    assert piplock_dict["default"]["click"]["version"].startswith("==2.")
