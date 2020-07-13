#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Kevin Postlethwait
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

"""Provides abstraction of service utility functions."""


import requests
import tempfile
import logging
import os

from thoth.sourcemanagement.enums import ServiceType

_LOGGER = logging.getLogger(__name__)


class Service:
    """Allows for abstraction of multiple different service with easy support of my by changing `services`."""

    @staticmethod
    def _keep_slug(slug: str):
        return slug

    @staticmethod
    def _encode_fslash(slug: str):
        return slug.replace("/", "%2F")

    # NOTE: config_url could be generated using construct_raw_file_url but I feel this makes the code easier to follow
    _SERVICES = {
        "github": {
            "token": "GITHUB_KEBECHET_TOKEN",
            "service_type": ServiceType.GITHUB,
            "config_url": "https://raw.githubusercontent.com/{slug}/{branch}/.thoth.yaml",
            "auth": {"header": "Authorization", "value": "token {token}"},
            "slug_method": _keep_slug.__func__,  # type: ignore
        },
        "gitlab": {
            "token": "GITLAB_KEBECHET_TOKEN",
            "service_type": ServiceType.GITLAB,
            "config_url": "https://gitlab.com/api/v4/projects/{slug}/repository/files/.thoth.yaml/raw?ref={branch}",
            "auth": {"header": "Private-Token", "value": "{token}"},
            "slug_method": _encode_fslash.__func__,  # type: ignore
        },
    }

    def __init__(self, service, url, branch="master"):
        """Initialize a Service object, calls constructor functions `slug_method` and `_generate_slug`."""
        if service not in self._SERVICES.keys():
            raise ValueError(f"{service} is not supported at this time")
        self.service = self._SERVICES[service]["service_type"]
        _LOGGER.info("%s service detected", service)
        self.token = os.environ[self._SERVICES[service]["token"]]
        self.branch = branch
        self.url = url
        self.service_info = self._SERVICES[service]
        slug = Service._generate_slug(url)
        self.slug = self._SERVICES[service]["slug_method"](slug)

    @staticmethod
    def _generate_slug(url: str):
        params = url.split("/")
        return "/".join(params[3:])

    def get_kebechet_download_url(self):
        """Get the download url of the .kebechet.yaml."""
        return self.service_info["config_url"].format(
            slug=self.slug, branch=self.branch
        )

    def get_auth_header(self):
        """Get the authorization header for this services api."""
        return {
            self.service_info["auth"]["header"]: self.service_info["auth"][
                "value"
            ].format(token=self.token)
        }

    def download_kebechet_config(self):
        """Return a temporary file containing this repos' .thoth.yaml contents."""
        down_url = self.get_kebechet_download_url()
        auth = self.get_auth_header()
        _LOGGER.info("Downloading from %s", down_url)
        resp = requests.get(down_url, headers=auth)
        file_ = tempfile.NamedTemporaryFile()
        file_.write(resp.content)
        file_.seek(0)
        _LOGGER.info(resp.content)
        return file_
