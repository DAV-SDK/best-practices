#!/usr/bin/env bash
# Test suite for bin/check-repo.sh and scripts/generate-site-data.sh. Uses a
# fake `gh` and `curl` (tests/fixtures/bin/) so no network access or GitHub
# credentials are required.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

export GH_FAKE_FIXTURES="${script_dir}/fixtures/repos"
export CURL_FAKE_CDASH_PROJECTS="${script_dir}/fixtures/cdash-projects.txt"
export CURL_FAKE_REPOLOGY_DIR="${script_dir}/fixtures/repology"
export PATH="${script_dir}/fixtures/bin:${PATH}"

check_repo="${repo_root}/bin/check-repo.sh"

pass=0
fail=0

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "ok - ${desc}"
    pass=$((pass + 1))
  else
    echo "not ok - ${desc} (expected '${expected}', got '${actual}')"
    fail=$((fail + 1))
  fi
}

assert_file() {
  local desc="$1" path="$2"
  if [[ -f "$path" ]]; then
    echo "ok - ${desc}"
    pass=$((pass + 1))
  else
    echo "not ok - ${desc} (missing: ${path})"
    fail=$((fail + 1))
  fi
}

assert_grep() {
  local desc="$1" pattern="$2" file="$3"
  if grep -qF -- "$pattern" "$file"; then
    echo "ok - ${desc}"
    pass=$((pass + 1))
  else
    echo "not ok - ${desc} ('${pattern}' not found in ${file})"
    fail=$((fail + 1))
  fi
}

# run_case <repo> <extra check-repo.sh args...> -- <desc> <score> <cdash> <glsync> <backport> <cdash_dashboard> <scorecard> <spack>
run_case() {
  local repo="$1"
  shift
  local extra_args=()
  while [[ "$1" != "--" ]]; do
    extra_args+=("$1")
    shift
  done
  shift
  local desc="$1" expected_score="$2" expected_cdash="$3" expected_glsync="$4" expected_backport="$5" expected_dash="$6" expected_scorecard="$7" expected_spack="$8"
  local output
  output=$("$check_repo" "$repo" "${extra_args[@]}")

  assert_eq "${desc} is valid JSON" "0" "$(jq -e . >/dev/null <<<"$output"; echo $?)"
  assert_eq "${desc} total_score" "$expected_score" "$(jq -r .total_score <<<"$output")"
  assert_eq "${desc} cdash_status" "$expected_cdash" "$(jq -r .cdash_status <<<"$output")"
  assert_eq "${desc} gh_gl_sync" "$expected_glsync" "$(jq -r .gh_gl_sync <<<"$output")"
  assert_eq "${desc} backport_action" "$expected_backport" "$(jq -r .backport_action <<<"$output")"
  assert_eq "${desc} cdash_dashboard" "$expected_dash" "$(jq -r .cdash_dashboard <<<"$output")"
  assert_eq "${desc} ossf_scorecard" "$expected_scorecard" "$(jq -r .ossf_scorecard <<<"$output")"
  assert_eq "${desc} spack_latest_release" "$expected_spack" "$(jq -r .spack_latest_release <<<"$output")"
}

# acme/full's default cdash-project guess ("full") is in the fake curl's
# fixture list and its default spack-package guess ("full") matches its
# latest release in the fake Repology fixtures, so all six checks pass.
run_case "acme/full" -- "acme/full" 6 true true true true true true
run_case "acme/none" -- "acme/none" 0 false false false false false false
run_case "acme/partial" -- "acme/partial" 2 false true true false false false

# branch selection: same repo, different result depending on which branch is checked
run_case "acme/branchy" -- "acme/branchy@default" 0 false false false false false false
run_case "acme/branchy" --branch "release-1.0" -- "acme/branchy@release-1.0" 4 true true true false true false

# explicit --cdash-project override, independent of the repo's default guess
run_case "acme/none" --cdash-project "override-project" -- "acme/none with cdash override" 1 false false false true false false

# --cdash-server: same project name exists on my.cdash.org but not on the
# default open.cdash.org, so the server actually has to be honored
run_case "acme/none" --cdash-project "hdf5-style-project" -- \
  "acme/none, project on default server (should not exist)" 0 false false false false false false
run_case "acme/none" --cdash-project "hdf5-style-project" --cdash-server "https://my.cdash.org" -- \
  "acme/none, project on my.cdash.org" 1 false false false true false false

# spack-latest-release: Repology is the source of truth for both the
# latest real version (its "newest"-status entry, which already excludes
# devel/rc-like versions) and what Spack currently packages. Real Spack
# packages often have a second "rolling"/"develop" Repology entry alongside
# the "newest" one, so the check must pick the "newest" spack entry
# specifically, not just the first "spack" entry in the response.
output=$("$check_repo" "acme/spacked")
assert_eq "acme/spacked: Spack's newest entry matches, ignoring its rolling/devel entry" "true" \
  "$(jq -r .spack_latest_release <<<"$output")"

output=$("$check_repo" "acme/outdated")
assert_eq "acme/outdated: Spack's version is behind Repology's newest version" "false" \
  "$(jq -r .spack_latest_release <<<"$output")"

output=$("$check_repo" "acme/nopkg")
assert_eq "acme/nopkg: no Repology data at all for this project" "false" \
  "$(jq -r .spack_latest_release <<<"$output")"

output=$("$check_repo" "acme/branchy" --branch "release-1.0")
assert_eq "acme/branchy@release-1.0 reports requested branch" "release-1.0" "$(jq -r .branch <<<"$output")"

# checks.d is a plugin directory: check-repo.sh should run whatever's in
# there, not a hardcoded set of checks. Point it at a synthetic checks.d
# with a passing and a failing script and confirm it picks both up.
plugin_checks_dir="$(mktemp -d)"
trap 'rm -rf "$plugin_checks_dir"' EXIT
printf '#!/usr/bin/env bash\nexit 0\n' >"${plugin_checks_dir}/10-always-yes.sh"
printf '#!/usr/bin/env bash\nexit 1\n' >"${plugin_checks_dir}/20-always-no.sh"
chmod +x "${plugin_checks_dir}"/*.sh

output=$(CHECKS_DIR="$plugin_checks_dir" "$check_repo" "acme/none")
assert_eq "custom checks.d: total_checks reflects the plugin directory" "2" "$(jq -r .total_checks <<<"$output")"
assert_eq "custom checks.d: total_score counts only the passing check" "1" "$(jq -r .total_score <<<"$output")"
assert_eq "custom checks.d: always-yes check passes" "true" "$(jq -r .always_yes <<<"$output")"
assert_eq "custom checks.d: always-no check fails" "false" "$(jq -r .always_no <<<"$output")"
rm -rf "$plugin_checks_dir"
trap - EXIT

if "$check_repo" >/dev/null 2>&1; then
  echo "not ok - running with no args should fail"
  fail=$((fail + 1))
else
  echo "ok - running with no args should fail"
  pass=$((pass + 1))
fi

assert_grep "check-repo.sh clones with --depth 1" "--depth 1" "${repo_root}/bin/check-repo.sh"

# generate-site-data.sh: index page (two group matrices), per-repo subpages, badges
site_tmp="$(mktemp -d)"
trap 'rm -rf "$site_tmp"' EXIT

printf 'acme/full\nacme/none\n' >"${site_tmp}/dav.txt"
printf 'acme/partial\nacme/branchy branch=release-1.0 cdash=hdf5-style-project cdash_server=https://my.cdash.org\n' >"${site_tmp}/tool.txt"
DAV_STACK_FILE="${site_tmp}/dav.txt" TOOL_STACK_FILE="${site_tmp}/tool.txt" SITE_DIR="${site_tmp}/site" \
  "${repo_root}/scripts/generate-site-data.sh" >/dev/null 2>&1

assert_file "site index.html exists" "${site_tmp}/site/index.html"
assert_file "site results.json exists" "${site_tmp}/site/results.json"
assert_file "site checks.html exists" "${site_tmp}/site/checks.html"
assert_file "site style.css exists" "${site_tmp}/site/style.css"
assert_file "acme/full badge exists" "${site_tmp}/site/badges/acme__full.svg"
assert_file "acme/full subpage exists" "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "index links to acme/full subpage" "repos/acme__full/index.html" "${site_tmp}/site/index.html"
assert_grep "index links to checks.html" "checks.html" "${site_tmp}/site/index.html"
assert_grep "index links to history.jsonl" 'href="history.jsonl"' "${site_tmp}/site/index.html"
assert_grep "index has viewport meta tag" 'name="viewport"' "${site_tmp}/site/index.html"
assert_grep "index links to stylesheet" 'href="style.css"' "${site_tmp}/site/index.html"
assert_grep "index has a favicon" '<link rel="icon"' "${site_tmp}/site/index.html"
assert_grep "checks.html has a favicon" '<link rel="icon"' "${site_tmp}/site/checks.html"
assert_grep "subpage has a favicon" '<link rel="icon"' "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "index rows carry data-label for mobile layout" 'data-label="Repository"' "${site_tmp}/site/index.html"
assert_grep "index has a DAV Stack section" "<h2>DAV Stack</h2>" "${site_tmp}/site/index.html"
assert_grep "index has a Tool Stack section" "<h2>Tool Stack</h2>" "${site_tmp}/site/index.html"
assert_eq "index renders two matrix tables" "2" "$(grep -oF 'class="matrix"' "${site_tmp}/site/index.html" | wc -l)"
assert_grep "index has a column per check" 'data-label="cdash-status"' "${site_tmp}/site/index.html"
assert_grep "index has a cdash-dashboard column" 'data-label="cdash-dashboard"' "${site_tmp}/site/index.html"
assert_grep "index has a spack-latest-release column" 'data-label="spack-latest-release"' "${site_tmp}/site/index.html"
assert_grep "subpage shows the spack package checked" "Spack package checked" "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "acme/full shows a pass in the matrix" 'data-label="cdash-status"><span class="result-pass">' "${site_tmp}/site/index.html"
assert_grep "acme/none shows a fail in the matrix" 'data-label="backport-action"><span class="result-fail">' "${site_tmp}/site/index.html"
assert_grep "subpage rows carry data-label for mobile layout" 'data-label="Check"' "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "subpage has a cdash-dashboard row" '<code>cdash-dashboard</code>' "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "stylesheet defines mobile card breakpoint" '@media (max-width: 640px)' "${site_tmp}/site/style.css"
assert_grep "acme/full badge is green (perfect score)" "#4c1" "${site_tmp}/site/badges/acme__full.svg"
assert_grep "acme/none badge is red (score 0)" "#e05d44" "${site_tmp}/site/badges/acme__none.svg"
assert_eq "results.json has 2 groups" "2" "$(jq '.groups | length' "${site_tmp}/site/results.json")"
assert_eq "DAV Stack group has 2 repos" "2" \
  "$(jq '.groups[] | select(.label=="DAV Stack") | .repos | length' "${site_tmp}/site/results.json")"
assert_eq "Tool Stack group has 2 repos" "2" \
  "$(jq '.groups[] | select(.label=="Tool Stack") | .repos | length' "${site_tmp}/site/results.json")"
assert_file "acme/branchy subpage exists" "${site_tmp}/site/repos/acme__branchy/index.html"
assert_grep "acme/branchy subpage shows the requested branch" "release-1.0" "${site_tmp}/site/repos/acme__branchy/index.html"
assert_grep "acme/branchy subpage shows its custom cdash_server" "my.cdash.org" "${site_tmp}/site/repos/acme__branchy/index.html"
assert_grep "acme/branchy badge is yellow (cdash_server override improves the score, but spack-latest-release still fails)" \
  "#dfb317" "${site_tmp}/site/badges/acme__branchy.svg"

# history.jsonl: each run appends one line with that run's results.json
assert_file "history.jsonl exists" "${site_tmp}/site/history.jsonl"
assert_eq "history.jsonl has one line after one run" "1" "$(wc -l <"${site_tmp}/site/history.jsonl")"
assert_eq "history.jsonl line is valid JSON" "0" "$(jq -e . >/dev/null <"${site_tmp}/site/history.jsonl"; echo $?)"
assert_eq "history.jsonl line matches results.json" "$(jq -c . "${site_tmp}/site/results.json")" \
  "$(tail -n1 "${site_tmp}/site/history.jsonl")"

# Re-running against the same site dir should append a second line, not
# overwrite the first (the workflow carries history.jsonl forward run to run).
DAV_STACK_FILE="${site_tmp}/dav.txt" TOOL_STACK_FILE="${site_tmp}/tool.txt" SITE_DIR="${site_tmp}/site" \
  "${repo_root}/scripts/generate-site-data.sh" >/dev/null 2>&1
assert_eq "history.jsonl has two lines after a second run" "2" "$(wc -l <"${site_tmp}/site/history.jsonl")"

rm -rf "$site_tmp"
trap - EXIT

echo
echo "${pass} passed, ${fail} failed"
[[ "$fail" -eq 0 ]]
