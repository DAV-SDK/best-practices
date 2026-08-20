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
history_file="${site_dir}/history.jsonl"
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

rm -f "${site_dir}/style.css"
cp "${repo_root}/static/style.css" "${site_dir}/style.css"

generated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

favicon_link='<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128203;</text></svg>">'

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
    spack_package=""
    for tok in "${tokens[@]:1}"; do
      case "$tok" in
        branch=*) branch="${tok#branch=}" ;;
        cdash_server=*) cdash_server="${tok#cdash_server=}" ;;
        cdash=*) cdash_project="${tok#cdash=}" ;;
        spack=*) spack_package="${tok#spack=}" ;;
      esac
    done

    echo "Checking ${repo}${branch:+@${branch}} (${label})..." >&2

    args=("$repo")
    [[ -n "$branch" ]] && args+=(--branch "$branch")
    [[ -n "$cdash_project" ]] && args+=(--cdash-project "$cdash_project")
    [[ -n "$cdash_server" ]] && args+=(--cdash-server "$cdash_server")
    [[ -n "$spack_package" ]] && args+=(--spack-package "$spack_package")
    result=$("$check_repo" "${args[@]}")
    group_results=$(jq --argjson r "$result" '. + [$r]' <<<"$group_results")

    score=$(jq -r .total_score <<<"$result")
    checked_branch=$(jq -r .branch <<<"$result")
    cdash_project_checked=$(jq -r .cdash_project <<<"$result")
    cdash_server_checked=$(jq -r .cdash_server <<<"$result")
    spack_package_checked=$(jq -r .spack_package <<<"$result")

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
${favicon_link}
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
  <p class="meta">Spack package checked: <code>${spack_package_checked}</code></p>
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

# Append this run's results as one line to history.jsonl, so progress over
# time can be pulled from a stable URL instead of only ever seeing the
# latest snapshot. The workflow carries this file forward from the previous
# gh-pages publish, so it accumulates run over run.
jq -c . "${site_dir}/results.json" >>"$history_file"

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

declare other_badges_section=""
for group_def in "${group_defs[@]}"; do
  label="${group_def%%:*}"
  file="${group_def#*:}"

  other_badges_section+="
  <h2>${label}</h2>
  <table class=\"matrix\">
  <thead>
    <tr>
      <th>Repository</th>
      <th>OpenSSF Scorecard</th>
      <th>LF Insights</th>
      <th>Corsa</th>
    </tr>"
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue

    read -ra tokens <<<"$line"
    repo="${tokens[0]}"
    
    IFS='/' read -ra _tmp <<<"$repo"
    project_name="${_tmp[1]}"

    # OpenSSF Scorecard
    img_name="$badges_dir/$project_name-openssf-scorecard.svg"
    $(wget -O "$img_name" "https://api.scorecard.dev/projects/github.com/$repo/badge" || true)
    other_badges_section+="
      <tr>
        <td>$repo</td>
        <td>"
    if ! grep -q "invalid repo path" "$img_name"; then
      other_badges_section+="<a href=\"https://scorecard.dev/viewer/?uri=github.com/$repo\"> <img src=\"$img_name\"> </a>"
    fi
    other_badges_section+="</td>
        "

    # Linux Foundation Insights
    img_name="$badges_dir/$project_name-lfx.svg"
    $(wget -O "$img_name" "https://insights.linuxfoundation.org/api/badge/health-score?project=$project_name" || true)
    other_badges_section+="<td>"
    if [[ -s $img_name ]]; then
      other_badges_section+="<a href=\"https://insights.linuxfoundation.org/project/$project_name\"> <img src=\"$img_name\"> </a>"
    fi
    other_badges_section+="</td>
        "

    corsa_name=$repo
    for tok in "${tokens[@]:1}"; do
      case "$tok" in
        corsa=*) corsa_name="${tok#corsa=}" ;;
      esac
    done
    # CORSA Catalog
    other_badges_section+="<td>
      <a href=\"https://corsa.center/dashboard/catalog/?category=all\&repo=$corsa_name\"> entry </a>
    </td>
    "

  other_badges_section+="</tr>"
  done < "$file"
  
  other_badges_section+="
  </thead>
  <tbody>
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
${favicon_link}
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <nav>
    <a href="checks.html">what do these checks mean?</a>
    <a href="history.jsonl">history (JSON Lines)</a>
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
${favicon_link}
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

  <h2><code>ossf-scorecard</code></h2>
  <p>The <code>ossf/scorecard-action</code> GitHub Action, from the
  <a href="https://securityscorecards.dev">OpenSSF Scorecard</a> project. It
  runs a battery of supply-chain security checks (branch protection, pinned
  dependencies, dangerous workflow patterns, and more) and publishes a
  score, giving an ongoing view of the repo's security posture.</p>

  <h2><code>spack-latest-release</code></h2>
  <p>Whether the version currently packaged by <a href="https://spack.io">Spack</a>
  matches the project's latest real release, using
  <a href="https://repology.org">Repology</a> as the source of truth for
  both (Repology's own version classification already excludes drafts,
  pre-releases, and rc/alpha/beta-style versions). Repos that pass it can be
  installed at their latest release through Spack right away, instead of
  requiring a package update first.</p>
</main>
</body>
</html>
HTML

echo "Wrote ${site_dir}/index.html, checks.html, style.css, results.json, badges/, repos/" >&2
