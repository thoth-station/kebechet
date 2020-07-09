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
import os
import yaml
import urllib3
import requests
import typing

from .exception import ConfigurationError
from thoth.sourcemanagement.enums import ServiceType
from .services import Service
from .payload_parser import PayloadParser

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Library-wide configuration."""

    def __init__(self):
        self._repositories = None

    def from_file(self, config_path: str):
        if config_path.startswith(("https://", "https://")):
            response = requests.get(config_path)
            response.raise_for_status()
            content = response.text
        else:
            with open(config_path) as config_file:
                content = config_file.read()

        try:
            self._repositories = yaml.safe_load(content).get("repositories") or []
        except Exception as exc:
            raise ConfigurationError(
                "Failed to parse configuration file: {str(exc)}"
            ) from exc

    @staticmethod
    def _managers_from_file(config_path: str):
        with open(config_path) as config_file:
            content = config_file.read()
        try:
            return yaml.safe_load(content).get("managers") or []
        except Exception as exc:
            raise ConfigurationError(
                "Failed to parse configuration file: {str(exc)}"
            ) from exc

    @staticmethod
    def _tls_verify_from_file(config_path: str):
        with open(config_path) as config_file:
            content = config_file.read()

        try:
            return yaml.safe_load(content).get("tls_verify") or False
        except Exception as exc:
            raise ConfigurationError(
                "Failed to parse configuration file: {str(exc)}"
            ) from exc

    @staticmethod
    def download_conf_from_url(url: str, service: str):
        _service_ = Service(service=service, url=url)
        tempfile = _service_.download_kebechet_config()
        return tempfile

    @classmethod
    def run_webhook(cls, payload: dict):
        _payload_ = PayloadParser(payload)
        parsed_payload = _payload_.parsed_data()
        if (
            parsed_payload
            and parsed_payload["url"] is not None
            and parsed_payload["service_type"] is not None
        ):
            cls.run_url(
                parsed_payload["url"],
                parsed_payload["service_type"],
                parsed_payload,
                True,
            )

    @classmethod
    def run_url(cls, url: str, service: str, parsed_payload: dict, tls_verify: bool):
        temp_file = cls.download_conf_from_url(url, service)
        _LOGGER.debug("Filename = %s", temp_file.name)

        global config
        from kebechet.managers import REGISTERED_MANAGERS

        tempfile = config.download_conf_from_url(url, service)
        managers = cls._managers_from_file(tempfile.name)

        # If called from run_webhook tls verify is always true.
        if tls_verify is None:
            tls_verify = cls._tls_verify_from_file(tempfile.name)

        scheme, _, host, _, slug, _, _ = urllib3.util.parse_url(url)
        slug = slug[1:]
        service_url = f"{scheme}://{host}"

        cls._tls_verification(service_url, slug, verify=tls_verify)

        if service_url and not service_url.startswith(("https://", "http://")):
            # We need to have this explicitly set for IGitt and also for security reasons.
            _LOGGER.error(
                "You have to specify protocol ('https://' or 'http://') in service URL "
                "configuration entry - invalid configuration %r",
                service_url,
            )

        if service_url and service_url.endswith("/"):
            service_url = service_url[:-1]

        _service_ = Service(service, url)
        token = _service_.token
        _LOGGER.debug("Using token %r%r", token[:3], "*" * len(token[3:]))

        for manager in managers:
            # We do pops on dict, which changes it. Let's create a soft duplicate so if a user uses
            # YAML references, we do not break.
            manager = dict(manager)
            try:
                manager_name = manager.pop("name")
            except Exception:
                _LOGGER.exception(
                    "No manager name provided in configuration entry for %r, ignoring entry",
                    slug,
                )
                continue
            kebechet_manager = REGISTERED_MANAGERS.get(manager_name)
            if not kebechet_manager:
                _LOGGER.error(
                    "Unable to find requested manager %r, skipping", manager_name
                )
                continue
            _LOGGER.info(f"Running manager %r for %r", manager_name, slug)
            manager_configuration = manager.get("configuration") or {}
            if manager:
                _LOGGER.warning(
                    "Ignoring option %r in manager entry for %r", manager, slug
                )
            try:
                instance = kebechet_manager(
                    slug, _service_.service, service_url, parsed_payload, token
                )
                instance.run(**manager_configuration)
            except Exception as exc:  # noqa F841
                _LOGGER.exception(
                    "An error occurred during run of manager %r %r for %r, skipping",
                    manager,
                    kebechet_manager,
                    slug,
                )

        temp_file.close()

    def iter_entries(self) -> typing.Iterable[typing.Tuple]:
        """Iterate over repositories listed."""
        for entry in self._repositories or []:
            try:
                items = dict(entry)
                value = (
                    items.get("managers") or [],
                    items.get("slug") or None,
                    items.get("service_type") or None,
                    items.get("service_url") or None,
                    items.get("token") or None,
                    items.get("tls_verify") or True,
                )

                if items:
                    _LOGGER.warning(
                        "Unknown configuration entry in configuration of %r: %r",
                        value[1],
                        items,
                    )

                yield value
            except KeyError:
                _LOGGER.exception(
                    "An error in your configuration - ignoring the given configuration entry..."
                )

    @staticmethod
    def _tls_verification(service_url: str, slug: str, verify: bool) -> None:
        """Turn off or on TLS verification based on configuration."""
        # We manage our own warnings, of course better ones!
        urllib3.disable_warnings()
        if not verify:
            _LOGGER.warning(
                "Turning off TLS certificate verification for %r hosted at %r",
                slug,
                service_url,
            )

        # Please close your eyes when reading this - it's pretty ugly solution but is somehow applicable to
        # the IGitt's handling of these methods.
        original_post = requests.Session.post
        original_delete = requests.Session.delete
        original_put = requests.Session.put
        original_get = requests.Session.get
        original_head = requests.Session.head
        original_patch = requests.Session.patch

        def post(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_post(*args, **kwargs, verify=verify)

        requests.Session.post = post  # type: ignore

        def delete(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_delete(*args, **kwargs, verify=verify)

        requests.Session.delete = delete  # type: ignore

        def put(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_put(*args, **kwargs, verify=verify)

        requests.Session.put = put  # type: ignore

        def get(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_get(*args, **kwargs, verify=verify)

        requests.Session.get = get  # type: ignore

        def head(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_head(*args, **kwargs, verify=verify)

        requests.Session.head = head  # type: ignore

        def patch(*args, **kwargs):
            kwargs.pop("verify", None)
            return original_patch(*args, **kwargs, verify=verify)

        requests.Session.patch = patch  # type: ignore

    @classmethod
    def run_analysis(cls, analysis_id: str, origin: str, service: str) -> None:
        """Run result managers (meant to be triggered automatically)."""
        global config
        from kebechet.managers import ThothAdviseManager, ThothProvenanceManager

        tempfile = config.download_conf_from_url(origin, service)
        managers = _Config._managers_from_file(tempfile.name)
        tls_verify = _Config._tls_verify_from_file(tempfile.name)

        scheme, _, host, _, slug, _, _ = urllib3.util.parse_url(origin)
        slug = slug[1:]
        service_url = f"{scheme}://{host}"

        cls._tls_verification(service_url, slug, verify=tls_verify)

        if service_url and not service_url.startswith(("https://", "http://")):
            # We need to have this explicitly set for IGitt and also for security reasons.
            _LOGGER.error(
                "You have to specify protocol ('https://' or 'http://') in service URL "
                "configuration entry - invalid configuration %r",
                service_url,
            )

        if service_url and service_url.endswith("/"):
            service_url = service_url[:-1]

        _service_ = Service(service, origin)
        token = _service_.token
        _LOGGER.debug("Using token %r%r", token[:3], "*" * len(token[3:]))

        kebechet_manager: typing.Union[
            typing.Type[ThothAdviseManager], typing.Type[ThothProvenanceManager]
        ]
        for manager in managers:
            manager_name = manager.pop("name")
            if analysis_id.startswith("adviser") and manager_name == "thoth-advise":
                kebechet_manager = ThothAdviseManager
                break
            elif (
                analysis_id.startswith("provenance")
                and manager_name == "thoth-provenance"
            ):
                kebechet_manager = ThothProvenanceManager
                break
            else:
                _LOGGER.debug(
                    "Manager %r does not correspond with id:%r, skipping",
                    manager_name,
                    analysis_id,
                )
        else:
            _LOGGER.error("No manager configuration found for id: %r", analysis_id)
            return

        manager_config = manager.get("configuration") or {}
        manager_config["analysis_id"] = analysis_id
        # TODO: Fail if users add config entries not relative to given manager (open an issue)
        instance = kebechet_manager(slug, _service_.service, service_url, token)
        instance.run(**manager_config)

    @classmethod
    def run(cls, configuration_file: str) -> None:
        """Run Kebechet using provided YAML configuration file."""
        global config
        from kebechet.managers import REGISTERED_MANAGERS

        config.from_file(configuration_file)

        for (
            managers,
            slug,
            service_type,
            service_url,
            token,
            tls_verify,
        ) in config.iter_entries():
            cls._tls_verification(service_url, slug, verify=tls_verify)

            if service_url and not service_url.startswith(("https://", "http://")):
                # We need to have this explicitly set for IGitt and also for security reasons.
                _LOGGER.error(
                    "You have to specify protocol ('https://' or 'http://') in service URL "
                    "configuration entry - invalid configuration {service_url!}"
                )
                continue

            if service_url and service_url.endswith("/"):
                service_url = service_url[:-1]

            if token:
                # Allow token expansion based on env variables.
                token = token.format(**os.environ)
                _LOGGER.debug("Using token '%r%r'", token[:3], "*" * len(token[3:]))

            for manager in managers:
                # We do pops on dict, which changes it. Let's create a soft duplicate so if a user uses
                # YAML references, we do not break.
                manager = dict(manager)
                try:
                    manager_name = manager.pop("name")
                except Exception:
                    _LOGGER.exception(
                        "No manager name provided in configuration entry for %r, ignoring entry",
                        slug,
                    )
                    continue

                kebechet_manager = REGISTERED_MANAGERS.get(manager_name)
                if not kebechet_manager:
                    _LOGGER.error(
                        "Unable to find requested manager %r, skipping", manager_name
                    )
                    continue

                _LOGGER.info(f"Running manager %r for %r", manager_name, slug)
                manager_configuration = manager.get("configuration") or {}
                if manager:
                    _LOGGER.warning(
                        "Ignoring option %r in manager entry for %r", manager, slug
                    )

                try:
                    instance = kebechet_manager(
                        # The service type is set by default to github.
                        slug,
                        ServiceType.by_name(service_type),
                        service_url,
                        None,
                        token,
                    )
                    instance.run(**manager_configuration)
                except Exception as exc:  # noqa F841
                    _LOGGER.exception(
                        "An error occurred during run of manager %r %r for %r, skipping",
                        manager,
                        kebechet_manager,
                        slug,
                    )
            _LOGGER.info("Finished management for %r", slug)


config = _Config()
