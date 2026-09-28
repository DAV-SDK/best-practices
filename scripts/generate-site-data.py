import argparse
import datetime
import json
import os
import shutil
import davbp.badges as badges
import davbp.check as check
import davbp.logger as logger
import davbp.repos as repos
import davbp.sitegen as sitegen

parser = argparse.ArgumentParser()
parser.add_argument(
    "--site-directory",
    default="site",
    help="The location to store the generated website files",
)
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--skip-clone", action="store_true")
parser.add_argument(
    "--repo", type=str, default="", help="Only check the repository REPO"
)

args = parser.parse_args()

site_directory = args.site_directory
filter_repos = args.repo != ""


if args.verbose:
    logger.make_verbose()


all_repos = repos.load("data/repos.json", args.skip_clone)

if filter_repos:
    for r in all_repos:
        if r.repo_name == args.repo:
            all_repos.clear()
            all_repos.append(r)
            break

    if len(all_repos) != 1:
        print(f"Unknown repository: {args.repo}")
        exit(1)


generated_at = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)


all_results: [check.RunResult] = []

for r in all_repos:
    check_results = check.run_checks(r)
    score = len([1 for c in check_results if c.result])
    all_results.append(
        check.RunResult(
            repo=r,
            results=check_results,
            score=score,
            badges={
                "peso": badges.generate_peso(
                    r, score, len(check_results), site_directory
                ),
                "ossf": badges.fetch_openssf(r, site_directory),
                "lfinsights": badges.fetch_lf_insights(r, site_directory),
            },
        )
    )
    print("\n")


if filter_repos:
    print(json.dumps(all_results, indent=2, default=lambda r: r.to_dict()))
    exit(0)

# Generate site
sitegen.make_root_page(all_results, site_directory, generated_at)
sitegen.make_repo_details_pages(all_results, site_directory, generated_at)
sitegen.make_check_description_page(site_directory)

# Copy generated files into the site directory
shutil.copyfile("static/favicon.svg", os.path.join(site_directory, "favicon.svg"))
shutil.copyfile("static/style.css", os.path.join(site_directory, "style.css"))


# Export results to the history
repos.dump(all_results, site_directory, generated_at)
