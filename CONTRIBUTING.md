# Contributing

Technical workflow, commands, and conventions for this marketplace. For AI-agent
behavioural rules and decision frameworks, see [AGENTS.md](AGENTS.md).

## Documentation hierarchy

One audience per file; reference, don't duplicate. Derived from the
[qte77 doc-structure canon](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md).

| File | Audience | Owns |
| --- | --- | --- |
| [README.md](README.md) | users / evaluators | what this is, why, how — the front door |
| CONTRIBUTING.md (this file) | contributors | commands, conventions, this hierarchy statement |
| [AGENTS.md](AGENTS.md) | AI agents | behavioural rules, decision frameworks (`CLAUDE.md` loads the same) |
| [CHANGELOG.md](CHANGELOG.md) | everyone | notable changes |

## Commands

```bash
make help         # list all recipes
make validate     # plugin structure + JSON syntax
make sync         # sync shared refs + the qte77 doc-structure canon into plugin dirs
make check_sync   # verify all copies match their source (incl. the canon diff-guard)
make lint_md      # markdownlint (--fix)
make test_install # marketplace add + install + cleanup
make docs_stage   # stage README/CHANGELOG/plugin READMEs into docs/ for mkdocs (gitignored)
```

## Releases

The root marketplace version (`.claude-plugin/marketplace.json` `metadata.version`) is separate from
per-plugin versions (see [Plugin versioning](#plugin-versioning)). To cut a release:

1. Run the **Bump Version** workflow (`workflow_dispatch`, `patch`/`minor`/`major`). It updates
   `metadata.version`, the README badge, and rolls `CHANGELOG.md` `[Unreleased]` into
   `## [X.Y.Z] - date` (see `.bumpversion.toml`), then opens a PR.
2. Merge that PR. **Tag Release** tags `vX.Y.Z` on `main` automatically.
3. Run the **Publish Release** workflow to create the GitHub Release from the CHANGELOG block.

All three call the shared `qte77/.github` reusable workflows. Tags are never deleted or moved.

## Conventional Commits

Per [`.gitmessage`](.gitmessage): `feat`, `fix`, `docs`, `chore`, `ci`, `refactor`,
`style`, `revert`, `test`; optional scope `type(scope):`. Split commits by type; PR titles match.

## Branches & PRs

- Branch names: `feat/TOPIC`, `fix/TOPIC`, `docs/TOPIC`, `chore/TOPIC`, `ci/TOPIC`.
- Never push directly to `main`; land via PR. Squash-merge is default; force-push only with `--force-with-lease`.
- Fill in the [pull request template](.github/pull_request_template.md).

## Plugin versioning

Any change under `plugins/<name>/` MUST bump that plugin's `version` in **both**
`plugins/<name>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (they must
match) — see [`.claude/rules/plugin-versioning.md`](.claude/rules/plugin-versioning.md). Stable
skills (`stability: stable`) also need `bash .github/scripts/compute-skill-hashes.sh --update`.

## CHANGELOG

Add an entry under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for any consumer-visible
change ([Keep a Changelog](https://keepachangelog.com/) format).

## Pre-merge

1. `make validate` + `make check_sync` clean
2. markdownlint + lychee clean (the CI `lint` workflow)
3. CHANGELOG `[Unreleased]` updated
4. Conventional Commits PR title
