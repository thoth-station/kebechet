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

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Library-wide configuration."""

    def __init__(self):
        self._update = None
        self._github_token = None

    def from_file(self, config_path: str):
        if config_path.startswith(('https://', 'https://')):
            response = requests.get(config_path)
            response.raise_for_status()
            content = response.text
        else:
            with open(config_path) as config_file:
                content = config_file.read()

        try:
            content = yaml.load(content)
        except Exception as exc:
            raise ConfigurationError("Failed to parse configuration file: {str(exc)}") from exc

        self._update = content.pop('update', None) or []
        self.github_token = content.pop('github_token', None)

        if content:
            _LOGGER.warning(f"Ingoring unknown configuration found in the YAML configuration file: {content}")

    @property
    def github_token(self) -> typing.Union[str, None]:
        """Get provided GitHub OAuth token for use of GitHub API."""
        return self._github_token or os.getenv('GITHUB_OAUTH_TOKEN')

    @github_token.setter
    def github_token(self, token):
        """Set GitHub OAuth token."""
        if token:
            self._github_token = token

    def iter_update(self):
        """Iterate over repositories listed for updates."""
        for update_entry in self._update or []:
            try:
                yield update_entry['slug'], update_entry.get('label')
            except KeyError:
                _LOGGER.exception("An error in your configuration - slug was not provided, ignoring...")

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet respecting configuration provided in Kebechet YAML configuration."""
        global config
        from .update import update

        config.from_file(configuration_file)

        for slug, label in config.iter_update():
            try:
                update(slug, label)
            except Exception as exc:
                _LOGGER.exception(f"An error occurred during update of {slug}")


config = _Config()
