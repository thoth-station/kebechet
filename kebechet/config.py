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
import typing
import yaml

import requests

from .exception import ConfigurationError
from .enums import ServiceType

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Library-wide configuration."""

    def __init__(self):
        self._github_token = None
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
                    items.pop('labels', [])

                if items:
                    _LOGGER.warning(f"Unknown configuration entry in configuration of {slug!r}: {items}")

                yield value
            except KeyError:
                _LOGGER.exception("An error in your configuration - ignoring the given configuration entry...")

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet using provided YAML configuration file."""
        global config
        from kebechet.managers import REGISTERED_MANAGERS

        config.from_file(configuration_file)

        for managers, slug, service_type, service_url, token, labels in config.iter_entries():
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
                token.format(**os.environ)

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


config = _Config()
