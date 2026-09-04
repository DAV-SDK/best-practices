"""
DAV/Tools internal dashboard check for CDash dashboard usage
"""

import requests
from requests.adapters import Retry, HTTPAdapter
from davbp import fsutils
from davbp import logger
from davbp import Repository as Repo


def check_dashboard_exists(repo: Repo) -> bool:
    """
    Check if a public CDash dashboard exists

    Args:
        repo (Repo): The source repository
    """

    url = repo.cdash_url

    logger.info(f"Checking dashboard for {url}")

    s = requests.Session()

    # Retry once before concluding the project has no dashboard
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    response = s.get(url)

    if not response.ok:
        if response.status_code != 404:
            print(f"cdash check failed for {url}: {response.reason}")
        return False

    return True


def check_status_exists(repo: Repo) -> bool:
    """
    Check if the Kitware/cdash-status workflow is used

    Args:
        repo (Repo): The source repository
    """

    return fsutils.grep_dir("Kitware/cdash-status", repo.clone_dir)
