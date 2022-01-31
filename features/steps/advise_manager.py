from behave import *
import toml
import json
from kebechet import managers
from kebechet.managers.thoth_advise import thoth_advise
from github import Repository, PaginatedList, PullRequest
from ogr.services.github import GithubProject, GithubIssue


@given("a user has opened a issue requesting an advise request")
def step_impl(context):
    context.issue = context.project.create_issue(
        title=thoth_advise.ADVISE_ISSUE_TITLE, body="foo"
    )


@when("advise manager is run")
def step_impl(context):
    advise_manager = managers.ThothAdviseManager(
        slug=context.project.full_repo_name,
        service=context.ogr_service,
        service_type="github",
    )
    advise_manager.run(labels=["bot"])


@then(
    "a comment on the issue indicating an advise has been scheduled is present in the issue"
)
def step_impl(context):
    starts_with = thoth_advise.STARTED_ADVISE_COMMENT[:10]
    comments = context.issue.get_comments(filter_regex=f"^{starts_with}")
    assert len(comments) == 1
