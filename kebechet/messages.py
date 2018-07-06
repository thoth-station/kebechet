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

"""Body of issues and pull requests automatically opened."""

# A base information for update that failed with all the relevant information.
_ISSUE_PIPENV_UPDATE_ALL_BASE = \
    """
##### Command

```
  $ {command}
```

<details>
  <summary>Standard output</summary>

```
{stdout}
```

</details>

<details>
  <summary>Standard error</summary>

```
{stderr}
```

</details>

<details>
  <summary>Environment details</summary>

```
{environment_details}
```

</details>

<details>
  <summary>Dependency graph</summary>

```
{dependency_graph}
```

</details>

"""

# Issued when updating all dependencies fails.
ISSUE_PIPENV_UPDATE_ALL = \
    """
Automatic dependency update failed for the current master with SHA {sha}.

The automatic dependency management cannot continue. Please fix errors reported bellow.

""" + _ISSUE_PIPENV_UPDATE_ALL_BASE + """

##### Notes

For more information, see [Pipfile](/{slug}/blob/{sha}/Pipfile) and [Pipfile.lock](/{slug}/blob/{sha}/Pipfile.lock).

Once this issue is resolved, the issue will be automatically closed by bot.

"""

# A refresh comment when master branch changed when updating all dependencies (issue was already created).
ISSUE_COMMENT_UPDATE_ALL = \
    """
Automatic dependency update still failing for the current master with SHA {sha}.
""" + _ISSUE_PIPENV_UPDATE_ALL_BASE


# A close comment when update all works again.
ISSUE_CLOSE_UPDATE_ALL = \
    """
Closing this issue as it is no longer relevant for the current master with SHA {sha}.
"""
