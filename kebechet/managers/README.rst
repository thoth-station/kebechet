Kebechet Managers
-----------------

This submodule states all the available managers in Kebechet. See each manager's submodule to get all available options each manager provides for you.

Developing your own manager
===========================

If you would like to develop your own manager, just derive from `ManagerBase` class and implement `run()` method.
This method accepts kwargs that are directly passed from configuration file (see `configuration` section of a configuration file):

.. code-block:: python

  class UpdateManager(ManagerBase):
      def run(self, labels: list):
          issue = self.get_issue_by_title("Hello from my Kebechet manager")
          if issue is None:
            self.project.create_issue(
              title="Hello from my Kebechet manager",
              body="This is an awesome issue sent automatically from Kebechet manager.",
              labels=labels
            )

If you wish to operate on repository source code, you can request to clone it:

.. code-block:: python

        from kebechet.utils import cloned_repo

        with cloned_repo(self.service_url, self.slug) as repo:
            with open('my_file.txt', 'w') as my_file:
                my_file.write("Hello, Kebechet!")

            repo.git.add(my_file)
            repo.git.push()

The last thing you need to do, is to register your manager to `REGISTERED_MANAGERS` constant (you can find it in `kebechet/managers/__init__.py` file) so Kebechet knows about your manager. Manager can be referenced by its name in lowercase (class name without the "manager" suffix).

Kebechet works as a part of Thoth Ecosystem, please raise an issue or add the new manager to the `KebechetGithubAppInstallations
<https://github.com/thoth-station/storages/blob/15ed39ef6c8d7bf58037046f3bab2465c5c4bb22/thoth/storages/graph/models.py#L1434>`_ table.
