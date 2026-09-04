"""
DAV/Tools internal dashboard repology check to see if spack contains the
latest release version of the package
"""

from davbp import fsutils
from davbp.Repository import Repository as Repo


def check_sync_exists(repo: Repo) -> bool:
    """
    Check if the gh-gl-sync action is used

    Args:
        repo (Repo): The source repository

    Returns:
        Return True if the action exists. False, otherwise.
    """

    return fsutils.grep_dir("gh-gl-sync", repo.clone_dir)
