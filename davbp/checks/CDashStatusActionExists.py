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

    @property
    def description(self) -> str:
        return """
            The <code>Kitware/cdash-status</code> GitHub Action. It reports CDash build
            and test results back onto a pull request as a status check. Repos that use
            it give reviewers CTest/CDash results directly in the PR, instead of
            requiring a separate visit to a CDash dashboard.
        """


check.register_check(CDashStatusActionExists())
