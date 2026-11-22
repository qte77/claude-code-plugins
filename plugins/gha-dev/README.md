# gha-dev

Skills for creating and publishing GitHub Actions to the Marketplace.

## Skills

| Skill | Trigger |
|-------|---------|
| `creating-gha` | Scaffolding a new action, writing BATS tests, preparing a Marketplace release |

## What It Provides

- **TDD workflow**: BATS infra tests first (RED), then implement to pass (GREEN)
- **Marketplace requirements**: `action.yaml` fields, branding, README format
- **Signed commit pattern**: blob→tree→commit→branch→PR→squash via `gh api`
- **Release flow**: `bump-my-version` + floating major tag (`v0`, `v1`, ...)

## Scripts

`scripts/check-mechanical-pr.py OWNER/REPO NUMBER` is the tier-1 check from the shared
`review-tiers` rule. It prints PASS only for a PR that changes pinned `uses:` lines (each SHA equals
its tag's commit, permissions unchanged) or a Dependabot same-major dependency bump, with all checks
green. Anything else prints FAIL with reasons and needs a reviewer. It needs `gh`; stdlib only.

## Settings

Grants Bash permissions for: `gh`, `bats`, `shellcheck`, `actionlint`.

## Install

```bash
claude plugin install gha-dev@qte77-claude-code-plugins
```
