Kebechet Update Manager
-----------------------

This manager is responsible for automatic updates of packages in a repository based on `Pipfile` or `requirements.txt`
file.

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
      # servie_url: <URL>
      # tls_verify: true/false
      managers:
        - name: update
          configuration:
            labels:
              # Labels for opened issues and pull requests.
              - bot

You can find this manager in action `here <https://github.com/thoth-station/kebechet/pull/46>`_, `here <https://github.com/thoth-station/kebechet/pull/85>`_ or `here <https://github.com/thoth-station/solver/issues/38>`_.

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>

