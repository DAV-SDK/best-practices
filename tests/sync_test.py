import davbp.sync_script as sync_script
import os
import pytest

repo_directories = {
    "tests/fixtures/repos/acme__branchy": True,
    "tests/fixtures/repos/acme__full": True,
    "tests/fixtures/repos/acme__none": False,
    "tests/fixtures/repos/acme__nopkg": False,
    "tests/fixtures/repos/acme__outdated": False,
    "tests/fixtures/repos/acme__partial": True,
    "tests/fixtures/repos/acme__spacked": False,
}


def test_check_sync_exists():
    for d in repo_directories:
        abs_path = os.path.abspath(d)
        found = sync_script.check_sync_exists(abs_path)
        expected = repo_directories[d]
        assert found == expected
