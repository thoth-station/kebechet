Kebechet Origin Manager
-----------------------

This manager will monitor your repository and will make sure you use desired packages based on configuration.

Also, this manager will preserve that external changes (e.g. package changes) do not affect your application.

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
      # service_url: <URL>
      # tls_verify: true/false
      managers:
        - name: origin
          warehouses:
            # A list of warehouses that are deployed within you infrasture.
            - https://pypi.org/simple

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
