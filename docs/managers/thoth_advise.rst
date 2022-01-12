Thoth Advise Manager
====================

This manager will manage your Python dependencies using Thoth's recommendation
system. Your repository will be automatically updated using Thoth's Python
dependency resolution engine `adviser
<https://github.com/thoth-station/adviser>`_.

Custom PyPI indexes are supported respecting `Pipfile
<https://pipenv.readthedocs.io/en/latest/advanced/#specifying-package-indexes>`__
syntax.

Pre-requisites
--------------

You must have:

#. a ``.thoth.yaml`` configuration file specifying:
       * at least one runtime environment
       * the requirements format
       * a hostname for ``Thoth`` (khemenu.thoth-station.ninja).

#. You must also state your dependencies using either ``requirements.txt`` (if
   ``requirements_format==(pip|pip-tools|pip-compile``) or ``Pipfile`` (if
   ``requirements_format==pipenv``)

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

An example configuration for thoth ``.thoth.yaml``

.. code-block:: yaml

  host: {THOTH_SERVICE_HOST}
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
    - name: thoth-advise
      configuration:
        labels: [bot, kebechet]  # these are the labels added to PRs and issues opened by this manager


Because this manager uses more of Thoth's services, a runtime environment, host
and requirements format should be defined in the configuration file. More
information about configuration options for ``.thoth.yaml`` can be found in the
`thoth-station/thamos <https://github.com/thoth-station/thamos>`__ repository.

Available Thoth advise commands
----------------------------------

To run this manager, open an issue with the title "Kebechet Advise". The creation of this issue will trigger the
execution of this manager.

Manager Author
--------------

Kevin Postlethwait <kpostlet@redhat.com>
