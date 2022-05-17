Feature: Kebechet's advise manager
  @with_repo
  Scenario: User can request advise on repo through GitHub issue
    Given a user has opened a issue requesting an advise request
     When advise manager is run
     Then a comment on the issue indicating an advise has been scheduled is present in the issue
