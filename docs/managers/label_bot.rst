Label Bot
=========

This manager will help label issues in your repositories powered by an AI model
based a pretrained NLP (Natural Language Processing) model, `RoBERTa
<https://ai.facebook.com/blog/roberta-an-optimized-method-for-pretraining-self-supervised-nlp-systems/>`_.
Find more about the model powering this manager `here
<https://github.com/thoth-station/Github-Issues-Classifier>`__.

Developer Note - Ensure Kebechet points to the API Url with help of the environment variable - ``LABELBOT_URL``
For example local dev - ``LABELBOT_URL = "http://localhost:8888"``

Configuration
-------------

N/A

Example
-------

An example configuration:

.. code-block:: yaml

    ...
    managers:
      - name: label-bot
        # This manager has no configuration.
    ...

An example of this version manager in action can be found `here <https://github.com/saisankargochhayat/kebechet_sample/issues/140>`__.

Manager Author
--------------

Sai Sankar Gochhayat <sgochhay@redhat.com>
