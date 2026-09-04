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

import requests
from requests.adapters import Retry, HTTPAdapter
from davbp import logger
from davbp.Repository import Repository as Repo


def _get_color(score: float) -> str:
    if score < 0.1:
        return "#FF0000"
    if score < 0.3:
        return "#FF4D4D"
    if score < 0.6:
        return "#DFB317"
    return "#44CC11"


def generate_peso(repo: Repo, site_dir: str) -> None:
    """
    Generate an SVG file for the PESO badge

    Args:
        repo (Repo): The source repository
        site_dir (str): The location to save the file
    """
    logger.info(f"Generating PESO badge for {repo.repo_name}")

    nchecks = len(repo.checks)
    score = repo.score

    label = "PESO Scorecard"
    label_w = len(label) * 7 + 10
    label_pos_x = label_w // 2

    message = f"{score}/{nchecks}"
    message_w = len(message) * 7 + 10
    message_pos_x = label_w + (message_w // 2)

    color = _get_color(score / nchecks)
    total_w = label_w + message_w

    with open(
        f"{site_dir}/badges/{repo.project_name}.svg", mode="w", encoding="utf-8"
    ) as fd:
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


def fetch_lf_insights(repo: Repo, site_dir: str) -> None:
    """
    Download the Linux Foundation Insights badge

    Args:
        repo (Repo): The source repository
        site_dir (str): The location to save the file
    """
    logger.info(f"Generating LF Insights badge for {repo.repo_name}")

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
        return

    filename = f"badges/{repo.project_name}-lfx.svg"

    repo.lfinsights = {
        "file": filename,
        "url": f"https://insights.linuxfoundation.org/project/{repo.project_name}",
    }

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", mode="w", encoding="utf-8") as fd:
        fd.write(response.text)


def fetch_openssf(repo: Repo, site_dir: str) -> None:
    """
    Download the Open Source Security Foundation badge

    Args:
        repo (Repo): The source repository
        site_dir (str): The location to save the file
    """
    logger.info(f"Generating OpenSSF badge for {repo.repo_name}")

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
        return

    # There isn't a badge available
    if "invalid repo path" in response.text:
        return

    filename = f"badges/{repo.project_name}-openssf-scorecard.svg"

    repo.ossf_scorecard = {
        "file": filename,
        "url": f"https://scorecard.dev/viewer/?uri={repo.git_provider}/{repo.repo_name}",
    }

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", mode="w", encoding="utf-8") as fd:
        fd.write(response.text)
