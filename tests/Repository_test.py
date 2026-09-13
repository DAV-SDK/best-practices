"""
Tests for constructing a Repository object
"""

from davbp.Repository import Repository as Repo


def _new_repo():
    data = {
        "repo": "example/test",
        "stack": "DAV",
        "spack": "example-spack",
        "corsa": "example-corsa",
        "cdash": "example-cdash",
        "cdash_server": "cdash.example.com",
        "git_provider": "example.com",
        "clone_dir": "test-clone-dir",
        "branch": "main",
    }
    return data


def test_simple():
    """ "Base repo should be unmodified"""
    repo = Repo(_new_repo(), skip_clone=True)
    assert repo.repo_name == "example/test"
    assert repo.stack == "DAV"
    assert repo.project_name == "test"
    assert repo.spack == "example-spack"
    assert repo.corsa == "example-corsa"
    assert repo.cdash == "example-cdash"
    assert repo.cdash_server == "cdash.example.com"
    assert repo.cdash_url == "cdash.example.com/index.php?project=example-cdash"
    assert repo.git_provider == "example.com"
    assert repo.clone_dir == "test-clone-dir"
    assert repo.git_branch == "main"


def test_defaults():
    """Check the defaults"""
    r = _new_repo()
    del r["spack"]
    del r["corsa"]
    del r["cdash"]
    del r["cdash_server"]
    del r["git_provider"]
    del r["clone_dir"]

    repo = Repo(r, skip_clone=True)
    assert repo.repo_name == "example/test"
    assert repo.stack == "DAV"
    assert repo.project_name == "test"
    assert repo.spack == repo.project_name
    assert repo.corsa == repo.repo_name
    assert repo.cdash == repo.project_name
    assert repo.cdash_server == "https://open.cdash.org"
    assert repo.cdash_url == f"{repo.cdash_server}/index.php?project={repo.cdash}"
    assert repo.git_provider == "github.com"
    assert repo.clone_dir == f"git-clones/{repo.project_name}"
    assert repo.git_branch == "main"


def test_required_name():
    """ "A repo without a name should raise a KeyError"""
    try:
        r = _new_repo()
        del r["name"]
        Repo(r, skip_clone=True)
    except KeyError:
        pass


def test_required_stack():
    """ "A repo without a stack should raise a KeyError"""
    try:
        r = _new_repo()
        del r["stack"]
        Repo(r, skip_clone=True)
    except KeyError:
        pass


def test_required_name_format():
    """ "A repo name not of the form 'org/project' should raise a RuntimeError"""
    try:
        r = _new_repo()
        r["name"] = "test"
        Repo(r, skip_clone=True)
    except RuntimeError:
        pass
