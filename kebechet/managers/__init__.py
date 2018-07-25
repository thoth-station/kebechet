"""Managers implemented in Kebechet."""

from .info import InfoManager
from .update import UpdateManager
from .version import VersionManager

REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager,
    'version': VersionManager,
}
