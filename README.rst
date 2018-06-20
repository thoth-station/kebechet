Kebechet
--------

  I'm Kebechet, goddess of freshness. I will keep your dependencies fresh and up-to-date.

Kebechet is a SourceOps bot that automates updating dependencies of your project. Currently, it supports managing and updating Python projects based on `pipenv <https://docs.pipenv.org/>`_ files (``Pipfile`` and ``Pipfile.lock``) or ``requirements.txt``/``requirements.in`` files (see `pip-tools <https://pypi.org/project/pip-tools/>`_ - Kebechet is a replacement for it)

Keeping your project dependencies up to date can be tricky. Sometimes updating a dependency causes a breakage of application functionality. Kebechet is a bot that automates creation of pull requests and automates managing your package dependencies so that a dependency update is one click far from inclusion to your application stack.

Why should I use Kebechet instead of other solutions?
=====================================================

Kebechet checks direct dependencies of your application and issues updates only if an update was released for these packages. That means you are not spammed with updates of indirect dependencies hidden somewhere deeply in dependency graph of your application. Also, direct dependencies are the dependencies you should care about the most in your application as these are the ones that your application directly uses.

On each direct dependency update there is issued a pull request which includes update of the direct dependency. However, as transitive dependencies of the updated dependency can get updated too, the pull request also includes update of the transitive dependencies (this is also the only way how transitive dependencies are updated by Kebechet) - that means there is created an update for dependency sub-graph introduced by the direct dependency.

By splitting updates into multiple pull requests for each direct dependency update, you do atomic changes in your application stack (atomic on direct dependency level). If a dependency (direct or indirect) breaks your application and this breakage is captured in CI (or later when performing bisect to find bugs), you can directly see update of which direct dependency caused issues.

Why should I pin down dependencies in my application?
=====================================================

Check `this StackOverflow thread <https://stackoverflow.com/questions/28509481>`_.

Forkflow for pipenv - ``Pipfile`` and ``Pipfile.lock``
======================================================

To use Kebechet with `pipenv <https://docs.pipenv.org>`_ you have to commit ``Pipfile`` and ``Pipfile.lock`` files into the root of your Git respository structure. Kebechet will automatically monitor these files and issue updates to ``Pipfile.lock`` on new package releases.

Forkflow for ``requirements.txt`` and ``requirements.in``
=========================================================

To use Kebechet with the old fashion ``requirements.in`` and ``requirements.txt`` files, commit ``requirements.in`` file into the root of your Git repository structure. Kebechet will automatically pin down packages for you and create an initial pull request with ``requirements.txt``. File ``requirements.in`` should state your direct dependencies and version specification you expect for dependency solver to be used during dependency resolution (you can also add restrictions for your indirect dependencies there to avoid updates of transitive dependencies introducing bugs). File ``requirements.txt`` is automatically managed by Kebechet and it will produce fully pinned down application stack for your application.

Managing development requirements using a separated ``requirements.in`` is currently not supported.

Configuration of Kebechet
=========================

Kebechet is configured using a simple YAML configuration file. In this configuration file you state which repositories you wish to keep updated. An example of a YAML configuration file that monitors Kebechet itself is shown below:

.. code-block:: yaml

    update:
      - slug: thoth-station/kebechet  # GitHub slug in form of <github-org>/<github-repo>
        label:
          - bot
          - kebechet

The ``label`` configuration option states a list of labels that should be applied to pull requests or issues that are automatically raised by Kebechet.

The YAML configuration file can be supplied directly as a path to a file on filesystem as well as as a URL to a file - handy for managing configuration of your Kebechet deployment in a Git repository (you have to supply a URL to a raw YAML configuration file).

Issues created by Kebechet
==========================

If there are any issues that have serious impact on Kebechet functionality, Kebechet will automatically open an issue in the given repository. These issues can be configuration issues of Kebechet itself, issues in your dependency management such as errors in dependency management files or issues with package retrieval (such as misconfiguration in Python indexes, resolving issues or package version removal).

Notes
=====

To issue an update to Git repository, Kebechet creates branches in the provided repository. These branches are named based the on direct dependency that caused updates with its version. If the remote Git already has the given branch present, there will be performed a check for the base (master) against which the pull request is opened. If there were made changes in the master branch, Kebechet automatically updates commit so all updates issued with Kebechet are done on top of the current master. Note these updates are desctructive for older commits in the pull request - use ``git cherry-pick`` from Kebechet's update branch if you would like to do changes in the source code with dependency updates.

Deploying Kebechet
=================

To deploy kebechet on OpenShift cluster. Use the following Ansible command with required parameters:

.. code-block:: console

  ansible-playbook \
    --extra-vars=OCP_URL= <openshift_cluster_url> \
    --extra-vars=OCP_TOKEN= <openshift_cluster_token> \
    --extra-vars=KEBECHET_INFRA_NAMESPACE= <openshift_cluster_namespace> \
    --extra-vars=KEBECHET_APPLICATION_NAMESPACE= <openshift_cluster_namespace> \
    --extra-vars=KEBECHET_CONFIGURATION= <github_repo_config.yaml> \
    --extra-vars=KEBECHET_TOKEN= <github_oauth_token> \
    --extra-vars=KEBECHET_SSH_PRIVATE_KEY_PATH= <github_ssh_private_key_path> \
    playbooks/provision.yaml


* ``KEBECHET_SSH_PRIVATE_KEY_PATH``: The path where the GitHub ssh private key is stored should be provided. (Example: $HOME/.ssh/id_rsa). If the field is undefined then the script will create the ssh keys for you and then you can set up the given public key to GitHub repository.

* ``KEBECHET_TOKEN``: To raise a pull request bot requires user rights and premissions. The GitHub OAuth tokens are to be set for raising pull request whenever updates are encounter by the Kebechet.

* ``KEBECHET_CONFIGURATION``: A YAML configuration file to be used for Kebechet to check for dependency updates.

* ``KEBECHET_INFRA_NAMESPACE``: The OpenShift namespace can be used for the infrastructural purposes, all the images stream are stored in the ``KEBECHET_INFRA_NAMESPACE``.

* ``KEBECHET_APPLICATION_NAMESPACE``: The OpenShift namespace can be used for the application purposes, all the templates, builds, secrets, configmap and jobs are stored in the ``KEBECHET_APPLICATION_NAMESPACE``.

* ``OCP_URL`` and ``OCP_TOKEN``: The OpenShift credentials are to be setup with the access token and url.
