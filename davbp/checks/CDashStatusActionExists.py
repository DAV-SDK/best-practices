"""
DAV/Tools internal dashboard check for the Kitware/cdash-status GitHub action
"""

import davbp.check as check
from davbp import fsutils
from davbp import logger
from davbp import Repository as Repo


class CDashStatusActionExists(check.Check):
    @property
    def name(self) -> str:
        return "cdash status"

    def run(self, repo: Repo) -> bool:
        """
        Check if the Kitware/cdash-status workflow is used

        Args:
            repo (Repo): The source repository
        """

        logger.info(f"Checking if cdash-status action exists for {repo.repo_name}")

        return fsutils.grep_dir("Kitware/cdash-status", repo.clone_dir)


check.register_check(CDashStatusActionExists())
