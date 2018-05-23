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

import logging

import click
import daiquiri

from kebechet import __version__ as kebechet_version
from kebechet import update

daiquiri.setup(level=logging.INFO)

_LOGGER = logging.getLogger('kebechet')


def _print_version(ctx, _, value):
    """Print Kebechet version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(kebechet_version)
    ctx.exit()


@click.command()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True,
              help="Be verbose about what's going on.")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print version and exit.")
@click.option('--repository', type=str, default=None, metavar='SLUG',
              help="A GitHub slug in a form of (org/repo) to check for updates.")
@click.option('--config', type=str, default=None, metavar='kebechet.yaml',
              help="A path to Kebechet configuration (can be also a URL).")
def cli(ctx=None, verbose=0, repository=None, config=None):
    """"""
    if ctx:
        ctx.auto_envvar_prefix = 'KEBECHET'

    if verbose:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode turned on")
        _LOGGER.debug(f"Passed options: {locals()}")

    update(repository)


if __name__ == '__main__':
    cli()
