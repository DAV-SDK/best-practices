#!/usr/bin/env bash
# Passes if $CDASH_PROJECT has a dashboard on $CDASH_SERVER.
set -euo pipefail

project_encoded=$(jq -rn --arg s "$CDASH_PROJECT" '$s | @uri')
http_code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
  "${CDASH_SERVER}/index.php?project=${project_encoded}")

[[ "$http_code" == "200" ]]
