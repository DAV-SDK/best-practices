import davbp.fsutils as fsutils


def check_sync_exists(git_workflow_dir: str) -> bool:
    """Check if the gh-gl-sync action is used"""

    return fsutils.grep_dir("gh-gl-sync", git_workflow_dir)
