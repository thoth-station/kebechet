Update Manager
==============

This manager is responsible for automatic updates of dependencies in a
repository based on ``Pipfile`` or ``requirements.txt`` file. It will only
update direct dependencies (and it's subdependencies) and will do so in an
atomic fashion; for each package being updated a seperate pull request will be
opened. This makes it clear which updates introduce breaking changes to unit
tests or other CI.

If no ``Pipfile.lock`` or ``requirements.txt`` files are found this manager will
create whichever is appropriate.

Open an issue titled `Kebechet update` to manually trigger an update for your
repository.

``Pipfile`` has higher precedence over ``requirements.in`` so if you
have both files present in your Git repository, only Pipfile.lock will be
managed.

Prerequisites
-------------

#. ``Pipfile`` or ``requirements.in`` or ``requirements-dev.in`` defining all
   direct dependencies

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
      - List[str]
      - REQUIRED
      - List of labels that are applied to any pull requests or issues opened
        by this manager.

Example
-------

An example configuration:

.. code-block::yaml
    ...
    managers:
      - name: update
        configuration:
          labels:
            # Labels for opened issues and pull requests.
            - bot
    ...

You can see this manager in action in these various scenarios:

- `Automatic dependency update <https://github.com/thoth-station/kebechet/pull/46>`_

- `Initial dependency lock <https://github.com/thoth-station/kebechet/pull/85>`_

- `Dependency update failure report <https://github.com/thoth-station/solver/issues/38>`_

- `Manual dependency update request <https://github.com/thoth-station/mi/issues/227>`_

Manager Author
--------------

Fridolin Pokorny <fridolin@redhat.com>
