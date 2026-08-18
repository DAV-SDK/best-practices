#!/usr/bin/env bash
# Checks a GitHub repository for a small set of best-practice CI integrations
# and prints the result as JSON. Requires the `gh` CLI to be authenticated.
#
# Does a shallow (--depth 1) clone of the requested branch (or the repo's
# default branch) and greps the checkout locally, rather than fetching the
# tree and every YAML file's content one API call at a time.
set -euo pipefail

CDASH_STATUS_ACTION="Kitware/cdash-status"
BACKPORT_ACTION="korthout/backport-action"
GL_SYNC_COMPONENT="gh-gl-sync"

usage() {
  cat <<EOF
Usage: $(basename "$0") <owner/repo> [branch]

Checks whether <owner/repo> (at <branch>, default: the repo's default
branch) uses:
  - the ${CDASH_STATUS_ACTION} GitHub Action
  - the ${GL_SYNC_COMPONENT} GitLab CI/CD component (any YAML file in the repo)
  - the ${BACKPORT_ACTION} GitHub Action

Prints a JSON object with one boolean per check and a total_score (0-3).
EOF
}

if [[ $# -lt 1 || $# -gt 2 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 1
fi

repo="$1"
branch="${2:-}"

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT

clone_args=(--depth 1 --single-branch --quiet)
if [[ -n "$branch" ]]; then
  clone_args+=(--branch "$branch")
fi

# Only YAML files are inspected, so skip fetching actual git-lfs blob
# content (large binary test data etc.) during checkout: it's unneeded and
# can fail the whole clone if the repo's LFS budget is exhausted.
GIT_LFS_SKIP_SMUDGE=1 gh repo clone "$repo" "$workdir" -- "${clone_args[@]}"

checked_branch=$(git -C "$workdir" rev-parse --abbrev-ref HEAD)

uses_cdash_status=false
uses_gh_gl_sync=false
uses_backport_action=false

while IFS= read -r -d '' file; do
  rel="${file#"$workdir"/}"

  if grep -qF "$GL_SYNC_COMPONENT" "$file"; then
    uses_gh_gl_sync=true
  fi

  if [[ "$rel" == .github/workflows/* ]]; then
    if grep -qF "$CDASH_STATUS_ACTION" "$file"; then
      uses_cdash_status=true
    fi
    if grep -qF "$BACKPORT_ACTION" "$file"; then
      uses_backport_action=true
    fi
  fi
done < <(find "$workdir" -type f \( -iname '*.yml' -o -iname '*.yaml' \) -not -path '*/.git/*' -print0)

total_score=0
if [[ "$uses_cdash_status" == true ]]; then total_score=$((total_score + 1)); fi
if [[ "$uses_gh_gl_sync" == true ]]; then total_score=$((total_score + 1)); fi
if [[ "$uses_backport_action" == true ]]; then total_score=$((total_score + 1)); fi

jq -n \
  --arg repo "$repo" \
  --arg branch "$checked_branch" \
  --argjson cdash_status "$uses_cdash_status" \
  --argjson gh_gl_sync "$uses_gh_gl_sync" \
  --argjson backport_action "$uses_backport_action" \
  --argjson total_score "$total_score" \
  '{
    repo: $repo,
    branch: $branch,
    cdash_status: $cdash_status,
    gh_gl_sync: $gh_gl_sync,
    backport_action: $backport_action,
    total_score: $total_score
  }'
