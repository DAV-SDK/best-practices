import os


def check_backport_exists(git_workflow_dir: str) -> bool:
    """Check if the korthout/backport-action action is used"""

    for root, _, files in os.walk(git_workflow_dir):
        if not ".github/workflows" in root:
            continue

        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f)) as fd:
                for line in fd.readlines():
                    if "korthout/backport-action" in line:
                        return True

    return False
