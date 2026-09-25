# planning

Planning agents and skills for feature implementation, refactoring, and backlog triage. Forward-looking, per-feature plans — distinct from the retrospective and cross-project synthesis skills in `cc-meta`.

## Skills

- **triaging-issues** — Triages open GitHub issues by ROI × feasibility: clusters by concern, scores each from the actual code, and proposes a P0–P3 plan with execution order, quick wins, and evidenced close candidates. Read-only.

## Agents

- **planner** — Expert feature/refactor planning specialist. Produces detailed implementation plans with phased steps, file-level specificity, dependency tracking, risk analysis, and testing strategy. Cherry-picked from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT).

## When to use each

| Task | Use |
|---|---|
| "Help me plan how to add feature X" | `planner` (this plugin) |
| "Triage the issues" / "What should we work on next?" | `triaging-issues` (this plugin) |
| "What am I working on across all my projects?" | `synthesizing-cc-bigpicture` (cc-meta) |
| "What did I learn from my recent plans?" | `distilling-plan-learnings` (cc-meta) |
| "Log what happened in this session" | `summarizing-session-end` (cc-meta) |

The `planner` agent is **prospective** (plans a specific thing); the cc-meta skills are **retrospective or cross-project** (orient, extract, log).

## Install

```bash
claude plugin install planning@qte77-claude-code-plugins
```
