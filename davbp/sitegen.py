import davbp.logger as logger
import os


def make_repo_details_pages(repos, output_dir: str, generated_at: str) -> None:
    logger.info("Writing project-speicific details pages")

    for r in repos:
        cur_dir = f"{output_dir}/repos/{r['name']}"
        os.makedirs(cur_dir, exist_ok=True)
        with open(f"{cur_dir}/index.html", "w") as fd:
            fd.write(f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{r['repo']} - DAV SDK Best Practices</title>
<link rel="icon" href="../../favicon.svg">
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
  <h1>{r['repo']}</h1>
  <p><a href="index.html"><img src="../../badges/{r['name']}.svg"></a></p>
  <p><a href="https://{r['git_provider']}/{r['repo']}">{r['git_provider']}/{r['repo']}</a> &middot; branch <code>{r['branch']}</code></p>
  <table>
  <thead>
      <tr>
      <th>Check</th>
      <th>Result</th>
  </tr>
  </thead>
  <tbody>
""")
            for c in r["checks"]:
                status = '<span class="result-fail">no</span>'
                if c.status:
                    status = '<span class="result-pass">yes</span>'

                fd.write(f"""
    <tr>
        <td data-label="Check"><code>{c.name}</code>
        <td data-label="Result">{status}</td>
    </tr>
    """)

            fd.write(f"""
  </tbody>
  </table>
  <p class="meta">CDash project checked: <code>{r['cdash']}</code> on <code>{r['cdash_server']}</code></p>
  <p class="meta">Spack package checked: <code>{r['spack']}</code></p>
  <footer>Generated: {generated_at}</footer>
</main>
</body>
</html>

""")


def _write_section(all_repos, label: str, fd) -> None:

    repos = [r for r in all_repos if r["stack"] == label]

    header = "".join([f"<th>{c.name}</th>\n" for c in repos[0]["checks"]])

    fd.write(f"""
<h2>{label} Stack</h2>
<table class="matrix">
<thead>
    <tr>
        <th>Repository</th>
        {header}
        <th>Score</th>
    </tr>
</thead>
<tbody>
""")

    for r in repos:
        fd.write(f"""
<tr>
    <td data-label="Repository">
        <a class="repo-link" href="repos/{r['name']}/index.html">{r['repo']}</a>
    </td>
""")

        for c in r["checks"]:
            fd.write("<td>")
            if c.status:
                fd.write('<span class="result-pass">yes</span>')
            else:
                fd.write('<span class="result-fail">no</span>')
            fd.write("</td>")

        fd.write(f"""
    <td data-label="Score">
        <a href="repos/{r['name']}/index.html">
            <img src="badges/{r['name']}.svg">
        </a>
    </td>
</tr>
""")

    fd.write(f"""
</tbody>
</table>
""")


def _write_other_badges_section(all_repos, label: str, fd) -> None:
    repos = [r for r in all_repos if r["stack"] == label]

    fd.write(f"""
<h2>{label} Stack</h2>
<table class="matrix">
<thead>
  <tr>
    <th>Repository</th>
    <th>OpenSSF Scorecard</th>
    <th>LF Insights</th>
    <th>Corsa</th>
  </tr>
</thead>
<tbody>
""")

    for r in repos:
        fd.write(f"""
    <tr>
        <td data-label="Repository">
            <a class="repo-link" href="repos/{r['name']}/index.html">{r['repo']}</a>
        </td>
        <td>
""")
        if "scorecard" in r:
            fd.write(f"""
            <a href="{r['scorecard']['url']}">
                <img src="{r['scorecard']['file']}">
            </a>
""")
        else:
            fd.write("-")
        fd.write(f"""
        </td>
        <td>
""")

        if "lfinsights" in r:
            fd.write(f"""
            <a href="{r['lfinsights']['url']}">
                <img src="{r['lfinsights']['file']}">
            </a>
""")
        else:
            fd.write("-")
        fd.write(f"""
        </td>
        <td>
            <a href="https://corsa.center/dashboard/catalog/?category=all&repo={r['corsa']}"> entry </a>
        </td>
    </tr>
""")

    fd.write(f"""
</tbody>
</table>
""")


def make_root_page(repos, output_dir: str, generated_at: str) -> None:
    logger.info("Writing root index.html")

    with open(os.path.join(output_dir, "index.html"), "w") as fd:
        fd.write(f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DOE PESO Best Practices</title>
<link rel="icon" href="favicon.svg">
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
  <p class="meta">Generated: {generated_at}</p>
""")

        _write_section(repos, "DAV", fd)
        _write_section(repos, "Tools", fd)

        fd.write("<hr>")

        _write_other_badges_section(repos, "DAV", fd)
        _write_other_badges_section(repos, "Tools", fd)

        fd.write(f"""\
</main>
</body>
</html>
        """)
