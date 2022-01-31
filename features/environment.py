import os
import random
import string
import shutil
from time import sleep

import requests
import git
from github import Github, AuthenticatedUser
from ogr.services.github import GithubService

ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
Github.get_repo


def _generate_repo_name():
    return "".join(random.choices(string.ascii_lowercase, k=8))


def _create_repo_from_integration_template(owner, repo_name):
    params = {
        "owner": "KPostOffice",
        "name": repo_name,
        "description": "Temporary repo for testing",
    }
    headers = {"Authorization": f"token {ACCESS_TOKEN}"}
    r = requests.post(
        "https://api.github.com/repos/kpostoffice/kebechet_integration_template/generate",
        json=params,
        headers=headers,
    )  # https://docs.github.com/en/rest/reference/repos#create-a-repository-using-a-template
    r.raise_for_status()


def _delete_repository(full_repo_name):
    headers = {"Authorization": f"token {ACCESS_TOKEN}"}
    requests.delete(
        f"https://api.github.com/repos/{full_repo_name}",
        headers=headers,
    )  # https://docs.github.com/en/rest/reference/repos#delete-a-repository


def before_all(context):
    context.ogr_service = GithubService(token=ACCESS_TOKEN)
    context.github = Github(ACCESS_TOKEN)


def before_scenario(context, scenario):
    if "with_repo" in scenario.tags:
        repo_name = _generate_repo_name()
        owner = context.github.get_user().login
        _create_repo_from_integration_template(owner, repo_name)
        context.full_repo_name = f"{owner}/{repo_name}"
        context.project = context.ogr_service.get_project(
            namespace=owner, repo=repo_name
        )
        context.repo = git.Repo.clone_from(
            f"git@github.com:{context.project.full_repo_name}.git",
            "/tmp/keb_integration",
        )
        sleep(5)


def after_scenario(context, scenario):
    if "with_repo" in scenario.tags:
        _delete_repository(context.full_repo_name)
        shutil.rmtree("/tmp/keb_integration")
