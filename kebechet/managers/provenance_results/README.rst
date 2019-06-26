Kebechet Provenance-results Manager
-----------------------
This manager is meant to be triggered by `results-api` by the `/post_provenance_results` endpoint

Options
=======
`labels`: specify the labels associated with pull requests and issues
`analysis_id`: the id of the completed provenance analysis
`slug`: git repo slug
`service`:
`service_url`

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
        - name: thoth-provenance
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

