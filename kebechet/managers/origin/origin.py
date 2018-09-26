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

"""Make sure correct artifacts are downloaded based on Pipfile.lock."""

import logging
import typing
import hashlib

from kebechet.managers.manager import ManagerBase
from kebechet.utils import construct_raw_file_url

from bs4 import BeautifulSoup
import requests
import toml

_LOGGER = logging.getLogger(__name__)
_DEFAULT_WAREHOUSES = ('https://pypi.python.org/simple',)


class _OriginCheckError(Exception):
    """An exception raised if there was a miss-match in computed hashes of artifacts.

    This exception is internal for this manager.
    """


class OriginManager(ManagerBase):
    """Preserve origin of artifacts being used."""

    def __init__(self, *args, **kwargs):
        """Initialize origin manager."""
        self.warehouses = None
        super().__init__(*args, **kwargs)

    def _download_pipfile_lock(self) -> dict:
        """Download Pipfile and Pipfile.lock from repository."""
        _LOGGER.debug("Downloading Pipfile.lock")
        file_url = construct_raw_file_url(self.service_url, self.slug, 'Pipfile.lock', self.service_type)
        response = requests.get(file_url)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _warehouse_api_package_info(package_name: str, package_version: str,
                                    warehouse_url: str, verify_tls: bool) -> dict:
        """Use API of the deployed Warehouse to gather package information."""
        if warehouse_url.endswith('/simple'):
            warehouse_url = warehouse_url[:-len('/simple')] + '/pypi'

        url = f"{warehouse_url}/{package_name}/{package_version}/json"
        _LOGGER.debug("Gathering information from Warehouse API: %r", url)
        response = requests.get(url, verify=verify_tls)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def _download_artifacts_sha(package_name: str, package_version: str, source_url: str,
                                verify_tls: bool) -> typing.Generator[tuple, None, None]:
        """Download the given artifact from Warehouse and compute its SHA."""
        url = f"{source_url}"
        # TODO: uncomment once AICoE index will be fixed
        #url = f"{source_url}/{package_name}/"
        _LOGGER.debug(f"Discovering package %r artifacts from %r", package_name, url)
        response = requests.get(url, verify=verify_tls)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        links = soup.find_all('a')
        for link in links:
            artifact_name = str(link['href']).rsplit('/', maxsplit=1)
            if len(artifact_name) == 2:
                # If full URL provided by index.
                artifact_name = artifact_name[1]
            else:
                artifact_name = artifact_name[0]

            if not artifact_name.startswith(package_name) or not artifact_name.endswith(('.tar.gz', '.whl')):
                _LOGGER.debug("Link does not look like a package for %r: %r", package_name, link['href'])
                continue

            if not artifact_name.startswith(f"{package_name}-{package_version}"):
                # TODO: this logic has to be improved as package version can be a suffix of another package version:
                #   mypackage-1.0.whl, mypackage-1.0.0.whl, ...
                # This will require parsing based on PEP or some better logic.
                _LOGGER.debug("Skipping link based on prefix (not artifact name?): %r", link['href'])
                continue

            artifact_url = f"{url}/{artifact_name}"
            _LOGGER.debug("Downloading artifact from url %r", artifact_url)
            response = requests.get(artifact_url, verify=verify_tls, stream=True)
            response.raise_for_status()

            digest = hashlib.sha256()
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    digest.update(chunk)

            digest = digest.hexdigest()
            _LOGGER.debug("Computed artifact sha256 digest for %r: %s", artifact_url, digest)
            yield artifact_name, digest

    def _check_package_indexes(self, result, package_name, package_version, sources):
        """Check existence of a package on the index and gather SHA of artifacts present there."""
        for source_name, (source_url, verify_tls) in sources.items():
            record = {}
            try:
                if source_url in self.warehouses:
                    package_info = self._warehouse_api_package_info(
                        package_name, package_version, source_url, verify_tls
                    )

                    # Gather all SHA, as pipenv does it this way.
                    for entry in package_info['releases'][package_version]:
                        # pipenv uses 'sha256:' prefix, try to make this compatible.
                        record[entry['filename']] = f"sha256:{entry['digests']['sha256']}"
                else:
                    # We need to explicitly download artifacts and compute their sha256.
                    artifacts = self._download_artifacts_sha(
                        package_name, package_version, source_url, verify_tls=verify_tls
                    )
                    for filename, digest in artifacts:
                        record[filename] = f"sha256:{digest}"

                if not record:
                    _LOGGER.debug(
                        f"No artifact for {package_name} in version {package_version} was found on "
                        f"index {source_name} ({source_url})"
                    )
                    continue

                if source_name not in result:
                    result[source_name] = {}

                if package_name not in result[source_name]:
                    result[source_name][package_name] = {}

                if package_version not in result[source_name][package_name]:
                    result[source_name][package_name][package_version] = {}

                # TODO; check that this record does not exist
                result[source_name][package_name][package_version] = record
            except Exception:  # FIXME: too broad except
                pass

        return result

    def _do_check_locked_packages(self, sources: dict, packages: dict) -> dict:
        artifacts = {}
        for package_name, package_info in packages.items():
            # TODO: handle VCS releases
            package_version = package_info['version']
            if not package_version.startswith('=='):
                raise ValueError("Package version of %r is not properly locked: %r", package_name, package_version)

            package_version = package_info['version'][len('=='):]
            self._check_package_indexes(artifacts, package_name, package_version, sources)

        return artifacts

    def _check_locked_packages(self, pipfile_lock: dict) -> None:
        """Check hashes in of locked packages against configuration stated in Pipfile."""
        # Just to optimize to O(1).
        sources = {}
        for source in pipfile_lock['_meta']['sources']:
            sources[source['name']] = (source['url'], source['verify_ssl'])

        _LOGGER.debug("Found configured sources: %s", sources)

        # TODO: handle default/develop in sane way
        #artifacts = self._do_check_locked_packages(sources, pipfile_lock['develop'])
        artifacts = self._do_check_locked_packages(sources, pipfile_lock['default'])

        # TODO: check against Pipfile.lock so we know which packages are locked in a wrong way
        # TODO: generate a report
        from pprint import pprint
        pprint(artifacts)

    def run(self, warehouses: list = None):
        """Check and, if requested, report origin of installed packages."""
        # We need to download Pipfile as well as it states which index should be used to download packages.
        pipfile_lock = self._download_pipfile_lock()

        # Make warehouse configuration available for methods.
        self.warehouses = warehouses or _DEFAULT_WAREHOUSES
        try:
            self._check_locked_packages(pipfile_lock)
        except _OriginCheckError as exc:
            _LOGGER.exception("There was an error in hash checks")
            # TODO: open an issue


if __name__ == '__main__':
    import daiquiri
    from kebechet.enums import ServiceType
    daiquiri.setup(level=logging.INFO)
    _LOGGER.setLevel(logging.DEBUG)

    instance = OriginManager(
        'fridex/test-aicoe-tensorflow', ServiceType.GITHUB, token='569f642ce9c135363c04d329e52bde96180b1c08'
    )
    instance.run()
