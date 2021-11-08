Configuration
=============

General Configuration
---------------------

.. start-general-config

To configure Kebechet, your repository should have a ``.thoth.yaml`` file in the
root directory of the repository. Below you can find an example configuration
file that has been annotated

.. code-block:: yaml

    host: khemenu.thoth-station.ninja   # url of Thoth's user-api
    requirements_format: pipenv         # tool used for managing python package dependencies
    overlays_dir: overlays              # if your repository contains more than one runtime environment

    runtime_environments:
    - name: rhel-8                      # this will be used to find the environment specific files <overlay-dir>/<name>
      operating_system:
        name: rhel
        version: "8"
        python_version: "3.8"
        recommendation_type: latest     # if thoth-advise is being used this indicates priority for dependencies

    managers:
    - name: foo
      configuration:                    # manager specific configuration
        labels: [bot]

.. end-general-config
