import datetime
import os


def make_repo_details_page(repo, output_dir: str) -> None:
    pass


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
