Thoth Provenance Manager
========================

This manager validates package hashes found in your ``Pipfile.lock`` against the
remote index. For more information about what this means go `here
<https://thoth-station.ninja/docs/developers/adviser/provenance_checks.html>`__
to Thoth's documentation. If the manager finds any problems it will open issues
in your repository.

Custom PyPI indexes are supported respecting `Pipfile` syntax.

Prerequisites
-------------

You must have:

#. a ``.thoth.yaml`` configuration file specifying:
       * at least one runtime environment
       * the requirements format
       * a hostname for ``Thoth`` (khemenu.thoth-station.ninja).

#. You must also state your dependencies using pipenv, using a ``Pipfile`` and
   ``Pipfile.lock``


Configuration
-------------

.. list-table::
    :align: left
    :header-rows: 1
    :widths: 20 20 20 60

    * - Name
      - Value Type
      - Default
      - Description
    * - labels
      - List[str]
      - REQUIRED
      - List of labels that are applied to any pull requests or issues opened
        by this manager.


Example
-------

An example configuration for thoth `.thoth.yaml`

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
--------------

Kevin Postlethwait <kpostlet@redhat.com>
