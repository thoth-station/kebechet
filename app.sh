#!/usr/bin/env sh
#
# This script is run by OpenShift's s2i. Here we guarantee that we run desired
# sub-command based on env-variables configuration.
#

case $KEBECHET_SUBCOMMAND in
    'run-url') 
        exec /opt/app-root/bin/python3 kebechet run-url $REPO_URL $SERVICE_NAME
        ;;
    'run-analysis') 
        exec /opt/app-root/bin/python3 kebechet run-analysis $REPO_URL $SERVICE_NAME $ANALYSIS_ID
        ;;
    *)
        echo "Application configuration error - invalid or no subcommand supplied"
        exit 1
        ;;
esac