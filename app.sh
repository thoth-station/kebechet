#!/usr/bin/env sh
#
# This script is run by OpenShift's s2i. Here we guarantee that we run desired
# sub-command based on env-variables configuration.
#

# Check whether there is a passwd entry for the container UID
myuid=$(id -u)
mygid=$(id -g)
uidentry=$(getent passwd $myuid)

# If there is no passwd entry for the container UID, attempt to create one
if [ -z "$uidentry" ] ; then
    if [ -w /etc/passwd ] ; then
        echo "$myuid:x:$myuid:$mygid:anonymous uid:/home/user:/bin/false" >> /etc/passwd
    else
        echo "Container ENTRYPOINT failed to add passwd entry for anonymous UID"
    fi
fi
# The git_ssh_command helps the server by pass the Host key checking while connecting to github.
export GIT_SSH_COMMAND='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

case $KEBECHET_SUBCOMMAND in
    'run-webhook')
        exec pipenv run python3 kebechet-cli run-webhook
        ;;
    'run-url')
        exec pipenv run python3 kebechet-cli run-url
        ;;
    'run-results')
        exec pipenv run python3 kebechet-cli run-results
        ;;
    'run')
        exec pipenv run python3 kebechet-cli run
        ;;
    *)
        echo "Application configuration error - invalid or no subcommand supplied"
        exit 1
        ;;
esac
