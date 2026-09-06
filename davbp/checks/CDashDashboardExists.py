"""
DAV/Tools internal dashboard check for CDash dashboard usage
"""

import requests
from requests.adapters import Retry, HTTPAdapter
import davbp.check as check
from davbp import fsutils
from davbp import logger
from davbp import Repository as Repo


class CDashDashboardExists(check.Check):
    @property
    def name(self) -> str:
        return "cdash dashboard"

    def run(self, repo: Repo) -> bool:
        """
        Check if a public CDash dashboard exists

        Args:
            repo (Repo): The source repository
        """

        logger.info(f"Checking if cdash dashboard exists for {repo.repo_name}")

        s = requests.Session()

        # Retry once before concluding the project has no dashboard
        retries = Retry(total=2, backoff_factor=1)
        s.mount("http://", HTTPAdapter(max_retries=retries))

        url = repo.cdash_url
        response = s.get(url)

        if not response.ok:
            if response.status_code != 404:
                print(f"cdash check failed for {url}: {response.reason}")
            return False

        return True


check.register_check(CDashDashboardExists())
