import davbp.fsutils as fsutils


def check_scorecard_exists(git_workflow_dir: str) -> bool:
    """Check if the OpenSSF scorecard exists"""

    return fsutils.grep_dir(
        "ossf/scorecard-action", git_workflow_dir, exclude_pattern=".github/workflows"
    )
