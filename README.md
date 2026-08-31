# best-practices

Checks the DoE PESO base repositories (DAV Stack and Tool Stack) for a few
CI best practices and publishes the results as a static site.

### Checks

- `cdash dashboard` - has a project dashboard on a CDash server
  (default [open.cdash.org](https://open.cdash.org); configurable per repo).
  A failed request is always retried once, since open.cdash.org
  occasionally times out.
- `cdash status` - uses the `Kitware/cdash-status` GitHub Action
- `gh gl sync` - uses the `gh-gl-sync` GitLab CI/CD component (in any
  YAML file in the repo)
- `backport action` - uses the `korthout/backport-action` GitHub Action
- `ossfscorecard` - uses the `ossf/scorecard-action` GitHub Action
- `spack latest release` - the version currently packaged by
  [Spack](https://spack.io) matches the project's latest real release,
  using [Repology](https://repology.org) as the source of truth for both
  (Repology's own version classification already excludes drafts,
  pre-releases, and rc/alpha/beta-style versions)

### Adding a check

Create a new module in `scripts/`, add it to the list of checks in
`generate-site-data.py`, and then add a description for it in
`static/checks.html`.

## Requirements

- `git`
- `python 3.10` or newer

See `pyproject.toml` for additional python packages used.

## Checking a single repo

To see the results for the repo `foo/bar`, run
`scripts/generate-site-data.py --repo="foo/bar"`. See
`scripts/generate-site-data.py --help` for details. The output is the raw JSON
used to generate the site content.


## Generating the site locally

```sh

python3 -m venv .env
source .env/bin/activate
pip install -e .

python3 scripts/generate-site-data.py --verbose
```

By default creates the website from the repositories described in `data/repos.json`
and stores it in `site/`. The input file format is:

```
[
  {
    "repo": "example/foo",
    "cdash": "Foo",
    "cdash_server": "https://my.cdash.org",
    "stack": "DAV",
    "git_provider": "gitlab.com",
    "branch": "dev",
    "corsa": "example/Foo",
    "spack": "py-foo"
  }
]
```

All fields except `repo` and `stack` are optional.


## Running tests

```sh
pytest tests/
```

## Publishing

`.github/workflows/update-site.yml` runs `generate-site-data.sh` every hour
(and on manual dispatch) and publishes `site/` to the `gh-pages`
branch. GitHub Pages must be configured (Settings > Pages) to serve from
that branch.

Each run also appends its `results.json` as one line to `site/history.jsonl`.
The workflow carries that file forward from the previous `gh-pages` publish
before regenerating, so it accumulates one line per run over time and is
readable at a stable URL (e.g.
`https://dav-sdk.github.io/best-practices/history.jsonl`) for tracking
progress.
