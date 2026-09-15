"""
Tests for the CDashStatusActionExists check
"""

from davbp.checks.CDashStatusActionExists import CDashStatusActionExists as status
from davbp.Repository import Repository as Repo

test_repos = [
    {
        "repo": Repo(
            {
                "repo": "acme/branchy",
                "clone_dir": "tests/fixtures/repos/branchy/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/branchy",
                "clone_dir": "tests/fixtures/repos/branchy/release-1.0",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": True,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/full",
                "clone_dir": "tests/fixtures/repos/full/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": True,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/none",
                "clone_dir": "tests/fixtures/repos/none/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/nopkg",
                "clone_dir": "tests/fixtures/repos/nopkg/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/outdated",
                "clone_dir": "tests/fixtures/repos/outdated/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/partial",
                "clone_dir": "tests/fixtures/repos/partial/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
    {
        "repo": Repo(
            {
                "repo": "acme/spacked",
                "clone_dir": "tests/fixtures/repos/spacked/default",
                "stack": "DAV",
                "branch": "main",
            },
            skip_clone=True,
        ),
        "status": False,
    },
]


def test_CDashStatusActionExists():
    """Basic test"""
    for r in test_repos:
        assert status().run(r["repo"]) == r["status"]


def test_CDashStatusActionExists_wrong_answer():
    """Ensure no false results"""
    for r in test_repos:
        r["status"] = not r["status"]
        assert status().run(r["repo"]) != r["status"]
