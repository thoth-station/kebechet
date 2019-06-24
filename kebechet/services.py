#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019 Kevin Postlethwait
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

from .enums import ServiceType

_LOGGER = logging.getLogger(__name__)


def _keep_slug(slug: str):
    return slug


def _encode_fslash(slug: str):
    return slug.replace("/", "%2F")


# NOTE: config_url could be generated using construct_raw_file_url but I feel this makes the code easier to follow
services = {
    "github": {
        "service_type": ServiceType.GITHUB,
        "config_url": "https://raw.githubusercontent.com/{slug}/{branch}/.kebechet.yaml",
        "auth": {"header": "Authorization", "value": "token {token}"},
        "slug_method": _keep_slug,
    },
    "gitlab": {
        "service_type": ServiceType.GITLAB,
        "config_url": "https://gitlab.com/api/v4/projects/{slug}/repository/files/.kebechet.yaml/raw?ref={branch}",
        "auth": {"header": "Private-Token", "value": "{token}"},
        "slug_method": _encode_fslash,
    },
}


class Service():
    """Allows for abstraction of multiple different service with easy support of my by changing `services`."""

    def __init__(self, service, url, token, branch="master"):
        """Initialize a Service object, calls constructor functions `slug_method` and `_generate_slug`."""
        if service not in services.keys():
            _LOGGER.warning("Service not supported")
            raise ValueError(f"{service} is not supported at this time")
        self.service = services[service]["service_type"]
        _LOGGER.info(f"{service} service detected")
        self.branch = branch
        self.url = url
        self.token = token
        self.service_info = services[service]
        slug = Service._generate_slug(url)
        self.slug = services[service]["slug_method"](slug)

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
        """Return a temporary file containing this repos' .kebechet.yaml contents."""
        down_url = self.get_kebechet_download_url()
        auth = self.get_auth_header()
        _LOGGER.info(f"Downloading from {down_url}")
        resp = requests.get(down_url, headers=auth)
        file_ = tempfile.NamedTemporaryFile()
        file_.write(resp.content)
        _LOGGER.info(resp.content)
        return file_
