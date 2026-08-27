import os


def check_sync_exists(git_workflow_dir: str) -> bool:
    """Check if the gh-gl-sync action is used"""

    for root, _, files in os.walk(git_workflow_dir):
        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f)) as fd:
                for line in fd.readlines():
                    if "gh-gl-sync" in line:
                        return True

    return False
