Pipfile Requirements Manager
============================

This manager synchronizes ``requirements.txt`` with a repository's required
dependencies (``Pipfile``), or a repository's entire locked dependency stack
(``Pipfile.lock``).

This is especially helpful if you use `pipenv <https://docs.pipenv.org>`_ for
dependency management but you would like to still use requirements.txt file -
e.g. because of `setup.py` where you state `install_requires` for your
application (can be tricky to do directly in `setup.py` as toml is not in the
Python standard library).

Configuration
-------------

.. list-table::
    :align: left
    :header-rows: 1
    :widths: 20 20 20 60

    * - Name
      - Value
      - Default
      - Description
    * - lockfile
      - boolean
      - false
      - if true then ``requirements.txt`` is synced with
        ``Pipfile.lock`` otherwise it is synced with ``Pipfile``

Example
-------

An example configuration:

.. code-block:: yaml

    ...
    managers:
      - name: pipfile-requirements
        configuration:
          # Set to true if you would like to state fully pinned down software stack of your application.
          lockfile: true  # Defaults to false.
    ...

An example of this version manager in action can be found `here <https://github.com/thoth-station/kebechet/issues/404>`__.

Manager Author
--------------

Fridolin Pokorny <fridolin@redhat.com>
