# workspace-setup

Deploys workspace rules, statusline, governance files, and base settings via SessionStart hook.

Self-contained — all CC-specific files bundled in the plugin, no external dependencies.

## Deployed files

- **rules/*.md** → `.claude/rules/` — core principles, context management, compound learning, CI status checks
- **scripts/statusline.sh** → `.claude/scripts/` — status line display. World clock off by default. Two ways to opt in: (1) **persistent** — set `CC_WORLD_CLOCK="Asia/Tokyo,Europe/Paris,Europe/London,UTC,America/New_York,America/Los_Angeles"` in your shell rc (needs CC restart to change); (2) **live toggle** — write the same comma-separated zone list to `~/.claude/world-clock` (next prompt render picks it up; `rm` the file to turn off). Env var wins over file. Use east-to-west / sunrise order or any IANA zones you prefer. Each entry is either a bare zone (`Europe/Paris` → label `Paris`) or `Zone=Label` to override the rendered label (`America/New_York=NYC` → label `NYC`). Zones render on a dedicated line below the main statusline; invalid zones show as `?<name>`. See the comment block at the top of `.claude/scripts/statusline.sh` for the curated shortlist and usage notes.
- **settings/settings-base.json** → `.claude/settings.json` — lightweight defaults (statusline, context7, attribution)
- **governance/AGENTS.md** → `AGENTS.md` — agent behavioral rules and decision framework
- **governance/AGENT_LEARNINGS.md** → `AGENT_LEARNINGS.md` — pattern discovery template
- **governance/AGENT_REQUESTS.md** → `AGENT_REQUESTS.md` — human escalation protocol
- **governance/README.md** → `README.md` — value-first front door, derived from the [qte77 doc-structure canon](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md)
- **governance/CONTRIBUTING.md** → `CONTRIBUTING.md` — technical workflows + the `## Documentation hierarchy` statement

All files use copy-if-not-exists (won't overwrite).

## Persisting ~/.claude across container rebuilds

`scripts/link-claude-home.sh` is a copyable snippet, not something this plugin invokes itself. Copy it into your repo (e.g. `scripts/link-claude-home.sh`) and call it first in `.devcontainer/devcontainer.json`'s `onCreateCommand`, before any step that installs or touches Claude Code:

```json
"onCreateCommand": "bash scripts/link-claude-home.sh && make setup_all"
```

It symlinks `$HOME/.claude` to `/workspaces/.claude-files` (override with `CLAUDE_HOME_DIR` / `CLAUDE_HOME_PERSIST_DIR`) so memory, sessions, settings, and credentials survive a container rebuild — on platforms like GitHub Codespaces, everything outside `/workspaces` is cleared on rebuild, everything inside it persists.

This can't live in a plugin hook: `SessionStart` only fires once Claude Code (and this plugin) are already installed, which itself requires `~/.claude` to already be linked — a hook can't bootstrap the directory it lives inside. The `SessionStart` hook below does still warn if it detects `~/.claude` isn't a symlink, for visibility in sessions where it happens to run, but it can't self-heal.

Note this only covers `~/.claude` itself — `~/.claude.json` (trust/permission state per project, marketplace/onboarding flags) is a separate sibling file outside `~/.claude`, and it deliberately has **no fix here** ([decided not to build one](https://github.com/qte77/claude-code-plugins/issues/203)). Symlinking an individual live-rewritten file is a known-risky pattern — Claude Code config writes aren't verified atomic-rename-safe on every path, which silently breaks a file symlink (directory symlinks like `~/.claude` above aren't affected; see [#199](https://github.com/qte77/claude-code-plugins/issues/199) failure mode 1) — and the value (re-approving trust dialogs after a rebuild) didn't clear the bar against that risk plus this file's unresolved redaction question (it carries `oauthAccount`). The `SessionStart` hook still warns if `~/.claude.json` isn't linked, purely for visibility.

## read-once hook

PreToolUse hook that prevents redundant file re-reads within a session.
Saves ~2K tokens per blocked re-read (~40% reduction in typical workflows).

- **Mode**: warn (default) — allows read with advisory; set `READ_ONCE_MODE=deny` to block
- **TTL**: 1200s (20 min) — cache expires after this; set `READ_ONCE_TTL` to override
- **Diff mode**: set `READ_ONCE_DIFF=1` to show diffs instead of full re-reads for changed files
- **PostCompact**: cache clears automatically when CC compacts context
- **Partial reads**: offset/limit reads always pass through (never cached)
- **Disable**: set `READ_ONCE_DISABLED=1`

Based on [Bande-a-Bonnot/Boucle-framework](https://github.com/Bande-a-Bonnot/Boucle-framework) (MIT).

## Install

```bash
claude plugin install workspace-setup@qte77-claude-code-plugins
```

For sandbox settings, use `workspace-sandbox` instead.
