import davbp.logger as logger
from jinja2 import Environment, FileSystemLoader
import os


def make_repo_details_pages(repos, output_dir: str, generated_at: str) -> None:
    logger.info("Writing project-speicific details pages")

    env = Environment(loader=FileSystemLoader("templates"))

    for r in repos:
        cur_dir = f"{output_dir}/repos/{r['name']}"
        os.makedirs(cur_dir, exist_ok=True)

        with open(f"{cur_dir}/index.html", "w") as fd:
            template = env.get_template("repo.index.jinja")
            fd.write(template.render(repo=r, generated_at=generated_at))


def make_root_page(repos, output_dir: str, generated_at: str) -> None:
    logger.info("Writing root index.html")

    env = Environment(loader=FileSystemLoader("templates"))

    with open(f"{output_dir}/index.html", "w") as fd:
        template = env.get_template("root.index.jinja")
        fd.write(template.render(all_repos=repos, generated_at=generated_at))
