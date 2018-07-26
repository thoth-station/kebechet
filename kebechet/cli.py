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

"""The Command Line Interface."""


import logging

import click
import daiquiri

from kebechet import __version__ as kebechet_version
from kebechet.config import config

daiquiri.setup(level=logging.INFO)

_LOGGER = logging.getLogger('kebechet')


def _print_version(ctx, _, value):
    """Print Kebechet version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(kebechet_version)
    ctx.exit()


@click.group()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, envvar='KEBECHET_VERBOSE',
              help="Be verbose about what's going on.")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print version and exit.")
def cli(ctx=None, verbose=0):
    """The CLI."""
    if ctx:
        ctx.auto_envvar_prefix = 'KEBECHET'

    if verbose:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode turned on")


@cli.command('run')
@click.argument('configuration', metavar='config', envvar='KEBECHET_CONFIGURATION_PATH')
def cli_run(configuration):
    """Run Kebechet using provided YAML configuration file."""
    config.run(configuration)


if __name__ == '__main__':
    cli()
