Kebechet Thamos-Advise Manager
-----------------------

This manager is responsible for automatic updates of dependencies in a repository based on `Pipfile`
file, it uses `thamos.lib` to communicate with `thoth` user API

A prerequisite for this manager is to have `Pipfile` and `.thoth.yaml`, present in the repo.
`Pipfile` should state all direct dependencies (with possible required specifications).
`.thoth.yaml` should contain a valid configuration for `thamos`


* `Pipfile` - respecting `pipenv <https://github.com/pypa/pipenv>`_ tool
* `Pipfile.lock` - automatically managed by this manager - states all pinned down versions of your application stack

.. `Pipfile` has higher precedence over `requirements.in` so if you have both files present in your Git repository, only Pipfile.lock will be managed.

If you do not have `Pipfile.lock` present in your repository, this manager will automatically open a pull request with initial dependency lock.

Custom PyPI indexes are supported respecting `Pipfile` syntax.

If there is any issue in your application stack, the Thamos-Advise manager will open an issue with all the info and will try to resolve issue for you if possible by opening a pull request for you.

.. Manager will automatically rebase opened pull requests on top of the current master if master changes so changes are always tested in your CI with the recent master.

Why should I pin down dependencies in my application?
=====================================================

Check `this StackOverflow thread <https://stackoverflow.com/questions/28509481>`_.

Why should I use this manager instead of other solutions?
=========================================================

Thoth has digested a wide range of software stacks on different hardware configurations.  By using this manager you are leveraging this accumulated knowledge so that you can ensure that your Python application is the fastest and most secure that it can be.

Forkflow for pipenv - ``Pipfile`` and ``Pipfile.lock``
======================================================

To use Kebechet with `pipenv <https://docs.pipenv.org>`_ you have to commit ``Pipfile`` and files into the root of your Git respository structure. Kebechet will automatically monitor these files and issue updates to ``Pipfile.lock`` whenver there is a change to either your `Pipfile` or updates to the knowledge base. 

.. To use Kebechet with the old fashion ``requirements.in`` and ``requirements.txt`` files, commit ``requirements.in`` file into the root of your Git repository structure. Kebechet will automatically pin down packages for you and create an initial pull request with ``requirements.txt``. File ``requirements.in`` should state your direct dependencies and version specification you expect for dependency solver to be used during dependency resolution (you can also add restrictions for your indirect dependencies there to avoid updates of transitive dependencies introducing bugs). File ``requirements.txt`` is automatically managed by Kebechet and it will produce fully pinned down application stack for your application.

Options
=======
`labels`: specify the labels associated with pull requests and issues

`rectype`: specify the recommendation type that `thoth` should use

Example
=======

An example configuration for kebechet:

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
        - name: thoth-advise
          configuration:
            labels:
              # Labels for opened issues and pull requests.
              - bot

An example configuration for thamos `.thoth.yaml`

NOTE: This configuration file should be in the root directory of your repository

.. code-block:: yaml

  host: {THOTH_SERVICE_HOST}
  tls_verify: true
  requirements_format: pipenv
                
  runtime_environments:
  - name: '{os_name}:{os_version}'
    operating_system:
      name: {os_name}
      version: '{os_version}'
    hardware:
      cpu_family: {cpu_family}
      cpu_model: {cpu_model}
    python_version: '{python_version}'
    cuda_version: {cuda_version}
    recommendation_type: stable
    limit_latest_versions: null

A more detailed description of `thamos` can be found `here <https://github.com/thoth-station/thamos>`_

You can see this manager in action `here <https://github.com/thoth-station/kebechet/pull/46>`_, `here <https://github.com/thoth-station/kebechet/pull/85>`_ or `here <https://github.com/thoth-station/solver/issues/38>`_.

Manager Author
==============

Kevin Postlethwait <kpostlet@redhat.com>

