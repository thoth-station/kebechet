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

import logging
import os
import typing

import git
import yaml

from kebechet.managers.manager import ManagerBase
from kebechet.utils import cloned_repo

_LOGGER = logging.getLogger(__name__)

_KEBECHET_CONFIG_FILE_NAME = "kebechet.yml"
_GIT_TOKEN_VARIABLE = "${GIT_SECRET_TOKEN}"
_GIT_BRANCH_NAME = "kebechet-initialization"
_GIT_COMMIT_MESSAGE = "Creating kebechet YAML file"
_GIT_MR_LABELS = ["enhancement"]
_GIT_MR_BODY = """" 
                Creates a YAML file with kebechet settings following this struct:
                
               """


def create_config_file(service_type, slug: str):
    if slug == "":
        _LOGGER.error("Initialization failed due to an error extracting repository slug")
        return

    config = {
        "repositories": [{
            "slug": slug,
            "token": _GIT_TOKEN_VARIABLE,
            "service_type": service_type,
            "managers": []
        }]
    }

    with open("kebechet.yml", "w") as config_file:
        config_file.write(yaml.dump(config, sort_keys=False))


class InitManager(ManagerBase):
    """Manager for initializing Kebechet configs"""

    def run(self, repo_path: str = None, token: str = None, service_type: str = None, slug: str = None)\
            -> typing.Optional[dict]:

        for file_name in os.listdir(repo_path):
            if file_name == _KEBECHET_CONFIG_FILE_NAME:
                _LOGGER.warning(f"There is already a file called {_KEBECHET_CONFIG_FILE_NAME}")

        if self.has_mr_opened(_GIT_BRANCH_NAME):
            _LOGGER.warning(
                f" There is already a new merge Request opened with kebechet YAML file, skipping"
            )
            return

        with cloned_repo(self.service_url, self.slug, depth=1) as repo:

            os.environ[_GIT_TOKEN_VARIABLE] = token
            create_config_file(service_type=service_type, slug=slug)

            repo.git.checkout("-B", _GIT_BRANCH_NAME)

            repo.index.add([_KEBECHET_CONFIG_FILE_NAME])
            repo.index.commit(_GIT_COMMIT_MESSAGE)
            repo.remote().push(_GIT_BRANCH_NAME, force=True)

            request = self.sm.open_merge_request(
                _GIT_COMMIT_MESSAGE,
                _GIT_BRANCH_NAME,
                body=_GIT_MR_BODY,
                labels=_GIT_MR_LABELS
            )

            _LOGGER.info(
                f"Opened merge request with {request.number} for kebechet initialization {self.slug} "
            )

    def has_mr_opened(self, branch_name) -> bool:
        for mr in self.sm.repository.merge_requests:
            if mr.head_branch_name == branch_name:
                return True
        return False
