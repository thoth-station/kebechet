Version Manager
===============

This manager updates version information for your project. It allows for either
semantic versioning or calendar versioning. It will also generate changelogs
based on commits since the last version released.

Edit version information in sources and open a pull request with tagged commit.

This manager can simplify package releases for you. If you open an issue that
requests new version release, this manager will do actions needed on source code
level.

.. caution:: This manager does **NOT** create new releases. It only creates the
    changes in source code and changelogs. Additional CI must be added.

A requirement to make this manager operational is that your version should be
stated as a string in your ``setup.py``, ``version.py``, ``__about__.py``,
``__init__.py``, ``app.py`` or ``wsgi.py`` file in a variable named
``__version__``.

Optionally, Changelogs using Machine Learning and NLP can be generated through
`Glyph <https://github.com/thoth-station/glyph>`_

Prerequisites
-------------

#. You need one of the following files: ``setup.py``, ``version.py``,
   ``__about.py``, ``__init__.py``, ``app.py`` or ``wsgi.py`` to contain the
   following line::

      __version__="<current-version-string>"

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
      - List[string]
      - REQUIRED
      - List of labels that are applied to any pull requests or issues opened
        by this manager.
    * - maintainers
      - Optional[List[string]]
      - ``null``
      - State authorized maintainers that can request package releases. This
        manager will also respect an OWNERS file for the same purpose.
    * - assignees
      - Optional[List]
      - ``null``
      - A list of users to assigin to the opened pull request
    * - changelog_file
      - boolean
      - false
      - Add release information to CHANGELOG.md file automatically.
    * - changelog_smart
      - boolean
      - true
      - Choose between smart or regular changelogs
    * - changelog_classifier
      - string
      - "FASTTEXT"
      - see Glyphs `README <https://github.com/thoth-station/glyph>`_ for a list
        of supported classifiers
    * - changelog_format
      - string
      - "CLUSTER_SIMILAR"
      - see Glyphs `README`_ for a list of supported formatters
    * - pr_releases
      - boolean
      - true
      - automatically create releases from appropriately labeled PRs
    * - release_label_config
      - Object[str, List[str]]
      - | release_label_config:

            |  calendar: [calendar-release]
            |  major: [major-release]
            |  minor: [minor-release]
            |  patch: [patch-release]
            |  pre: [pre-release]
            |  build: [build-release]
            |  finalize: [finalize-version]
      - list of labels in a PR that will trigger a specific type of release. Setting configuration for only a subset
        of the release types will leave the rest of the defaults unchanged.

Example
-------

An example configuration:

.. code-block:: yaml

    ...
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
          release_label_config:
            # calendar: [calendar-release] remains unchanged
            major: [major-v]
            minor: [minor-v]
            patch: [patch-v]
            # pre: [pre-release] remains unchanged
            # build: [build-release] remains unchanged
            finalize: []

An example of this version manager in action can be found `here
<https://github.com/thoth-station/kebechet/issues/98>`_.

Available Package release commands
----------------------------------

To run this manager, open an issue with one of the following titles:

* "2018.7.26 release" - changes version to "2018.7.26"
* "New calendar release" - creates release based on `calver
  <https://calver.org>`_
* "New major release" - bumps major release version respecting `semver
  <https://semver.org/>`_
* "New minor release" - bumps minor release version respecting `semver`_
* "New patch release" - bumps patch release version respecting `semver`_
* "New pre-release" - creates a pre-release respecting `semver`_
* "New build release" - creates a new build release respecting `semver`_

Manager Author
--------------

Fridolin Pokorny <fridolin@redhat.com>


..
