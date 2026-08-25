import os


def check_scorecard_exists(git_workflow_dir: str) -> bool:
    """Check if the OpenSSF scorecard exists"""

    for root, _, files in os.walk(git_workflow_dir):
        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f)) as fd:
                for line in fd.readlines():
                    if "ossf/scorecard-action" in line:
                        return True

    return False
