# CI Status Checks

Constraints for getting a PR's required checks green. Promoted from `qte77/qte77`
`AGENT_LEARNINGS.md` (PRs #158/#159) via claude-code-plugins#192.

- **Stuck `CodeFactor: ERROR`** (null description / empty target URL on a head SHA, often on
  docs-only PRs): bring the branch up to date with the default branch — `gh pr update-branch <n>`
  or `git merge origin/main` — so the fresh SHA gets a clean re-analysis.
- **Never push empty "nudge CI" commits.** The stuck SHA keeps its errored status, and the empty
  commits pollute history.
- **Never `--admin`-merge past a failing or absent required check.** An admin override is never a
  way around CI.
