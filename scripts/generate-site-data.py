import argparse
import davbp.backport as backport
import davbp.badges as badges
import davbp.cdash as cdash
from collections import namedtuple
import datetime
import json
import davbp.logger as logger
import os
import davbp.ossf as ossf
import davbp.repos as repos
import shutil
import davbp.sitegen as sitegen
import davbp.spack as spack
import davbp.sync_script as sync_script

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


all_repos = repos.load("data/repos.json")

if filter_repos:
    for r in all_repos:
        if r["repo"] == args.repo:
            all_repos.clear()
            all_repos.append(r)
            break

    if len(all_repos) != 1:
        print(f"Unknown repository: {args.repo}")
        exit(1)

for r in all_repos:
    # Make sure all cdash configs are set up
    cdash.init_urls(r)

    # git-clone the repo
    repos.clone(r, args.skip_clone)

# Create site layout
if not os.path.exists(f"{site_directory}/badges"):
    os.makedirs(f"{site_directory}/badges")


Check = namedtuple("Check", "name status")

generated_at = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

# Run the checks
for r in all_repos:

    # fmt: off
    r["checks"] = [
        # Is there a CDash dashboard?
        Check("cdash dashboard", cdash.check_dashboard_exists(r["cdash_url"])),

        # Does it use the Kitware/cdash-status action?
        Check("cdash status", cdash.check_status_exists(r["clone_dir"])),

        # Check if the gh-gl-sync action is used
        Check("gh-gl sync", sync_script.check_sync_exists(r["clone_dir"])),

        # Check if the korthout/backport-action action is used
        Check("backport action", backport.check_backport_exists(r["clone_dir"])),

        # Check if the OpenSSF scorecard exists
        Check("ossf scorecard", ossf.check_scorecard_exists(r["clone_dir"])),

        # Check if spack package has latest version
        Check("spack latest release", spack.check_spack_status(r))
    ]
    # fmt: on

    # Score stats
    r["score"] = len([1 for c in r["checks"] if c.status])

    badges.generate_peso(r, site_directory)
    badges.fetch_openssf(r, site_directory)
    badges.fetch_lf_insights(r, site_directory)


if filter_repos:
    print(json.dumps(all_repos, indent=2))
    exit(0)

# Generate site
sitegen.make_root_page(all_repos, site_directory, generated_at)
sitegen.make_repo_details_pages(all_repos, site_directory, generated_at)

# Copy generated files into the site directory
shutil.copyfile("static/favicon.svg", os.path.join(site_directory, "favicon.svg"))
shutil.copyfile("static/style.css", os.path.join(site_directory, "style.css"))
shutil.copyfile("static/checks.html", os.path.join(site_directory, "checks.html"))


# Export results to the history
with open(os.path.join(site_directory, "history.jsonl"), "a") as fd:
    fd.write(json.dumps(all_repos))
