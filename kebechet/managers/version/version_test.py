import unittest
import typing

from unittest.mock import patch

from git import Repo
from kebechet.enums import ServiceType
from kebechet.managers import VersionManager


class FakeRepo(object):
    def __init__(self, *args, **kwargs):
        """Initialize FakeRepo instance."""
        self.git = FakeGit


class FakeGit(object):
    @staticmethod
    def log(*args, **kwargs) -> str:
        """Return fake logs."""
        return "Fake Log entry"

    @staticmethod
    def rev_list(*args, maxparents=0, **kwargs) -> str:
        """Return Fake rev list."""
        return "\n".join(["rev1", "rev2", "rev3", "rev4", "rev5"][: (maxparents + 1)])

    @staticmethod
    def tag(*args, **kwargs) -> typing.List[str]:
        """Return Fake repository tags."""
        return "\n".join(["0.1.0", "v0.2.0", "v1.0.0"])


class TestVersionManager(unittest.TestCase):
    """Test VersionManager."""

    manager = VersionManager(
        slug="fake-user/fake-repo", service_type=ServiceType.GITHUB
    )

    def test__compute_changelog(self):
        """Test VersionManager._compute_changelog static method."""
        # check that tag and version are matched correctly
        fake_repo = FakeRepo()
        with patch.object(FakeGit, "log") as patch_log:
            # exact match
            _ = self.manager._compute_changelog(
                repo=fake_repo,
                old_version="0.1.0",
                new_version="0.2.0",
                version_file=False,
            )
            patch_log.assert_called_with(
                f"0.1.0..HEAD", no_merges=True, format="* %s"
            )

            # tag starting with 'v'
            _ = self.manager._compute_changelog(
                repo=fake_repo,
                old_version="0.2.0",
                new_version="0.3.0",
                version_file=False,
            )
            patch_log.assert_called_with(
                f"v0.2.0..HEAD", no_merges=True, format="* %s"
            )
            
            # mismatch
            _ = self.manager._compute_changelog(
                repo=fake_repo,
                old_version="1.1.0",
                new_version="1.2.0",
                version_file=False,
            )
            patch_log.assert_called_with(
                f"rev1..HEAD", no_merges=True, format="* %s"
            )
