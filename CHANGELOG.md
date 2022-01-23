# Changelog for the Kebechet - a Thoth bot

## Release 1.7.3 (2022-01-23T07:07:01)
* :ship: Release of version 1.7.2 (#979)
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* pop enabled config
* check before trying to unshallow a repo
* Enable TLS verification
* Enable TLS verification in the sample default configuration
* Release of version 1.7.1
* remove all references to get user
* Unpin fasttext version from Pipfile
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* Release of version 1.7.0
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* use analysis-id 4 branch name to avoid collisions
* Add branch for if thoth configuration blocks advise submission
* add documentation for advise issue
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* add link to manager doc above managers block in minimal yaml
* update version manager to act on PR merge with labels
* Suggest users to use Thamos CLI to create requirements file
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* Release of version 1.6.8
* Fix the links to each manager's README
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* create_pr for manager class with default value for forknamespace
* check if update needs rebase
* use env variable for kebechets name
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
* Release of version 1.6.7 (#932)
* Runtime environment name must not use colon
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* Fix format string reference to environment name
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* remove kebechet- prefix from version branch (used for image tag)
* :boat: Release of version 1.6.6
* if no depth is passed fetch full history
* add kebechet- to all branch names
* :boat: Release of version 1.6.5
* clean repo after using
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* :boat: Release of version 1.6.4
* check if .git exists so that we don't catch all gitcommand exceptions (#909)
* if we have already cloned to dir, return repo from dir
* :boat: Release of version 1.6.3
* :fire: patch the circuler import fix for keb version in utils
* Release of version 1.6.2
* Remove the maintainers section from .thoth.yaml
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* Track advise status using GitHub issue
* patch the fasttext version for build fix
* Release of version 1.6.1 (#897)
* add keb version to issue body
* Release of version 1.6.0
* add triage/accepted labels to release issue template to prevent Prow from starting a traige
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* Add Goern, Harshad and Pep as approvers
* :bomb: use https based url in the pre-commit
* :turtle: Support python 3.9 in kebechet dependency management
* reraise github server exception
* allow clone dir to be passed as environment variable
* use approvers section of OWNERS file as default maintainers
* do not report dependency manager exception on support (#878)
* add custom exception for known failure cases and open issues for failed manager
* change key value for getting results from advise endpoint
* use sphinx for Kebechet documentation
* Release of version 1.5.5
* checks for num lines to avoid out-of-bounds exception
* :turtle: patch read write method for changelog update
* set self.runtime_environment and use for all issue titles
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* Release of version 1.5.4
* check if issue already exists
* Release of version 1.5.3
* catch ssl errors as it is a networking issue
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* create changelog file if it doesn't exist
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* make changelog not smart by default
* add enabled flag to manager configuration
* don't require locked version for old deps
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* add checks for local installations and pkgs bundled by pipenv
* check for none indicating function failed
* create issue if no requirements found for runtime env
* if PR already exists warn and continue
* Release of version 1.5.2
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment (#837)
* add KPostOffice to approvers
* only create one issue per exc per line
* Release of version 1.5.1
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* Fix markdown format for table rows
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* :bug: fix some typos
* do not raise issue for conn error
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* add link to repository which caused exception
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
* get relative path of overlay currently being updated for link
* Release of version 1.5.0
* instead of opening issues in user repo open in thoth-station/support
* updated README files to reflect current state of Kebechet
* Minor format improvements in the README
* log if issue creation is disabled
* add unregistered manager which adds thoth-config
* convert README from RST to MD
* add return statement
* pull runtime_environment directly from advise results
* if requirements.txt does not exist it must be created
* Format traceback with Python backtick code
* Release of version 1.4.1
* Empty commit for a new release
* removed unused -dev dependencies
* advise manager with overlays
* Release of version 1.4.0 (#773)
* :arrow_up: Automatic update of dependencies by Kebechet (#768)
* add args to get access token
* open issues on repo when managers fail
* make update manager work with overlays
* :arrow_up: Automatic update of dependencies by Kebechet
* Release of version 1.3.3
* :arrow_up: Automatic update of dependencies by Kebechet
* :sparkles: add some Kubernetes-inspired Labels to Issues opened by Kebechet
* fix issue 746
* :arrow_up: Automatic update of dependencies by Kebechet
* :arrow_up: Automatic update of dependencies by Kebechet
* fixed bug with unrelated histories where khebhut doesn't create PR
* pass environment name to managers and add documentation for expected manager behaviour
* update from template project
* add priority/critical-urgent label to all bot related issue templates
* use upstream solution for adding assignees
* :arrow_up: Automatic update of dependencies by Kebechet
* Release of version 1.3.2
* use ogr to get app auth token
* :arrow_up: updated labels of issue templates
* pre-commit issue
* Update kebechet/managers/version/version.py
* Fixed prepending when Title exists
* Fixed small bug in which original changelog was removed
* Fixed README to remove legacy example configuration
* changed appending changelog to prepending changelog
* :arrow_up: Automatic update of dependencies by Kebechet
* Release of version 1.3.1
* add docs for locally running Kebechet
* Update OWNERS
* add ogr dep to Pipfile
* :arrow_up: Automatic update of dependencies by Kebechet
* :arrow_up: Automatic update of dependencies by Kebechet
* Release of version 1.3.0
* remove thoth-sourcemanagement from Kebechet (#725)
* :arrow_up: Automatic update of dependencies by Kebechet (#724)
* :hatched_chick: update the prow resource limits (#723)
* :arrow_up: Automatic update of dependencies by Kebechet
* :arrow_up: Automatic update of dependencies by Kebechet
* use thamos.lib.write_files
* :zap: pre-commit fixes for the master branch
* :arrow_up: Automatic update of dependencies by Kebechet (#716)
* :arrow_up: Automatic update of dependencies by Kebechet (#713)
* :arrow_up: Automatic update of dependencies by Kebechet
* :arrow_up: Automatic update of dependencies by Kebechet (#709)
* add kebechet metadata when sending request to thamos (#699)
* :arrow_up: Automatic update of dependencies by Kebechet (#708)
* remove todo
* :arrow_up: Automatic update of dependencies by Kebechet (#706)
* :arrow_up: Automatic update of dependencies by Kebechet (#703)
* :arrow_up: fix some formatting and update pre-commit plugins
* :sparkles: reconfgured CI/CD to use prow and aicoe-ci
* :arrow_up: Automatic update of dependencies by Kebechet (#697)
* add justification based on metadata if possible
* :arrow_up: Automatic update of dependencies by Kebechet (#695)
* :arrow_up: Automatic update of dependencies by Kebechet (#694)
* :arrow_up: Automatic update of dependencies by Kebechet (#692)
* :arrow_up: Automatic update of dependencies by Kebechet (#691)
* Release of version 1.2.4 (#690)
* :arrow_up: Automatic update of dependencies by kebechet. (#687)
* write outputs of pipenv lock -r to output file (#686)
* :arrow_up: Automatic update of dependencies by kebechet. (#685)
* :arrow_up: Automatic update of dependencies by kebechet. (#684)
* :arrow_up: Automatic update of dependencies by kebechet. (#682)
* Automatically close update merge request if no longer relevant (#661)
* :arrow_up: Automatic update of dependencies by kebechet. (#677)
* :arrow_up: Automatic update of dependencies by kebechet. (#668)
* Fixed log message (#673)
* Delete branch if the pull request has been already closed
* removed bissenbay, thanks for your contributions!
* :bug: fix some flake8 complains
* :sparkles: add a little more linky footer to PRs
* Thoth Labelmanager (#656)
* :arrow_up: Automatic update of dependencies by kebechet. (#666)
* Release of version 1.2.3 (#667)
* :arrow_up: Automatic update of dependencies by kebechet. (#660)
* :arrow_up: Automatic update of dependencies by kebechet. (#658)
* :arrow_up: Automatic update of dependencies by kebechet. (#655)
* add a little more linky footer to PRs (#607)
* :arrow_up: Automatic update of dependencies by kebechet. (#651)
* fix the name of the imagestream to-be looked up (#650)
* Release of version 1.2.2 (#649)
* Relock to fix typing_extensions relock (#646)
* Update OWNERS
* Missing typing extensions (#645)
* Release of version 1.2.1 (#642)
* port to python38 (#621)
* Release of version 1.2.0 (#638)
* :arrow_up: Automatic update of dependencies by kebechet. (#636)
* statisfy the need of python38-devel libraries (#635)
* newline adjustment for consistency of body for kinda issues (#631)
* Fixed wrong function accessed (#633)
* :arrow_up: Automatic update of dependencies by kebechet. (#630)
* Added warning if release tag is missing. (#628)
* Slug wrongly set (#627)
* Release of version 1.1.4 (#626)
* The release PR should close the issue (#606)
* Release of version 1.1.3 (#624)
* Req was using pipenv 2018 (#615)
* :arrow_up: Automatic update of dependencies by kebechet. (#613)
* Add Sai to project owners (#611)
* Add AICOE Config (#600)
* Release of version 1.1.2 (#604)
* Updated to pipenv 2020 (#602)
* Release of version 1.1.1 (#599)
* Update manager non-atomic updates (#597)
* Release of version 1.1.0 (#596)
* Added modifications to use gitpython (#594)
* :honeybee: upgrade pip for kebechet container image (#593)
* Release of version 1.0.10 (#592)
* Updated source-management and fixed version test (#590)
* Remove unnecessary quotes (#589)
* Enabled github app authentication (#587)
* precommit happy
* Link formatted
* added a clickable link to readme
* :sparkles: :pencil: updated the readme, now we deploy via kustomize rather than ansible
* Precommit fixes
* Added reminder to add to thoth stroage
* Fix typo
* Add manual request example
* Release of version 1.0.9
* Updated glyph
* updated github templates
* Make pre-commit happy
* Fixed version test
* Release of version 1.0.8
* Updated glyph to 0.13
* Release of version 1.0.7
* Updated dependencies
* fixed imports
* Release of version 1.0.6
* Update versions
* Release of version 1.0.5
* Update .thoth.yaml
* :pushpin: Automatic update of dependency gitpython from 3.1.7 to 3.1.8
* :pushpin: Automatic update of dependency thoth-glyph from 0.1.0 to 0.1.1
* :pushpin: Automatic update of dependency sentry-sdk from 0.17.0 to 0.17.4
* :pushpin: Automatic update of dependency thamos from 0.11.1 to 0.12.2
* :pushpin: Automatic update of dependency thoth-common from 0.16.1 to 0.18.2
* Fix formatting when wrong version identifier is found
* Fix reStructuredText issues
* Release of version 1.0.4
* Add GitHub's PR template
* Skip empty new lines in update manager
* Update requirements.txt
* Revert "Updated to pipenv 2020.8.13 and locked"
* Release of version 1.0.3
* Updated to pipenv 2020.8.13 and locked
* Release of version 1.0.2
* Fix GitHub templates location
* Fix formatting when smart changelogs are created
* Enable smart logs by default
* Add release templates to let Kebechet release itself
* Fixed added context to multiple version string error.
* :pushpin: Automatic update of dependency pytest-cov from 2.10.0 to 2.10.1 (#490)
* :pushpin: Automatic update of dependency thamos from 0.11.0 to 0.11.1 (#489)
* :pushpin: Automatic update of dependency thoth-common from 0.16.0 to 0.16.1 (#488)
* Document CHANGELOG.md file generation and assignees (#487)
* Minor fix
* ThothGlyphException import added
* return statement added in Glyph exception
* Extra line removed
* String concatenation fix
* Minor fix
* Updated Version Manager's README to include Glyph's specifications
* Pipfile updated, Glyph's exceptions handled
* Optionally generate intelligent release logs using Glyph
* return statement added in Glyph exception
* Extra line removed
* :pushpin: Automatic update of dependency thamos from 0.10.6 to 0.11.0 (#486)
* String concatenation fix
* Minor fix
* Updated Version Manager's README to include Glyph's specifications
* Pipfile updated, Glyph's exceptions handled
* Optionally generate intelligent release logs using Glyph
* :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#482)
* :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#481)
* :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0 (#480)
* Formatted commit messages with backticks. (#477)
* :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#476)
* :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#475)
* :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2 (#474)
* Relock fix  (#468)
* :pushpin: Automatic update of dependency gitpython from 3.1.3 to 3.1.7 (#471)
* :pushpin: Automatic update of dependency thamos from 0.10.5 to 0.10.6 (#472)
* Precommit fixes (#470)
* Cronjob cleanup-job can be archived
* :pushpin: Automatic update of dependency thoth-common from 0.13.13 to 0.14.1
* keep the application up-to-date with pre-commit
* Remove thoth-station/package-analyzer
* Update version manager documentation
* Add CodeQL security scanning (#425)
* Remove build-analyzers
* Update OWNERS
* Remove graph-sync-scheduler
* Update OWNERS
* Remove result-api and workload-operator
* :pushpin: Automatic update of dependency thoth-common from 0.13.12 to 0.13.13
* :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.9 to 0.3.0
* Limit version release log to 300
* keep wf for SLI
* Make config parsing more safe
* Piplock using 2018
* Pin older version of Pipenv during the build
* :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
* Added python 3.8
* New piplock
* :pushpin: Automatic update of dependency thoth-common from 0.13.11 to 0.13.12
* Fix attribute error while parsing YAML
* Fix if maintainers are not stated in OWNERS file
* Change logger to info to monitor on cluster
* :pushpin: Automatic update of dependency pytest-timeout from 1.4.0 to 1.4.1
* :pushpin: Automatic update of dependency semver from 2.10.1 to 2.10.2
* :pushpin: Automatic update of dependency pytest-cov from 2.9.0 to 2.10.0
* :pushpin: Automatic update of dependency pytest-timeout from 1.3.4 to 1.4.0
* Remove old member
* fresh piplock
* str cast moved to return
* Typo fix
* Coala errors
* Perform manual update of dependencies
* Release of version 1.0.1
* Add repo for solver error classifier
* Correct template
* add pre-commit config
* added a 'tekton trigger tag_release pipeline issue'
* Add thoth-station/datasets
* Add version release for advise-reporter
* :pushpin: Automatic update of dependency pipenv from 2018.11.26 to 2020.5.28
* Consider app.py and wsgi.py as a source for version
* :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
* :pushpin: Automatic update of dependency thamos from 0.10.1 to 0.10.2
* :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0
* :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
* :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
* kebechet should be capitalized
* :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
* Added repo
* Added repo
* Revert "Fix if automatic relocking PR exists"
* :pushpin: Automatic update of dependency thamos from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
* use source type enum
* remove metadata prefix
* Added update and version to slo
* :pushpin: Automatic update of dependency toml from 0.10.0 to 0.10.1
* :pushpin: Automatic update of dependency semver from 2.10.0 to 2.10.1
* use metadata option when calling thamos advise
* Fixed coala errors
* Print version as info
* Print version as info
* Update README.rst
* Update README
* :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.7 to 0.2.9
* Fix test imports
* :pushpin: Automatic update of dependency pytest from 5.4.1 to 5.4.2
* Added sesheta as mainatianer in version manager
* Added source management
* fixed coala
* coala fix
* Comments on pr if modified pr found.
* :pushpin: Automatic update of dependency semver from 2.9.1 to 2.10.0
* Fix if automatic relocking pr exists
* :pushpin: Automatic update of dependency pylint from 2.5.1 to 2.5.2
* :pushpin: Automatic update of dependency pylint from 2.5.0 to 2.5.1
* :pushpin: Automatic update of dependency gitpython from 3.1.1 to 3.1.2
* :pushpin: Automatic dependency re-locking
* Fixed coala errors
* Added instruction for manual trigger and closses issue
* Added instruction for manual trigger and closses issue"
* :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
* :pushpin: Automatic update of dependency thamos from 0.9.4 to 0.10.0
* Changed image source to infra"
* :pushpin: Automatic update of dependency thamos from 0.9.3 to 0.9.4
* :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
* :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
* Updated name to kebechet
* :pushpin: Automatic update of dependency pylint from 2.4.4 to 2.5.0
* :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
* Updated template and workflow to use openshift image
* Changed template name to kebechet-job
* Added argo workflow and oc template
* :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
* Add SLO-reporter repo
* :pushpin: Automatic update of dependency thamos from 0.9.2 to 0.9.3
* Added cli endpoint envvar
* Add maintainer for thamos
* Changed liveness probe to 45mins.
* Coala fix
* Coala fix
* Fix parameters
* Fixed run-url cli error
* Fix job template
* :pushpin: Automatic update of dependency gitpython from 3.1.0 to 3.1.1
* Delete thoth_demo.yaml
* Added s2i notebook repos
* :pushpin: Automatic update of dependency thoth-common from 0.12.8 to 0.12.9
* :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.8
* :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
* :pushpin: Automatic update of dependency thamos from 0.9.1 to 0.9.2
* :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.6 to 0.2.7
* :pushpin: Automatic update of dependency thamos from 0.8.1 to 0.9.1
* :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.12.6
* Removed fstrings
* Fixed coala errors
* removed extra files
* Removed try catch
* Fixed syntax
* Addressed comments
* Added error handling in case version control is used
* Add support for advise-reporter
* Support for thoth unresolved-package-handler
* add maintainer for thoth-station/messaging
* :pushpin: Automatic update of dependency pyyaml from 5.3 to 3.13
* :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1
* :pushpin: Automatic update of dependency pytest from 5.3.5 to 5.4.0
* :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
* :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
* :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
* Delete thoth_demo.yaml
* fixed coala
* fixed coala
* Check standard package in package.json
* fixed commits
* fixed messages
* Revert "Fixed messages and create initial lock commits"
* Fixed messages and create initial lock commits
* Changed namespace to thoth
* kebechet only uses thoth sourcemanagement
* removed pin
* Fixed dependencies
* Latest git python
* Fix cron job run
* :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
* New Maintainer
* fixed coala
* printin to log
* Closes release request if no change
* Adjust .thoth.yaml configuration file
* Handle \r\n
* A big step towards general AI
* Fixed lambda x
* :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
* Fixed ogr migration errors
* Fixed ogr migration errors
* Fixed ogr migration errors
* :pushpin: Automatic update of dependency requests from 2.22.0 to 2.23.0
* Fixed gitlab payload
* Supporting cron job run
* Added to requirement.txt
* Gitlab works with usernames
* Added custom errors
* Removed IGitt from depedencies
* coala fix
* Updated managers to use ogr methods
* removed event variable
* removed event variable
* fixed list branches expecting json
* Removed IGitt from manager base class
* added different id for gitlab
* Added logic for assigning to issue.
* Added logic for assigning to issue.
* Added alternate source management
* OGR Migration
* Now passing the whole payload to the managers.
* ogr changes
* Adding ogr replacement
* Fixed coala errors"
* Added event conditions to managers
* Saving parsed dict in parser
* Added url parse and resolved comments"
* Update thoth.yaml
* Update .thoth.yaml
* Added raising exceptions
* Added suggested changes
* Add thoth-station/s2i repository
* Support for thoth package-update-job
* Fixed coala errors
* Added payload parsing
* Webhook propagated to config.
* Change cli to recieve payload as string
* Removed nested dictionary
* Fixed typos
* Added sub command
* Removed demo yaml file
* Added manager back to iter
* changed if condn
* Fixed coala errors
* Reverted run method
* Fixed coala errors
* Use only slug
* temp close moved
* Run with managers from respective repos
* Introduce second instance of Kebechet
* :smiling_imp: added durandom_64fbc27e213f5a61c975ab29df94536b88f03270 to Kebechet
* Add new mantainer
* kebechet also support release of AICoE SrcOpsMetrics
* Support for AICoE SrcOpsMetrics
* Add new maintainer
* Happy new year!
* Add thoth-station/s2i-thoth repo
* Fix number attribute error
* support graph-backup-job with dependency updates.
* Add thoth-pybench to monitored repos
* Support for AICoE Fraud Detection
* Sort repositories based upon their dependencies
* updated templates with annotations
* Use the generic webhook for build trigger
* github ref point to master
* Fix permission issues
* use /tmp for a .cache directory
* Adjust Pipenv cache in the correct place
* Adjust cache location when run in the cluster due to perms
* :green_heart: added Thoth's Stub-API Repository
* :sparkles: added an annotation to each object created, so that we know the version of the template that created the object
* Enable version manager for AICoE/prometheus-api-client-python
* Migrate to pytest
* Add docstrings to satisfy coala linter.
* Make `v` optional in tag when matching version
* Support for AICoE  ludus
* Development packages are not mandatory in Pipfile
* added the AICoE repos
* Add thoth-station/messaging to monitored repos
* :lock: relocked
* Update README.rst
* Fix wrong slug for the sesheta repo
* Do not monitor conu repo
* Add package-analyzer to monitored repos
* Update templates and cli options
* Propagate deployment name for sentry environment
* Add build-analyzers to monitored repos
* Use UBI8 as base image
* Small changes to env names
* Remove osiris and osiris observer
* Fix list in YAML
* Update READMEs
* Update READMEs
* Coala formatting
* Combine configuration files
* Addressing comments
* Whoops
* Coala formatting
* Review suggestions
* Trigger Sesheta
* Trigger Sesheta
* Add "Finalize version" to accepted titles
* Be consistent with issue title case
* Make maintainers case insensitive
* CronJobs are now in apiVersion v1beta1
* Changed env variable names
* Forgot to save app.sh
* Adding subcommand should keep original functionality of cronjob
* Changes based on suggestions
* Update buildConfig-template.yaml
* Fixed coala formatting issues
* Fixed origin format
* Add @harshad16 to maintainers of thoth-lab
* Removed test values in job template
* Removed test values in job template
* Forgot to clone repo before doing provenance check
* Back to docker
* cli
* Wrong name for subcommand
* app.sh executable
* Update Pipfile.lock
* Remove result managers
* Recombined manager but has two distinct logical branches
* Single missing quotation
* Merge run-url
* git tokens are now in secrets
* Subcommands
* Split thoth managers to remove waiting
* Forgot a line
* Changes based on review
* Update to work with s2i
* Updated job template
* Made a services class
* Coala formatting
* Forgot to save
* Implemented suggestions
* Configure starting deadline seconds to large number
* Changed to use environment variable
* Creation of kebechet job template
* Missing period
* Manual format
* Auto format
* GitLab url run
* Manager runs for GitHub
* First commit
* Add invectio for management
* :sparkles: using the new trigger-build zuul job
* :sparkles: using the new trigger-build zuul job
* :sparkles: using the new trigger-build zuul job
* Add CermakM to list of thoth-lab maintainers
* Update based on suggestions
* Updated based on suggestions
* Added thamos to Pipfile for new managers
* Updated README
* Logging info as well as auto retrying on Thamos failures
* Auto format
* Remove completed TODOs
* Provenance manager (basic) complete
* Labels were not being applied
* Automatically opens issues if thoth adviser returns error
* Updated readme with thamos configuration example
* Removed _advise_wrap in anticpation of thamos.lib.advise_here()
* Changed name to be more specific
* Changed README and removed unnecessary code that was copied over
* advise and write have been seperated so that if result is error an issue is opened
* Forgot to included init that makes manager accesible
* Basic thoth manager
* Version manager searches for __about__.py as well
* :lock: relocked
* Add Francesco to maintainers section of thoth-storages
* Use emojis in commit messages not in pull-request titles
* :sparkles: now using a bit of gitmoji
* Add Thoth's configuration file
* Do not forget to install thoth-common
* 🔥hotfixing the trailing space...
* that part of the webhook url is not required
* Use safe_load() instead of load()
* Use safe_load() instead of load()
* Kill Kebechet after 2 hours if it was not able compute results
* Fix coala warning
* Use Thoth's init_logging routine
* Do not use update manager in graph-sync-scheduler
* added graph-sync-scheduler to configuration file
* Add init-job to monitored repos
* It's already 2019
* Add build-watcher to monitored repos
* Add @CermakM to maintainers for osiris
* Add osiris and osiris build-observer
* Add operators to monitored repos
* Add thoth-python to monitored repos
* Add long description for PyPI
* Remove markers from requirements file
* Set env variables to suppress pipenv emojis
* use thoth-* jobs in pipeline
* added metrics-exports
* Monitor AICoE/prometheus-flatliner repository
* Monitor Thoth's management API
* Lower log level when something goes wrong when running Pipenv
* Correctly fix attribute error
* Fix attribute error
* Propagate issue body to pull request on version updates
* Add amun-client to monitored repos
* Fix wrong manager name
* Fix wrong value configuration
* Pipenv has been fixed upstream
* Fix version manager
* Initial dependency lock
* Do not forget to install sentry-sdk
* Let Kebechet do the locking
* Fixes to make Kebechet work in deployment
* Add Sentry support
* Distinguish pip and Pipenv cache
* New Pipenv does not respect PIPENV_CACHE_DIR
* A temporary fix to avoid recent Pipenv issues
* Add Amun API repository for monitoring
* Be case insensitive with issue titles triggering new versions
* Fix repo name
* Monitor AICoE/log-anomaly-detector for updates
* put some more labels in, adjusted successfulJobsHistoryLimit
* hotfix
* added thamos project
* Fix computing of changelog
* Log activities done during changelog computation
* Enable change log files on Thoth repos
* Place related before reported changelog
* Fix initial lock issues
* added requirements-dev.txt compatibility
* Update .zuul.yaml
* Add CVE update job to monitored repos
* An array is expected
* Be consistent with git push
* Configure git on repo clone
* Fix commit
* Fix handling of versions when Pipfile is used
* Fix key to packages in Pipfile
* Expand configuration to start using pipfile-requirements
* Fix f-string
* using an obfuscated URL
* now with a build trigger in the post pipeline
* now with a build trigger in the post pipeline
* Do not cache images in build config
* Version can be stated in version.py
* Do calendar release with full year
* Compute changelog on releases
* Initial dependency lock
* Remove Pipfile.lock to get initial lock
* Print Kebechet version on startup
* Fix user assignment to issue
* new templates
* added srcops-testing
* Introduce Pipfile requirements.txt manager
* Assign users to the release issue
* Use related instead of fixes
* Do not tag commits
* Fix tagging of commit
* Fix version handling issues
* Another attempt to fix requests issue
* Make sure IGitt does not propagate verify arguments
* Try to fix IGitt requests handling
* Remove duplicit requests
* Make Kebechet compatible with recent IGitt release
* Use dev release of IGitt
* Install IGitt from git repo correctly
* Fix IGitt requirement
* Install IGitt from repository
* Do not forget to install semver
* Use IGitt directly from git repository for now
* Initial dependency lock
* Let Kebechet relock dependencies with semver lib
* Implement semver and calver for automated releases
* Inspect also version.py for version information
* Minor fixes in README file
* State how version manager looks for version
* Add user-cont/conu for managing updates
* Fix typo in docs
* Update README.rst
* Fix typo in docs
* Remove unused import
* Adjusted based on review comments
* Last documentation bits
* Document managers section
* Update documentation for version manager
* Update documentation for update manager
* Update documentation for info manager
* Create a soft copy for YAML links
* Let only maintainers release new packages
* Add version manager for Thoth repos
* Issue handling and minor fixes
* Fix missing packages
* Push also tags
* Implement version change logic
* Introduce version manager for automatic version releases
* Remove unused arguments
* Move info messages into correct module
* Introduce manager configuration entry
* Initial dependency lock
* Provide README files for managers
* Place all managers into their own modules
* Pin down gitpython because of IGitt
* Ask Kebechet for initial lock
* Fix a typo in attribute name
* Add Sesheta to monitored repos
* Adjust template labels
* Use description instead of non-existing body attribute
* Report end run for config entry
* Fix another subscription error
* Fix typo
* Fix key error exception
* Fix token expanding from env vars
* Install sources directly from GitHub repo
* GitLab support fixes and extensions
* Add GitLab support
* Utilize repo cloning
* Fix bound method call
* No need to print context in verbose mode
* Hide token in logs
* Fix calling checkout
* We have to explicitly install dependency version
* Install Kebechet from git repo for now
* Initial dependency lock
* Delete Pipfile.lock for relocking dependencies
* Fix hash computation
* Run info manager on thoth-station repos
* Introduce managers abstraction
* Checkout to master after changes
* Fix bound method call
* Close initial lock issue when no longer relevant
* Code refactoring
* Fix CI failures
* Close no management issue when it is no longer relevant
* Report issue on initial lock failure
* Initial dependency locking
* Update .zuul.yaml
* Open an issue if no dependency management is found
* Automatic update of dependency pyyaml from 3.12 to 3.13
* Report broken build environment
* Automatic update of dependency pytest from 3.6.2 to 3.6.3
* Delete old branches from remote
* Automatic update of dependency pipenv from 2018.5.18 to 2018.7.1
* No need to install it anymore
* Notify about a rebase of pull requests
* Add support for silent bot
* Kebechet now reports issues on GitHub
* Introduce a wrapper for running pipenv
* Improvements in logic
* Remove pydocstyle from direct dependencies
* just minor wording tweaks
* renamed KEBECHET_CONFIGURATION to KEBECHET_CONFIGURATION_PATH all over the place
* Fix local setup
* some minor tweaks
* Version 1.0.0
* Do not allow pre-releases in updates
* Simplify code for with statement
* Update .zuul.yaml
* Install gcc-c++ for native builds
* using only zuul for releaseing to pypi
* Version 1.0.0-rc.5
* Explicitly update dependencies to their latest version
* Add a generic webhook for triggering builds
* Update __init__.py
* reparing 1.0.0-rc.4
* Update .zuul.yaml
* trigger
* fixing coala Errors
* added all we need for coala
* added the default coala configuration file
* added upload to pypi
* added initial zuul config
* added initial zuul config
* Update old PRs on top of the current master
* Monitor Jupyter Notebook for updates
* Fix syntax error in Ansible scripts
* Document Kebechet usage and design decisions
* implemented Dockerfile, buildconfig, cronjobconfig, configmap templates.
* updated username to reviewers in OWNERS
* Add support for requirements.txt
* Version 1.0.0-rc.2
* Explicitly name env variables to configure options
* Add missing pyyaml dependency
* Provide a CLI to run kebechet
* Add missing gitpython dependency
* Add a not for future generations
* Create OWNERS
* Remove approve label for auto approval
* fixed the semver
* added VSCode directory
* Add OpenShift templates
* Add configuration file for Thoth
* Implementation improvements - a first working implementation
* Update README.rst
* Initial project import

## Release 1.7.2 (2022-01-23T15:31:23)

- Add branch for if thoth configuration blocks advise submission
- check before trying to unshallow a repo
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- pop enabled config
- check before trying to unshallow a repo
- Enable TLS verification
- Unpin fasttext version from Pipfile
- Enable TLS verification in the sample default configuration

## Release 1.7.1 (2022-01-17T15:31:23)

- remove all references to get user
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment

## Release 1.7.0 (2022-01-13T16:23:54)

- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- use analysis-id 4 branch name to avoid collisions
- add documentation for advise issue
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- add link to manager doc above managers block in minimal yaml
- update version manager to act on PR merge with labels
- Suggest users to use Thamos CLI to create requirements file
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- check if update needs rebase

## Release 1.6.8 (2022-01-05T12:38:37)

- Fix the links to each manager's README
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- create_pr for manager class with default value for forknamespace
- use env variable for kebechets name
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel-8 environment

## Release 1.6.7 (2021-11-26T18:41:48)

- Fix format string reference to environment name
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- remove kebechet- prefix from version branch (used for image tag)

## Release 1.6.6 (2021-11-18T16:47:27)

- No computed changelog
- if no depth is passed fetch full history
- add kebechet- to all branch names

## Release 1.6.5 (2021-11-17T16:47:27)

- clean repo after using
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment

## Release 1.6.4 (2021-11-17T06:47:27)

- check if .git exists so that we don't catch all gitcommand exceptions (#909)
- if we have already cloned to dir, return repo from dir

## Release 1.6.3 (2021-11-16T06:47:27)

- :fire: patch the circuler import fix for keb version in utils
- reraise github server exception

## Release 1.6.2 (2021-11-15T06:47:27)

- Remove the maintainers section from .thoth.yaml
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- Track advise status using GitHub issue
- patch the fasttext version for build fix

## Release 1.6.1 (2021-11-09T06:47:27)

- add keb version to issue body
- :turtle: Support python 3.9 in kebechet dependency management
- use sphinx for Kebechet documentation

## Release 1.6.0 (2021-11-03T08:32:59)

- add triage/accepted labels to release issue template to prevent Prow from starting a traige
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- Add Goern, Harshad and Pep as approvers
- :bomb: use https based url in the pre-commit
- allow clone dir to be passed as environment variable
- use approvers section of OWNERS file as default maintainers
- do not report dependency manager exception on support (#878)
- add custom exception for known failure cases and open issues for failed manager
- change key value for getting results from advise endpoint
- set self.runtime_environment and use for all issue titles

## Release 1.5.5 (2021-10-14T18:00:50)

- add checks for num lines to avoid out-of-bounds exception
- patch read write method for changelog update
- checks for num lines to avoid out-of-bounds exception
- :turtle: patch read write method for changelog update
- Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- catch ssl errors as it is a networking issue

## Release 1.5.4 (2021-10-12T14:03:50)

- check if issue already exists
- create changelog file if it doesn't exist

## Release 1.5.3 (2021-10-11T20:43:58)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- add enabled flag to manager configuration
- don't require locked version for old deps
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- add checks for local installations and pkgs bundled by pipenv
- check for none indicating function failed
- create issue if no requirements found for runtime env
- log if issue creation is disabled

  ### Improvements

- make changelog not smart by default

- if PR already exists warn and continue

## Release 1.5.2 (2021-09-27T21:37:47)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment (#837)
- add KPostOffice to approvers
- only create one issue per exc per line
- Fix markdown format for table rows
- get relative path of overlay currently being updated for link

  ### Improvements

- Minor format improvements in the README

## Release 1.5.1 (2021-09-23T19:16:52)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- add link to repository which caused exception
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment
- :arrow_up: Automatic update of dependencies by Kebechet for the rhel:8 environment

  ### Bug Fixes

- :bug: fix some typos

- do not raise issue for conn error

## Release 1.5.0 (2021-09-15T16:02:53)

### Features

- add unregistered manager which adds thoth-config
- convert README from RST to MD
- add return statement

  ### Bug Fixes

- instead of opening issues in user repo open in thoth-station/support

- if requirements.txt does not exist it must be created

  ### Improvements

- updated README files to reflect current state of Kebechet

- pull runtime_environment directly from advise results

- removed unused -dev dependencies

  ### Other

- Format traceback with Python backtick code

## Release 1.4.1 (2021-08-18T16:49:22)

### Features

- Empty commit for a new release

## [1.0.0-rc.4] - 2018-Jun-25 - goern

### Added

Starting with this release we have a Zuul-CI pipeline that:

- lints on Pull Requrest and gate/merge
- uploads to pypi (test) on tag

  ## Release 1.0.1 (2020-06-05T11:15:40)

- Add repo for solver error classifier

- Correct template

- add pre-commit config

- added a 'tekton trigger tag_release pipeline issue'

- Add thoth-station/datasets

- Add version release for advise-reporter

- :pushpin: Automatic update of dependency pipenv from 2018.11.26 to 2020.5.28

- Consider app.py and wsgi.py as a source for version

- :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7

- :pushpin: Automatic update of dependency thamos from 0.10.1 to 0.10.2

- :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0

- :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6

- :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5

- kebechet should be capitalized
- :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
- Added repo
- Added repo
- Revert "Fix if automatic relocking PR exists"
- :pushpin: Automatic update of dependency thamos from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
- use source type enum
- remove metadata prefix
- Added update and version to slo
- :pushpin: Automatic update of dependency toml from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency semver from 2.10.0 to 2.10.1
- use metadata option when calling thamos advise
- Fixed coala errors
- Print version as info
- Print version as info
- Update README.rst
- Update README
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.7 to 0.2.9
- Fix test imports
- :pushpin: Automatic update of dependency pytest from 5.4.1 to 5.4.2
- Added sesheta as mainatianer in version manager
- Added source management
- fixed coala
- coala fix
- Comments on pr if modified pr found.
- :pushpin: Automatic update of dependency semver from 2.9.1 to 2.10.0
- Fix if automatic relocking pr exists
- :pushpin: Automatic update of dependency pylint from 2.5.1 to 2.5.2
- :pushpin: Automatic update of dependency pylint from 2.5.0 to 2.5.1
- :pushpin: Automatic update of dependency gitpython from 3.1.1 to 3.1.2
- :pushpin: Automatic dependency re-locking
- Fixed coala errors
- Added instruction for manual trigger and closses issue
- Added instruction for manual trigger and closses issue"
- :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
- :pushpin: Automatic update of dependency thamos from 0.9.4 to 0.10.0
- Changed image source to infra"
- :pushpin: Automatic update of dependency thamos from 0.9.3 to 0.9.4
- :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
- :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
- Updated name to kebechet
- :pushpin: Automatic update of dependency pylint from 2.4.4 to 2.5.0
- :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
- Updated template and workflow to use openshift image
- Changed template name to kebechet-job
- Added argo workflow and oc template
- :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
- Add SLO-reporter repo
- :pushpin: Automatic update of dependency thamos from 0.9.2 to 0.9.3
- Added cli endpoint envvar
- Add maintainer for thamos
- Changed liveness probe to 45mins.
- Coala fix
- Coala fix
- Fix parameters
- Fixed run-url cli error
- Fix job template
- :pushpin: Automatic update of dependency gitpython from 3.1.0 to 3.1.1
- Delete thoth_demo.yaml
- Added s2i notebook repos
- :pushpin: Automatic update of dependency thoth-common from 0.12.8 to 0.12.9
- :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.8
- :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
- :pushpin: Automatic update of dependency thamos from 0.9.1 to 0.9.2
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.6 to 0.2.7
- :pushpin: Automatic update of dependency thamos from 0.8.1 to 0.9.1
- :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.12.6
- Removed fstrings
- Fixed coala errors
- removed extra files
- Removed try catch
- Fixed syntax
- Addressed comments
- Added error handling in case version control is used
- Add support for advise-reporter
- Support for thoth unresolved-package-handler
- add maintainer for thoth-station/messaging
- :pushpin: Automatic update of dependency pyyaml from 5.3 to 3.13
- :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1
- :pushpin: Automatic update of dependency pytest from 5.3.5 to 5.4.0
- :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- Delete thoth_demo.yaml
- fixed coala
- fixed coala
- Check standard package in package.json
- fixed commits
- fixed messages
- Revert "Fixed messages and create initial lock commits"
- Fixed messages and create initial lock commits
- Changed namespace to thoth
- kebechet only uses thoth sourcemanagement
- removed pin
- Fixed dependencies
- Latest git python
- Fix cron job run
- :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
- New Maintainer
- fixed coala
- printin to log
- Closes release request if no change
- Adjust .thoth.yaml configuration file
- Handle \r\n
- A big step towards general AI
- Fixed lambda x
- :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
- Fixed ogr migration errors
- Fixed ogr migration errors
- Fixed ogr migration errors
- :pushpin: Automatic update of dependency requests from 2.22.0 to 2.23.0
- Fixed gitlab payload
- Supporting cron job run
- Added to requirement.txt
- Gitlab works with usernames
- Added custom errors
- Removed IGitt from depedencies
- coala fix
- Updated managers to use ogr methods
- removed event variable
- removed event variable
- fixed list branches expecting json
- Removed IGitt from manager base class
- added different id for gitlab
- Added logic for assigning to issue.
- Added logic for assigning to issue.
- Added alternate source management
- OGR Migration
- Now passing the whole payload to the managers.
- ogr changes
- Adding ogr replacement
- Fixed coala errors"
- Added event conditions to managers
- Saving parsed dict in parser
- Added url parse and resolved comments"
- Update thoth.yaml
- Update .thoth.yaml
- Added raising exceptions
- Added suggested changes
- Add thoth-station/s2i repository
- Support for thoth package-update-job
- Fixed coala errors
- Added payload parsing
- Webhook propagated to config.
- Change cli to recieve payload as string
- Removed nested dictionary
- Fixed typos
- Added sub command
- Removed demo yaml file
- Added manager back to iter
- changed if condn
- Fixed coala errors
- Reverted run method
- Fixed coala errors
- Use only slug
- temp close moved
- Run with managers from respective repos
- Introduce second instance of Kebechet
- :smiling_imp: added durandom_64fbc27e213f5a61c975ab29df94536b88f03270 to Kebechet
- Add new mantainer
- kebechet also support release of AICoE SrcOpsMetrics
- Support for AICoE SrcOpsMetrics
- Add new maintainer
- Happy new year!
- Add thoth-station/s2i-thoth repo
- Fix number attribute error
- support graph-backup-job with dependency updates.
- Add thoth-pybench to monitored repos
- Support for AICoE Fraud Detection
- Sort repositories based upon their dependencies
- updated templates with annotations
- Use the generic webhook for build trigger
- github ref point to master
- Fix permission issues
- use /tmp for a .cache directory
- Adjust Pipenv cache in the correct place
- Adjust cache location when run in the cluster due to perms
- :green_heart: added Thoth's Stub-API Repository
- :sparkles: added an annotation to each object created, so that we know the version of the template that created the object
- Enable version manager for AICoE/prometheus-api-client-python
- Migrate to pytest
- Add docstrings to satisfy coala linter.
- Make `v` optional in tag when matching version
- Support for AICoE ludus
- Development packages are not mandatory in Pipfile
- added the AICoE repos
- Add thoth-station/messaging to monitored repos
- :lock: relocked
- Update README.rst
- Fix wrong slug for the sesheta repo
- Do not monitor conu repo
- Add package-analyzer to monitored repos
- Update templates and cli options
- Propagate deployment name for sentry environment
- Add build-analyzers to monitored repos
- Use UBI8 as base image
- Small changes to env names
- Remove osiris and osiris observer
- Fix list in YAML
- Update READMEs
- Update READMEs
- Coala formatting
- Combine configuration files
- Addressing comments
- Whoops
- Coala formatting
- Review suggestions
- Trigger Sesheta
- Trigger Sesheta
- Add "Finalize version" to accepted titles
- Be consistent with issue title case
- Make maintainers case insensitive
- CronJobs are now in apiVersion v1beta1
- Changed env variable names
- Forgot to save app.sh
- Adding subcommand should keep original functionality of cronjob
- Changes based on suggestions
- Update buildConfig-template.yaml
- Fixed coala formatting issues
- Fixed origin format
- Add @harshad16 to maintainers of thoth-lab
- Removed test values in job template
- Removed test values in job template
- Forgot to clone repo before doing provenance check
- Back to docker
- cli
- Wrong name for subcommand
- app.sh executable
- Update Pipfile.lock
- Remove result managers
- Recombined manager but has two distinct logical branches
- Single missing quotation
- Merge run-url
- git tokens are now in secrets
- Subcommands
- Split thoth managers to remove waiting
- Forgot a line
- Changes based on review
- Update to work with s2i
- Updated job template
- Made a services class
- Coala formatting
- Forgot to save
- Implemented suggestions
- Configure starting deadline seconds to large number
- Changed to use environment variable
- Creation of kebechet job template
- Missing period
- Manual format
- Auto format
- GitLab url run
- Manager runs for GitHub
- First commit
- Add invectio for management
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- Add CermakM to list of thoth-lab maintainers
- Update based on suggestions
- Updated based on suggestions
- Added thamos to Pipfile for new managers
- Updated README
- Logging info as well as auto retrying on Thamos failures
- Auto format
- Remove completed TODOs
- Provenance manager (basic) complete
- Labels were not being applied
- Automatically opens issues if thoth adviser returns error
- Updated readme with thamos configuration example
- Removed _advise_wrap in anticpation of thamos.lib.advise_here()
- Changed name to be more specific
- Changed README and removed unnecessary code that was copied over
- advise and write have been seperated so that if result is error an issue is opened
- Forgot to included init that makes manager accesible
- Basic thoth manager
- Version manager searches for **about**.py as well
- :lock: relocked
- Add Francesco to maintainers section of thoth-storages
- Use emojis in commit messages not in pull-request titles
- :sparkles: now using a bit of gitmoji
- Add Thoth's configuration file
- Do not forget to install thoth-common
- 🔥hotfixing the trailing space...
- that part of the webhook url is not required
- Use safe_load() instead of load()
- Use safe_load() instead of load()
- Kill Kebechet after 2 hours if it was not able compute results
- Fix coala warning
- Use Thoth's init_logging routine
- Do not use update manager in graph-sync-scheduler
- added graph-sync-scheduler to configuration file
- Add init-job to monitored repos
- It's already 2019
- Add build-watcher to monitored repos
- Add @CermakM to maintainers for osiris
- Add osiris and osiris build-observer
- Add operators to monitored repos
- Add thoth-python to monitored repos
- Add long description for PyPI
- Remove markers from requirements file
- Set env variables to suppress pipenv emojis
- use thoth-* jobs in pipeline
- added metrics-exports
- Monitor AICoE/prometheus-flatliner repository
- Monitor Thoth's management API
- Lower log level when something goes wrong when running Pipenv
- Correctly fix attribute error
- Fix attribute error
- Propagate issue body to pull request on version updates
- Add amun-client to monitored repos
- Fix wrong manager name
- Fix wrong value configuration
- Pipenv has been fixed upstream
- Fix version manager
- Initial dependency lock
- Do not forget to install sentry-sdk
- Let Kebechet do the locking
- Fixes to make Kebechet work in deployment
- Add Sentry support
- Distinguish pip and Pipenv cache
- New Pipenv does not respect PIPENV_CACHE_DIR
- A temporary fix to avoid recent Pipenv issues
- Add Amun API repository for monitoring
- Be case insensitive with issue titles triggering new versions
- Fix repo name
- Monitor AICoE/log-anomaly-detector for updates
- put some more labels in, adjusted successfulJobsHistoryLimit
- hotfix
- added thamos project
- Fix computing of changelog
- Log activities done during changelog computation
- Enable change log files on Thoth repos
- Place related before reported changelog
- Fix initial lock issues
- added requirements-dev.txt compatibility
- Update .zuul.yaml
- Add CVE update job to monitored repos
- An array is expected
- Be consistent with git push
- Configure git on repo clone
- Fix commit
- Fix handling of versions when Pipfile is used
- Fix key to packages in Pipfile
- Expand configuration to start using pipfile-requirements
- Fix f-string
- using an obfuscated URL
- now with a build trigger in the post pipeline
- now with a build trigger in the post pipeline
- Do not cache images in build config
- Version can be stated in version.py
- Do calendar release with full year
- Compute changelog on releases
- Initial dependency lock
- Remove Pipfile.lock to get initial lock
- Print Kebechet version on startup
- Fix user assignment to issue
- new templates
- added srcops-testing
- Introduce Pipfile requirements.txt manager
- Assign users to the release issue
- Use related instead of fixes
- Do not tag commits
- Fix tagging of commit
- Fix version handling issues
- Another attempt to fix requests issue
- Make sure IGitt does not propagate verify arguments
- Try to fix IGitt requests handling
- Remove duplicit requests
- Make Kebechet compatible with recent IGitt release
- Use dev release of IGitt
- Install IGitt from git repo correctly
- Fix IGitt requirement
- Install IGitt from repository
- Do not forget to install semver
- Use IGitt directly from git repository for now
- Initial dependency lock
- Let Kebechet relock dependencies with semver lib
- Implement semver and calver for automated releases
- Inspect also version.py for version information
- Minor fixes in README file
- State how version manager looks for version
- Add user-cont/conu for managing updates
- Fix typo in docs
- Update README.rst
- Fix typo in docs
- Remove unused import
- Adjusted based on review comments
- Last documentation bits
- Document managers section
- Update documentation for version manager
- Update documentation for update manager
- Update documentation for info manager
- Create a soft copy for YAML links
- Let only maintainers release new packages
- Add version manager for Thoth repos
- Issue handling and minor fixes
- Fix missing packages
- Push also tags
- Implement version change logic
- Introduce version manager for automatic version releases
- Remove unused arguments
- Move info messages into correct module
- Introduce manager configuration entry
- Initial dependency lock
- Provide README files for managers
- Place all managers into their own modules
- Pin down gitpython because of IGitt
- Ask Kebechet for initial lock
- Fix a typo in attribute name
- Add Sesheta to monitored repos
- Adjust template labels
- Use description instead of non-existing body attribute
- Report end run for config entry
- Fix another subscription error
- Fix typo
- Fix key error exception
- Fix token expanding from env vars
- Install sources directly from GitHub repo
- GitLab support fixes and extensions
- Add GitLab support
- Utilize repo cloning
- Fix bound method call
- No need to print context in verbose mode
- Hide token in logs
- Fix calling checkout
- We have to explicitly install dependency version
- Install Kebechet from git repo for now
- Initial dependency lock
- Delete Pipfile.lock for relocking dependencies
- Fix hash computation
- Run info manager on thoth-station repos
- Introduce managers abstraction
- Checkout to master after changes
- Fix bound method call
- Close initial lock issue when no longer relevant
- Code refactoring
- Fix CI failures
- Close no management issue when it is no longer relevant
- Report issue on initial lock failure
- Initial dependency locking
- Update .zuul.yaml
- Open an issue if no dependency management is found
- Automatic update of dependency pyyaml from 3.12 to 3.13
- Report broken build environment
- Automatic update of dependency pytest from 3.6.2 to 3.6.3
- Delete old branches from remote
- Automatic update of dependency pipenv from 2018.5.18 to 2018.7.1
- No need to install it anymore
- Notify about a rebase of pull requests
- Add support for silent bot
- Kebechet now reports issues on GitHub
- Introduce a wrapper for running pipenv
- Improvements in logic
- Remove pydocstyle from direct dependencies
- just minor wording tweaks
- renamed KEBECHET_CONFIGURATION to KEBECHET_CONFIGURATION_PATH all over the place
- Fix local setup
- some minor tweaks

## Release 1.0.2 (2020-08-27T06:36:58)

- Fix GitHub templates location
- Fix formatting when smart changelogs are created
- Enable smart logs by default
- Add release templates to let Kebechet release itself
- Fixed added context to multiple version string error.
- :pushpin: Automatic update of dependency pytest-cov from 2.10.0 to 2.10.1 (#490)
- :pushpin: Automatic update of dependency thamos from 0.11.0 to 0.11.1 (#489)
- :pushpin: Automatic update of dependency thoth-common from 0.16.0 to 0.16.1 (#488)
- Document CHANGELOG.md file generation and assignees (#487)
- Minor fix
- ThothGlyphException import added
- return statement added in Glyph exception
- Extra line removed
- String concatenation fix
- Minor fix
- Updated Version Manager's README to include Glyph's specifications
- Pipfile updated, Glyph's exceptions handled
- Optionally generate intelligent release logs using Glyph
- return statement added in Glyph exception
- Extra line removed
- :pushpin: Automatic update of dependency thamos from 0.10.6 to 0.11.0 (#486)
- String concatenation fix
- Minor fix
- Updated Version Manager's README to include Glyph's specifications
- Pipfile updated, Glyph's exceptions handled
- Optionally generate intelligent release logs using Glyph
- :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#482)
- :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#481)
- :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0 (#480)
- Formatted commit messages with backticks. (#477)
- :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#476)
- :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#475)
- :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2 (#474)
- Relock fix (#468)
- :pushpin: Automatic update of dependency gitpython from 3.1.3 to 3.1.7 (#471)
- :pushpin: Automatic update of dependency thamos from 0.10.5 to 0.10.6 (#472)
- Precommit fixes (#470)
- Cronjob cleanup-job can be archived
- :pushpin: Automatic update of dependency thoth-common from 0.13.13 to 0.14.1
- keep the application up-to-date with pre-commit
- Remove thoth-station/package-analyzer
- Update version manager documentation
- Add CodeQL security scanning (#425)
- Remove build-analyzers
- Update OWNERS
- Remove graph-sync-scheduler
- Update OWNERS
- Remove result-api and workload-operator
- :pushpin: Automatic update of dependency thoth-common from 0.13.12 to 0.13.13
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.9 to 0.3.0
- Limit version release log to 300
- keep wf for SLI
- Make config parsing more safe
- Piplock using 2018
- Pin older version of Pipenv during the build
- :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
- Added python 3.8
- New piplock
- :pushpin: Automatic update of dependency thoth-common from 0.13.11 to 0.13.12
- Fix attribute error while parsing YAML
- Fix if maintainers are not stated in OWNERS file
- Change logger to info to monitor on cluster
- :pushpin: Automatic update of dependency pytest-timeout from 1.4.0 to 1.4.1
- :pushpin: Automatic update of dependency semver from 2.10.1 to 2.10.2
- :pushpin: Automatic update of dependency pytest-cov from 2.9.0 to 2.10.0
- :pushpin: Automatic update of dependency pytest-timeout from 1.3.4 to 1.4.0
- Remove old member
- fresh piplock
- str cast moved to return
- Typo fix
- Coala errors
- Perform manual update of dependencies
- Release of version 1.0.1
- Add repo for solver error classifier
- Correct template
- add pre-commit config
- added a 'tekton trigger tag_release pipeline issue'
- Add thoth-station/datasets
- Add version release for advise-reporter
- :pushpin: Automatic update of dependency pipenv from 2018.11.26 to 2020.5.28
- Consider app.py and wsgi.py as a source for version
- :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
- :pushpin: Automatic update of dependency thamos from 0.10.1 to 0.10.2
- :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0
- :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
- :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
- kebechet should be capitalized
- :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
- Added repo
- Added repo
- Revert "Fix if automatic relocking PR exists"
- :pushpin: Automatic update of dependency thamos from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
- use source type enum
- remove metadata prefix
- Added update and version to slo
- :pushpin: Automatic update of dependency toml from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency semver from 2.10.0 to 2.10.1
- use metadata option when calling thamos advise
- Fixed coala errors
- Print version as info
- Print version as info
- Update README.rst
- Update README
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.7 to 0.2.9
- Fix test imports
- :pushpin: Automatic update of dependency pytest from 5.4.1 to 5.4.2
- Added sesheta as mainatianer in version manager
- Added source management
- fixed coala
- coala fix
- Comments on pr if modified pr found.
- :pushpin: Automatic update of dependency semver from 2.9.1 to 2.10.0
- Fix if automatic relocking pr exists
- :pushpin: Automatic update of dependency pylint from 2.5.1 to 2.5.2
- :pushpin: Automatic update of dependency pylint from 2.5.0 to 2.5.1
- :pushpin: Automatic update of dependency gitpython from 3.1.1 to 3.1.2
- :pushpin: Automatic dependency re-locking
- Fixed coala errors
- Added instruction for manual trigger and closses issue
- Added instruction for manual trigger and closses issue"
- :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
- :pushpin: Automatic update of dependency thamos from 0.9.4 to 0.10.0
- Changed image source to infra"
- :pushpin: Automatic update of dependency thamos from 0.9.3 to 0.9.4
- :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
- :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
- Updated name to kebechet
- :pushpin: Automatic update of dependency pylint from 2.4.4 to 2.5.0
- :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
- Updated template and workflow to use openshift image
- Changed template name to kebechet-job
- Added argo workflow and oc template
- :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
- Add SLO-reporter repo
- :pushpin: Automatic update of dependency thamos from 0.9.2 to 0.9.3
- Added cli endpoint envvar
- Add maintainer for thamos
- Changed liveness probe to 45mins.
- Coala fix
- Coala fix
- Fix parameters
- Fixed run-url cli error
- Fix job template
- :pushpin: Automatic update of dependency gitpython from 3.1.0 to 3.1.1
- Delete thoth_demo.yaml
- Added s2i notebook repos
- :pushpin: Automatic update of dependency thoth-common from 0.12.8 to 0.12.9
- :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.8
- :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
- :pushpin: Automatic update of dependency thamos from 0.9.1 to 0.9.2
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.6 to 0.2.7
- :pushpin: Automatic update of dependency thamos from 0.8.1 to 0.9.1
- :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.12.6
- Removed fstrings
- Fixed coala errors
- removed extra files
- Removed try catch
- Fixed syntax
- Addressed comments
- Added error handling in case version control is used
- Add support for advise-reporter
- Support for thoth unresolved-package-handler
- add maintainer for thoth-station/messaging
- :pushpin: Automatic update of dependency pyyaml from 5.3 to 3.13
- :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1
- :pushpin: Automatic update of dependency pytest from 5.3.5 to 5.4.0
- :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- Delete thoth_demo.yaml
- fixed coala
- fixed coala
- Check standard package in package.json
- fixed commits
- fixed messages
- Revert "Fixed messages and create initial lock commits"
- Fixed messages and create initial lock commits
- Changed namespace to thoth
- kebechet only uses thoth sourcemanagement
- removed pin
- Fixed dependencies
- Latest git python
- Fix cron job run
- :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
- New Maintainer
- fixed coala
- printin to log
- Closes release request if no change
- Adjust .thoth.yaml configuration file
- Handle \r\n
- A big step towards general AI
- Fixed lambda x
- :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
- Fixed ogr migration errors
- Fixed ogr migration errors
- Fixed ogr migration errors
- :pushpin: Automatic update of dependency requests from 2.22.0 to 2.23.0
- Fixed gitlab payload
- Supporting cron job run
- Added to requirement.txt
- Gitlab works with usernames
- Added custom errors
- Removed IGitt from depedencies
- coala fix
- Updated managers to use ogr methods
- removed event variable
- removed event variable
- fixed list branches expecting json
- Removed IGitt from manager base class
- added different id for gitlab
- Added logic for assigning to issue.
- Added logic for assigning to issue.
- Added alternate source management
- OGR Migration
- Now passing the whole payload to the managers.
- ogr changes
- Adding ogr replacement
- Fixed coala errors"
- Added event conditions to managers
- Saving parsed dict in parser
- Added url parse and resolved comments"
- Update thoth.yaml
- Update .thoth.yaml
- Added raising exceptions
- Added suggested changes
- Add thoth-station/s2i repository
- Support for thoth package-update-job
- Fixed coala errors
- Added payload parsing
- Webhook propagated to config.
- Change cli to recieve payload as string
- Removed nested dictionary
- Fixed typos
- Added sub command
- Removed demo yaml file
- Added manager back to iter
- changed if condn
- Fixed coala errors
- Reverted run method
- Fixed coala errors
- Use only slug
- temp close moved
- Run with managers from respective repos
- Introduce second instance of Kebechet
- :smiling_imp: added durandom_64fbc27e213f5a61c975ab29df94536b88f03270 to Kebechet
- Add new mantainer
- kebechet also support release of AICoE SrcOpsMetrics
- Support for AICoE SrcOpsMetrics
- Add new maintainer
- Happy new year!
- Add thoth-station/s2i-thoth repo
- Fix number attribute error
- support graph-backup-job with dependency updates.
- Add thoth-pybench to monitored repos
- Support for AICoE Fraud Detection
- Sort repositories based upon their dependencies
- updated templates with annotations
- Use the generic webhook for build trigger
- github ref point to master
- Fix permission issues
- use /tmp for a .cache directory
- Adjust Pipenv cache in the correct place
- Adjust cache location when run in the cluster due to perms
- :green_heart: added Thoth's Stub-API Repository
- :sparkles: added an annotation to each object created, so that we know the version of the template that created the object
- Enable version manager for AICoE/prometheus-api-client-python
- Migrate to pytest
- Add docstrings to satisfy coala linter.
- Make `v` optional in tag when matching version
- Support for AICoE ludus
- Development packages are not mandatory in Pipfile
- added the AICoE repos
- Add thoth-station/messaging to monitored repos
- :lock: relocked
- Update README.rst
- Fix wrong slug for the sesheta repo
- Do not monitor conu repo
- Add package-analyzer to monitored repos
- Update templates and cli options
- Propagate deployment name for sentry environment
- Add build-analyzers to monitored repos
- Use UBI8 as base image
- Small changes to env names
- Remove osiris and osiris observer
- Fix list in YAML
- Update READMEs
- Update READMEs
- Coala formatting
- Combine configuration files
- Addressing comments
- Whoops
- Coala formatting
- Review suggestions
- Trigger Sesheta
- Trigger Sesheta
- Add "Finalize version" to accepted titles
- Be consistent with issue title case
- Make maintainers case insensitive
- CronJobs are now in apiVersion v1beta1
- Changed env variable names
- Forgot to save app.sh
- Adding subcommand should keep original functionality of cronjob
- Changes based on suggestions
- Update buildConfig-template.yaml
- Fixed coala formatting issues
- Fixed origin format
- Add @harshad16 to maintainers of thoth-lab
- Removed test values in job template
- Removed test values in job template
- Forgot to clone repo before doing provenance check
- Back to docker
- cli
- Wrong name for subcommand
- app.sh executable
- Update Pipfile.lock
- Remove result managers
- Recombined manager but has two distinct logical branches
- Single missing quotation
- Merge run-url
- git tokens are now in secrets
- Subcommands
- Split thoth managers to remove waiting
- Forgot a line
- Changes based on review
- Update to work with s2i
- Updated job template
- Made a services class
- Coala formatting
- Forgot to save
- Implemented suggestions
- Configure starting deadline seconds to large number
- Changed to use environment variable
- Creation of kebechet job template
- Missing period
- Manual format
- Auto format
- GitLab url run
- Manager runs for GitHub
- First commit
- Add invectio for management
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- Add CermakM to list of thoth-lab maintainers
- Update based on suggestions
- Updated based on suggestions
- Added thamos to Pipfile for new managers
- Updated README
- Logging info as well as auto retrying on Thamos failures
- Auto format
- Remove completed TODOs
- Provenance manager (basic) complete
- Labels were not being applied
- Automatically opens issues if thoth adviser returns error
- Updated readme with thamos configuration example
- Removed _advise_wrap in anticpation of thamos.lib.advise_here()
- Changed name to be more specific
- Changed README and removed unnecessary code that was copied over
- advise and write have been seperated so that if result is error an issue is opened
- Forgot to included init that makes manager accesible
- Basic thoth manager
- Version manager searches for **about**.py as well
- :lock: relocked
- Add Francesco to maintainers section of thoth-storages
- Use emojis in commit messages not in pull-request titles
- :sparkles: now using a bit of gitmoji
- Add Thoth's configuration file
- Do not forget to install thoth-common
- 🔥hotfixing the trailing space...
- that part of the webhook url is not required
- Use safe_load() instead of load()
- Use safe_load() instead of load()
- Kill Kebechet after 2 hours if it was not able compute results
- Fix coala warning
- Use Thoth's init_logging routine
- Do not use update manager in graph-sync-scheduler
- added graph-sync-scheduler to configuration file
- Add init-job to monitored repos
- It's already 2019
- Add build-watcher to monitored repos
- Add @CermakM to maintainers for osiris
- Add osiris and osiris build-observer
- Add operators to monitored repos
- Add thoth-python to monitored repos
- Add long description for PyPI
- Remove markers from requirements file
- Set env variables to suppress pipenv emojis
- use thoth-* jobs in pipeline
- added metrics-exports
- Monitor AICoE/prometheus-flatliner repository
- Monitor Thoth's management API
- Lower log level when something goes wrong when running Pipenv
- Correctly fix attribute error
- Fix attribute error
- Propagate issue body to pull request on version updates
- Add amun-client to monitored repos
- Fix wrong manager name
- Fix wrong value configuration
- Pipenv has been fixed upstream
- Fix version manager
- Initial dependency lock
- Do not forget to install sentry-sdk
- Let Kebechet do the locking
- Fixes to make Kebechet work in deployment
- Add Sentry support
- Distinguish pip and Pipenv cache
- New Pipenv does not respect PIPENV_CACHE_DIR
- A temporary fix to avoid recent Pipenv issues
- Add Amun API repository for monitoring
- Be case insensitive with issue titles triggering new versions
- Fix repo name
- Monitor AICoE/log-anomaly-detector for updates
- put some more labels in, adjusted successfulJobsHistoryLimit
- hotfix
- added thamos project
- Fix computing of changelog
- Log activities done during changelog computation
- Enable change log files on Thoth repos
- Place related before reported changelog
- Fix initial lock issues
- added requirements-dev.txt compatibility
- Update .zuul.yaml
- Add CVE update job to monitored repos
- An array is expected
- Be consistent with git push
- Configure git on repo clone
- Fix commit
- Fix handling of versions when Pipfile is used
- Fix key to packages in Pipfile
- Expand configuration to start using pipfile-requirements
- Fix f-string
- using an obfuscated URL
- now with a build trigger in the post pipeline
- now with a build trigger in the post pipeline
- Do not cache images in build config
- Version can be stated in version.py
- Do calendar release with full year
- Compute changelog on releases
- Initial dependency lock
- Remove Pipfile.lock to get initial lock
- Print Kebechet version on startup
- Fix user assignment to issue
- new templates
- added srcops-testing
- Introduce Pipfile requirements.txt manager
- Assign users to the release issue
- Use related instead of fixes
- Do not tag commits
- Add user-cont/conu for managing updates

## Release 1.0.3 (2020-08-27T17:30:24)

### Features

- Release of version 1.0.2
- Fix GitHub templates location
- Fix formatting when smart changelogs are created
- Enable smart logs by default
- Add release templates to let Kebechet release itself
- Fixed added context to multiple version string error.
- ThothGlyphException import added
- return statement added in Glyph exception
- Updated Version Manager's README to include Glyph's specifications
- Pipfile updated, Glyph's exceptions handled
- Optionally generate intelligent release logs using Glyph
- return statement added in Glyph exception
- Updated Version Manager's README to include Glyph's specifications
- Pipfile updated, Glyph's exceptions handled
- Optionally generate intelligent release logs using Glyph
- Formatted commit messages with backticks. (#477)
- Cronjob cleanup-job can be archived
- keep the application up-to-date with pre-commit
- Remove thoth-station/package-analyzer
- Update version manager documentation
- Add CodeQL security scanning (#425)
- Remove build-analyzers
- Update OWNERS
- Remove graph-sync-scheduler
- Update OWNERS
- Limit version release log to 300
- keep wf for SLI
- Piplock using 2018
- Pin older version of Pipenv during the build
- Added python 3.8
- New piplock
- Change logger to info to monitor on cluster
- Remove old member
- fresh piplock
- str cast moved to return
- Coala errors
- Perform manual update of dependencies
- Release of version 1.0.1
- Add repo for solver error classifier
- Correct template
- add pre-commit config
- added a 'tekton trigger tag_release pipeline issue'
- Add thoth-station/datasets
- Add version release for advise-reporter
- Consider app.py and wsgi.py as a source for version
- kebechet should be capitalized
- Added repo
- Added repo
- Revert "Fix if automatic relocking PR exists"
- Added update and version to slo
- use metadata option when calling thamos advise
- Fixed coala errors
- Print version as info
- Print version as info
- Update README.rst
- Update README
- Added sesheta as mainatianer in version manager
- Added source management
- Comments on pr if modified pr found.
- Fix if automatic relocking pr exists
- :pushpin: Automatic dependency re-locking
- Fixed coala errors
- Changed image source to infra"
- Updated name to kebechet
- Changed template name to kebechet-job
- Added argo workflow and oc template
- Add SLO-reporter repo
- Added cli endpoint envvar
- Add maintainer for thamos
- Changed liveness probe to 45mins.
- Fix parameters
- Fixed run-url cli error
- Fix job template
- Delete thoth_demo.yaml
- Added s2i notebook repos
- Removed fstrings
- Fixed coala errors
- Removed try catch
- Fixed syntax
- Addressed comments
- Add support for advise-reporter
- Support for thoth unresolved-package-handler
- add maintainer for thoth-station/messaging
- Delete thoth_demo.yaml
- Revert "Fixed messages and create initial lock commits"
- Fixed messages and create initial lock commits
- Changed namespace to thoth
- Fixed dependencies
- Latest git python
- Fix cron job run
- New Maintainer
- printin to log
- Closes release request if no change
- Adjust .thoth.yaml configuration file
- Handle \r\n
- A big step towards general AI
- Fixed lambda x
- Fixed ogr migration errors
- Fixed ogr migration errors
- Fixed ogr migration errors
- Fixed gitlab payload
- Supporting cron job run
- Added to requirement.txt
- Gitlab works with usernames
- Added custom errors
- Removed IGitt from depedencies
- added different id for gitlab
- Added logic for assigning to issue.
- Added logic for assigning to issue.
- Added alternate source management
- OGR Migration
- Now passing the whole payload to the managers.
- ogr changes
- Adding ogr replacement
- Fixed coala errors"
- Added event conditions to managers
- Saving parsed dict in parser
- Update thoth.yaml
- Update .thoth.yaml
- Added raising exceptions
- Added suggested changes
- Add thoth-station/s2i repository
- Support for thoth package-update-job
- Fixed coala errors
- Added payload parsing
- Webhook propagated to config.
- Change cli to recieve payload as string
- Removed nested dictionary
- Added sub command
- Removed demo yaml file
- Added manager back to iter
- changed if condn
- Fixed coala errors
- Fixed coala errors
- Use only slug
- temp close moved
- Run with managers from respective repos
- Introduce second instance of Kebechet
- :smiling_imp: added durandom_64fbc27e213f5a61c975ab29df94536b88f03270 to Kebechet
- Add new mantainer
- kebechet also support release of AICoE SrcOpsMetrics
- Support for AICoE SrcOpsMetrics
- Add new maintainer
- Happy new year!
- Add thoth-station/s2i-thoth repo
- Fix number attribute error
- support graph-backup-job with dependency updates.
- Add thoth-pybench to monitored repos
- Support for AICoE Fraud Detection
- Sort repositories based upon their dependencies
- updated templates with annotations
- Use the generic webhook for build trigger
- github ref point to master
- Fix permission issues
- Adjust Pipenv cache in the correct place
- :green_heart: added Thoth's Stub-API Repository
- Enable version manager for AICoE/prometheus-api-client-python
- Migrate to pytest
- Add docstrings to satisfy coala linter.
- Make `v` optional in tag when matching version
- Support for AICoE ludus
- Development packages are not mandatory in Pipfile
- added the AICoE repos
- Add thoth-station/messaging to monitored repos
- :lock: relocked
- Update README.rst
- Do not monitor conu repo
- Add package-analyzer to monitored repos
- Update templates and cli options
- Propagate deployment name for sentry environment
- Add build-analyzers to monitored repos
- Use UBI8 as base image
- Small changes to env names
- Fix list in YAML
- Update READMEs
- Update READMEs
- Coala formatting
- Combine configuration files
- Addressing comments
- Whoops
- Coala formatting
- Review suggestions
- Trigger Sesheta
- Trigger Sesheta
- Add "Finalize version" to accepted titles
- Be consistent with issue title case
- Make maintainers case insensitive
- CronJobs are now in apiVersion v1beta1
- Forgot to save app.sh
- Adding subcommand should keep original functionality of cronjob
- Changes based on suggestions
- Update buildConfig-template.yaml
- Fixed coala formatting issues
- Fixed origin format
- Add @harshad16 to maintainers of thoth-lab
- Forgot to clone repo before doing provenance check
- Back to docker
- cli
- Wrong name for subcommand
- app.sh executable
- Update Pipfile.lock
- Remove result managers
- Recombined manager but has two distinct logical branches
- Single missing quotation
- Merge run-url
- git tokens are now in secrets
- Subcommands
- Split thoth managers to remove waiting
- Forgot a line
- Changes based on review
- Update to work with s2i
- Updated job template
- Made a services class
- Coala formatting
- Forgot to save
- Implemented suggestions
- Configure starting deadline seconds to large number
- Creation of kebechet job template
- Missing period
- Manual format
- Auto format
- GitLab url run
- Manager runs for GitHub
- First commit
- Add invectio for management
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- :sparkles: using the new trigger-build zuul job
- Add CermakM to list of thoth-lab maintainers
- Update based on suggestions
- Updated based on suggestions
- Added thamos to Pipfile for new managers
- Updated README
- Logging info as well as auto retrying on Thamos failures
- Auto format
- Remove completed TODOs
- Provenance manager (basic) complete
- Labels were not being applied
- Updated readme with thamos configuration example
- Removed _advise_wrap in anticpation of thamos.lib.advise_here()
- Changed name to be more specific
- Forgot to included init that makes manager accesible
- Basic thoth manager
- Version manager searches for **about**.py as well
- :lock: relocked
- Add Francesco to maintainers section of thoth-storages
- Add Thoth's configuration file
- Do not forget to install thoth-common
- 🔥hotfixing the trailing space...
- that part of the webhook url is not required
- Use safe_load() instead of load()
- Use safe_load() instead of load()
- Fix coala warning
- Use Thoth's init_logging routine
- Do not use update manager in graph-sync-scheduler
- added graph-sync-scheduler to configuration file
- Add init-job to monitored repos
- It's already 2019
- Add build-watcher to monitored repos
- Add @CermakM to maintainers for osiris
- Add operators to monitored repos
- Add thoth-python to monitored repos
- Add long description for PyPI
- Remove markers from requirements file
- Set env variables to suppress pipenv emojis
- added metrics-exports
- Monitor AICoE/prometheus-flatliner repository
- Monitor Thoth's management API
- Fix attribute error
- Add amun-client to monitored repos
- Fix version manager
- Initial dependency lock
- Do not forget to install sentry-sdk
- Let Kebechet do the locking
- Fixes to make Kebechet work in deployment
- Add Sentry support
- Add Amun API repository for monitoring
- Be case insensitive with issue titles triggering new versions
- Fix repo name
- Monitor AICoE/log-anomaly-detector for updates
- hotfix
- added thamos project
- Fix computing of changelog
- Log activities done during changelog computation
- Enable change log files on Thoth repos
- Place related before reported changelog
- Fix initial lock issues
- added requirements-dev.txt compatibility
- Update .zuul.yaml
- Add CVE update job to monitored repos
- An array is expected
- Be consistent with git push
- Configure git on repo clone
- Fix commit
- Fix key to packages in Pipfile
- Expand configuration to start using pipfile-requirements
- Fix f-string
- using an obfuscated URL
- now with a build trigger in the post pipeline
- now with a build trigger in the post pipeline
- Do not cache images in build config
- Version can be stated in version.py
- Do calendar release with full year
- Compute changelog on releases
- Initial dependency lock
- Remove Pipfile.lock to get initial lock
- Print Kebechet version on startup
- Fix user assignment to issue
- new templates
- added srcops-testing
- Introduce Pipfile requirements.txt manager
- Assign users to the release issue
- Do not tag commits
- Fix tagging of commit
- Fix version handling issues
- Remove duplicit requests
- Make Kebechet compatible with recent IGitt release
- Use dev release of IGitt
- Install IGitt from git repo correctly
- Fix IGitt requirement
- Install IGitt from repository
- Do not forget to install semver
- Use IGitt directly from git repository for now
- Initial dependency lock
- Let Kebechet relock dependencies with semver lib
- Inspect also version.py for version information
- State how version manager looks for version
- Add user-cont/conu for managing updates
- Update README.rst
- Remove unused import
- Adjusted based on review comments
- Last documentation bits
- Document managers section
- Update documentation for version manager
- Update documentation for update manager
- Create a soft copy for YAML links
- Let only maintainers release new packages
- Add version manager for Thoth repos
- Fix missing packages
- Push also tags
- Implement version change logic
- Introduce version manager for automatic version releases
- Remove unused arguments
- Introduce manager configuration entry
- Initial dependency lock
- Provide README files for managers
- Place all managers into their own modules
- Pin down gitpython because of IGitt
- Ask Kebechet for initial lock
- Add Sesheta to monitored repos
- Adjust template labels
- Use description instead of non-existing body attribute
- Fix another subscription error
- Fix token expanding from env vars
- Install sources directly from GitHub repo
- GitLab support fixes and extensions
- Add GitLab support
- Utilize repo cloning
- Fix bound method call
- No need to print context in verbose mode
- Hide token in logs
- Fix calling checkout
- We have to explicitly install dependency version
- Install Kebechet from git repo for now
- Initial dependency lock
- Delete Pipfile.lock for relocking dependencies
- Fix hash computation
- Run info manager on thoth-station repos
- Introduce managers abstraction
- Fix bound method call
- Fix CI failures
- Initial dependency locking
- Update .zuul.yaml
- Open an issue if no dependency management is found
- Report broken build environment
- Delete old branches from remote
- Notify about a rebase of pull requests
- Add support for silent bot
- Kebechet now reports issues on GitHub
- Introduce a wrapper for running pipenv
- Improvements in logic
- Remove pydocstyle from direct dependencies
- renamed KEBECHET_CONFIGURATION to KEBECHET_CONFIGURATION_PATH all over the place
- Fix local setup
- Version 1.0.0
- Do not allow pre-releases in updates
- Update .zuul.yaml
- Install gcc-c++ for native builds
- using only zuul for releaseing to pypi
- Version 1.0.0-rc.5
- Explicitly update dependencies to their latest version
- Add a generic webhook for triggering builds
- Update **init**.py
- reparing 1.0.0-rc.4
- Update .zuul.yaml
- trigger
- added the default coala configuration file
- added upload to pypi
- added initial zuul config
- added initial zuul config
- Update old PRs on top of the current master
- Monitor Jupyter Notebook for updates
- implemented Dockerfile, buildconfig, cronjobconfig, configmap templates.
- updated username to reviewers in OWNERS
- Add support for requirements.txt
- Version 1.0.0-rc.2
- Explicitly name env variables to configure options
- Add missing pyyaml dependency
- Provide a CLI to run kebechet
- Add missing gitpython dependency
- Add a not for future generations
- Create OWNERS
- Remove approve label for auto approval
- added VSCode directory
- Add OpenShift templates
- Add configuration file for Thoth
- Update README.rst
- Initial project import

  ### Bug Fixes

- Minor fix

- String concatenation fix

- Minor fix

- String concatenation fix

- Minor fix

- Relock fix (#468)

- Precommit fixes (#470)

- Fix attribute error while parsing YAML

- Fix if maintainers are not stated in OWNERS file

- Typo fix

- fixed coala

- coala fix

- Coala fix

- Coala fix
- Added error handling in case version control is used
- fixed coala
- fixed coala
- fixed commits
- fixed messages
- fixed coala
- coala fix
- fixed list branches expecting json
- Adjust cache location when run in the cluster due to perms
- :sparkles: added an annotation to each object created, so that we know the version of the template that created the object
- Fix wrong slug for the sesheta repo
- Automatically opens issues if thoth adviser returns error
- advise and write have been seperated so that if result is error an issue is opened
- Use emojis in commit messages not in pull-request titles
- Kill Kebechet after 2 hours if it was not able compute results
- Lower log level when something goes wrong when running Pipenv
- Correctly fix attribute error
- Fix wrong manager name
- Fix wrong value configuration
- Pipenv has been fixed upstream
- New Pipenv does not respect PIPENV_CACHE_DIR
- A temporary fix to avoid recent Pipenv issues
- Fix handling of versions when Pipfile is used
- Use related instead of fixes
- Another attempt to fix requests issue
- Make sure IGitt does not propagate verify arguments
- Try to fix IGitt requests handling
- Minor fixes in README file
- Issue handling and minor fixes
- Fix key error exception
- Checkout to master after changes
- Close initial lock issue when no longer relevant
- Close no management issue when it is no longer relevant
- Report issue on initial lock failure
- fixing coala Errors
- Fix syntax error in Ansible scripts
- fixed the semver

  ### Improvements

- Updated to pipenv 2020.8.13 and locked

- Document CHANGELOG.md file generation and assignees (#487)

- Extra line removed

- Extra line removed

- Remove result-api and workload-operator

- Make config parsing more safe

- use source type enum

- Fix test imports

- Added instruction for manual trigger and closses issue

- Added instruction for manual trigger and closses issue"

- Updated template and workflow to use openshift image

- removed extra files

- Check standard package in package.json

- kebechet only uses thoth sourcemanagement
- removed pin
- Updated managers to use ogr methods
- removed event variable
- removed event variable
- Added url parse and resolved comments"
- Fixed typos
- Reverted run method
- use /tmp for a .cache directory
- Remove osiris and osiris observer
- Changed env variable names
- Removed test values in job template
- Removed test values in job template
- Changed to use environment variable
- :sparkles: now using a bit of gitmoji
- Add osiris and osiris build-observer
- use thoth-* jobs in pipeline
- Distinguish pip and Pipenv cache
- put some more labels in, adjusted successfulJobsHistoryLimit
- Implement semver and calver for automated releases
- Fix typo in docs
- Fix typo in docs
- Update documentation for info manager
- Move info messages into correct module
- Fix a typo in attribute name
- Report end run for config entry
- Fix typo
- Code refactoring
- No need to install it anymore
- just minor wording tweaks
- some minor tweaks
- added all we need for coala
- Document Kebechet usage and design decisions
- Implementation improvements - a first working implementation

  ### Non-functional

- Propagate issue body to pull request on version updates

  ### Other

- remove metadata prefix

- Removed IGitt from manager base class

- Changed README and removed unnecessary code that was copied over

- Simplify code for with statement

  ### Automatic Updates

- :pushpin: Automatic update of dependency pytest-cov from 2.10.0 to 2.10.1 (#490)

- :pushpin: Automatic update of dependency thamos from 0.11.0 to 0.11.1 (#489)

- :pushpin: Automatic update of dependency thoth-common from 0.16.0 to 0.16.1 (#488)

- :pushpin: Automatic update of dependency thamos from 0.10.6 to 0.11.0 (#486)

- :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#482)

- :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.1 (#481)

- :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0 (#480)

- :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#476)

- :pushpin: Automatic update of dependency pytest-timeout from 1.4.1 to 1.4.2 (#475)

- :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2 (#474)

- :pushpin: Automatic update of dependency gitpython from 3.1.3 to 3.1.7 (#471)

- :pushpin: Automatic update of dependency thamos from 0.10.5 to 0.10.6 (#472)

- :pushpin: Automatic update of dependency thoth-common from 0.13.13 to 0.14.1

- :pushpin: Automatic update of dependency thoth-common from 0.13.12 to 0.13.13
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.9 to 0.3.0
- :pushpin: Automatic update of dependency requests from 2.23.0 to 2.24.0
- :pushpin: Automatic update of dependency thoth-common from 0.13.11 to 0.13.12
- :pushpin: Automatic update of dependency pytest-timeout from 1.4.0 to 1.4.1
- :pushpin: Automatic update of dependency semver from 2.10.1 to 2.10.2
- :pushpin: Automatic update of dependency pytest-cov from 2.9.0 to 2.10.0
- :pushpin: Automatic update of dependency pytest-timeout from 1.3.4 to 1.4.0
- :pushpin: Automatic update of dependency pipenv from 2018.11.26 to 2020.5.28
- :pushpin: Automatic update of dependency thoth-common from 0.13.6 to 0.13.7
- :pushpin: Automatic update of dependency thamos from 0.10.1 to 0.10.2
- :pushpin: Automatic update of dependency pytest-cov from 2.8.1 to 2.9.0
- :pushpin: Automatic update of dependency thoth-common from 0.13.5 to 0.13.6
- :pushpin: Automatic update of dependency thoth-common from 0.13.4 to 0.13.5
- :pushpin: Automatic update of dependency thoth-common from 0.13.3 to 0.13.4
- :pushpin: Automatic update of dependency thamos from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency pyyaml from 3.13 to 5.3.1
- :pushpin: Automatic update of dependency toml from 0.10.0 to 0.10.1
- :pushpin: Automatic update of dependency semver from 2.10.0 to 2.10.1
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.7 to 0.2.9
- :pushpin: Automatic update of dependency pytest from 5.4.1 to 5.4.2
- :pushpin: Automatic update of dependency semver from 2.9.1 to 2.10.0
- :pushpin: Automatic update of dependency pylint from 2.5.1 to 2.5.2
- :pushpin: Automatic update of dependency pylint from 2.5.0 to 2.5.1
- :pushpin: Automatic update of dependency gitpython from 3.1.1 to 3.1.2
- :pushpin: Automatic update of dependency thoth-common from 0.13.1 to 0.13.2
- :pushpin: Automatic update of dependency thamos from 0.9.4 to 0.10.0
- :pushpin: Automatic update of dependency thamos from 0.9.3 to 0.9.4
- :pushpin: Automatic update of dependency thoth-common from 0.13.0 to 0.13.1
- :pushpin: Automatic update of dependency click from 7.1.1 to 7.1.2
- :pushpin: Automatic update of dependency pylint from 2.4.4 to 2.5.0
- :pushpin: Automatic update of dependency thoth-common from 0.12.10 to 0.13.0
- :pushpin: Automatic update of dependency thoth-common from 0.12.9 to 0.12.10
- :pushpin: Automatic update of dependency thamos from 0.9.2 to 0.9.3
- :pushpin: Automatic update of dependency gitpython from 3.1.0 to 3.1.1
- :pushpin: Automatic update of dependency thoth-common from 0.12.8 to 0.12.9
- :pushpin: Automatic update of dependency thoth-common from 0.12.7 to 0.12.8
- :pushpin: Automatic update of dependency thoth-common from 0.12.6 to 0.12.7
- :pushpin: Automatic update of dependency thamos from 0.9.1 to 0.9.2
- :pushpin: Automatic update of dependency thoth-sourcemanagement from 0.2.6 to 0.2.7
- :pushpin: Automatic update of dependency thamos from 0.8.1 to 0.9.1
- :pushpin: Automatic update of dependency thoth-common from 0.10.11 to 0.12.6
- :pushpin: Automatic update of dependency pyyaml from 5.3 to 3.13
- :pushpin: Automatic update of dependency pytest from 5.4.0 to 5.4.1
- :pushpin: Automatic update of dependency pytest from 5.3.5 to 5.4.0
- :pushpin: Automatic update of dependency thoth-common from 0.10.9 to 0.10.11
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- :pushpin: Automatic update of dependency click from 7.0 to 7.1.1
- :pushpin: Automatic update of dependency thoth-common from 0.10.8 to 0.10.9
- :pushpin: Automatic update of dependency thoth-common from 0.10.7 to 0.10.8
- :pushpin: Automatic update of dependency requests from 2.22.0 to 2.23.0
- Automatic update of dependency pyyaml from 3.12 to 3.13
- Automatic update of dependency pytest from 3.6.2 to 3.6.3
- Automatic update of dependency pipenv from 2018.5.18 to 2018.7.1

## Release 1.0.4 (2020-08-31T08:27:38)

### Features

- Add GitHub's PR template
- Skip empty new lines in update manager
- Update requirements.txt

  ### Improvements

- Revert "Updated to pipenv 2020.8.13 and locked"

## Release 1.0.5 (2020-09-11T17:33:31)

### Features

- Update .thoth.yaml
- Fix reStructuredText issues

  ### Bug Fixes

- Fix formatting when wrong version identifier is found

  ### Automatic Updates

- :pushpin: Automatic update of dependency gitpython from 3.1.7 to 3.1.8

- :pushpin: Automatic update of dependency thoth-glyph from 0.1.0 to 0.1.1

- :pushpin: Automatic update of dependency sentry-sdk from 0.17.0 to 0.17.4

- :pushpin: Automatic update of dependency thamos from 0.11.1 to 0.12.2

- :pushpin: Automatic update of dependency thoth-common from 0.16.1 to 0.18.2

## Release 1.0.6 (2020-09-18T10:59:54)

### Features

- Update versions

## Release 1.0.7 (2020-09-21T15:54:56)

### Features

- Updated dependencies

  ### Bug Fixes

- fixed imports

## Release 1.0.8 (2020-09-22T15:13:49)

### Features

- Updated glyph to 0.13

## Release 1.0.9 (2020-09-23T16:20:11)

### Features

- Updated glyph
- updated github templates
- Make pre-commit happy

  ### Improvements

- Fixed version test

## Release 1.0.10 (2020-11-12T19:06:36)

### Features

- Remove unnecessary quotes (#589)
- Enabled github app authentication (#587)
- precommit happy
- Link formatted
- added a clickable link to readme
- Added reminder to add to thoth stroage
- Add manual request example

  ### Bug Fixes

- Updated source-management and fixed version test (#590)

- Precommit fixes

  ### Improvements

- :sparkles: :pencil: updated the readme, now we deploy via kustomize rather than ansible

- Fix typo

## Release 1.1.0 (2020-11-18T18:13:51)

### Features

- :honeybee: upgrade pip for kebechet container image (#593)

  ### Improvements

- Added modifications to use gitpython (#594)

## Release 1.1.1 (2020-11-19T20:26:20)

### Features

- Update manager non-atomic updates (#597)

## Release 1.1.2 (2020-11-20T17:54:27)

### Features

- Updated to pipenv 2020 (#602)

## Release 1.1.3 (2020-11-24T18:20:49)

### Features

- Req was using pipenv 2018 (#615)
- :arrow_up: Automatic update of dependencies by kebechet. (#613)
- Add Sai to project owners (#611)

## Release 1.1.4 (2020-11-24T20:47:19)

### Bug Fixes

- The release PR should close the issue (#606)

## Release 1.2.0 (2020-12-03T20:32:37)

### Features

- statisfy the need of python38-devel libraries (#635)
- Fixed wrong function accessed (#633)
- :arrow_up: Automatic update of dependencies by kebechet. (#630)
- Added warning if release tag is missing. (#628)
- Slug wrongly set (#627)

  ### Improvements

- newline adjustment for consistency of body for kinda issues (#631)

## Release 1.2.1 (2020-12-03T21:47:41)

### Features

- port to python38 (#621)

## Release 1.2.2 (2020-12-04T14:28:28)

### Features

- Update OWNERS
- Missing typing extensions (#645)

  ### Bug Fixes

- Relock to fix typing_extensions relock (#646)

## Release 1.2.3 (2021-01-11T17:45:28)

### Features

- :arrow_up: Automatic update of dependencies by kebechet. (#660)
- :arrow_up: Automatic update of dependencies by kebechet. (#658)
- :arrow_up: Automatic update of dependencies by kebechet. (#655)
- add a little more linky footer to PRs (#607)
- :arrow_up: Automatic update of dependencies by kebechet. (#651)

  ### Bug Fixes

- fix the name of the imagestream to-be looked up (#650)

## Release 1.2.4 (2021-02-01T08:10:16)

### Features

- :arrow_up: Automatic update of dependencies by kebechet. (#687)
- write outputs of pipenv lock -r to output file (#686)
- :arrow_up: Automatic update of dependencies by kebechet. (#685)
- :arrow_up: Automatic update of dependencies by kebechet. (#684)
- :arrow_up: Automatic update of dependencies by kebechet. (#682)
- Automatically close update merge request if no longer relevant (#661)
- :arrow_up: Automatic update of dependencies by kebechet. (#677)
- :arrow_up: Automatic update of dependencies by kebechet. (#668)
- Fixed log message (#673)
- :sparkles: add a little more linky footer to PRs
- Thoth Labelmanager (#656)
- :arrow_up: Automatic update of dependencies by kebechet. (#666)

  ### Bug Fixes

- :bug: fix some flake8 complains

  ### Improvements

- removed bissenbay, thanks for your contributions!

## Release 1.3.0 (2021-06-02T21:26:33)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet (#724)
- :hatched_chick: update the prow resource limits (#723)
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet (#716)
- :arrow_up: Automatic update of dependencies by Kebechet (#713)
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet (#709)
- add kebechet metadata when sending request to thamos (#699)
- :arrow_up: Automatic update of dependencies by Kebechet (#708)
- :arrow_up: Automatic update of dependencies by Kebechet (#706)
- :arrow_up: Automatic update of dependencies by Kebechet (#703)
- :arrow_up: Automatic update of dependencies by Kebechet (#697)
- add justification based on metadata if possible
- :arrow_up: Automatic update of dependencies by Kebechet (#695)
- :arrow_up: Automatic update of dependencies by Kebechet (#694)
- :arrow_up: Automatic update of dependencies by Kebechet (#692)
- :arrow_up: Automatic update of dependencies by Kebechet (#691)

  ### Bug Fixes

- :zap: pre-commit fixes for the master branch

- :arrow_up: fix some formatting and update pre-commit plugins

  ### Improvements

- :sparkles: reconfgured CI/CD to use prow and aicoe-ci

  ### Other

- remove thoth-sourcemanagement from Kebechet (#725)

- remove todo

- Delete branch if the pull request has been already closed

## Release 1.3.1 (2021-06-09T11:13:43)

### Features

- Update OWNERS
- add ogr dep to Pipfile
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet

## Release 1.3.2 (2021-06-14T06:18:31)

### Features

- use ogr to get app auth token
- pre-commit issue
- Update kebechet/managers/version/version.py
- Fixed prepending when Title exists
- Fixed README to remove legacy example configuration
- changed appending changelog to prepending changelog
- add docs for locally running Kebechet

  ### Bug Fixes

- Fixed small bug in which original changelog was removed

## Release 1.3.3 (2021-06-30T16:07:37)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet
- pass environment name to managers and add documentation for expected manager behaviour
- update from template project
- add priority/critical-urgent label to all bot related issue templates
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: updated labels of issue templates

  ### Bug Fixes

- fix issue 746

- fixed bug with unrelated histories where khebhut doesn't create PR

  ### Improvements

- use upstream solution for adding assignees

- use thamos.lib.write_files

## Release 1.4.0 (2021-08-02T08:06:03)

### Features

- :arrow_up: Automatic update of dependencies by Kebechet (#768)
- add args to get access token
- make update manager work with overlays
- :arrow_up: Automatic update of dependencies by Kebechet
- :arrow_up: Automatic update of dependencies by Kebechet
- :sparkles: add some Kubernetes-inspired Labels to Issues opened by Kebechet
