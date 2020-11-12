"""Tests for version manager."""

import pytest

from unittest.mock import patch

from git import Repo  # noqa F401
from thoth.sourcemanagement.enums import ServiceType
from kebechet.managers import VersionManager


class FakeRepo(object):
    """Repo class for testing purposes."""

    def __init__(self, *args, **kwargs):
        """Initialize FakeRepo instance."""
        self.git = FakeGit


class FakeGit(object):
    """Git class for testing purposes."""

    @staticmethod
    def log(*args, **kwargs) -> str:
        """Return fake logs."""
        return "Fake Log entry"

    @staticmethod
    def rev_list(*args, maxparents=0, **kwargs) -> str:
        """Return Fake rev list."""
        return "\n".join(["rev1", "rev2", "rev3", "rev4", "rev5"][: (maxparents + 1)])

    @staticmethod
    def tag(*args, **kwargs) -> str:
        """Return Fake repository tags."""
        return "\n".join(["0.1.0", "v0.2.0", "v1.0.0"])


class TestVersionManager:
    """Test version manager."""

    manager = VersionManager(
        slug="fake-user/fake-repo",
        service_type=ServiceType.GITHUB,
        token="test-token-xxx",
    )

    @pytest.mark.parametrize(
        "old_version,new_version,tag",
        [
            ("0.1.0", "0.2.0", "0.1.0"),
            ("0.2.0", "0.3.0", "v0.2.0"),
            ("1.1.0", "1.2.0", "rev1"),
        ],
    )
    def test__compute_changelog(self, old_version, new_version, tag):
        """Test VersionManager._compute_changelog static method."""
        # check that tag and version are matched correctly
        fake_repo = FakeRepo()

        with patch.object(FakeGit, "log") as patch_log:
            _ = self.manager._compute_changelog(
                repo=fake_repo,
                old_version=old_version,
                new_version=new_version,
                version_file=False,
                changelog_smart=False,
                changelog_classifier=None,
                changelog_format=None,
            )
            patch_log.assert_called_with(f"{tag}..HEAD", no_merges=True, format="* %s")
