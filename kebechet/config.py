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

        # TODO: make possible to pass GitLab/GitHub API for each entry
        # TODO: make possible to use different GitLab/GitHub tokens for each entry

    @property
    def github_token(self) -> typing.Union[str, None]:
        """Get provided GitHub OAuth token for use of GitHub API."""
        return self._github_token or os.getenv('GITHUB_OAUTH_TOKEN')

    @github_token.setter
    def github_token(self, token):
        """Set GitHub OAuth token."""
        if token:
            self._github_token = token

    def iter_entries(self):
        """Iterate over repositories listed for updates."""
        for entry in self._repositories or []:
            try:
                # TODO: once we support different github/gitlab APIs and tokens per each, assign changes here
                yield entry['slug'], entry.get('labels'), entry['managers']
            except KeyError:
                _LOGGER.exception("An error in your configuration - ignoring the given configuration entry...")

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet using provided YAML configuration file."""
        global config
        from kebechet.managers import REGISTERED_MANAGERS

        config.from_file(configuration_file)

        for slug, labels, managers in config.iter_entries():
            for manager in managers:
                kebechet_manager = REGISTERED_MANAGERS.get(manager)

                if not kebechet_manager:
                    _LOGGER.error("Unable to find requested manager {manager!r}, skipping")

                _LOGGER.info(f"Running manager {manager!r} for {slug!r}")
                try:
                    kebechet_manager().run(slug, labels)
                except Exception as exc:
                    _LOGGER.exception(
                        f"An error occurred during run of manager {manager!r} {kebechet_manager} for {slug}, skipping"
                    )


config = _Config()
