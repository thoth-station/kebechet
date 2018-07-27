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
                    items.pop('tls_verify', True)

                if items:
                    _LOGGER.warning(f"Unknown configuration entry in configuration of {value[1]!r}: {items}")

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

        # Please close your eyes when reading this - it's pretty ugly solution but is somehow applicable to
        # the IGitt's handling of these methods.
        original_post = requests.Session.post
        original_delete = requests.Session.delete
        original_put = requests.Session.put
        original_get = requests.Session.get
        original_head = requests.Session.head
        original_patch = requests.Session.patch

        def post(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_post(*args, **kwargs, verify=verify)
        requests.Session.post = post

        def delete(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_delete(*args, **kwargs, verify=verify)
        requests.Session.delete = delete

        def put(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_put(*args, **kwargs, verify=verify)
        requests.Session.put = put

        def get(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_get(*args, **kwargs, verify=verify)
        requests.Session.get = get

        def head(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_head(*args, **kwargs, verify=verify)
        requests.Session.head = head

        def patch(*args, **kwargs):
            kwargs.pop('verify', None)
            return original_patch(*args, **kwargs, verify=verify)
        requests.Session.patch = patch

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet using provided YAML configuration file."""
        global config
        from kebechet.managers import REGISTERED_MANAGERS

        config.from_file(configuration_file)

        for managers, slug, service_type, service_url, token, tls_verify in config.iter_entries():
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
                # We do pops on dict, which changes it. Let's create a soft duplicate so if a user uses
                # YAML references, we do not break.
                manager = dict(manager)
                try:
                    manager_name = manager.pop('name')
                except Exception:
                    _LOGGER.exception(f"No manager name provided in configuration entry for {slug}, ignoring entry")
                    continue

                kebechet_manager = REGISTERED_MANAGERS.get(manager_name)
                if not kebechet_manager:
                    _LOGGER.error("Unable to find requested manager %r, skipping", manager_name)
                    continue

                _LOGGER.info(f"Running manager %r for %r", manager_name, slug)
                manager_configuration = manager.pop('configuration', {})
                if manager:
                    _LOGGER.warning(f"Ignoring option {manager} in manager entry for {slug}")

                try:
                    instance = kebechet_manager(slug, ServiceType.by_name(service_type), service_url, token)
                    instance.run(**manager_configuration)
                except Exception as exc:
                    _LOGGER.exception(
                        f"An error occurred during run of manager {manager!r} {kebechet_manager} for {slug}, skipping"
                    )

            _LOGGER.info(f"Finished management for {slug!r}")


config = _Config()
