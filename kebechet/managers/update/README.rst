Kebechet Update Manager
-----------------------

This manager is responsible for automatic updates of dependencies in a repository based on `Pipfile` or `requirements.txt`
file.

Open an issue titled `Kebechet update` to manually trigger an update for your repository.

A prerequisite for this manager is to have `Pipfile`, `requirements.in` or `requirements-dev.in` present in the repo.
These files should state all direct dependencies (with possible required specifications).

* `Pipfile` - respecting `pipenv <https://github.com/pypa/pipenv>`_ tool
* `requirements.in` - respecting old fashion `requirements.{txt,in}` files stating all the direct dependencies for your application
* `requirements-dev.in` - respecting old fashion `requirements-dev.{txt,in}` files stating all the direct dependencies for your application when doing development
* `Pipfile.lock` - automatically managed by this manager - states all pinned down versions of your application stack
* `requirements.txt` - automatically managed by manager - respecting old fashion `requiremnets.{txt,in}` files stating all pinned down dependencies of your application; this convention was adopted from `pip-tools <https://github.com/jazzband/pip-tools>`_
* `requirements.txt` - automatically managed by manager - respecting old fashion `requiremnets-dev.{txt,in}` files stating all pinned down dependencies needed for development

`Pipfile` has higher precedence over `requirements.in` so if you have both files present in your Git repository, only Pipfile.lock will be managed.

If you do not have `requirements.txt` nor `Pipfile.lock` present in your repository, this manager will automatically open a pull request with initial dependency lock.

Custom PyPI indexes are supported respecting `requirements.{txt,in}` and `Pipfile` syntax.

If there is any issue in your application stack, the Update manager will open an issue with all the info and will try to resolve issue for you if possible by opening a pull request for you.

Manager will automatically rebase opened pull requests on top of the current master if master changes so changes are always tested in your CI with the recent master.

Why should I pin down dependencies in my application?
=====================================================

Check `this StackOverflow thread <https://stackoverflow.com/questions/28509481>`__.

Why should I use this manager instead of other solutions?
=========================================================

Kebechet Update manager checks direct dependencies of your application and issues updates only if an update was released for these packages. That means you are not spammed with updates of indirect dependencies hidden somewhere deeply in dependency graph of your application. Also, direct dependencies are the dependencies you should care about the most in your application as these are the ones that your application directly uses.

On each direct dependency update there is issued a pull request which includes update of the direct dependency. However, as transitive dependencies of the updated dependency can get updated too, the pull request also includes update of the transitive dependencies (this is also the only way how transitive dependencies are updated by this update manager) - that means there is created an update for dependency sub-graph introduced by the direct dependency.

By splitting updates into multiple pull requests for each direct dependency update, you do atomic changes in your application stack (atomic on direct dependency level). If a dependency (direct or indirect) breaks your application and this breakage is captured in CI (or later when performing bisect to find bugs), you can directly see update of which direct dependency caused issues.

Forkflow for pipenv - ``Pipfile`` and ``Pipfile.lock``
======================================================

To use Kebechet with `pipenv <https://docs.pipenv.org>`_ you have to commit ``Pipfile`` and ``Pipfile.lock`` files into the root of your Git respository structure. Kebechet will automatically monitor these files and issue updates to ``Pipfile.lock`` on new package releases.

Forkflow for ``requirements.txt`` and ``requirements.in``
=========================================================

To use Kebechet with the old fashion ``requirements.in`` and ``requirements.txt`` files, commit ``requirements.in`` file into the root of your Git repository structure. Kebechet will automatically pin down packages for you and create an initial pull request with ``requirements.txt``. File ``requirements.in`` should state your direct dependencies and version specification you expect for dependency solver to be used during dependency resolution (you can also add restrictions for your indirect dependencies there to avoid updates of transitive dependencies introducing bugs). File ``requirements.txt`` is automatically managed by Kebechet and it will produce fully pinned down application stack for your application.

Example
=======

An example configuration:

.. code-block:: yaml

  repositories:
    - slug: thoth-station/kebechet
      # State token explicitly or let it expand from env vars:
      token: '{SECRET_TOKEN_IN_ENV}'
      service_type: github  # or gitlab
      # Optionally for self-hosted services:
      # service_url: <URL>
      # tls_verify: true/false
      managers:
        - name: update
          configuration:
            labels:
              # Labels for opened issues and pull requests.
              - bot

You can see this manager in action `here <https://github.com/thoth-station/kebechet/pull/46>`_, `here <https://github.com/thoth-station/kebechet/pull/85>`_ or `here <https://github.com/thoth-station/solver/issues/38>`_.

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
