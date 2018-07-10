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


"""This will handle al the GitHub webhooks."""

import os
from flask import Flask

from .enums import ServiceType
from .managers import UpdateManager, InfoManager
from .webhooks import webhook


__name__ = 'kebechet'
__version__ = '1.1.0-dev'
__author__ = 'Fridolin Pokorny <fridolin.pokorny@gmail.com>'


def create_webhook_receiver():
    """Create, configure and return the Flask application."""
    app = Flask(__name__)
    app.config['KEBECHET_GITHUB_WEBHOOK_SECRET'] = os.environ.get(
        'KEBECHET_GITHUB_WEBHOOK_SECRET')
    app.register_blueprint(webhook)

    return(app)
