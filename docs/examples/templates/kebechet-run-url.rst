Argo Kebechet Run URL
=====================

Secret Definition
-----------------

.. code-block:: yaml

  apiVersion: v1
  kind: Secret
  metadata:
    name: kebechet
  type: Opaque
  data:
    github-oauth-token: ...
    gitlab-oauth-token: ...
    pagure-oauth-token: ...
    GITHUB_APP_ID: ...
    ssh-private-key: |  # mounted in volume
      ...
    KEBBHUT_GITHUB_PRIVATE_KEY: |  # mounted in volume
      ...

Argo Workflow Template
----------------------

.. code-block:: yaml

  apiVersion: argoproj.io/v1alpha1
  kind: WorkflowTemplate
  metadata:
    name: kebechet-run-url
    labels:
      component: kebechet
  spec:
    templates:
      - name: kebechet-run-url
        inputs:
          parameters:
          - name: KEBECHET_REPO_URL
          - name: KEBECHET_SERVICE_NAME
          - name: KEBECHET_METADATA
        container:
          image: kebechet:latest
          env:
            - name: KEBECHET_SUBCOMMAND
              value: "run-url"
            - name: KEBECHET_REPO_URL
              value: "{{inputs.parameters.KEBECHET_REPO_URL}}"
            - name: KEBECHET_SERVICE_NAME
              value: "{{inputs.parameters.KEBECHET_SERVICE_NAME}}"
            - name: KEBECHET_METADATA
              value: "{{inputs.parameters.KEBECHET_METADATA}}"
            - name: GITHUB_APP_ID
              valueFrom:
                secretKeyRef:
                  key: GITHUB_APP_ID
                  name: kebechet
            - name: GITHUB_PRIVATE_KEY_PATH
              value: "/home/user/github/github-privatekey"
            - name: GITHUB_KEBECHET_TOKEN
              valueFrom:
                secretKeyRef:
                  key: github-oauth-token
                  name: kebechet
            - name: GITLAB_KEBECHET_TOKEN
              valueFrom:
                secretKeyRef:
                  key: gitlab-oauth-token
                  name: kebechet
            - name: PAGURE_KEBECHET_TOKEN
              valueFrom:
                secretKeyRef:
                  key: pagure-oauth-token
                  name: kebechet
          volumeMounts:
            - name: ssh-config
              mountPath: /home/user/.ssh
              readOnly: true
            - name: github-app-privatekey
              mountPath: /home/user/github
              readOnly: true
