Kebechet Info Manager
-----------------------

Open an issue titled `Kebechet info` and Kebechet will provide you information about
packages detected and Kebechet setup. The issue will be closed automatically by Kebechet.

Example
=======

An example of configuration for this manager:

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
        - name: info
          # This manager has no configuration.

An example of this manager in action can be found in `this issue <https://github.com/thoth-station/kebechet/issues/96>`_.

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
