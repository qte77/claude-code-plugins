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
`review-tiers` rule. It prints PASS only for a PR with at least one checks result, all green, in one of
two shapes. Pins: workflow files (plus changelog files, which are not line-checked) where every changed
line is a pinned `uses:` line, each added line replaces a removed line of the same action and path,
each new SHA is its tag's commit and no `permissions:` line changed. Bumps: lock files only, by
Dependabot, with every version change in the title, package table and `Updates` lines (not release notes) staying
within the same major (same minor for 0.x), and a group's "N updates" matching the packages parsed. It fails if the head moves while it runs. Anything else prints FAIL with
reasons and needs a reviewer. It needs `gh`; stdlib only.

## Settings

Grants Bash permissions for: `gh`, `bats`, `shellcheck`, `actionlint`.

## Install

```bash
claude plugin install gha-dev@qte77-claude-code-plugins
```
