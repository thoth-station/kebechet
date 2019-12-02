#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2019 Ronan Souza
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

"""Initialize your Kebechet by creating a YAML file."""

import logging
import os
import typing

from kebechet.managers.manager import ManagerBase
from kebechet.utils import cloned_repo
from .util import (
    _GIT_TOKEN_VARIABLE,
    _GIT_BRANCH_NAME,
    _GIT_COMMIT_MESSAGE,
    _GIT_MR_BODY,
    _GIT_MR_LABELS,
    _KEBECHET_CONFIG_FILE_NAME,
    create_config_file,
)

_LOGGER = logging.getLogger(__name__)


class InitManager(ManagerBase):
    """Manager for initializing Kebechet config file."""

    def run(
            self,
            token: str = None,
            service_type: str = None,
            slug: str = None,
            managers: str = None,
    ) -> typing.Optional[dict]:
        """Run the Initialization Manager."""
        if self.has_mr_opened(_GIT_BRANCH_NAME):
            return

        for file_name in os.listdir(os.getcwd()):
            if file_name == _KEBECHET_CONFIG_FILE_NAME:
                _LOGGER.warning(
                    f"There is already a file called {_KEBECHET_CONFIG_FILE_NAME}"
                )

        with cloned_repo(self.service_url, self.slug, depth=1) as repo:
            os.environ[_GIT_TOKEN_VARIABLE] = token

            valid_managers = self.__get_valid_managers(managers)

            create_config_file(
                service_type=service_type, slug=self.slug, managers=valid_managers
            )

            repo.git.checkout("-b", _GIT_BRANCH_NAME)

            repo.index.add([_KEBECHET_CONFIG_FILE_NAME])
            repo.index.commit(_GIT_COMMIT_MESSAGE)
            repo.remote().push(_GIT_BRANCH_NAME, force=True)

            request = self.sm.open_merge_request(
                _GIT_COMMIT_MESSAGE,
                _GIT_BRANCH_NAME,
                body=_GIT_MR_BODY.format(
                    file_name=_KEBECHET_CONFIG_FILE_NAME,
                    tls_verify="false",
                    managers="NOT_IMPLEMENTED_YET",
                ),
                labels=_GIT_MR_LABELS,
            )

            _LOGGER.info(
                f"Opened merge request with {request.number} for kebechet initialization {self.slug} "
            )

    def has_mr_opened(self, branch_name) -> bool:
        """Check if has already a Merge Request from a given branch."""
        for mr in self.sm.repository.merge_requests:
            if mr.head_branch_name == branch_name:
                _LOGGER.exception(
                    f" There is already a new merge Request opened with kebechet YAML file, skipping"
                )
                return True
        return False

    def __get_valid_managers(self, managers: str) -> typing.List[str]:
        from kebechet.managers import REGISTERED_MANAGERS

        valid_managers = []
        if managers is None:
            return valid_managers
        managers = managers.split(",")
        for manager in managers:
            if manager not in REGISTERED_MANAGERS:
                _LOGGER.warning(
                    f"There is no manager called {manager}, ignoring it"
                )
            else:
                valid_managers.append(manager)

        return valid_managers
