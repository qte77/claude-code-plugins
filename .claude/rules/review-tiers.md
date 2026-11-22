# Review Tiers

Match review effort to what a PR can break. Classify by the diff, not the title.

## Tiers

- **Tier 1, no AI reviewer:** only workflow pin bumps (`uses:` lines) by trusted bots (Dependabot,
  github-actions), never fork or outside-author PRs. A deterministic check passes the PR: each SHA
  equals the tag's commit, the tag stays in the same major version and does not go lower, permissions
  are unchanged, the merge state is clean and all checks are green.
- **Tier 2:** one fresh reviewer on a mid-tier model, for major-version bumps (read the release
  notes), every lock-file or manifest bump, docs and ordinary code.
- **Tier 3:** one fresh reviewer on the strongest model, with a time-boxed brief, for hooks,
  permissions, rulesets, workflow triggers or injection, tokens and secrets.

## Rules

- **Fix rounds:** diff the reviewed diff against the new one and check only that delta against the
  requested fixes. Start a new review only if the delta goes beyond them.
- **Merge pinned to the reviewed head commit** (`--match-head-commit`), so nothing unreviewed lands.
- **Classify by the diff:** a PR titled "bump" that touches a workflow trigger is tier 3.

## Why

AI reviews of mechanical PRs found nothing a script would not; reviews of security logic found real defects.

The tier-1 check ships as `check-mechanical-pr.py` in the `gha-dev` plugin.
