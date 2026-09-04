"""
DAV/Tools internal dashboard check for the Open Source Security Foundation
dashboard check
"""

from davbp import fsutils
from davbp.Repository import Repository as Repo


def check_scorecard_exists(repo: Repo) -> bool:
    """
    Check if the OpenSSF scorecard exists

    Args:
        repo (Repo): The source repository
    """

    return fsutils.grep_dir(
        "ossf/scorecard-action", repo.clone_dir, include_pattern=".github/workflows"
    )
