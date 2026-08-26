import logger
import os
import requests
from requests.adapters import Retry, HTTPAdapter


def _get_color(score: float) -> str:
    if score < 0.1:
        return "#FF0000"
    if score < 0.3:
        return "#FF4D4D"
    if score < 0.6:
        return "#DFB317"
    return "#44CC11"


def generate_peso(repo, site_dir: str) -> None:
    logger.info(f"Generating PESO badge for {repo['name']}")

    nchecks = len(repo["checks"])
    score = repo["score"]

    label = "PESO Scorecard"
    label_w = len(label) * 7 + 10
    label_pos_x = label_w // 2

    message = f"{score}/{nchecks}"
    message_w = len(message) * 7 + 10
    message_pos_x = label_w + (message_w // 2)

    color = _get_color(score / nchecks)
    total_w = label_w + message_w

    with open(f"{site_dir}/badges/{repo['name']}.svg", "w") as fd:
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


def fetch_lf_insights(repo, site_dir: str) -> None:
    logger.info(f"Generating LF Insights badge for {repo['name']}")

    s = requests.Session()

    # Retry once before failing
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    url = f"https://insights.linuxfoundation.org/api/badge/health-score?project={repo['name']}"

    response = s.get(url)

    if not response.ok:
        if response.status_code != 404:
            print(
                f"Failed to fetch Linux Insights badge for {repo['name']}: {response.reason}"
            )
        return

    filename = f"badges/{repo['name']}-lfx.svg"

    repo["lfinsights"] = {
        "file": filename,
        "url": f"https://insights.linuxfoundation.org/project/{repo['name']}",
    }

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", "w") as fd:
        fd.write(response.text)


def fetch_openssf(repo, site_dir: str) -> None:
    logger.info(f"Generating OpenSSF badge for {repo['name']}")

    s = requests.Session()

    # Retry once before failing
    retries = Retry(total=2, backoff_factor=1)
    s.mount("http://", HTTPAdapter(max_retries=retries))

    url = f"https://api.scorecard.dev/projects/github.com/{repo['repo']}/badge"

    response = s.get(url)

    if not response.ok:
        if response.status_code != 404:
            print(f"Failed to fetch OSSF badge for {repo['name']}: {response.reason}")
        return

    # There isn't a badge available
    if "invalid repo path" in response.text:
        return

    filename = f"badges/{repo['name']}-openssf-scorecard.svg"

    repo["scorecard"] = {
        "file": filename,
        "url": f"https://scorecard.dev/viewer/?uri=github.com/{repo['repo']}",
    }

    # The reponse is just text describing an SVG, so we can save it as-is
    with open(f"{site_dir}/{filename}", "w") as fd:
        fd.write(response.text)
