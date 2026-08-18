#!/usr/bin/env bash
# Passes if any YAML file in $REPO_DIR references the gh-gl-sync GitLab
# CI/CD component (it can be included from anywhere GitLab CI reads, not
# just .gitlab-ci.yml).
set -euo pipefail

found=false
while IFS= read -r -d '' file; do
  if grep -qF "gh-gl-sync" "$file"; then
    found=true
    break
  fi
done < <(find "${REPO_DIR}" -type f \( -iname '*.yml' -o -iname '*.yaml' \) -not -path '*/.git/*' -print0)

[[ "$found" == true ]]
