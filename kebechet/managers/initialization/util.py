"""Just some utility methods."""
import git
import yaml

_KEBECHET_CONFIG_FILE_NAME = "kebechet.yaml"
_GIT_TOKEN_VARIABLE = "${KEBECHET_TOKEN}"
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


def create_config_file(service_type, slug: str):
    """Create a config file using a given git slug."""
    config = {
        "repositories": [
            {
                "slug": slug,
                "token": _GIT_TOKEN_VARIABLE,
                "service_type": service_type,
                "managers": [{"name": "info"}],
            }
        ]
    }

    with open(_KEBECHET_CONFIG_FILE_NAME, "w") as config_file:
        config_file.write(yaml.dump(config, sort_keys=False))
