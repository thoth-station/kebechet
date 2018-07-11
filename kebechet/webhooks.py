#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This is the webhook receiver..."""


import os
import logging
import hmac
import json

import requests

from flask import request, Blueprint, jsonify, current_app
from git import Repo


ENDPOINT_URL = os.getenv('KEBESCHET_MATTERMOST_ENDPOINT_URL', None)


_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

webhook = Blueprint('webhook', __name__, url_prefix='')


def notify_channel(message):
    """Send message to Mattermost Channel."""
    payload = {'text': message,
               'icon_url': 'https://avatars1.githubusercontent.com/u/33906690'}

    r = requests.post(ENDPOINT_URL, json=payload)
    if r.status_code != 200:
        _LOGGER.error(f"cant POST to {ENDPOINT_URL}")


def handle_github_open_issue(issue):
    """Will handle with care."""
    _LOGGER.info(f"An Issue has been opened: {issue['url']}")

    if issue['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(f"[{issue['user']['login']}]({issue['user']['url']}) just "
                   f"opened an issue: [{issue['title']}]({issue['html_url']})...")


def handle_github_open_pullrequest(pullrequest):
    """Will handle with care."""
    _LOGGER.info(f"A Pull Request has been opened: {pullrequest['url']}")

    if pullrequest['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(f"[{pullrequest['user']['login']}]({pullrequest['user']['url']}) just "
                   f"opened a pull request: '[{pullrequest['title']}]({pullrequest['html_url']})'...")


def handle_github_open_pullrequest_merged_successfully(pullrequest):
    """Will handle with care."""
    _LOGGER.info(
        f"A Pull Request has been successfully merged: {pullrequest}")

    if pullrequest['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(
        f":tada: Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})' of "
        f"[{pullrequest['head']['repo']['full_name']}]({pullrequest['head']['repo']['html_url']}) "
        f"has been successfully merged!")


@webhook.route('/github', methods=['POST'])
def handle_github_webhook():
    """Entry point for github webhook."""
    if ENDPOINT_URL is None:
        _LOGGER.error('No Mattermost incoming webhook URL supplied!')
        exit(-2)

    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')

    secret = str.encode(current_app.config.get(
        'KEBECHET_GITHUB_WEBHOOK_SECRET'))

    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()

    if hmac.compare_digest(hashhex, signature):
        payload = request.json

        if 'issue' in payload.keys():
            if payload['action'] == 'opened':
                handle_github_open_issue(payload['issue'])
        if 'pull_request' in payload.keys():
            if payload['action'] == 'opened':
                handle_github_open_issue(payload['pull_request'])
            elif payload['action'] == 'closed':
                if payload['pull_request']['merged']:
                    handle_github_open_pullrequest_merged_successfully(
                        payload['pull_request'])
        else:
            _LOGGER.debug(
                f"Received a github webhook {json.dumps(request.json)}")
    else:
        _LOGGER.error(
            f"Webhook secret mismatch: me: {hashhex} != them: {signature}")

    return jsonify({"message": "thanks!"}), 200
