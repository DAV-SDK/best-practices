import os


def grep_dir(value: str, directory: str, include_pattern: str | None = None) -> bool:
    for root, _, files in os.walk(directory):
        if include_pattern is not None and not include_pattern in root:
            continue

        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f)) as fd:
                for line in fd.readlines():
                    if value in line:
                        return True

    return False
