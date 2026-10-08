"""
Convenience wrappers around standard filesystem utilities
"""

import os


def grep_dir(value: str, directory: str, include_pattern: str | None = None) -> bool:
    """
    Recursively search for content in files

    Args:
        value (str): A text value to search for in all files
        directory (str): The starting directory to search under
        include_pattern (str): Only include files matching this pattern

    Return:
        True if a file containing `value` was found. False, otherwise.
    """
    for root, _, files in os.walk(directory, followlinks=False):
        if include_pattern is not None and not include_pattern in root:
            continue

        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            full_path = os.path.join(root, f)

            # Skip symlinks since we'll also find the linked-to file
            if os.path.islink(full_path):
                continue

            with open(full_path, mode="r", encoding="utf-8") as fd:
                for line in fd.readlines():
                    if value in line:
                        return True

    return False
