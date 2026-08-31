import davbp.cdash as cdash
import pytest


def _new_repo():
    data = {
        "name": "example",
        "cdash": "example-cdash",
        "cdash_server": "cdash.example.com",
    }
    return data


def test_init_urls_simple():
    # Base repo should be unmodified
    repo = _new_repo()
    cdash.init_urls(repo)
    assert repo["name"] == "example"
    assert repo["cdash_server"] == "cdash.example.com"
    assert repo["cdash"] == "example-cdash"
    assert repo["cdash_url"] == "cdash.example.com/index.php?project=example-cdash"


def test_init_urls_defaults():
    # Check the defaults
    repo = _new_repo()
    del repo["cdash"]
    del repo["cdash_server"]

    cdash.init_urls(repo)
    assert repo["name"] == "example"
    assert repo["cdash_server"] == "https://open.cdash.org"
    assert repo["cdash"] == "example"
    assert repo["cdash_url"] == "https://open.cdash.org/index.php?project=example"
