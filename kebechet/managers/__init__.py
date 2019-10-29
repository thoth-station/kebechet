"""Managers implemented in Kebechet."""

from .initialization import InitManager
from .info import InfoManager
from .update import UpdateManager
from .version import VersionManager
from .pipfile_requirements import PipfileRequirementsManager
from .thoth_advise import ThothAdviseManager
from .thoth_provenance import ThothProvenanceManager

REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager,
    'version': VersionManager,
    'pipfile-requirements': PipfileRequirementsManager,
    'thoth-advise': ThothAdviseManager,
    'thoth-provenance': ThothProvenanceManager,
    'init': InitManager
}
