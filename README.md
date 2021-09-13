Kebechet
========

> I'm Kebechet, goddess of freshness. I will keep your sources and dependencies fresh and up-to-date.

Kebechet is a SourceOps bot that automates updating dependencies of your project. Currently, it supports managing and
updating Python projects based on [pipenv](https://docs.pipenv.org/) files (`Pipfile` and `Pipfile.lock`) or
`requirements.txt`/`requirements.in` files (see [pip-tools](https://pypi.org/project/pip-tools/) - Kebechet is a
replacement for it).

Kebechet is many bots masking themselves as a single bot.  The main rationale behind the creation of Kebechet was that
it should be able to do simple repetitive actions, providing value by updating dependencies, tagging new versions, etc.
Adding a new action should be "easy", a new manager can interact with the GitHub, GitLab, or Pagure APIs using
[packit/ogr](https://github.com/packit/ogr) and interact with git using
[GitPython](https://gitpython.readthedocs.io/en/stable/).

For a full list of managers go [here](kebechet/managers/README.rst).

User Guide
----------

### Configuration

To start using Kebechet you should begin by creating a configuration file in the root of your repository, this
configuration file should have the name `.thoth.yaml`. This configuration file can contain other Thoth based
configuration, but for our purposes we will focus only on the aspects which pertain to Kebechet. Below is an example of
the `.thoth.yaml` file found in this repository:

```yaml
host: khemenu.thoth-station.ninja
tls_verify: false
requirements_format: pipenv

runtime_environments:
  - name: rhel:8
    operating_system:
      name: rhel
      version: "8"
    python_version: "3.8"
    recommendation_type: latest

managers:
  - name: pipfile-requirements
  - name: update
    configuration:
      labels: [bot]
  - name: info
  - name: version
    configuration:
      maintainers:
        - sesheta
        - goern
        - fridex
      assignees:
        - sesheta
      labels: [bot]
      changelog_file: true
```

To start you only need to define the managers section:

```yaml
...
managers:
  - name: pipfile-requirements
  - name: update
    configuration:
      labels: [bot]
  - name: info
  - name: version
    configuration:
      maintainers:
        - sesheta
        - goern
        - fridex
      assignees:
        - sesheta
      labels: [bot]
      changelog_file: true
...
```

Each entry of managers corresponds with a manager defined in Kebechet. A mapping from names to managers can be found in
the `__init__.py` file of `kebechet.managers` under [REGISTERED_MANAGERS](kebechet/managers/__init__.py). Manager
configuration is a list of key-value pairs which can be used to configure individual managers; individual manager
configuration can be found in each of their [READMEs](kebechet/managers/README.rst).

### Bot Installation

Once you have created a configuration file in your repository, you are ready to install the bot. Thoth only supports a
GitHub bot at this time. To install it, visit [this](https://github.com/marketplace/khebhut) link and install it for all
repos which you have created configuration for. After you have done this, Kebechet should be installed on your repo and
making contributions.

If you need to run Kebechet on a different service, take a look at [deploying Kebechet](#deploying-kebechet)

Issues created by Kebechet
--------------------------

If there are any issues that have serious impact on Kebechet functionality, Kebechet will automatically open an issue in the given repository. These issues can be configuration issues of Kebechet itself or issues in manager itself.

Suppressing bot verbosity
-------------------------

Bot updates pull requests and issues and notifies about updates via comments (to issues or pull requests). You can suppress this behaviour by setting lable 'silent-bot' to issue or to a pull request. The bot will still perform updates but update comments will not be added.

This is especially helpful for example if you have failing updates of your dependency and you would like to keep the pull request opened and check for fix later. Setting 'silent-bot' label to the PR will suppress Kebechet to post updates and you will not retrieve spam messages anymore.

Deploying Kebechet
------------------

To deploy Kebechet on an OpenShift cluster use kustomize and the [Thoth Application template
files](https://github.com/thoth-station/thoth-application/tree/master/kebechet). Please ensure all the input parameters
are correctly set for each of the templates.

If Kebechet finds the env variables, `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY_PATH`, it is going to authenticate as a
Github Application.

Otherwise its going to fallback to look for an OAuth token to authenticate for an successful run. For GitLab and Pagure,
OAuth tokens are the only autentication method for the API. The OAuth token the application looks for is dependent on
the service type it is being run on, the form of the token will look like so, `<GITHUB|GITLAB|PAGURE>_KEBECHET_TOKEN`.

In all cases the SSH key is needed to commit code changes.

Running Kebechet Locally for Development
----------------------------------------

This guide is specific to GitHub. To run locally you need to [create a personal access
token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
on GitHub and add it to) your envvars (`$ export GITHUB_KEBECHET_TOKEN=<your-token>`). Then all you need to do is run
the Kebechet-CLI in the virtual environment generated by pipenv by running either:

1. `$ pipenv run PYTHON_PATH=. kebechet-cli run-url -u <url-to-github-repo> -s <service-type>`
1. `$ PYTHON_PATH=. kebechet-cli run-url -u <url-to-github-repo> -s <service-type>`

where \<service-type\> is GITHUB

This assumes you have a repository with proper configuration files and is ready for Kebechet to manage. For a very minimal repo see [here](<https://github.com/KPostOffice/khebhut_test>)

This guide can also be used to interact with GitLab and Pagure, the only difference being that the token must be generated for the specifice service, service-type should be GITLAB or PAGURE and the token env var should be \<service-type\>\_KEBECHET\_TOKEN

Notes
-----

To issue an update to Git repository, Kebechet creates branches in the provided repository.
