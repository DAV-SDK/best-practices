"""
DAV/Tools internal dashboard check for the korthout/backport-action
"""

import davbp.check as check
from davbp import fsutils
from davbp.Repository import Repository as Repo


class BackportActionExists(check.Check):
    @property
    def name(self) -> str:
        return "backport action"

    def run(self, repo: Repo) -> bool:
        """
        Check if the korthout/backport-action action is used

        Args:
            repo (Repo): The source repository
        """

        return fsutils.grep_dir(
            "korthout/backport-action",
            repo.clone_dir,
            include_pattern=".github/workflows",
        )


check.register_check(BackportActionExists())
