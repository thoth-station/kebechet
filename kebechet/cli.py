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

"""The Command Line Interface."""


import logging
import os
from typing import Optional

import click
import json
from thoth.common import init_logging
from kebechet.exception import WebhookPayloadError

from kebechet import __version__ as kebechet_version
from kebechet.kebechet_runners import run, run_url, run_webhook, run_analysis

init_logging(logging_env_var_start="KEBECHET_LOG_")

_LOGGER = logging.getLogger("kebechet")


def _print_version(ctx, _, value):
    """Print Kebechet version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(kebechet_version)
    ctx.exit()


@click.group()
@click.pass_context
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    envvar="KEBECHET_VERBOSE",
    help="Be verbose about what's going on.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print version and exit.",
)
def cli(ctx=None, verbose=0):
    """CLI."""
    if ctx:
        ctx.auto_envvar_prefix = "KEBECHET"

    _LOGGER.info("Kebechet version: %r", kebechet_version)

    if verbose:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode turned on")


@cli.command("run")
@click.option("-s", "--service", envvar="KEBECHET_SERVICE_NAME", required=True)
@click.option("-n", "--namespace", envvar="KEBECHET_PROJECT_NAMESPACE", required=True)
@click.option("-p", "--project", envvar="KEBECHET_PROJECT_NAME", required=True)
@click.option("-u", "--service-url", envvar="KEBECHET_SERVICE_URL")
@click.option("-e", "--runtime-environment", envvar="KEBECHET_RUNTIME_ENVIRONMENT")
def cli_run(
    service: str,
    namespace: str,
    project: str,
    service_url: Optional[str] = None,
    runtime_environment: Optional[str] = None,
):
    """Run Kebechet using provided YAML configuration file."""
    run(
        service_type=service,
        namespace=namespace,
        project=project,
        service_url=service_url,
        runtime_environment=runtime_environment,
    )


@cli.command("run-results")
@click.option("-o", "--origin", envvar="KEBECHET_REPO_URL", required=True)
@click.option("-s", "--service", envvar="KEBECHET_SERVICE_NAME", required=True)
@click.option(
    "-i", "--analysis_id", metavar="id", envvar="KEBECHET_ANALYSIS_ID", required=True
)
@click.option(
    "-m", "--thoth-adviser-metadata", envvar="THOTH_ADVISER_METADATA", required=True
)
@click.option("-e", "--runtime-environment", envvar="KEBECHET_RUNTIME_ENVIRONMENT")
def cli_run_results(
    origin: str,
    service: str,
    analysis_id: str,
    thoth_adviser_metadata: str,
    runtime_environment: Optional[str] = None,
):
    """Run Kebechet after results are received (meant to be triggered automatically)."""
    kebechet_metadata = json.loads(thoth_adviser_metadata)["kebechet_metadata"]
    run_analysis(
        analysis_id=analysis_id,
        origin=origin,
        service=service,
        kebechet_metadata=kebechet_metadata,
        runtime_environment=runtime_environment,
    )


@cli.command("run-url")
@click.option(
    "-u",
    "--url",
    envvar="KEBECHET_REPO_URL",
)
@click.option("-s", "--service", envvar="KEBECHET_SERVICE_NAME")
@click.option("-m", "--metadata", envvar="KEBECHET_METADATA")
@click.option("-e", "--runtime-environment", envvar="KEBECHET_RUNTIME_ENVIRONMENT")
def cli_run_url(
    url: str,
    service: str,
    metadata: Optional[str] = None,
    runtime_environment: Optional[str] = None,
):
    """Run Kebechet by providing url to a git repository service."""
    if metadata is not None:
        meta = json.loads(metadata)
    else:
        meta = None
    run_url(
        url=url,
        service=service,
        kebechet_metadata=meta,
        runtime_environment=runtime_environment,
    )


@cli.command("run-webhook")
@click.argument("web_payload", nargs=1, envvar="KEBECHET_PAYLOAD", required=True)
def cli_run_webhook(web_payload: str):
    """Run Kebechet by providing a webhook payload."""
    payload = None
    if os.path.isfile(web_payload):
        with open(web_payload) as f:
            payload = json.load(f)
    else:
        # If the json is passed a string.
        payload = json.loads(web_payload)
    if not payload:
        raise WebhookPayloadError("Webhook payload is empty or cannot be parsed.")
    run_webhook(payload=payload)


if __name__ == "__main__":
    cli()
