#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
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
import yaml
import requests
import typing
from typing import Dict, Any, TextIO
from .exception import ConfigurationError

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Library-wide configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @classmethod
    def from_file(cls, f: typing.Union[str, TextIO]):
        if isinstance(f, str):
            if f.startswith(("https://", "https://")):
                response = requests.get(f)
                response.raise_for_status()
                content = response.text
            else:
                with open(f) as config_file:
                    content = config_file.read()
        elif hasattr(f, "read"):
            content = f.read()
        else:
            raise ValueError("Type of f must be Union[str, TextIO].")

        try:
            return _Config(yaml.safe_load(content))
        except Exception as exc:
            raise ConfigurationError(
                "Failed to parse configuration file: {str(exc)}"
            ) from exc

    @property
    def managers(self):
        return self.config.get("managers") or []

    @property
    def tls_verify(self):
        return self.config.get("tls_verify") or False
