Kebechet Advise-Results Manager
-----------------------
This manager is automatically triggered after the `ThothAdviseManager` finishes.  It will take the results and create pull requests and issues based on the info gathered

Options
=======
`labels`: specify the labels associated with pull requests and issues
`analysis_id`: id of the advise results 
`origin`: specify the repository that the results are for 

Example
=======

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

Manager Author
==============

Kevin Postlethwait <kpostlet@redhat.com>

