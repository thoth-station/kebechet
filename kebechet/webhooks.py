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

GITHUB_MATTERMOST_MAPPING = {
    "goern": "goern",
    "fridex": "fridolin",
    "hashard16": "hnalla",
    "ace2107": "akash2107",
    "durandom": "hild",
    "sub-mod": "subin",
    "sushmithaaredhatdev": "sushmitha_nagarajan",
    "vpavlin": "vpavlin"
}

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

webhook = Blueprint('webhook', __name__, url_prefix='')


def mattermost_username_by_github_user(github: str) -> str:
    """Map a GitHub User to a Mattermost User."""
    mattermost = None

    try:
        mattermost = GITHUB_MATTERMOST_MAPPING[github]
    except KeyError as exp:
        _LOGGER.exception(exp)

    if not mattermost:
        mattermost = github

    return f'@{mattermost}'


def notify_channel(message: str) -> None:
    """Send message to Mattermost Channel."""
    payload = {'text': message,
               'icon_url': 'https://avatars1.githubusercontent.com/u/33906690'}

    r = requests.post(ENDPOINT_URL, json=payload)
    if r.status_code != 200:
        _LOGGER.error(f"cant POST to {ENDPOINT_URL}")


def handle_github_open_issue(issue: dict) -> None:
    """Will handle with care."""
    _LOGGER.info(f"An Issue has been opened: {issue['url']}")

    if issue['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(f"[{issue['user']['login']}]({issue['user']['url']}) just "
                   f"opened an issue: [{issue['title']}]({issue['html_url']})... :glowstick:")


def handle_github_open_pullrequest(pullrequest: dict) -> None:
    """Will handle with care."""
    _LOGGER.info(f"A Pull Request has been opened: {pullrequest['url']}")

    if pullrequest['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(f"_{mattermost_username_by_github_user(pullrequest['user']['login'])}_ just "
                   f"opened a pull request: '[{pullrequest['title']}]({pullrequest['html_url']})'...")


def handle_github_open_pullrequest_merged_successfully(pullrequest: dict) -> None:
    """Will handle with care."""
    _LOGGER.info(
        f"A Pull Request has been successfully merged: {pullrequest}")

    if pullrequest['title'].startswith('Automatic update of dependency'):
        return

    notify_channel(
        f":tada: Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})' was successfully "
        f"merged into [{pullrequest['base']['repo']['full_name']}]({pullrequest['base']['repo']['html_url']}) ")


def handle_github_pull_request_review(pullrequest: dict, review: dict) -> None:
    """Will handle with care."""
    return


def handle_github_pull_request_review_requested(
        pullrequest: dict) -> None:
    """Will handle with care."""

    for requested_reviewer in pullrequest['requested_reviewers']:
        notify_channel(
            f":play_or_pause_button: a review by _{mattermost_username_by_github_user(requested_reviewer['login'])}_"
            f" has been requested for "
            f"Pull Request '[{pullrequest['title']}]({pullrequest['html_url']})'")


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

        # this will give use the event type...
        event_type = payload['action']

        if 'pull_request' in event_type:
            if payload['action'] == 'opened':
                handle_github_open_pullrequest(payload['pull_request'])
            elif payload['action'] == 'closed':
                if payload['pull_request']['merged']:
                    handle_github_open_pullrequest_merged_successfully(
                        payload['pull_request'])
        elif 'issue' in event_type:
            if payload['action'] == 'opened':
                handle_github_open_issue(payload['issue'])
        elif 'pull_request_review' in event_type:
            handle_github_pull_request_review(
                payload['pull_request'], payload['review'])
        elif 'review_requested' in event_type:
            handle_github_pull_request_review_requested(
                payload['pull_request'])
        else:
            _LOGGER.debug(
                f"Received a github webhook {json.dumps(request.json)}")
    else:
        _LOGGER.error(
            f"Webhook secret mismatch: me: {hashhex} != them: {signature}")

    return jsonify({"message": "thanks!"}), 200
