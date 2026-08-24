import argparse
import cdash
from collections import namedtuple
import logger
import repos

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


Check = namedtuple("Check", "name status")

# Run the checks
for r in all_repos:

    # fmt: off
    r["checks"] = [
        # Is there a CDash dashboard?
        Check("cdash dashboard", cdash.check_dashboard_exists(r["cdash_url"]))
    ]
    # fmt: on
