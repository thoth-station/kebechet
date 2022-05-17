Feature: Kebechet's Update Manager
  @with_repo
  Scenario:
    Given repository with a `click` version (==1.0.0) older than defined constraint (<=2.0.0)
     When update manager is run
     Then PR is opened with `click==2.0` in Pipfile.lock
