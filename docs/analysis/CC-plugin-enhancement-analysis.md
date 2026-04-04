---
title: CC Plugin Development — Pitfalls and Patterns
purpose: Actionable reference for building Claude Code plugins — structure, gotchas, and ecosystem patterns.
created: 2026-03-01
updated: 2026-04-04
---

## Plugin Structure

```text
plugin-name/
├── .claude-plugin/plugin.json   # Required — name, version, description
├── commands/                    # Slash commands (.md, user-invoked)
├── agents/                      # Subagent definitions (.md)
├── skills/skill-name/SKILL.md   # Agent skills (auto-invoked)
├── hooks/hooks.json             # Event handlers
├── scripts/                     # Helper scripts
├── .mcp.json                    # MCP server definitions
└── README.md
```

All component directories at plugin root — not inside `.claude-plugin/`.

## Key Gotchas

**Skills**: Description is the trigger — vague = false activations. Use `context: fork` for research skills to avoid context pollution. Pair with a command for discoverability.

**Agents**: Own context window — no lead conversation carry-over. Define narrow scope.

**Hooks**: Timeouts default low — long scripts get killed silently. SessionStart hooks must be idempotent (`copy-if-not-exists`). `$CLAUDE_PLUGIN_ROOT` for internal paths.

**Marketplace**: Each plugin needs its own `plugin.json` in addition to the marketplace entry.

## Patterns That Work

- **Commands wrapping skills** — commands handle discoverability, skills hold logic
- **Symlinked references** for DRY across skills
- **Fork context** for research skills (`context: fork`)
- **Tiered plugins** — infrastructure (hooks, settings) separate from domain (skills, commands)

## Common Pitfalls

- Over-engineering: swarm orchestration for simple tasks, pipeline chaining when sequential skills suffice
- Under-engineering: no README, skills without commands, hooks without timeouts
- Context traps: research skills without fork, large uncompacted reference docs, verbose hook output

## Publishing Checklist

- [ ] `plugin.json` has name, version, description, author, keywords
- [ ] README documents purpose, install, usage, all components
- [ ] Skill descriptions are precise trigger conditions
- [ ] Research skills use `context: fork`
- [ ] SessionStart hooks are idempotent
- [ ] Commands exist for user-invokable skills
- [ ] No duplicated logic between commands and skills
- [ ] `$CLAUDE_PLUGIN_ROOT` used for all internal paths

## Ecosystem Patterns (March 2026)

| Pattern | Maturity |
|---------|----------|
| Commands wrapping skills | Established |
| PreToolUse safety guardrails | Established |
| Prompt-based hooks (no scripts) | Established |
| Parallel agent teams | Experimental |
| Stop hooks for iteration loops | Experimental |
| UserPromptSubmit skill routing | Experimental |

## References

- [Official plugin docs](https://code.claude.com/docs/en/plugins)
- [claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [Canonical analysis](https://github.com/qte77/ai-agents-research/tree/main/docs/cc-native/plugins-ecosystem)
