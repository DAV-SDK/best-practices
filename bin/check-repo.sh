#!/usr/bin/env bash
# Checks a GitHub repository for a small set of best-practice CI integrations
# and prints the result as JSON. Requires the `gh` CLI to be authenticated.
set -euo pipefail

CDASH_STATUS_ACTION="Kitware/cdash-status"
BACKPORT_ACTION="korthout/backport-action"
GL_SYNC_COMPONENT="gh-gl-sync"

usage() {
  cat <<EOF
Usage: $(basename "$0") <owner/repo>

Checks whether <owner/repo> uses:
  - the ${CDASH_STATUS_ACTION} GitHub Action
  - the ${GL_SYNC_COMPONENT} GitLab CI/CD component (any YAML file in the repo)
  - the ${BACKPORT_ACTION} GitHub Action

Prints a JSON object with one boolean per check and a total_score (0-3).
EOF
}

if [[ $# -ne 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 1
fi

repo="$1"

default_branch=$(gh api "repos/${repo}" --jq .default_branch)

tree_paths=$(gh api "repos/${repo}/git/trees/${default_branch}?recursive=1" \
  --jq '.tree[] | select(.type == "blob") | .path')
mapfile -t yaml_files < <(grep -E '\.ya?ml$' <<<"$tree_paths" || true)

uses_cdash_status=false
uses_gh_gl_sync=false
uses_backport_action=false

for path in "${yaml_files[@]}"; do
  [[ -z "$path" ]] && continue

  content=$(gh api -H "Accept: application/vnd.github.raw" \
    "repos/${repo}/contents/${path}?ref=${default_branch}")

  if grep -qF "$GL_SYNC_COMPONENT" <<<"$content"; then
    uses_gh_gl_sync=true
  fi

  if [[ "$path" == .github/workflows/* ]]; then
    if grep -qF "$CDASH_STATUS_ACTION" <<<"$content"; then
      uses_cdash_status=true
    fi
    if grep -qF "$BACKPORT_ACTION" <<<"$content"; then
      uses_backport_action=true
    fi
  fi
done

total_score=0
if [[ "$uses_cdash_status" == true ]]; then total_score=$((total_score + 1)); fi
if [[ "$uses_gh_gl_sync" == true ]]; then total_score=$((total_score + 1)); fi
if [[ "$uses_backport_action" == true ]]; then total_score=$((total_score + 1)); fi

jq -n \
  --arg repo "$repo" \
  --argjson cdash_status "$uses_cdash_status" \
  --argjson gh_gl_sync "$uses_gh_gl_sync" \
  --argjson backport_action "$uses_backport_action" \
  --argjson total_score "$total_score" \
  '{
    repo: $repo,
    cdash_status: $cdash_status,
    gh_gl_sync: $gh_gl_sync,
    backport_action: $backport_action,
    total_score: $total_score
  }'
