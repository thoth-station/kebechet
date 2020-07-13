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

"""Common and useful utilities for managers."""

import logging
import platform
import typing
import git

import delegator
import kebechet

from kebechet.exception import PipenvError
from thoth.sourcemanagement.enums import ServiceType
from thoth.sourcemanagement.sourcemanagement import SourceManagement


_LOGGER = logging.getLogger(__name__)


def _init_service_url(service_type: ServiceType = None, service_url: str = None) -> str:
    """Needed for the cron job to initialize the service_url if not provided."""
    if service_type == ServiceType.GITHUB:
        service_url = service_url or "https://github.com"
    elif service_type == ServiceType.GITLAB:
        service_url = service_url or "https://gitlab.com"
    else:
        raise NotImplementedError

    return service_url


class ManagerBase:
    """A base class for manager instances holding common and useful utilities."""

    def __init__(
        self,
        slug,
        service_type: ServiceType = None,
        service_url: str = None,
        parsed_payload: dict = None,
        token: str = None,
    ):
        """Initialize manager instance for talking to services."""
        self.service_type = service_type or ServiceType.GITHUB
        # This needs to be called before instantiation of service url, if not provided.
        self.service_url = _init_service_url(service_type, service_url)
        # Allow token expansion from env vars.
        self.slug = slug
        # Parsed payload structure can be accessed in payload_parser.py
        self.parsed_payload = None
        if parsed_payload:
            self.parsed_payload = parsed_payload
        self.owner, self.repo_name = self.slug.split("/", maxsplit=1)
        self.sm = SourceManagement(self.service_type, self.service_url, token, slug)
        self._repo = None

    @property
    def repo(self):
        """Get repository on which we work on."""
        return self._repo

    @repo.setter
    def repo(self, repo: git.Repo):
        """Set repository information and all derived information needed."""
        self._repo = repo
        self.slug = repo.remote().url.split(":", maxsplit=1)[1][: -len(".git")]

    @classmethod
    def get_environment_details(
        cls, as_dict=False
    ) -> typing.Union[str, typing.Dict[str, str]]:
        """Get details for environment in which Kebechet runs."""
        try:
            pipenv_version = cls.run_pipenv("pipenv --version")
        except PipenvError as exc:
            pipenv_version = f"Failed to obtain pipenv version:\n{exc.stderr}"

        return (
            f"""
Kebechet version: {kebechet.__version__}
Python version: {platform.python_version()}
Platform: {platform.platform()}
pipenv version: {pipenv_version}
"""
            if not as_dict
            else {
                "kebechet_version": kebechet.__version__,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "pipenv_version": pipenv_version,
            }
        )

    @staticmethod
    def run_pipenv(cmd: str):
        """Run pipenv, raise :ref:kebechet.exception.PipenvError on any error holding all the information."""
        _LOGGER.debug(f"Running pipenv command {cmd!r}")
        result = delegator.run(cmd)
        if result.return_code != 0:
            _LOGGER.warning(result.err)
            raise PipenvError(result)

        return result.out

    @classmethod
    def get_dependency_graph(cls, graceful: bool = False):
        """Get dependency graph of the project."""
        try:
            cls.run_pipenv("pipenv install --dev --skip-lock")
            return cls.run_pipenv("pipenv graph")
        except PipenvError as exc:
            if not graceful:
                raise
            return f"Unable to obtain dependency graph:\n\n{exc.stderr}"

    def run(self, labels: list) -> typing.Optional[dict]:
        """Run the given manager implementation."""
        raise NotImplementedError
