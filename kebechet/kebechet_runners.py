#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018, 2019, 2020, 2021 Fridolin Pokorny, Kevin Postlethwait
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

"""Methods for running Kebechet."""

import logging
import os
import urllib3
from typing import Dict, Any, List, Optional, Tuple

from .utils import (
    download_kebechet_config,
    create_ogr_service,
    _create_issue_from_exception,
)
from .payload_parser import PayloadParser
from .config import _Config

from kebechet.managers import (
    REGISTERED_MANAGERS,
    ConfigInitializer,
    ManagerFailedException,
)
from . import __version__ as keb_version
from github import GithubException
from requests.exceptions import SSLError

_LOGGER = logging.getLogger("kebechet")


def _parse_url_4_args(url: str) -> Tuple[str, str, str, str]:
    """
    Parse url for args required by kebechet_runners.run(...).

    args:
    url to remote git repository

    returns:
    tuple: (slug, namespace, project, service_url)
    """
    scheme, _, host, _, slug, _, _ = urllib3.util.parse_url(url)
    slug = slug[1:]
    namespace = slug.split("/")[0]
    project = slug.split("/")[1]

    service_url = f"{scheme}://{host}"

    return (slug, namespace, project, service_url)


def run_webhook(payload: Dict[str, Any]):
    """Run Kebechet using payload from webhook."""
    _payload_ = PayloadParser(payload)
    parsed_payload = _payload_.parsed_data()

    if parsed_payload is not None:
        url = parsed_payload.get("url")  # type: Optional[str]
        service_type = parsed_payload.get("service_type")  # type: Optional[str]
    else:
        url = None
        service_type = None

    if parsed_payload and (url is not None) and (service_type is not None):
        run_url(url, service_type, parsed_payload)
    else:
        raise ValueError(
            "The parsed payload is missing required values:\n"
            f"payload exists: {bool(parsed_payload)}\n"
            f"payload['url'] is present: {url is not None}\n"  # type: ignore
            f"payload['service_type'] is present: {service_type is not None}"  # type: ignore
        )


def run_url(
    url: str,
    service: str,
    parsed_payload: Optional[Dict[str, Any]] = None,
    kebechet_metadata: Optional[Dict[str, Any]] = None,
    analysis_id: Optional[str] = None,
    runtime_environment: Optional[str] = None,
):
    """Run Kebechet by specifying URL of repository to run on."""
    slug, namespace, project, service_url = _parse_url_4_args(url)

    run(
        service_type=service,
        service_url=service_url,
        namespace=namespace,
        project=project,
        parsed_payload=parsed_payload,
        metadata=kebechet_metadata,
        analysis_id=analysis_id,
        runtime_environment=runtime_environment,
    )


def run_analysis(
    analysis_id: str,
    origin: str,
    service: str,
    runtime_environment: Optional[str] = None,
) -> None:
    """Run result managers (meant to be triggered automatically)."""
    slug, namespace, project, service_url = _parse_url_4_args(origin)

    run(
        service_type=service,
        service_url=service_url,
        namespace=namespace,
        project=project,
        enabled_managers=["thoth-provenance", "thoth-advise"],
        analysis_id=analysis_id,
        runtime_environment=runtime_environment,
    )


def run(
    service_type: str,
    namespace: str,
    project: str,
    service_url: Optional[str],
    enabled_managers: List[str] = list(REGISTERED_MANAGERS.keys()),
    parsed_payload: Optional[Dict[Any, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    analysis_id: Optional[str] = None,
    runtime_environment: Optional[str] = None,
) -> None:
    """Run Kebechet using provided YAML configuration file."""
    token = os.getenv(f"{service_type.upper()}_KEBECHET_TOKEN")

    ogr_service = create_ogr_service(
        service_type=service_type,
        service_url=service_url,
        token=token,
        github_app_id=os.getenv("GITHUB_APP_ID"),
        github_private_key_path=os.getenv("GITHUB_PRIVATE_KEY_PATH"),
    )

    slug = f"{namespace}/{project}"

    try:
        with download_kebechet_config(ogr_service, namespace, project) as f:
            config = _Config.from_file(f)
    except FileNotFoundError:
        _LOGGER.info("No Kebechet found in repo. Opening PR with simple configuration.")
        ConfigInitializer(
            slug=slug,
            service=ogr_service,
            service_type=service_type,
        ).run()
        return

    managers = config.managers

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

        if manager_name not in enabled_managers:
            _LOGGER.debug(
                "Skipping manager %r because it is not in the list of enabled managers.",
                manager_name,
            )
            continue

        kebechet_manager = REGISTERED_MANAGERS.get(manager_name)
        if not kebechet_manager:
            _LOGGER.error("Unable to find requested manager %r, skipping", manager_name)
            continue

        _LOGGER.info("Running manager %r for %r", manager_name, slug)
        manager_configuration = manager.get("configuration") or {}

        if analysis_id:
            manager_configuration["analysis_id"] = analysis_id

        try:
            if manager_configuration.get("enabled", True):
                instance = kebechet_manager(
                    slug=slug,
                    service=ogr_service,
                    service_type=service_type,
                    parsed_payload=parsed_payload,
                    metadata=metadata,
                    runtime_environment=runtime_environment,
                )
                instance.run(**manager_configuration)
        except Exception as exc:  # noqa F841
            _LOGGER.exception(
                "An error occurred during run of manager %r %r for %r, skipping",
                manager,
                kebechet_manager,
                slug,
            )
            if (
                isinstance(exc, GithubException)
                and exc.status == 410
                and isinstance(exc.data, dict)
                and (message := exc.data.get("message")) is not None
                and "issue" in message.lower()  # type: ignore
                and "disable" in message.lower()  # type: ignore
            ):
                _LOGGER.info("Cannot open issue because it is disabled on this repo.")
                continue
            elif isinstance(exc, GithubException) and exc.status >= 500:
                raise exc  # reraise server error as the response could be flaky (behaviour dependent on retry policy).
            elif isinstance(exc, ConnectionError):
                continue
            elif isinstance(exc, SSLError):
                continue
            elif isinstance(exc, ManagerFailedException):
                continue

            _create_issue_from_exception(
                keb_version=keb_version,
                manager_name=manager_name,
                ogr_service=ogr_service,
                slug=slug,
                exc=exc,
            )

    _LOGGER.info("Finished management for %r", slug)
