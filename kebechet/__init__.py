"""Update dependencies stated in the Pipfile.lock for the given repo or repositories."""

from thoth.sourcemanagement.enums import ServiceType  # noqa F401
from .managers import InfoManager  # noqa F401
from .managers import UpdateManager  # noqa F401

__name__ = "kebechet"
__version__ = "1.0.7"
__author__ = "Fridolin Pokorny <fridolin.pokorny@gmail.com>"
