"""
DAV/Tools internal dashboard check for the korthout/backport-action
"""

from davbp import fsutils
from davbp.Repository import Repository as Repo


def check_backport_exists(repo: Repo) -> bool:
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
