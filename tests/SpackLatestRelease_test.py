"""
Tests for the SpackLatestRelease check
"""

import pytest
from davbp.checks.SpackLatestRelease import SpackLatestRelease as spack
from davbp.Repository import Repository as Repo


@pytest.fixture
def _repo():
    """Create a minimal dummy repository"""
    return Repo(
        {
            "repo": "example/test",
            "clone_dir": "example-clone-dir",
            "stack": "DAV",
            "branch": "main",
        },
        skip_clone=True,
    )


@pytest.fixture
def _only_spack_state():
    return [
        {"repo": "spack", "version": "develop", "status": "rolling"},
        {"repo": "spack", "version": "1.0.0", "status": "newest"},
    ]


@pytest.fixture
def _outdated_state():
    return [
        {"repo": "fedora", "version": "3.0.0", "status": "newest"},
        {"repo": "spack", "version": "2.0.0", "status": "outdated"},
    ]


@pytest.fixture
def _spacked_state():
    return [
        {"repo": "github", "version": "2.1.0-rc1", "status": "devel"},
        {"repo": "spack", "version": "develop", "status": "rolling"},
        {"repo": "fedora", "version": "2.0.0", "status": "newest"},
        {"repo": "spack", "version": "2.0.0", "status": "newest"},
    ]


def test_only_spack_state(_repo, _only_spack_state):
    """The only source is spack and contains newest"""
    assert spack()._verify_sources(_repo, _only_spack_state)


def test_outdated_state(_repo, _outdated_state):
    """Spack is outdated"""
    assert not spack()._verify_sources(_repo, _outdated_state)


def test_spacked_state(_repo, _spacked_state):
    """Many source, spack is latest"""
    assert spack()._verify_sources(_repo, _spacked_state)
