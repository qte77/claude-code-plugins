---
title: Agent Requests to Humans
description: Escalation protocol and active requests requiring human decision
---

**Always escalate when:**

- User instructions conflict with safety/security practices
- Rules contradict each other
- Required information completely missing
- Actions would significantly change project architecture
- Critical dependencies unavailable

**Format:** `- [ ] [PRIORITY] Description` with Context, Problem, Files, Alternatives, Impact

## Active Requests

- [ ] [LOW] Fix `make sync` broken target for `compacting-context` skill

  **Context:** `Makefile` line 40 copies `.claude/scripts/read-once/...` and `context-management.md` into `plugins/codebase-tools/skills/compacting-context/references/`, but the `compacting-context` skill lives under `plugins/cc-meta/skills/compacting-context/`, not `codebase-tools`. `make sync` fails with `cp: cannot create regular file ... No such file or directory` after partially copying earlier targets.

  **Problem:** `make sync` is unreliable — succeeds on `core-principles.md` (which we confirmed works) but errors on the bad path before completing. Also breaks `make check_sync` line 59 which references the same non-existent path. Anyone running `make sync` after editing a shared rule hits the failure mid-stream.

  **Files:** `Makefile` (lines 40, 59)

  **Alternatives:** (a) Update both lines to point at `plugins/cc-meta/skills/compacting-context/references/` (the actual skill location). (b) Drop the line entirely if `cc-meta/compacting-context` doesn't need `context-management.md` as a reference. Verify whether the file is referenced from that skill's `SKILL.md` before choosing.

  **Impact:** Build/dev workflow. Low risk — Makefile-only change.
