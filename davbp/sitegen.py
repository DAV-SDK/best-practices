"""
Facilities to render the DAV/Tools dashboard using Jinja2 templates
"""

import os
from jinja2 import Environment, FileSystemLoader
from davbp import logger
from davbp.check import RunResult, _all_checks


def make_repo_details_pages(
    results: [RunResult], output_dir: str, generated_at: str
) -> None:
    """
    Create repo-specific detail pages

    Args:
        repos ([Repo]): list of source repositories
        output_dir (str): Directory to store the web pages
        generated_at (str): Timestamp of when site was generated
    """

    logger.info("Writing project-speicific details pages")

    env = Environment(loader=FileSystemLoader("templates"))

    for r in results:
        cur_dir = f"{output_dir}/repos/{r.repo.project_name}"
        os.makedirs(cur_dir, exist_ok=True)

        with open(f"{cur_dir}/index.html", mode="w", encoding="utf-8") as fd:
            template = env.get_template("repo.index.jinja")
            fd.write(template.render(result=r, generated_at=generated_at))


def make_root_page(results: [RunResult], output_dir: str, generated_at: str) -> None:
    """
    Create primary dashboard page for DAV/Tools dashboard

    Args:
        repos ([Repo]): list of source repositories
        output_dir (str): Directory to store the web pages
        generated_at (str): Timestamp of when site was generated
    """

    logger.info("Writing root index.html")

    env = Environment(loader=FileSystemLoader("templates"))

    with open(f"{output_dir}/index.html", mode="w", encoding="utf-8") as fd:
        results = sorted(
            results, key=lambda x: (x.repo.stack, x.repo.repo_name.lower())
        )
        template = env.get_template("root.index.jinja")
        fd.write(template.render(all_results=results, generated_at=generated_at))


def make_check_description_page(output_dir: str) -> None:
    """Create page for for check descriptions"""

    logger.info("Writing checks.html")

    env = Environment(loader=FileSystemLoader("templates"))

    with open(f"{output_dir}/checks.html", mode="w", encoding="utf-8") as fd:
        template = env.get_template("checks.jinja")
        fd.write(template.render(checks=_all_checks))
