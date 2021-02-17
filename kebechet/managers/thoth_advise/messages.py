#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2020 Kevin Postlethwait
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

"""Body of issues and pull requests automatically opened."""

DEFAULT_PR_BODY = (
    """Automatic update of Pipfile.lock by Kebechet thoth-advise manager."""
)

MISSING_PACKAGE_VERSION_PR_BODY = """
Version {version} of {package} has gone missing from {index}.  This package is currently used in your project.

Thoth has automatically run `advise` on your repository as a result. This PR contains an automatic update of \
Pipfile.lock by Kebechet thoth-advise manager.
"""

MISSING_PACKAGE_VERSION_ISSUE_BODY = """
Version {version} of {package} has gone missing from {index}. This package is currently used by your project.

This has caused your application stack to become unsolvable. Please loosen your version constraints for {package}.
"""

NEW_CVE_PR_BODY = """
Project Thoth registered new CVE for version {version} of {package}. This package is currently used in your project.

Thoth has automatically run `advise` on your repository as a result. This PR contains an automatic update of \
Pipfile.lock by Kebechet thoth-advise manager.
"""

NEW_CVE_ISSUE_BODY = """
Project Thoth registered new CVE for version {version} of {package}. This package is currently used by your project.

This has caused your application stack to become unsolvable. Please loosen your version constraints for {package} or \
change your recommendation type.
"""

MISSING_PACKAGE_PR_BODY = """
{package} has gone missing from {index}. This package was being used by your project as a transitive dependency.

Thoth was able to find versions of dependencies to avoid using {package} in the locked application stack. This PR \
contains an automatic update of Pipfile.lock by Kebechet thoth-advise manager.
"""

MISSING_PACKAGE_ISSUE_BODY = """
{package} has gone missing from {index}. This package is currently used in your project. This issue is critical and \
will result in failed builds.

Please find another index which hosts this package or refactor to use a different library.
"""

HASH_MISMATCH_PR_BODY = """
Version {version} of {package} on {index} has hashes which no longer match those stored in Thoth's database. This \
indicates that the package maintainers likely added or removed an artifact (binary).

Thoth has automatically run `advise` on your repository as a result. This PR contains an automatic update of \
Pipfile.lock by Kebechet thoth-advise manager.
"""

HASH_MISMATCH_ISSUE_BODY = """
Version {version} of {package} on {index} has hashes which no longer match those stored in Thoth's database. This \
indicates that package maintainers likely removed an artifact (binary).

This has caused your application stack to become unsolvable. Please loosen version constraints or change your runtime \
environment.
"""

NEW_RELEASE_PR_BODY = """
Version {version} of {package} was released. {package} is used in your project so Thoth automatically ran advise on \
your application stack.

This PR contains an automatic update of Pipfile.lock by Kebechet thoth-advise manager.
"""
