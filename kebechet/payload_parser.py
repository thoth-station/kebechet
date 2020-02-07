#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2020 Sai Sankar Gochhayat
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

"""Provides abstraction of payload parsing functions."""

from .enums import ServiceType
import logging

_LOGGER = logging.getLogger(__name__)


class PayloadParser():
    """Allow Kebechet to parse webhook payload of different services."""

    _GITHUB = "api.github.com"
    _GITLAB = "gitlab.com"

    _IGNORED_GITHUB_EVENTS = ['installation', 'integration_installation']

    def __init__(self, payload: dict):
        """Initialize the parameters we require from the services."""
        self.service_type = None
        self.url = None
        self.event = None

        # For github webhooks
        if 'event' in payload:
            if payload['event'] not in self._IGNORED_GITHUB_EVENTS:
                github_payload = payload['payload']
                if self._GITHUB in github_payload['sender']['url']:
                    self.service_type = 'github'
                    self.event = payload['event']
                    self.github_parser(github_payload)
        # For gitlab webhooks
        elif 'project' in payload:
            if self._GITLAB in payload['project']['web_url']:
                self.service_type = 'gitlab'
        else:
            _LOGGER.exception("Payload passed is not supported.")

    def github_parser(self, payload):
        """Parse Github data."""
        self.url = payload["repository"]["html_url"]

    def gitlab_parser(self, payload):
        """Parse Gitlab data."""
        self.url = payload['project']['web_url']
        self.event = payload['object_kind']

    def parsed_data(self):
        """Return the parsed data if its of a supported service."""
        if not self.service_type:
            return None
        parsed_payload = {
            'service_type': self.service_type,
            'url': self.url,
            'event': self.event
        }
        return parsed_payload
