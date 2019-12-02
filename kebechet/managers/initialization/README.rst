Kebechet Initialization Manager
-------------------------------

Create a kebechet configuration file with a given list of managers.

This manager automatically creates a Pull Request on your repo with the kebechet.yaml
configuration file created.


Example
=======

run `kebechet init --token=$KEBECHET_TOKEN --managers=info,update`

It will generate a file like:

.. code-block:: yaml

        repositories:
        - slug: thoth-station/kebechet
          token: '{KEBECHET_TOKEN}'
          service_type: github
          managers:
          - name: info
          - name: update
            configuration:
              labels:
              - kebechet
              - bot


Manager Author
==============

Ronan Souza <ronan.souza@ccc.ufcg.edu.br>
