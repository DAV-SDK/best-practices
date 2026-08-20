#!/usr/bin/env bash
# Passes if the version Spack packages for $SPACK_PACKAGE matches the
# latest real release, per repology.org's tracking of the Spack repository
# and its own "newest" version classification (which already excludes
# drafts, pre-releases, and rc/alpha/beta-style versions).
set -euo pipefail

project_json=$(curl -s --max-time 15 \
  -A "best-practices-checker (+https://github.com/DAV-SDK/best-practices)" \
  "https://repology.org/api/v1/project/${SPACK_PACKAGE}")

latest_version=$(jq -r '[.[] | select(.status == "newest") | .version][0] // empty' <<<"$project_json")
spack_version=$(jq -r '[.[] | select(.repo == "spack" and .status == "newest") | .version][0] // empty' <<<"$project_json")

[[ -n "$latest_version" && -n "$spack_version" ]] || exit 1
[[ "$spack_version" == "$latest_version" ]]
