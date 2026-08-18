#!/usr/bin/env bash
# Test suite for bin/check-repo.sh. Uses a fake `gh` CLI (tests/fixtures/bin/gh)
# so no network access or real GitHub credentials are required.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

export GH_FAKE_FIXTURES="${script_dir}/fixtures/repos"
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
  if grep -qF "$pattern" "$file"; then
    echo "ok - ${desc}"
    pass=$((pass + 1))
  else
    echo "not ok - ${desc} ('${pattern}' not found in ${file})"
    fail=$((fail + 1))
  fi
}

run_case() {
  local repo="$1" expected_score="$2" expected_cdash="$3" expected_glsync="$4" expected_backport="$5"
  local output
  output=$("$check_repo" "$repo")

  assert_eq "${repo} is valid JSON" "0" "$(jq -e . >/dev/null <<<"$output"; echo $?)"
  assert_eq "${repo} total_score" "$expected_score" "$(jq -r .total_score <<<"$output")"
  assert_eq "${repo} cdash_status" "$expected_cdash" "$(jq -r .cdash_status <<<"$output")"
  assert_eq "${repo} gh_gl_sync" "$expected_glsync" "$(jq -r .gh_gl_sync <<<"$output")"
  assert_eq "${repo} backport_action" "$expected_backport" "$(jq -r .backport_action <<<"$output")"
}

run_case "acme/full" 3 true true true
run_case "acme/none" 0 false false false
run_case "acme/partial" 2 false true true

if "$check_repo" >/dev/null 2>&1; then
  echo "not ok - running with no args should fail"
  fail=$((fail + 1))
else
  echo "ok - running with no args should fail"
  pass=$((pass + 1))
fi

# generate-site-data.sh: index page, per-repo subpages, and badges
site_tmp="$(mktemp -d)"
trap 'rm -rf "$site_tmp"' EXIT

printf 'acme/full\nacme/none\nacme/partial\n' >"${site_tmp}/repos.txt"
REPOS_FILE="${site_tmp}/repos.txt" SITE_DIR="${site_tmp}/site" \
  "${repo_root}/scripts/generate-site-data.sh" >/dev/null 2>&1

assert_file "site index.html exists" "${site_tmp}/site/index.html"
assert_file "site results.json exists" "${site_tmp}/site/results.json"
assert_file "site checks.html exists" "${site_tmp}/site/checks.html"
assert_file "site style.css exists" "${site_tmp}/site/style.css"
assert_file "acme/full badge exists" "${site_tmp}/site/badges/acme__full.svg"
assert_file "acme/full subpage exists" "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "index links to acme/full subpage" "repos/acme__full/index.html" "${site_tmp}/site/index.html"
assert_grep "index links to checks.html" "checks.html" "${site_tmp}/site/index.html"
assert_grep "index has viewport meta tag" 'name="viewport"' "${site_tmp}/site/index.html"
assert_grep "index links to stylesheet" 'href="style.css"' "${site_tmp}/site/index.html"
assert_grep "index rows carry data-label for mobile layout" 'data-label="Repository"' "${site_tmp}/site/index.html"
assert_grep "subpage rows carry data-label for mobile layout" 'data-label="Check"' "${site_tmp}/site/repos/acme__full/index.html"
assert_grep "stylesheet defines mobile card breakpoint" '@media (max-width: 640px)' "${site_tmp}/site/style.css"
assert_grep "acme/full badge is green (score 3)" "#4c1" "${site_tmp}/site/badges/acme__full.svg"
assert_grep "acme/none badge is red (score 0)" "#e05d44" "${site_tmp}/site/badges/acme__none.svg"
assert_eq "results.json has 3 repos" "3" "$(jq '.repos | length' "${site_tmp}/site/results.json")"

rm -rf "$site_tmp"
trap - EXIT

echo
echo "${pass} passed, ${fail} failed"
[[ "$fail" -eq 0 ]]
