import argparse
import logger
import repos

parser = argparse.ArgumentParser()
parser.add_argument(
    "--site-directory",
    default="site",
    help="The location to store the generated website files",
)
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()
site_directory = args.site_directory

if args.verbose:
    logger.make_verbose()


all_repos = repos.load("data/repos.json")
