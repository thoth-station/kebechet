Kebechet Advise-Results Manager
-----------------------
This manager will manage your Python dependencies using Thoths recommendation system. Your repository will be automatically updated with the optimal Python packages for your project without you having to lift your finger.

A prerequisite for this manager is to have Pipfile and .thoth.yaml, present in the repo. Pipfile should state all direct dependencies (with possible required specifications). .thoth.yaml should contain a valid configuration for thamos

    Pipfile - respecting _`pipenv <https://github.com/pypa/pipenv>`_ tool
    Pipfile.lock - automatically managed by this manager - states all pinned down versions of your application stack

If you do not have Pipfile.lock present in your repository, this manager will automatically open a pull request with initial dependency lock.

Custom PyPI indexes are supported respecting Pipfile syntax.

If there is any issue in your application stack, the Thamos-Advise manager will open an issue with all the info and will try to resolve issue for you if possible by opening a pull request for you.

Why should I pin down dependencies in my application?
=====================================================
Check _`this StackOverflow thread <https://stackoverflow.com/questions/28509481>`_.

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

