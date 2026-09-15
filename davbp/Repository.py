"""
Representation of a github/gitlab repository to analyze for the
DAV/Tools internal dashboard
"""

from typing import Any
import git
from davbp import logger


class Repository:
    def __init__(self, raw_input: dict[str, Any], skip_clone: bool = False):
        self.repo_name: str = raw_input["repo"]
        if self.repo_name is None:
            raise KeyError(f"No repo name in {raw_input}")

        self.stack: str = raw_input["stack"]
        if self.stack is None:
            raise KeyError(f"No stack in {raw_input}")

        # Use the repo name from 'org/repo' as the project's name
        org, project_name = self.repo_name.split("/")

        if org is None or project_name is None:
            raise RuntimeError(
                f"Repository name should be 'org/repo': {self.repo_name}"
            )

        self.project_name: str = project_name

        self.spack: str = raw_input.get("spack", project_name)

        self.corsa: str = raw_input.get("corsa", self.repo_name)

        self.cdash: str = raw_input.get("cdash", self.project_name)

        self.cdash_server: str = raw_input.get("cdash_server", "https://open.cdash.org")

        self.cdash_url: str = f"{self.cdash_server}/index.php?project={self.cdash}"

        self.git_provider: str = raw_input.get("git_provider", "github.com")

        self.clone_dir = raw_input.get("clone_dir", f"git-clones/{project_name}")

        if not skip_clone:
            self._clone(raw_input.get("branch"))

        self.git_branch: str = raw_input.get("branch")
        if self.git_branch is None:
            self.git_branch = self._read_git_branch()

    def _clone(self, branch: str) -> None:
        """git-clone the repository"""

        # We only ever inspect YAML files, so skip fetching actual git-lfs blob
        # content (large binary test data etc.) during checkout: it's unneeded
        # and can fail the whole clone if the repo's LFS budget is exhausted.
        env = {"GIT_LFS_SKIP_SMUDGE": "1"}

        opts = [" --depth 1", "--single-branch", "--quiet"]

        if branch is not None:
            opts.append(f'--branch "{branch}"')

        url = f"https://{self.git_provider}/{self.repo_name}"

        logger.info(f"Cloning {self.repo_name}")
        git.Repo.clone_from(url, to_path=self.clone_dir, env=env, multi_options=opts)

    def _read_git_branch(self) -> str:
        gitrepo = git.Repo(self.clone_dir)

        try:
            return gitrepo.active_branch.name
        except TypeError:
            # Indicates HEAD is detached
            return "DETACHED"
