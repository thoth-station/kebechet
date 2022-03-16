#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2020 Sai Sankar Gochhayat
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

RELEASE_TAG_MISSING_WARNING = """
---
**WARNING NOTE**
The release version mentioned in the source-code couldn't be found in git tags, \
    hence the release is created from the start.
If that is not the right behavior:

- Close this pull request & release issue.
- Fix the version string in source-code to reflect the latest git-tag, or create \
    the missing tag pointing to the last release sha.
- Create a new release issue.
---
"""

RELEASE_LABEL_CONFIG_INVALID = """
The `release_label_config` in your `version` manager configuration in
`.thoth.yaml` here is a list of valid configuration entries: `calendar`,
`major`, `minor`, `patch`, `pre`, `build`, `finalize`. They should all contain a
list strings which match the labels which you want to create the corresponding
releases for.
"""

ISSUE_BODY_NO_VERSION_IDENTIFIER_FOUND = """
Automated version release could not be completed.

Kebechet version manager expects a file with one of the following names: `["setup.py", "__init__.py", "__about__.py",
"version.py", "app.py", "wsgi.py"]` to contain the line:

```
...
__version__ = X.Y.Z
...
```

where `X.Y.Z` is the current semantic version. To fix this issue, add this line to one of these files. If none of these
files exist create one somewhere in your repository.

**Related**: #{github_id}
"""
