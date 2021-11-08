Quickstart Tutorials
====================

Welcome! This page is a series of short tutorials to get Kebechet running on
your repositories. The tutorials are in ascending complexity so we recommend
starting with installing the GitHub app and then moving up from there based on
your own personal use case.

GitHub Application
------------------

#. .. include:: configuration.rst
    :start-after: .. start-general-config
    :end-before: .. end-general-config
#. Go to this link `<https://github.com/marketplace/khebhut>`_
#. Choose the repositories and orgs that you want to install Kebechet on

Congratulations! You have now installed Kebechet and it will actively manage
your repositories. Kebechet's behaviour is highly dependent on which managers
you have installed we recommend familiarizing yourself with the managers you
installed. This service is provided by the Thoth team at Red Hat.

.. toctree::
    :glob:
    :caption: Managers:

    managers/*

Running Locally
---------------

Running Kebechet might interest you if you are a developer, someone looking to
deploy Kebechet on their own, or if you are just curious.

#. See step 1 of `GitHub Application`_

#. Setting up tokens and keys
    * SSH
        .. include:: authentication.rst
            :start-after: start-ssh-setup
            :end-before: end-ssh-setup
    * Personal Access Token (OAuth)
        .. include:: authentication.rst
            :start-after: start-oauth-setup
            :end-before: end-oauth-setup

#. Setting Environment Variables
    To interface with GitHub, GitLab, and Pagure you must set:
    ``GITHUB_KEBECHET_TOKEN``, ``GITLAB_KEBECHET_TOKEN``, and
    ``PAGURE_KEBECHET_TOKEN`` respectively. These are the "Personal Access
    Tokens" that you generated in the previous step.

    Beyond these there is no requirement for environment variables, however the
    CLI can be used by only setting environment variables. To see all of these
    values use the ``--help`` option when running the CLI.

#. Running Kebechet
    .. code-block::

        $ pipenv run PYTHON_PATH=. kebechet-cli run-url -u <url-to-github-repo> -s <GITHUB|GITLAB|PAGURE>

    To get more information about the available commands run::

        $ pipenv run PYTHON_PATH=. kebechet-cli --help

    And to get more information about a specific command, including cli-options,
    run::

        $ pipenv run PYTHON_PATH=. kebechet-cli <command> --help


Deploying Kebechet
------------------

We release Kebechet images on `quay.io
<https://quay.io/repository/thoth-station/kebechet-job>`_. The entry point for
the container is ``app.sh`` in the root directory of the Git repository.

Argo
....

Project Thoth uses Argo Workflows for our deployment of Kebechet. Here is a link
to a basic `workflow template <examples/templates/kebechet-run-url>`_ to run Kebechet.

Todo
....

If you want to deploy Kebechet using different tooling please reachout if you
need help or extend the documentation so others can benefit from your
experience.
