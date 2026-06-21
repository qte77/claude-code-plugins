<!-- DERIVED — do not hand-edit. Source of truth:
     https://raw.githubusercontent.com/qte77/qte77/main/docs/templates/CONTRIBUTING.template.md
     Regenerate with 'make sync'; verify with 'make check_sync'. Tracking: qte77/claude-code-plugins#170 -->
<!-- @sync:begin (content below mirrors the SoT verbatim) -->
<!--
  Canonical CONTRIBUTING skeleton for qte77 repos. Copy to your repo root and fill in.
  Contract & rules: https://github.com/qte77/qte77/blob/main/docs/doc-structure.md
  Keep the `## Documentation hierarchy` statement (the doc-hierarchy SoT lives here). Keep
  `## Releasing` only if the repo cuts versioned releases; trim sections that don't apply.
-->

# Contributing

For agent behavioural rules see [AGENTS.md](AGENTS.md).

## Documentation hierarchy

One audience per file — reference, don't duplicate (estate contract: [doc-structure.md](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md)):

| File | Audience | Owns |
| --- | --- | --- |
| [README.md](README.md) | users / evaluators | what this is, why, how — the front door |
| CONTRIBUTING.md (this file) | contributors | workflow, commands, conventions, releasing |
| [AGENTS.md](AGENTS.md) | AI agents | behavioural rules, decision frameworks (`CLAUDE.md` loads the same) |
| [CHANGELOG.md](CHANGELOG.md) | everyone | notable changes by version |

## Commands

```bash
# the repo's build / test / lint entry points, e.g.
make help
markdownlint $(git ls-files '*.md')
lychee --offline $(git ls-files '*.md')
```

## Conventional Commits

`feat`, `fix`, `docs`, `chore`, `refactor`. Optional scope: `feat(SCOPE): ...`. PR titles match.

## Branches

- `feat/TOPIC`, `fix/TOPIC`, `docs/TOPIC`, `chore/TOPIC`
- Squash-merge is default. Force-push only with `--force-with-lease`, never to `main`.

## CHANGELOG

Add an entry under `[Unreleased]` for any consumer-visible change; lead with the file path. (Or use `changelog.d/` fragments via `make changelog_new` if the repo uses scriv.)

## Releasing

<!-- For repos that cut versioned releases. Delete this section for profile / docs / action-only repos. -->

Semi-automatic: a **human-authored** bump PR (so the merge is a real-user event → no bot `action_required` gotcha), automatic tag, one-command publish. SemVer; the version source of truth lives in the package manifest, mirrored in the README version badge (`-blue`).

1. Release PR: bump with the repo's tool (`uv run bump-my-version bump PART`, `npm version PART --no-git-tag-version`, …), update the README badge, and roll `## [Unreleased]` → `## [X.Y.Z] - DATE` in `CHANGELOG.md` (or `scriv collect`).
2. Merge → `tag-release` tags `vX.Y.Z` on the version change.
3. Optionally run `publish-release` for a GitHub Release from the matching `CHANGELOG.md` block. Tag-only is fine.

## Pre-merge

1. `markdownlint` clean
2. `lychee --offline` clean
3. CHANGELOG `[Unreleased]` updated
4. Conventional Commits title
