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

from thoth.sourcemanagement.enums import ServiceType  # noqa F401
import logging
from .exception import WebhookPayloadError
from urllib.parse import urlparse
from typing import Optional, Any, Dict

_LOGGER = logging.getLogger(__name__)


class PayloadParser:
    """Allow Kebechet to parse webhook payload of different services."""

    _GITHUB = "api.github.com"
    _GITLAB = "gitlab.com"

    _IGNORED_GITHUB_EVENTS = ["installation", "integration_installation"]

    def __init__(self, payload: dict) -> None:
        """Initialize the parameters we require from the services."""
        self.raw_payload = payload
        self.service_type = None
        self.url = None
        self.event = None
        self.parsed_payload: Optional[dict] = None

        # For github webhooks
        if "event" in payload:
            if payload["event"] not in self._IGNORED_GITHUB_EVENTS:
                github_payload = payload["payload"]
                parsed_url = urlparse(github_payload["sender"]["url"])
                if self._GITHUB in parsed_url.netloc:
                    self.service_type = "github"
                    self.event = payload["event"]
                    self.github_parser(github_payload)
        # For gitlab webhooks
        elif "payload" in payload:
            gitlab_payload = payload["payload"]
            parsed_url = urlparse(gitlab_payload["project"]["web_url"])
            if self._GITLAB in parsed_url.netloc:
                self.service_type = "gitlab"
                self.gitlab_parser(gitlab_payload)
        else:
            raise WebhookPayloadError("Payload passed is not supported.")

    def github_parser(self, payload: dict) -> None:
        """Parse Github data."""
        self.url = payload["repository"]["html_url"]

    def gitlab_parser(self, payload: dict) -> None:
        """Parse Gitlab data."""
        self.url = payload["project"]["web_url"]
        self.event = payload["object_kind"]

    def parsed_data(self) -> Optional[Dict[str, Optional[Any]]]:
        """Return the parsed data if its of a supported service."""
        if not self.service_type:
            return None
        self.parsed_payload = {
            "service_type": self.service_type,
            "url": self.url,
            "event": self.event,
            "raw_payload": self.raw_payload,
        }
        return self.parsed_payload
