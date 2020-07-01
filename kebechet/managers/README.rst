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
          self.sm.open_issue_if_not_exist(
            "Hello from my Kebechet manager",
            lambda: "This is an awesome issue sent automatically from Kebechet manager.",
            labels=labels
          )

As you can see above, you can access already instantiated `SourceManagement` class that provides useful routines when transparently
communicating with GitHub or GitLab services (what service you talk to is abstracted away).

If you wish to operate on repository source code, you can request to clone it:

.. code-block:: python

        from kebechet.utils import cloned_repo

        with cloned_repo(self.service_url, self.slug) as repo:
            with open('my_file.txt', 'w') as my_file:
                my_file.write("Hello, Kebechet!")

            repo.git.add(my_file)
            repo.git.push()

The last thing you need to do, is to register your manager to `REGISTERED_MANAGERS` constant (you can find it in `kebechet/managers/__init__.py` file) so Kebechet knows about your manager. Manager can be referenced by its name in lowercase (class name without the "manager" suffix).
