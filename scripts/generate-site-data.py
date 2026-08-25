import argparse
import backport
import badges
import cdash
from collections import namedtuple
import logger
import os
import ossf
import repos
import shutil
import spack
import sync_script

parser = argparse.ArgumentParser()
parser.add_argument(
    "--site-directory",
    default="site",
    help="The location to store the generated website files",
)
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--skip-clone", action="store_true")

args = parser.parse_args()
site_directory = args.site_directory

if args.verbose:
    logger.make_verbose()


all_repos = repos.load("data/repos.json")

for r in all_repos:
    # Make sure all cdash configs are set up
    cdash.init_urls(r)

    # git-clone the repo
    repos.clone(r, args.skip_clone)

# Create site layout
if not os.path.exists(f"{site_directory}/badges"):
    os.makedirs(f"{site_directory}/badges")


Check = namedtuple("Check", "name status")

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


# Copy generated files into the site directory
shutil.copyfile("static/favicon.svg", os.path.join(site_directory, "favicon.svg"))
shutil.copyfile("static/style.css", os.path.join(site_directory, "style.css"))
shutil.copyfile("static/checks.html", os.path.join(site_directory, "checks.html"))
