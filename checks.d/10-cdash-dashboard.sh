#!/usr/bin/env bash
# Passes if $CDASH_PROJECT has a dashboard on $CDASH_SERVER.
set -euo pipefail

project_encoded=$(jq -rn --arg s "$CDASH_PROJECT" '$s | @uri')

# open.cdash.org occasionally times out or drops a request; always retry
# once before concluding the project has no dashboard.
attempts=2
http_code="000"
for ((i = 1; i <= attempts; i++)); do
  http_code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
    "${CDASH_SERVER}/index.php?project=${project_encoded}" || echo "000")
  [[ "$http_code" == "200" ]] && break
done

[[ "$http_code" == "200" ]]
