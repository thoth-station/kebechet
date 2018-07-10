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

"""Common and useful utilities for managers."""

import logging
import platform
import typing

import delegator
import kebechet

from kebechet.exception import PipenvError

_LOGGER = logging.getLogger(__name__)


class Manager:
    """A base class for manager instances holding common and useful utilities."""

    @classmethod
    def get_environment_details(cls, as_dict=False) -> str:
        """Get details for environment in which Kebechet runs."""
        try:
            pipenv_version = cls.run_pipenv('pipenv --version')
        except PipenvError as exc:
            pipenv_version = f"Failed to obtain pipenv version:\n{exc.stderr}"

        return f"""
    Kebechet version: {kebechet.__version__}
    Python version: {platform.python_version()}
    Platform: {platform.platform()}
    pipenv version: {pipenv_version}
    """ if not as_dict else {
            'kebechet_version': kebechet.__version__,
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'pipenv_version': pipenv_version
        }

    @staticmethod
    def run_pipenv(cmd: str):
        """Run pipenv, raise :ref:kebechet.exception.PipenvError on any error holding all the information."""
        _LOGGER.debug(f"Running pipenv command {cmd!r}")
        result = delegator.run(cmd)
        if result.return_code != 0:
            _LOGGER.error(result.err)
            raise PipenvError(result)

        return result.out

    @classmethod
    def get_dependency_graph(cls, graceful: bool = False):
        """Get dependency graph of the project."""
        try:
            cls.run_pipenv('pipenv install --dev --skip-lock')
            return cls.run_pipenv('pipenv graph')
        except PipenvError as exc:
            if not graceful:
                raise
            return f"Unable to obtain dependency graph:\n\n{exc.stderr}"

    def run(self, slug: str, labels: list) -> typing.Optional[dict]:
        """Run the given manager implementation."""
        raise NotImplementedError
