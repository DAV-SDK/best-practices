# best-practices

Checks the DoE PESO base repositories (DAV Stack and Tool Stack) for a few
CI best practices and publishes the results as a static site, with one
matrix table per stack.

Each check is a standalone script in `checks.d/`:

- `10-cdash-dashboard.sh` - has a project dashboard on a CDash server
  (default [open.cdash.org](https://open.cdash.org); configurable per repo)
- `20-cdash-status.sh` - uses the `Kitware/cdash-status` GitHub Action
- `30-gh-gl-sync.sh` - uses the `gh-gl-sync` GitLab CI/CD component (in any
  YAML file in the repo)
- `40-backport-action.sh` - uses the `korthout/backport-action` GitHub Action
- `50-ossf-scorecard.sh` - uses the `ossf/scorecard-action` GitHub Action

### Adding a check

Drop an executable script into `checks.d/`, named `NN-check-name.sh` (`NN`
controls its ordering; `check-name` becomes its `check_name` key in the JSON
output and its column heading on the site - both `bin/check-repo.sh` and
`scripts/generate-site-data.sh` pick it up automatically, no other changes
needed). The script runs against the repo checkout with these in its
environment, and must exit 0 (check passes) or non-zero (fails):

- `REPO_DIR` - path to the shallow clone of the repo being checked
- `REPO` - `owner/repo`
- `BRANCH` - the branch actually checked
- `CDASH_PROJECT`, `CDASH_SERVER` - resolved CDash project name/server,
  for checks that need them

## Requirements

- [`gh`](https://cli.github.com/), authenticated (`gh auth login`)
- `git`
- `jq`
- `curl`
- `bash`

## Checking a single repo

```sh
./bin/check-repo.sh owner/repo [--branch BRANCH] [--cdash-project NAME] [--cdash-server URL]
```

`--branch` defaults to the repo's default branch; the repo is fetched with a
shallow (`--depth 1`) clone of just that branch, then checked locally.
`--cdash-project` defaults to the part of `owner/repo` after the slash, and
`--cdash-server` defaults to `https://open.cdash.org` - some projects run
their own CDash server (e.g. `HDFGroup/hdf5`'s is `https://my.cdash.org`),
and project names don't always match the GitHub repo name either (e.g.
`ornladios/ADIOS2`'s project is `ADIOS`).

```json
{
  "repo": "owner/repo",
  "branch": "main",
  "cdash_status": false,
  "gh_gl_sync": false,
  "backport_action": false,
  "cdash_dashboard": false,
  "cdash_project": "repo",
  "cdash_server": "https://open.cdash.org",
  "total_score": 0
}
```

## Generating the site locally

```sh
./scripts/generate-site-data.sh
```

By default this reads `data/repos-dav-stack.txt` and
`data/repos-tool-stack.txt` and writes the site to `site/`. Each file has one
`owner/repo` per line, optionally followed by whitespace-separated
`key=value` tokens:

```
ornladios/ADIOS2 branch=release_29 cdash=ADIOS
HDFGroup/hdf5 cdash=HDF5 cdash_server=https://my.cdash.org
```

All three paths can be overridden, e.g. to do a dry run without touching the
real `site/` directory:

```sh
DAV_STACK_FILE=/path/to/dav.txt TOOL_STACK_FILE=/path/to/tools.txt \
  SITE_DIR=/path/to/out ./scripts/generate-site-data.sh
```

## Running tests

```sh
./tests/run_tests.sh
```

Tests run against a fake `gh` and `curl` (`tests/fixtures/bin/`), so no
network access or GitHub authentication is required.

## Publishing

`.github/workflows/update-site.yml` runs `generate-site-data.sh` every hour
(and on manual dispatch) and publishes `site/` to the `gh-pages`
branch. GitHub Pages must be configured (Settings > Pages) to serve from
that branch.
