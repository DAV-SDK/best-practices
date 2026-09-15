"""
DAV/Tools internal dashboard check for the Open Source Security Foundation
dashboard check
"""

import davbp.check as check
from davbp import fsutils
from davbp import logger
from davbp.Repository import Repository as Repo


class OSSFScorecardActionExists(check.Check):
    @property
    def name(self) -> str:
        return "ossf scorecard action"

    def run(self, repo: Repo) -> bool:
        """
        Check if the OpenSSF scorecard exists

        Args:
            repo (Repo): The source repository
        """

        logger.info(f"Checking if ossf scorecard action exists for {repo.repo_name}")

        return fsutils.grep_dir(
            "ossf/scorecard-action", repo.clone_dir, include_pattern=".github/workflows"
        )

    @property
    def description(self) -> str:
        return """
            The <code>ossf/scorecard-action</code> GitHub Action, from the
            <a href="https://securityscorecards.dev">OpenSSF Scorecard</a> project. It
            runs a battery of supply-chain security checks (branch protection, pinned
            dependencies, dangerous workflow patterns, and more) and publishes a
            score, giving an ongoing view of the repo's security posture.
        """


check.register_check(OSSFScorecardActionExists())
