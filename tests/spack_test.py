import davbp.spack as spack
import pytest


@pytest.fixture
def repo():
    return {"spack": "example"}


@pytest.fixture
def full_state():
    return [
        {"repo": "spack", "version": "develop", "status": "rolling"},
        {"repo": "spack", "version": "1.0.0", "status": "newest"},
    ]


@pytest.fixture
def outdated_state():
    return [
        {"repo": "fedora", "version": "3.0.0", "status": "newest"},
        {"repo": "spack", "version": "2.0.0", "status": "outdated"},
    ]


@pytest.fixture
def spacked_state():
    return [
        {"repo": "github", "version": "2.1.0-rc1", "status": "devel"},
        {"repo": "spack", "version": "develop", "status": "rolling"},
        {"repo": "fedora", "version": "2.0.0", "status": "newest"},
        {"repo": "spack", "version": "2.0.0", "status": "newest"},
    ]


def test_check_spack_status_full(repo, full_state):
    assert spack._verify_sources(repo, full_state)


def test_check_spack_status_outdated(repo, outdated_state):
    assert not spack._verify_sources(repo, outdated_state)


def test_check_spack_status_spacked(repo, spacked_state):
    assert spack._verify_sources(repo, spacked_state)
