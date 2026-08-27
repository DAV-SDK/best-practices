import davbp.logger as logger
import os
import requests
from requests.adapters import Retry, HTTPAdapter


def init_urls(repo) -> None:
    # Give a default for the CDash instance
    if "cdash" not in repo:
        repo["cdash"] = repo["name"]

    if "cdash_server" not in repo:
        repo["cdash_server"] = "https://open.cdash.org"

    repo["cdash_url"] = f"{repo['cdash_server']}/index.php?project={repo['cdash']}"


def check_dashboard_exists(url: str) -> bool:
    """Check if the dashboard exists"""

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


def check_status_exists(git_workflow_dir: str) -> bool:
    """Check if the Kitware/cdash-status workflow is used"""

    for root, _, files in os.walk(git_workflow_dir):
        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue

            with open(os.path.join(root, f)) as fd:
                for line in fd.readlines():
                    if "Kitware/cdash-status" in line:
                        return True

    return False
