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
    for root, _, files in os.walk(directory):
        if include_pattern is not None and not include_pattern in root:
            continue

        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f), mode="r", encoding="utf-8") as fd:
                for line in fd.readlines():
                    if value in line:
                        return True

    return False
