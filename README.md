# best-practices

Checks the DoE PESO DAV SDK base repositories for a few CI best practices and
publishes the results as a static site.

Checks performed on each repo:

- uses the `Kitware/cdash-status` GitHub Action
- uses the `gh-gl-sync` GitLab CI/CD component (in any YAML file in the repo)
- uses the `korthout/backport-action` GitHub Action

## Requirements

- [`gh`](https://cli.github.com/), authenticated (`gh auth login`)
- `git`
- `jq`
- `bash`

## Checking a single repo

```sh
./bin/check-repo.sh owner/repo [branch]
```

`branch` is optional and defaults to the repo's default branch. The repo is
fetched with a shallow (`--depth 1`) clone of just that branch, then checked
locally.

```json
{
  "repo": "owner/repo",
  "branch": "main",
  "cdash_status": false,
  "gh_gl_sync": false,
  "backport_action": false,
  "total_score": 0
}
```

## Generating the site locally

```sh
./scripts/generate-site-data.sh
```

By default this reads repos from `data/repos.txt` (one `owner/repo` per
line, optionally followed by a branch, e.g. `owner/repo release-1.0`) and
writes the site to `site/`. Both paths can be overridden, e.g. to do a dry
run without touching the real `site/` directory:

```sh
REPOS_FILE=/path/to/repos.txt SITE_DIR=/path/to/out ./scripts/generate-site-data.sh
```

## Running tests

```sh
./tests/run_tests.sh
```

Tests run against a fake `gh` (`tests/fixtures/bin/gh`), so no network access
or GitHub authentication is required.

## Publishing

`.github/workflows/update-site.yml` runs `generate-site-data.sh` every 4
hours (and on manual dispatch) and publishes `site/` to the `gh-pages`
branch. GitHub Pages must be configured (Settings > Pages) to serve from
that branch.
