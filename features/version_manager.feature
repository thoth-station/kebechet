Feature: Kebechet's Version Manager

    @with_repo
    Scenario: test version manager minor update issue
        Given a repository with a minor update issue and a new file
         When Kebechet version manager is run
         Then pull request is opened with updated version string

    @with_repo
    Scenario: version manager updates version string after pull request with label set
        Given a pull request is merged with a new file
         When kebechet receives webhook corresponding to a merged PR with minor-release label set
         Then pull request is opened with updated version string
