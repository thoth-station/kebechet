"""Managers implemented in Kebechet."""

from .update import UpdateManager
from .info import InfoManager

REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager
}
