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
`review-tiers` rule, for workflow pin bumps only. It prints PASS when all of these hold:

- The author is a trusted bot (Dependabot or github-actions).
- Only workflow files change (the root `CHANGELOG.md` and new or edited `changelog.d/*.md|rst`
  fragments may ride along, unread; a new fragment must be a regular file). The files in the diff equal
  the PR's file list, which must be under 100 files.
- In every change block, each removed `uses:` line pairs with an added line that differs only in SHA
  and tag comment (same indentation, action and path). The tag moves up within the same major version
  (same minor for 0.x), the SHA is that tag's commit, and no `permissions:` line changes.
- No rename, copy, mode change, binary, added or deleted file (a new changelog fragment excepted), no
  control or Unicode separator character in a changed line, and the diff is valid UTF-8.
- The merge state is clean, the check list is non-empty and all green, and the head did not move while
  it ran.

Residuals by design: a pin with the same tag and a new SHA passes (it looks like a moved tag; the check
proves the SHA matches the tag today, not that the tag is trustworthy), and without required checks on
the base branch a slow workflow may not have registered its check yet. Lock-file bumps are not checked;
they are tier 2. Anything else prints FAIL with reasons. It needs `gh`; stdlib only.

## Settings

Grants Bash permissions for: `gh`, `bats`, `shellcheck`, `actionlint`.

## Install

```bash
claude plugin install gha-dev@qte77-claude-code-plugins
```
