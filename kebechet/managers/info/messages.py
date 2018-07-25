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

"""Body of issues automatically opened for information."""


INFO_REPORT = \
    """
Information about dependency management for the current master branch with SHA {sha}.

<details>
  <summary>Dependency graph</summary>

```
{dependency_graph}
```

</details>

<details>
  <summary>Environment details</summary>

```
{environment_details}
```

</details>

"""