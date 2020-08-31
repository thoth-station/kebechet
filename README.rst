Kebechet
--------

  I'm Kebechet, goddess of freshness. I will keep your sources and dependencies fresh and up-to-date.

Kebechet is a SourceOps bot that automates updating dependencies of your project. Currently, it supports managing and updating Python projects based on `pipenv <https://docs.pipenv.org/>`_ files (``Pipfile`` and ``Pipfile.lock``) or ``requirements.txt``/``requirements.in`` files (see `pip-tools <https://pypi.org/project/pip-tools/>`_ - Kebechet is a replacement for it)

Configuration of Kebechet
=========================

Kebechet is configured using a simple YAML configuration file. Check documentation of managers to get all the available options.

Each configuration entry configures a manager. Please check `managers and examples <https://github.com/thoth-station/kebechet/tree/master/kebechet/managers>`_ to get info about configuration options.

The YAML configuration file can be supplied directly as a path to a file on filesystem as well as a URL to a file - handy for managing configuration of your Kebechet deployment in a Git repository (you have to supply a URL to a raw YAML configuration file).

Managers
========

Kebechet consists of managers that perform certain actions.

A list of managers with their configuration (documentation lives in the manger directory) can be found `in the repo <https://github.com/thoth-station/kebechet/tree/master/kebechet/managers>`_.

Issues created by Kebechet
==========================

If there are any issues that have serious impact on Kebechet functionality, Kebechet will automatically open an issue in the given repository. These issues can be configuration issues of Kebechet itself or issues in manager itself.

Suppressing bot verbosity
=========================

Bot updates pull requests and issues and notifies about updates via comments (to issues or pull requests). You can suppress this behaviour by setting lable 'silent-bot' to issue or to a pull request. The bot will still perform updates but update comments will not be added.

This is especially helpful for example if you have failing updates of your dependency and you would like to keep the pull request opened and check for fix later. Setting 'silent-bot' label to the PR will suppress Kebechet to post updates and you will not retrieve spam messages anymore.

Notes
=====

To issue an update to Git repository, Kebechet creates branches in the provided repository.

Deploying Kebechet
==================

To deploy kebechet on OpenShift cluster. Use the following Ansible command with required parameters:

.. code-block:: console

  ansible-playbook \
    --extra-vars=OCP_URL=<openshift_cluster_url> \
    --extra-vars=OCP_TOKEN=<openshift_cluster_token> \
    --extra-vars=KEBECHET_INFRA_NAMESPACE=<openshift_cluster_namespace> \
    --extra-vars=KEBECHET_APPLICATION_NAMESPACE=<openshift_cluster_namespace> \
    --extra-vars=KEBECHET_CONFIGURATION_PATH=<config.yaml> \
    --extra-vars=KEBECHET_TOKEN=<oauth_token> \
    --extra-vars=KEBECHET_SSH_PRIVATE_KEY_PATH=<git_ssh_private_key_path> \
    playbooks/provision.yaml


* ``KEBECHET_SSH_PRIVATE_KEY_PATH``: The path where the GitHub ssh private key is stored should be provided. (Example: $HOME/.ssh/id_rsa). If the field is undefined then the script will create the ssh keys for you and then you can set up the given public key to GitHub repository.

* ``KEBECHET_TOKEN``: To raise a pull request bot requires user rights and premissions. The GitHub OAuth tokens are to be set for raising pull request whenever updates are encounter by the Kebechet.

* ``KEBECHET_CONFIGURATION_PATH``: Path to the YAML configuration file to be used for Kebechet to check for dependency updates.

* ``KEBECHET_INFRA_NAMESPACE``: The OpenShift namespace can be used for the infrastructural purposes, all the images stream are stored in the ``KEBECHET_INFRA_NAMESPACE``.

* ``KEBECHET_APPLICATION_NAMESPACE``: The OpenShift namespace can be used for the application purposes, all the templates, builds, secrets, configmap and jobs are stored in the ``KEBECHET_APPLICATION_NAMESPACE``.

* ``OCP_URL`` and ``OCP_TOKEN``: The OpenShift credentials used to login to.
