# codebase-tools

Codebase research, quality hardening, and build error resolution with ACE-FCA principles. (Context compaction lives in cc-meta: `compacting-context`.)

## Skills

- **researching-codebase** — Investigates codebase before planning, gathering context in an isolated fork
- **hardening-codebase** — Nine-phase quality tightening workflow (architecture → audit → tighten → fix → docs quality → tests → 4-agent review → refactor → ship)

## Agents

- **build-error-resolver** — Build and TypeScript error resolution specialist. Fixes build/type errors with minimal diffs, no architectural edits. Cherry-picked from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT).

> **Tip:** For up-to-date library docs during research, install the [context7](https://github.com/upstash/context7) plugin from the Claude Code marketplace (`claude plugin install context7`).

## Install

```bash
claude plugin install codebase-tools@qte77-claude-code-plugins
```
