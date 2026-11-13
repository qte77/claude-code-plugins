# CI Status Checks

Constraints for getting a PR's required checks green. Promoted from `qte77/qte77`
`AGENT_LEARNINGS.md` (PRs #158/#159) via claude-code-plugins#192.

- **Stuck `CodeFactor: ERROR`** (null description / empty target URL on a head SHA, often on
  docs-only PRs): bring the branch up to date with the default branch — `gh pr update-branch <n>`
  or `git merge origin/main` — so the fresh SHA gets a clean re-analysis.
- **Never push empty "nudge CI" commits.** The stuck SHA keeps its errored status, and the empty
  commits pollute history.
- **Never merge past a failing or absent required check.** Overriding branch protection is never a
  way around CI.
- **A required check that never reports blocks the merge for good.** If the check's app is not
  enabled for the repo, or its run stays "in progress" on an up-to-date head commit, both merge and
  auto-merge wait forever, and a ruleset without bypass actors leaves no override. Before making a
  check required, confirm it reports on the repo's recent PRs. When a run is stuck on an
  up-to-date branch, the owner re-runs it from the check's own service; updating the branch does
  not help when there is nothing to merge in. Seen 2026-11-09 to 11-12 on gha-dirtree-to-readme#109,
  ldnmxx-hack#356, agenthud-agui-a2ui#324 and office-forge-orchestrator#42.
