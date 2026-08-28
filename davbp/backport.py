import davbp.fsutils as fsutils


def check_backport_exists(git_workflow_dir: str) -> bool:
    """Check if the korthout/backport-action action is used"""

    return fsutils.grep_dir(
        "korthout/backport-action",
        git_workflow_dir,
        exclude_pattern=".github/workflows",
    )
