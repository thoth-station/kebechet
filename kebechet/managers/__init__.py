"""Managers implemented in Kebechet."""

from .update import UpdateManager
from .info import InfoManager
from .approval import ApprovelManager


REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager,
    'approval': ApprovelManager
}
