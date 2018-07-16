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

"""Configuration Class."""

import logging
import os
from functools import partialmethod
import yaml

import urllib3
import requests

from .exception import ConfigurationError
from .enums import ServiceType

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Library-wide configuration."""

    def __init__(self):
        self._repositories = None

    def from_file(self, config_path: str):
        if config_path.startswith(('https://', 'https://')):
            response = requests.get(config_path)
            response.raise_for_status()
            content = response.text
        else:
            with open(config_path) as config_file:
                content = config_file.read()

        try:
            self._repositories = yaml.load(content).pop('repositories') or []
        except Exception as exc:
            raise ConfigurationError("Failed to parse configuration file: {str(exc)}") from exc

    def iter_entries(self) -> tuple:
        """Iterate over repositories listed."""
        for entry in self._repositories or []:
            try:
                items = dict(entry)
                value = items.pop('managers'), \
                    items.pop('slug'), \
                    items.pop('service_type', None), \
                    items.pop('service_url', None), \
                    items.pop('token', None), \
                    items.pop('labels', []), \
                    items.pop('tls_verify', True)

                if items:
                    _LOGGER.warning(f"Unknown configuration entry in configuration of {slug!r}: {items}")

                yield value
            except KeyError:
                _LOGGER.exception("An error in your configuration - ignoring the given configuration entry...")

    @staticmethod
    def _tls_verification(service_url: str, slug: str, verify: bool) -> None:
        """Turn off or on TLS verification based on configuration."""
        # We manage our own warnings, of course better ones!
        urllib3.disable_warnings()
        if not verify:
            _LOGGER.warning(f"Turning off TLS certificate verification for {slug} hosted at {service_url}")

        to_patch = {
            'post': requests.Session.post,
            'delete': requests.Session.delete,
            'put': requests.Session.put,
            'get': requests.Session.get,
            'head': requests.Session.head,
            'patch': requests.Session.patch
        }
        for name, method in to_patch.items():
            # The last partial method will apply.
            setattr(requests.Session, name, partialmethod(method, verify=verify))

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet using provided YAML configuration file."""
        global config
        from kebechet.managers import REGISTERED_MANAGERS

        config.from_file(configuration_file)

        for managers, slug, service_type, service_url, token, labels, tls_verify in config.iter_entries():
            cls._tls_verification(service_url, slug, verify=tls_verify)

            if service_url and not service_url.startswith(('https://', 'http://')):
                # We need to have this explicitly set for IGitt and also for security reasons.
                _LOGGER.error(
                    "You have to specify protocol ('https://' or 'http://') in service URL "
                    "configuration entry - invalid configuration {service_url!}"
                )
                continue

            if service_url and service_url.endswith('/'):
                service_url = service_url[:-1]

            if token:
                # Allow token expansion based on env variables.
                token = token.format(**os.environ)
                _LOGGER.debug(f"Using token '{token[:3]}{'*'*len(token[3:])}'")

            for manager in managers:
                kebechet_manager = REGISTERED_MANAGERS.get(manager)

                if not kebechet_manager:
                    _LOGGER.error("Unable to find requested manager {manager!r}, skipping")

                _LOGGER.info(f"Running manager {manager!r} for {slug!r}")
                try:
                    kebechet_manager(slug, ServiceType.by_name(service_type), service_url, token).run(labels)
                except Exception as exc:
                    _LOGGER.exception(
                        f"An error occurred during run of manager {manager!r} {kebechet_manager} for {slug}, skipping"
                    )

            _LOGGER.info(f"Finished management for {slug!r}")


config = _Config()
