Kebechet Version Manager
-----------------------

Edit version information in sources and open a pull request with tagged commit.

This manager can simplify package releases for you. If you open an issue that requests new version release, this manager will do actions needed on source code level.

A requirement to make this manager operational is that your version should be stated as a string in your ``setup.py``, ``version.py``, ``__about__.py``, ``__init__.py``, ``app.py`` or ``wsgi.py`` file in a variable named ``__version__``.


Available Package release commands
==================================

To run this manager, open an issue with one of the following titles:

* "2018.7.26 release" - changes version to "2018.7.26"
* "New calendar release" - creates release based on `calver <https://calver.org>`_
* "New major release" - bumps major release version respecting `semver <https://semver.org/>`_
* "New minor release" - bumps minor release version respecting `semver <https://semver.org/>`_
* "New patch release" - bumps patch release version respecting `semver <https://semver.org/>`_
* "New pre-release" - creates a pre-release respecting `semver <https://semver.org/>`_
* "New build release" - creates a new build release respecting `semver <https://semver.org/>`_


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
        - name: version
          configuration:
            labels:
              # Labels for opened issues and pull requests.
              - bot
            maintainers:
              # State authorized maintainers that can request package releases. This configuration is optional and
              # you can provide OWNERS YAML file in your repository with the same configuration
              # present (maintainers key with a list of maintainers).
              - fridex
            assignees:
              # A list of users to assign the opened pull request.
              - sesheta
            # Add release information to CHANGELOG.md file automatically.
            changelog_file: true

An example of this version manager in action can be found `here <https://github.com/thoth-station/kebechet/issues/98>`_.

Generating Smart Release Logs
=======

Optionally, Changelogs using Machine Learning and NLP can be generated through `Glyph <https://github.com/thoth-station/glyph>`_

.. code-block:: yaml

          configuration:
            changelog_smart: <true/false> (boolean to choose amongst smart or regular changelogs)
            changelog_classifier: <NAME OF ML CLASSIFIER> See Glyph's README for list of supported classifiers
            changelog_format: <NAME OF CHANGELOG FORMAT> See Glyph's README for list of supported formatters

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
