"""
DAV/Tools internal dashboard repology check to see if spack contains the
latest release version of the package
"""

import davbp.check as check
from davbp import fsutils
from davbp import logger
from davbp.Repository import Repository as Repo


class SyncActionExists(check.Check):
    @property
    def name(self) -> str:
        return "gh-gl sync"

    def run(self, repo: Repo) -> bool:
        """
        Check if the gh-gl-sync action is used

        Args:
            repo (Repo): The source repository

        Returns:
            Return True if the action exists. False, otherwise.
        """

        logger.info(f"Checking if gh-gl-sync action exists for {repo.repo_name}")

        return fsutils.grep_dir("gh-gl-sync", repo.clone_dir)


check.register_check(SyncActionExists())
