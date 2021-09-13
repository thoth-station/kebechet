Kebechet Thamos-Provenance_check Manager
----------------------------------------

The purpose of this manager is to use Thoth's ability to conduct provenance checks to ensure that your Python dependency sources are valid
file, it uses :code:`thamos.lib` to communicate with **Thoth** user API

A prerequisite for this manager is to have :code:`Pipfile` and :code:`Pipfile.lock`, and :code:`.thoth.yaml`, present in
the repo. :code:`Pipfile` should state all direct dependencies (with possible required specifications).
:code:`Pipfile.lock` should hold all the lock data associated with the Python software stack generated either by
`thamos.lib.advise()` or `pipenv sync` :code:`.thoth.yaml` should contain a valid configuration for :code:`thamos`

* **Pipfile** - respecting `pipenv <https://pipenv.readthedocs.io/en/latest/advanced/#specifying-package-indexes>`__ tool
* **Pipfile.lock** - states all pinned down versions of your application stack

Custom PyPI indexes are supported respecting `Pipfile` syntax.

If there is any issue in your application stack, this manager will create issues in your repository

Why should I use this manager instead of other solutions?
=========================================================

Provenance checks are make sure that your locked down dependencies are discoverable within the index that you stated
with the correct indexes and SHA values.

Forkflow for pipenv - ``Pipfile`` and ``Pipfile.lock``
======================================================

To use Kebechet with `pipenv <https://docs.pipenv.org>`__ you have to commit ``Pipfile`` and ``Pipfile.lock`` files into
the root of your Git respository structure. Kebechet will automatically monitor these files and create issues if any
problems are found through thoth provenance checks

Example
=======

An example configuration for thoth `.thoth.yaml`

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

  managers:
    - name: thoth-provenance
      configuration:
        labels: [bot] # Labels for opened issues and pull requests.

Because this manager uses more of Thoth's services, a runtime environment, host and requirements format should be
defined in the configuration file. More information about configuration options for .thoth.yaml can be found `in the
thoth-station/thamos repository <https://github.com/thoth-station/thamos>`__.

Manager Author
==============

Kevin Postlethwait <kpostlet@redhat.com>
