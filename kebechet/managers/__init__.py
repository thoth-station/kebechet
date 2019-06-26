"""Managers implemented in Kebechet."""

from .info import InfoManager
from .update import UpdateManager
from .version import VersionManager
from .pipfile_requirements import PipfileRequirementsManager
from .thoth_advise import ThothAdviseManager
from .thoth_provenance import ThothProvenanceManager
from .advise_results import AdviseResultsManager
from .provenance_results import ProvenanceResultsManager

REGISTERED_MANAGERS = {
    'update': UpdateManager,
    'info': InfoManager,
    'version': VersionManager,
    'pipfile-requirements': PipfileRequirementsManager,
    'thoth-advise': ThothAdviseManager,
    'thoth-provenance': ThothProvenanceManager
}
