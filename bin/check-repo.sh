#!/usr/bin/env bash
# Checks a GitHub repository against every check script in checks.d/ and
# prints the result as JSON. Requires the `gh` CLI to be authenticated.
#
# Does a shallow (--depth 1) clone of the requested branch (or the repo's
# default branch) once, then runs each checks.d/*.sh script against it.
# Each check script gets REPO_DIR, REPO, BRANCH, CDASH_PROJECT, and
# CDASH_SERVER in its environment, and must exit 0 (pass) or non-zero
# (fail). Its filename (minus a leading "NN-" ordering prefix and the .sh
# suffix, with dashes turned into underscores) becomes its JSON key, e.g.
# checks.d/20-cdash-status.sh -> "cdash_status".
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checks_dir="${CHECKS_DIR:-$(cd "${script_dir}/../checks.d" && pwd)}"
DEFAULT_CDASH_SERVER="https://open.cdash.org"

usage() {
  cat <<EOF
Usage: $(basename "$0") <owner/repo> [--branch BRANCH] [--cdash-project NAME]
       [--cdash-server URL]

Runs every check script in ${checks_dir} against <owner/repo> (at BRANCH,
default: the repo's default branch). NAME defaults to the part of
<owner/repo> after the slash, and URL defaults to ${DEFAULT_CDASH_SERVER};
both are only used by checks that look up a CDash dashboard.

Prints a JSON object with one boolean per check script and a total_score.
EOF
}

if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 1
fi

repo="$1"
shift

branch=""
cdash_project=""
cdash_server="$DEFAULT_CDASH_SERVER"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      [[ $# -ge 2 ]] || { usage; exit 1; }
      branch="$2"
      shift 2
      ;;
    --cdash-project)
      [[ $# -ge 2 ]] || { usage; exit 1; }
      cdash_project="$2"
      shift 2
      ;;
    --cdash-server)
      [[ $# -ge 2 ]] || { usage; exit 1; }
      cdash_server="$2"
      shift 2
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done
cdash_project="${cdash_project:-${repo##*/}}"

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT

clone_args=(--depth 1 --single-branch --quiet)
if [[ -n "$branch" ]]; then
  clone_args+=(--branch "$branch")
fi

# Check scripts only ever inspect YAML files, so skip fetching actual
# git-lfs blob content (large binary test data etc.) during checkout: it's
# unneeded and can fail the whole clone if the repo's LFS budget is
# exhausted.
GIT_LFS_SKIP_SMUDGE=1 gh repo clone "$repo" "$workdir" -- "${clone_args[@]}"

checked_branch=$(git -C "$workdir" rev-parse --abbrev-ref HEAD)

result=$(jq -n --arg repo "$repo" --arg branch "$checked_branch" '{repo: $repo, branch: $branch}')

total_score=0
total_checks=0
for check_script in "${checks_dir}"/*.sh; do
  [[ -x "$check_script" ]] || continue

  name="$(basename "$check_script" .sh)"
  name="${name#*-}"
  key="${name//-/_}"

  total_checks=$((total_checks + 1))
  passed=false
  if REPO_DIR="$workdir" REPO="$repo" BRANCH="$checked_branch" \
     CDASH_PROJECT="$cdash_project" CDASH_SERVER="$cdash_server" \
     "$check_script"; then
    passed=true
    total_score=$((total_score + 1))
  fi

  result=$(jq --arg k "$key" --argjson v "$passed" '.[$k] = $v' <<<"$result")
done

jq --arg cdash_project "$cdash_project" --arg cdash_server "$cdash_server" \
  --argjson total_score "$total_score" --argjson total_checks "$total_checks" \
  '. + {cdash_project: $cdash_project, cdash_server: $cdash_server, total_score: $total_score, total_checks: $total_checks}' \
  <<<"$result"
