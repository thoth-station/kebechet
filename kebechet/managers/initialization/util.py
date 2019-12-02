"""Just some utility methods."""
from typing import Dict, List, Any

import git
import yaml

_KEBECHET_CONFIG_FILE_NAME = "kebechet.yaml"
_KEBECHET_MANAGER_LABELS = ["kebechet", "bot"]
_GIT_TOKEN_VARIABLE = "{KEBECHET_TOKEN}"
_GIT_BRANCH_NAME = "kebechet-initialization"
_GIT_COMMIT_MESSAGE = "Creating kebechet YAML file"
_GIT_MR_LABELS = ["enhancement", "bot"]
_GIT_MR_BODY = """"
# Initialization Manager.
It creates a `{file_name}` file with the following settings:
    * TSL verification: {tls_verify}
    * Managers: {managers}
## Notes
 * Make sure you have a environment file called `KEBECHET_TOKEN` in your system.

> This PR was created by a bot.
    """


class SlugNotFoundException(Exception):
    """Exception raised when no slug is found."""

    pass


def get_slug(path):
    """Get the git slug from .git folder from a given path."""
    repo = git.Repo(path)
    reader = repo.config_reader()
    reader.read()
    url = reader.get_value('remote "origin"', "url")

    if url.endswith(".git"):
        url = url[: -len(".git")]

    return __get_slug_from_url(url)


def __get_slug_from_url(url: str) -> str:
    slug_slash = False

    for i in range(len(url) - 1, 0, -1):
        if not slug_slash and url[i] == "/":
            slug_slash = True
        elif url[i] in ["/", ":"]:
            return url[i + 1:]

    raise SlugNotFoundException


def __get_user_from_slug(slug: str) -> str:
    for i in range(len(slug)):
        if slug[i] == "/":
            return slug[:i]


def create_config_file(service_type, managers, slug: str):
    """Create a config file using a given git slug."""
    config = {
        "repositories": [
            {"slug": slug, "token": _GIT_TOKEN_VARIABLE, "service_type": service_type, }
        ]
    }

    username = __get_user_from_slug(slug)
    managers_config = __get_managers_config(managers=managers, username=username)
    if len(managers_config) > 0:
        config["repositories"][0]["managers"] = managers_config

    with open(_KEBECHET_CONFIG_FILE_NAME, "w") as config_file:
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        config_file.write(yaml.dump(config, sort_keys=False, Dumper=noalias_dumper))


def __get_managers_config(managers: List, username: str) -> List[Dict[str, Any]]:
    configs = {
        "update": {"labels": _KEBECHET_MANAGER_LABELS, },
        "version": {"labels": _KEBECHET_MANAGER_LABELS, "maintainers": [username], },
        "thoth-provenance": {"labels": _KEBECHET_MANAGER_LABELS, },
        "thoth-advise": {"labels": _KEBECHET_MANAGER_LABELS, },
        "pipfile-requirements": {"lockfile": "false"},
    }

    conf = []

    for manager in managers:
        if manager in ["info"]:
            conf.append(
                {"name": manager, }
            )
        else:
            conf.append({"name": manager, "configuration": configs[manager]})

    return conf
