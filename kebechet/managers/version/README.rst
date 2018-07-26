Kebechet Version Manager
-----------------------

Edit version information in sources and open a pull request with tagged commit.

This manager can simplify package releases for you. If you open an issue that states requests


Available Package release commands
==================================

To run this manager, open an issue with one of the following titles:

* "2018.7.26 release" - changes version to "2018.7.26"
* "New calendar release" (WIP) - creates release based on `calver <https://calver.org>`_
* "New major release" (WIP) - bumps major release version respecting `semver <https://semver.org/>`_
* "New minor release" (WIP) - bumps minor release version respecting `semver <https://semver.org/>`_
* "New patch release" (WIP) - bumps patch release version respecting `semver <https://semver.org/>`_
* "New major pre-release" (WIP) - creates a new major pre-release respecting `semver <https://semver.org/>`_
* "New minor pre-release" (WIP) - creates a new minor pre-release respecting `semver <https://semver.org/>`_
* "New patch pre-release" (WIP) - creates a new patch pre-release respecting `semver <https://semver.org/>`_
* "New major build release" (WIP) - creates a new major prerelease respecting `semver <https://semver.org/>`_
* "New minor build release" (WIP) - creates a new minor prerelease respecting `semver <https://semver.org/>`_
* "New patch build release" (WIP) - creates a new patch prerelease respecting `semver <https://semver.org/>`_


This manager will automatically bump version based on issue request, opens a pull request with tagged commit that states
version and links pull request to the issue you opened to close it on merge.

There are done operations only on the source code level, the actual release is not performed (different manager or your CI).

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
        - name: update
          configuration:
            labels:
              # Labels for opened issues and pull requests.
              - bot
            maintainers:
              # State authorized maintainers that can request package releases. This configuration is optional and
              # you can provide OWNERS YAML file in your repository with the same configuration
              # present (maintainers key with a list of maintainers).
              - fridex

An example of this version manager in action can be found `here <https://github.com/thoth-station/kebechet/issues/98>`_.

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
