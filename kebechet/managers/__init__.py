"""Managers implemented in Kebechet."""

from .info import InfoManager
from .update import UpdateManager
from .version import VersionManager
from .pipfile_requirements import PipfileRequirementsManager
from .thoth import ThothManager

REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager,
    'version': VersionManager,
    'pipfile-requirements': PipfileRequirementsManager,
    'thoth': ThothManager
}
