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

To deploy Kebechet on an OpenShift cluster use kustomize and the `Thoth Application template files <https://github.com/thoth-station/thoth-application/tree/master/kebechet>`_.
Please ensure all the input parameters are correctly set for each of the templates.

If Kebechet finds the env variables, `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY_PATH`, it is going to authenticate as a Github Application.

Otherwise its going to fallback to look for an OAuth token to authenticate for an successful run.
In both cases the SSH key is needed to commit code changes.
