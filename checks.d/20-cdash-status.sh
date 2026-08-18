#!/usr/bin/env bash
# Passes if a .github/workflows/*.y*ml file in $REPO_DIR uses the
# Kitware/cdash-status GitHub Action.
set -euo pipefail

found=false
while IFS= read -r -d '' file; do
  if grep -qF "Kitware/cdash-status" "$file"; then
    found=true
    break
  fi
done < <(find "${REPO_DIR}/.github/workflows" -type f \( -iname '*.yml' -o -iname '*.yaml' \) -print0 2>/dev/null)

[[ "$found" == true ]]
