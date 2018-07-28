Kebechet Pipfile Requirements Manager
-------------------------------------

This manager will help you keep your dependencies stated in `requirements.txt` in sync with `Pipfile` or `Pipfile.lock`.

This is especially helpful if you use `pipenv <https://docs.pipenv.org>`_ for dependency management but you would
like to still use requirements.txt file - e.g. because of `setup.py` where you state `install_requires` for
your application (can be tricky to do directly in `setup.py` as toml is not in the Python standard library).

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
        - name: pipfile-requirements
          configuration:
            # Set to true if you would like to state fully pinned down software stack of your application.
            lockfile: true  # Defaults to false.

An example of this version manager in action can be found `here <https://github.com/thoth-station/kebechet/issues/404>`_.

Manager Author
==============

Fridolin Pokorny <fridolin@redhat.com>
