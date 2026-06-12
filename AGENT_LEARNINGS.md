---
title: Agent Learning Documentation
description: Non-obvious patterns that prevent repeated mistakes across sprints
---

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **Example**: Working code
- **References**: Related files

## Learned Patterns

### Workflows pushing to a shared branch need `concurrency:`

- **Context**: GHA workflows that push to a long-lived shared branch (`gh-pages`, deployment, release) from multiple jobs or via repeated `workflow_dispatch`.
- **Problem**: Parallel runs each fetch the branch, do work, then push — second pusher hits non-fast-forward rejection. Wasted compute scales with run length (we lost 48 min of commit generation).
- **Solution**: Declare a workflow-level concurrency group keyed by the shared branch.
- **Example**:

  ```yaml
  concurrency:
    group: gh-pages-paint
    cancel-in-progress: false
  ```

- **References**: qte77/gha-contribution-ascii PR #77; failed run 23672476504.

### Plugins bundle a dynamic workflow as a `scriptPath`-referenced `.js` file

- **Context**: Shipping a parallel fan-out dynamic workflow inside a marketplace plugin so a skill can drive it (e.g. `auditing-readme` batch repo audit, `auditing-code-security` OWASP fan-out).
- **Problem**: `workflows/` is NOT a plugin component type (components are skills, agents, hooks, MCP, LSP, monitors, themes), so a plugin cannot register a `/<name>` workflow, and authoring one inline each run is non-deterministic.
- **Solution**: Ship the script as a plain bundled file; have the SKILL.md instruct Claude to call the Workflow tool by absolute path via `${CLAUDE_PLUGIN_ROOT}` (substituted in skill content). A skill whose instructions tell Claude to call Workflow is itself a documented opt-in, so it works with `ultracode` off. `args` reaches the script as a JSON string — parse defensively. Keep workflow agents read-only so the only permission to pre-grant is the Workflow tool itself.
- **Example**:

  ```js
  // SKILL.md gate: Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/x.js", args })
  const a = typeof args === 'string' ? JSON.parse(args) : (args ?? {})
  ```

- **References**: `plugins/readme-generator/workflows/audit-repos.js` (#162), `plugins/security-audit/workflows/audit-owasp.js`; `.claude/rules/skill-authoring.md`.
