import git
import json
import davbp.logger as logger


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

        if not "spack" in r:
            r["spack"] = project_name

        if not "corsa" in r:
            r["corsa"] = r["repo"]

        if not "git_provider" in r:
            r["git_provider"] = "github.com"

    return repos


def clone(repo, skip: bool) -> None:
    """git-clone all of the repositories"""

    # We only ever inspect YAML files, so skip fetching actual git-lfs blob
    # content (large binary test data etc.) during checkout: it's unneeded
    # and can fail the whole clone if the repo's LFS budget is exhausted.
    env = {"GIT_LFS_SKIP_SMUDGE": "1"}

    opts = [" --depth 1", "--single-branch", "--quiet"]

    if "branch" in repo:
        opts.append(f"--branch \"{repo['branch']}\"")

    url = f"https://{repo['git_provider']}/{repo['repo']}"

    repo["clone_dir"] = f"git-clones/{repo['name']}"

    gitrepo = None
    if not skip:
        logger.info(f"Cloning {repo['repo']}")
        gitrepo = git.Repo.clone_from(
            url, to_path=repo["clone_dir"], env=env, multi_options=opts
        )

    if not "branch" in repo:
        if not gitrepo:
            gitrepo = git.Repo(repo["clone_dir"])

        try:
            repo["branch"] = gitrepo.active_branch.name
        except TypeError:
            # Indicates HEAD is detached
            repo["branch"] = "detached"
