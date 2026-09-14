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

    @property
    def description(self) -> str:
        return """
            The <code>korthout/backport-action</code> GitHub Action. It automatically
            opens a backport pull request to a maintenance or release branch when a
            merged PR is labeled for backporting. Repos that use it reduce the manual,
            error-prone work of cherry-picking
            fixes onto release branches.
        """


check.register_check(BackportActionExists())
