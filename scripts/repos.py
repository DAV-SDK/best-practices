import json


def load(file: str):
    with open(file) as fd:
        repos = json.load(fd)

    # Skip disabled repos
    repos = [
        r for r in repos if not ("disabled" in r and r["disabled"].lower() == "true")
    ]

    for r in repos:
        # Use the repo name from 'org/repo' as the project's name
        _, project_name = r["repo"].split("/")
        r["name"] = project_name

    return repos
