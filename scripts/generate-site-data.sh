#!/usr/bin/env bash
# Runs bin/check-repo.sh over the DAV Stack and Tool Stack repo lists and
# renders the static site published to gh-pages: an index page with one
# matrix table per stack, a per-repo subpage, an SVG score badge per repo,
# a checks explainer page, and results.json.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

check_repo="${repo_root}/bin/check-repo.sh"
site_dir="${SITE_DIR:-${repo_root}/site}"
export CHECKS_DIR="${CHECKS_DIR:-${repo_root}/checks.d}"

dav_stack_file="${DAV_STACK_FILE:-${repo_root}/data/repos-dav-stack.txt}"
tool_stack_file="${TOOL_STACK_FILE:-${repo_root}/data/repos-tool-stack.txt}"
group_defs=(
  "DAV Stack:${dav_stack_file}"
  "Tool Stack:${tool_stack_file}"
)

# The set and order of checks come straight from checks.d/: a filename like
# checks.d/20-cdash-status.sh becomes the check name "cdash-status" (its
# JSON key is "cdash_status"), so the site adapts automatically to whatever
# check scripts exist, in the order their filenames sort in.
check_names=()
for check_script in "${CHECKS_DIR}"/*.sh; do
  [[ -x "$check_script" ]] || continue
  name="$(basename "$check_script" .sh)"
  name="${name#*-}"
  check_names+=("$name")
done
total_checks=${#check_names[@]}

badges_dir="${site_dir}/badges"
repos_dir="${site_dir}/repos"
rm -rf "$badges_dir" "$repos_dir"
mkdir -p "$badges_dir" "$repos_dir"

generated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

badge_color() {
  local score="$1"
  if [[ "$score" -eq "$total_checks" ]]; then
    echo "#4c1"
  elif [[ "$score" -eq 0 ]]; then
    echo "#e05d44"
  else
    echo "#dfb317"
  fi
}

# make_badge <label> <message> <color> <out_file>
make_badge() {
  local label="$1" message="$2" color="$3" out="$4"
  local label_w message_w total_w
  label_w=$(((${#label} * 7) + 10))
  message_w=$(((${#message} * 7) + 10))
  total_w=$((label_w + message_w))

  cat >"$out" <<SVG
<svg xmlns="http://www.w3.org/2000/svg" width="${total_w}" height="20" role="img" aria-label="${label}: ${message}">
  <rect width="${total_w}" height="20" fill="#555"/>
  <rect x="${label_w}" width="${message_w}" height="20" fill="${color}"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="$((label_w / 2))" y="14">${label}</text>
    <text x="$((label_w + (message_w / 2)))" y="14">${message}</text>
  </g>
</svg>
SVG
}

check_cell() {
  if [[ "$1" == true ]]; then
    echo '<span class="result-pass">yes</span>'
  else
    echo '<span class="result-fail">no</span>'
  fi
}

cat >"${site_dir}/style.css" <<'CSS'
:root {
  color-scheme: light dark;
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #6b7280;
  --border: #e5e7eb;
  --card: #f9fafb;
  --accent: #2563eb;
  --pass: #15803d;
  --fail: #b91c1c;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a;
    --fg: #e5e7eb;
    --muted: #94a3b8;
    --border: #1e293b;
    --card: #1e293b;
    --accent: #60a5fa;
    --pass: #4ade80;
    --fail: #f87171;
  }
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.5;
}

.container {
  max-width: 60rem;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

header.site-header {
  border-bottom: 1px solid var(--border);
  padding: 1rem;
}

header.site-header nav a {
  color: var(--accent);
  text-decoration: none;
  margin-right: 1.25rem;
  font-size: 0.9rem;
}
header.site-header nav a:hover { text-decoration: underline; }

h1 { font-size: 1.5rem; margin: 0 0 0.5rem; word-break: break-word; }
h2 { font-size: 1.1rem; margin-top: 2rem; }

.meta { color: var(--muted); font-size: 0.875rem; }

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: var(--card);
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  text-align: left;
  padding: 0.6rem 0.9rem;
  border-bottom: 1px solid var(--border);
}

th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}

tr:last-child td { border-bottom: none; }
td img { vertical-align: middle; }

a.repo-link { color: var(--fg); text-decoration: none; font-weight: 500; }
a.repo-link:hover { color: var(--accent); }

.result-pass { color: var(--pass); font-weight: 600; }
.result-fail { color: var(--fail); font-weight: 600; }

footer {
  margin-top: 2rem;
  color: var(--muted);
  font-size: 0.8rem;
}

code {
  background: var(--card);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.9em;
}

/* Matrix table (index page): one uniform-width column per check, so the
   yes/no marks line up vertically like a real matrix. */
table.matrix { table-layout: fixed; }
table.matrix th:first-child, table.matrix td:first-child { width: 22%; }
table.matrix th:not(:first-child), table.matrix td:not(:first-child) { width: 13%; }
table.matrix th:last-child, table.matrix td:last-child { width: 26%; }
@media (min-width: 641px) {
  table.matrix th:not(:first-child), table.matrix td:not(:first-child) {
    text-align: center;
  }
}

/* Below this width, turn each table row into a stacked card instead of
   forcing horizontal scrolling on a narrow screen. */
@media (max-width: 640px) {
  table, thead, tbody, tr, th, td { display: block; width: 100%; }
  thead { display: none; }
  tr {
    margin-bottom: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  td {
    display: flex;
    align-items: center;
    min-height: 2.2rem;
    padding-left: 45%;
    position: relative;
    border-bottom: 1px solid var(--border);
  }
  td:last-child { border-bottom: none; }
  td::before {
    content: attr(data-label);
    position: absolute;
    left: 0.9rem;
    width: 40%;
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--muted);
  }
}
CSS

groups_json="[]"
declare -A group_rows_by_label

for group_def in "${group_defs[@]}"; do
  label="${group_def%%:*}"
  file="${group_def#*:}"
  [[ -f "$file" ]] || { echo "Missing repos file: ${file}" >&2; exit 1; }

  group_results="[]"
  rows=""

  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    read -ra tokens <<<"$line"
    repo="${tokens[0]}"
    branch=""
    cdash_project=""
    cdash_server=""
    for tok in "${tokens[@]:1}"; do
      case "$tok" in
        branch=*) branch="${tok#branch=}" ;;
        cdash_server=*) cdash_server="${tok#cdash_server=}" ;;
        cdash=*) cdash_project="${tok#cdash=}" ;;
      esac
    done

    echo "Checking ${repo}${branch:+@${branch}} (${label})..." >&2

    args=("$repo")
    [[ -n "$branch" ]] && args+=(--branch "$branch")
    [[ -n "$cdash_project" ]] && args+=(--cdash-project "$cdash_project")
    [[ -n "$cdash_server" ]] && args+=(--cdash-server "$cdash_server")
    result=$("$check_repo" "${args[@]}")
    group_results=$(jq --argjson r "$result" '. + [$r]' <<<"$group_results")

    score=$(jq -r .total_score <<<"$result")
    checked_branch=$(jq -r .branch <<<"$result")
    cdash_project_checked=$(jq -r .cdash_project <<<"$result")
    cdash_server_checked=$(jq -r .cdash_server <<<"$result")

    subpage_check_rows=""
    matrix_check_cells=""
    for name in "${check_names[@]}"; do
      key="${name//-/_}"
      value=$(jq -r --arg k "$key" '.[$k]' <<<"$result")
      subpage_check_rows="${subpage_check_rows}<tr><td data-label=\"Check\"><code>${name}</code></td><td data-label=\"Result\">$(check_cell "$value")</td></tr>
"
      matrix_check_cells="${matrix_check_cells}<td data-label=\"${name}\">$(check_cell "$value")</td>"
    done

    slug="${repo//\//__}"
    repo_dir="${repos_dir}/${slug}"
    mkdir -p "$repo_dir"

    make_badge "PESO Scorecard" "${score}/${total_checks}" "$(badge_color "$score")" "${badges_dir}/${slug}.svg"

    cat >"${repo_dir}/index.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${repo} - DAV SDK Best Practices</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<header class="site-header">
  <nav>
    <a href="../../index.html">&larr; all repositories</a>
    <a href="../../checks.html">what do these checks mean?</a>
  </nav>
</header>
<main class="container">
  <h1>${repo}</h1>
  <p><a href="index.html"><img src="../../badges/${slug}.svg" alt="${score}/${total_checks} checks passing"></a></p>
  <p><a href="https://github.com/${repo}">github.com/${repo}</a> &middot; branch <code>${checked_branch}</code></p>
  <table>
  <thead><tr><th>Check</th><th>Result</th></tr></thead>
  <tbody>
  ${subpage_check_rows}</tbody>
  </table>
  <p class="meta">CDash project checked: <code>${cdash_project_checked}</code> on <code>${cdash_server_checked}</code></p>
  <footer>Generated: ${generated_at}</footer>
</main>
</body>
</html>
HTML

    rows="${rows}<tr>\
<td data-label=\"Repository\"><a class=\"repo-link\" href=\"repos/${slug}/index.html\">${repo}</a></td>\
${matrix_check_cells}\
<td data-label=\"Score\"><a href=\"repos/${slug}/index.html\"><img src=\"badges/${slug}.svg\" alt=\"${score}/${total_checks} checks passing\"></a></td>\
</tr>
"
  done <"$file"

  group_rows_by_label["$label"]="$rows"
  groups_json=$(jq --arg label "$label" --argjson repos "$group_results" \
    '. + [{label: $label, repos: $repos}]' <<<"$groups_json")
done

jq -n --argjson groups "$groups_json" --arg generated_at "$generated_at" \
  '{generated_at: $generated_at, groups: $groups}' >"${site_dir}/results.json"

matrix_header_cells="<th>Repository</th>"
for name in "${check_names[@]}"; do
  matrix_header_cells="${matrix_header_cells}<th><code>${name}</code></th>"
done
matrix_header_cells="${matrix_header_cells}<th>Score</th>"

index_sections=""
for group_def in "${group_defs[@]}"; do
  label="${group_def%%:*}"
  index_sections="${index_sections}
  <h2>${label}</h2>
  <table class=\"matrix\">
  <thead><tr>${matrix_header_cells}</tr></thead>
  <tbody>
  ${group_rows_by_label[$label]}</tbody>
  </table>
"
done

cat >"${site_dir}/index.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DAV SDK Best Practices</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <nav>
    <a href="checks.html">what do these checks mean?</a>
  </nav>
</header>
<main class="container">
  <h1>DoE PESO best-practices checklist</h1>
  <p class="meta">Generated: ${generated_at}</p>
  ${index_sections}
</main>
</body>
</html>
HTML

cat >"${site_dir}/checks.html" <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Checks explained - DAV SDK Best Practices</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <nav><a href="index.html">&larr; all repositories</a></nav>
</header>
<main class="container">
  <h1>What do these checks mean?</h1>

  <h2><code>cdash-dashboard</code></h2>
  <p>Whether the project has a dashboard on a CDash server (by default
  <a href="https://open.cdash.org">open.cdash.org</a>; some projects run
  their own, e.g. HDFGroup/hdf5's is my.cdash.org). A project dashboard
  there aggregates CTest results (build, test, and coverage) submitted from
  machines across the team, giving a shared view of build health beyond a
  single CI run.</p>

  <h2><code>cdash-status</code></h2>
  <p>The <code>Kitware/cdash-status</code> GitHub Action. It reports CDash build
  and test results back onto a pull request as a status check. Repos that use
  it give reviewers CTest/CDash results directly in the PR, instead of
  requiring a separate visit to a CDash dashboard.</p>

  <h2><code>gh-gl-sync</code></h2>
  <p>A GitLab CI/CD component that mirrors GitHub activity into a GitLab
  pipeline. Repos that use it can run CI on GitLab-hosted runners (for example
  for hardware or platforms not available on GitHub-hosted runners) while
  staying in sync with GitHub pull requests and issues.</p>

  <h2><code>backport-action</code></h2>
  <p>The <code>korthout/backport-action</code> GitHub Action. It automatically
  opens a backport pull request to a maintenance or release branch when a
  merged PR is labeled for backporting. Repos that use it reduce the manual,
  error-prone work of cherry-picking
  fixes onto release branches.</p>
</main>
</body>
</html>
HTML

echo "Wrote ${site_dir}/index.html, checks.html, style.css, results.json, badges/, repos/" >&2
