Kebechet
--------

I'm Kebechet, goddess of freshness. I will keep your dependencies fresh and up-to-date.

Deployment of Kebechet
----------------------

To deploy kebechet on openshift cluster.
Use the following ansible command with required parameters:

.. code-block:: console

  ansible-playbook \
    --extra-vars=OCP_URL= <openshift_cluster_url> \
    --extra-vars=OCP_TOKEN= <openshift_cluster_token> \
    --extra-vars=KEBECHET_INFRA_NAMESPACE= <openshift_cluster_namespace> \
    --extra-vars=KEBECHET_APPLICATION_NAMESPACE= <openshift_cluster_namespace> \
    --extra-vars=KEBECHET_CONFIGURATION= <github_repo_config.yaml> \
    --extra-vars=KEBECHET_TOKEN= <github_oauth_token> \
    --extra-vars=KEBECHET_SSH_PRIVATE_KEY_PATH= <github_ssh_private_key_path> \
    playbooks/provision.yaml


* KEBECHET_SSH_PRIVATE_KEY_PATH: The path where the GitHub ssh private key is stored should be provided. (Example: $HOME/.ssh/id_rsa).If the field is undefined then the script will create the ssh keys for you and then you can set up the given public key to Github repository.

* KEBECHET_TOKEN: To raise the pull request bot requires user rights and premissions.The Github oauth tokens are to be set for rasing pull request whenever updates are encounter by the kebechet-bot.

* KEBECHET_CONFIGURATION: The GitHub Repository for which you want to setup Kebechet-bot, for that repository a configuration Yaml file should be provided.

* KEBECHET_INFRA_NAMESPACE: The Openshift namespace can be used for the infrastructural purposes, all the images stream are stored in the INFRA_NAMESPACE.

* KEBECHET_APPLICATION_NAMESPACE: THe Openshift namespace can be used for the application purposes, all the templates, builds, secrets, configmap and jobs are stored in the APPLICATION_NAMESPACE.

* OCP_URL and OCP_TOKEN: The Openshift credentials are to be setup with the access token and url.