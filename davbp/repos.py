"""
Helper utilities for reading repository data
"""

import json
import os
from davbp import check
from davbp import logger
from davbp import Repository as Repo


def load(file: str, skip_clone: bool):
    """
    Load JSON-encoded descriptions for one or more repositories

    Args:
        file (str): The input file (in JSON format)
        skip_clone (bool): If True, skip git-clone for each repository
    """

    logger.info(f"Loading repositories from {file}")

    with open(file, mode="r", encoding="utf-8") as fd:
        # Skip disabled repos
        return [
            Repo.Repository(r, skip_clone)
            for r in json.load(fd)
            if not ("disabled" in r and r["disabled"].lower() == "true")
        ]


def dump(results: [check.RunResult], directory: str, gentime: str) -> None:
    output = {
        "generated_at": gentime,
        "groups": [
            {
                "label": "DAV Stack",
                "repos": [r for r in results if r.repo.stack == "DAV"],
            },
            {
                "label": "Tool Stack",
                "repos": [r for r in results if r.repo.stack == "Tools"],
            },
        ],
    }

    filename = os.path.join(directory, "history.jsonl")
    with open(filename, mode="a", encoding="utf-8") as fd:
        fd.write(json.dumps(output, default=lambda x: x.to_dict()))
