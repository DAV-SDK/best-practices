import json
import davbp.logger as logger
import os
import requests
from requests.adapters import Retry, HTTPAdapter


def _get_spack_newest(srcs) -> str:
    for src in srcs:
        if src["repo"] == "spack" and src["status"] == "newest":
            return src["version"]

    return None


def _get_newest_any(srcs) -> str:
    for src in srcs:
        if src["status"] == "newest":
            return src["version"]

    return None


def _verify_sources(repo, srcs) -> bool:
    newest = _get_newest_any(srcs)

    if newest is None:
        logger.warn(f"Failed to find newest version for {repo['spack']}")
        return False

    spack_newest = _get_spack_newest(srcs)

    if spack_newest is None:
        logger.warn(f"Failed to find newest spack version for {repo['spack']}")
        return False

    return newest == spack_newest


def check_spack_status(repo) -> bool:
    """Check if the spack package contains the latest release"""

    logger.info(f"Checking latest spack release for {repo['name']}")

    s = requests.Session()

    # Retry once before concluding the project has no dashboard
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    url = f"https://repology.org/api/v1/project/{repo['spack']}"

    headers = {
        "User-Agent": "best-practices-checker (+https://github.com/DAV-SDK/best-practices)"
    }

    response = s.get(url, headers=headers)

    if not response.ok:
        if response.status_code != 404:
            print(f"spack check failed for {url}: {response.reason}")
        return False

    srcs = json.loads(response.text)

    return _verify_sources(repo, srcs)
