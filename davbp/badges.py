"""
Tools for creating badges for DAV/Tools projects

Three badges are provided:

    PESO
        A custom badge representing the score for internal DAV/Tools
        best practices checks.

    LF Insights
        The badge provided by the Linux Foundation Insights project.
        https://insights.linuxfoundation.org/

    OpenSSF scorecard
        The badge provided by the Open Source Security Foundation scorecard
        https://openssf.org/projects/scorecard/
"""

from dataclasses import dataclass
import os
import requests
from requests.adapters import Retry, HTTPAdapter
from davbp import logger
from davbp.Repository import Repository as Repo


@dataclass
class Badge:
    """
    A badge representing a check's score

    url (str): The site hosting the details of the badge
    file (str): The location of the stored badge SVG file
    """

    url: str = None
    file: str = None


def _init_dir(site_directory: str) -> None:
    if not os.path.exists(f"{site_directory}/badges"):
        os.makedirs(f"{site_directory}/badges")


def _get_color(score: float) -> str:
    if score < 0.1:
        return "#FF0000"
    if score < 0.3:
        return "#FF4D4D"
    if score < 0.6:
        return "#DFB317"
    return "#44CC11"


def generate_peso(repo: Repo, score: int, num_checks: int, site_dir: str) -> Badge:
    """
    Generate an SVG file for the PESO badge

    Args:
        repo (Repo): The source repository
        score (int): The number of passed checks
        num_checks (int): The total number of checks
        site_dir (str): The location to save the file

    Returns
        The PESO badge
    """

    logger.info(f"Generating PESO badge for {repo.repo_name}")

    _init_dir(site_dir)

    label = "PESO Scorecard"
    label_w = len(label) * 7 + 10
    label_pos_x = label_w // 2

    message = f"{score}/{num_checks}"
    message_w = len(message) * 7 + 10
    message_pos_x = label_w + (message_w // 2)

    color = _get_color(score / num_checks)
    total_w = label_w + message_w

    filename = f"{site_dir}/badges/{repo.project_name}.svg"
    with open(filename, mode="w", encoding="utf-8") as fd:
        fd.write(f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20" role="img" aria-label="{label}: {message}">
  <rect width="{total_w}" height="20" fill="#555"/>
  <rect x="{label_w}" width="{message_w}" height="20" fill="{color}"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_pos_x}" y="14">{label}</text>
    <text x="{message_pos_x}" y="14">{message}</text>
  </g>
</svg>
        """)

    return Badge(file=filename)


def fetch_lf_insights(repo: Repo, site_dir: str) -> Badge:
    """
    Download the Linux Foundation Insights badge

    Args:
        repo (Repo): The source repository
        site_dir (str): The location to save the file
    """

    logger.info(f"Generating LF Insights badge for {repo.repo_name}")

    _init_dir(site_dir)

    s = requests.Session()

    # Retry once before failing
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    url = f"https://insights.linuxfoundation.org/api/badge/health-score?project={repo.project_name}"

    response = s.get(url)

    if not response.ok:
        logger.warn(
            f"Failed to fetch Linux Insights badge for {repo.repo_name}: {response.reason}"
        )
        return Badge()

    filename = f"badges/{repo.project_name}-lfx.svg"

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", mode="w", encoding="utf-8") as fd:
        fd.write(response.text)

    url = f"https://insights.linuxfoundation.org/project/{repo.project_name}"
    return Badge(url, filename)


def fetch_openssf(repo: Repo, site_dir: str) -> Badge:
    """
    Download the Open Source Security Foundation badge

    Args:
        repo (Repo): The source repository
        site_dir (str): The location to save the file
    """

    logger.info(f"Generating OpenSSF badge for {repo.repo_name}")

    _init_dir(site_dir)

    s = requests.Session()

    # Retry once before failing
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    url = (
        f"https://api.scorecard.dev/projects/{repo.git_provider}/{repo.repo_name}/badge"
    )
    response = s.get(url)

    if not response.ok:
        logger.warn(
            f"Failed to fetch OSSF badge for {repo.repo_name}: {response.reason}"
        )
        return Badge()

    # There isn't a badge available
    if "invalid repo path" in response.text:
        return Badge()

    filename = f"badges/{repo.project_name}-openssf-scorecard.svg"

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", mode="w", encoding="utf-8") as fd:
        fd.write(response.text)

    url = f"https://scorecard.dev/viewer/?uri={repo.git_provider}/{repo.repo_name}"
    return Badge(url, filename)
