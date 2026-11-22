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
`review-tiers` rule. It prints PASS only when the author is a trusted bot (Dependabot or
github-actions), the merge state is clean, the check list is non-empty and all green, and the head
did not move while it ran, for one of two shapes:

- **Pins**: workflow files only (changelog entries may ride along). Each removed `uses:` line pairs
  with an added line that differs only in SHA and tag comment; the tag moves up within the same
  major (same minor for 0.x) and the SHA is that tag's commit; no `permissions:` change.
- **Bumps** (Dependabot only): lock files and manifests only; every commit by Dependabot with a
  verified signature; version changes from the title, package table and `Updates` lines stay within
  the same major, a group's "N updates" matches the packages parsed; a manifest line may only swap
  the version of a bumped package. Lock files are not read line by line.

It rejects renames, copies, mode changes, binary or added or deleted files (a new changelog fragment
excepted), control or Unicode separator characters in changed lines, and invalid UTF-8. Anything
else prints FAIL with reasons and needs a reviewer. It needs `gh`; stdlib only.

## Settings

Grants Bash permissions for: `gh`, `bats`, `shellcheck`, `actionlint`.

## Install

```bash
claude plugin install gha-dev@qte77-claude-code-plugins
```
