# workspace-sandbox

Deploys workspace rules, statusline script, and eased sandbox settings via SessionStart hook.

Uses the **hybrid approach**: network sandbox ON, filesystem relaxed for multi-repo
Codespace workflows. The container provides filesystem isolation; CC provides
network exfiltration protection.

## Deployed files

- **rules/*.md** → `.claude/rules/` — core principles, context management, compound learning, CI status checks, unattended execution, read discipline, review tiers
- **scripts/statusline.sh** → `.claude/scripts/` — status line display. The context field shows the share of the window in use and the share at which compaction fires (`ctx:46% used·compact@50%`, from `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`; `!` when at most 3% usable is left). World clock off by default. Two ways to opt in: (1) **persistent** — set `CC_WORLD_CLOCK="Asia/Tokyo,Europe/Paris,Europe/London,UTC,America/New_York,America/Los_Angeles"` in your shell rc (needs CC restart to change); (2) **live toggle** — write the same comma-separated zone list to `~/.claude/world-clock` (next prompt render picks it up; `rm` the file to turn off). Env var wins over file. Use east-to-west / sunrise order or any IANA zones you prefer. Each entry is either a bare zone (`Europe/Paris` → label `Paris`) or `Zone=Label` to override the rendered label (`America/New_York=NYC` → label `NYC`). Zones render on a dedicated line below the main statusline; invalid zones show as `?<name>`. See the comment block at the top of `.claude/scripts/statusline.sh` for the curated shortlist and usage notes.
- **settings/.gitignore** → `.gitignore` — hides bwrap phantom files from git status
- **settings/settings-sandbox.json** → `.claude/settings.json` — eased sandbox, permissions, env vars; its `env` sets `BASH_MAX_OUTPUT_LENGTH` `15000` (characters of Bash output kept in context) and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` `50` (percentage of the auto-compact window at which auto-compaction fires; it can only lower the threshold, and applies only in sessions that compact before the model's context limit), see [env vars](https://code.claude.com/docs/en/env-vars). If `.claude/settings.json` is tracked by git, or git cannot say, the hook leaves it untouched, writes nothing else for settings and prints one warning line. Git cannot say when git is missing or errors, when `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` is set in the environment, or when `realpath -m` (GNU coreutils, not on stock macOS) is unavailable; then the whole settings step is skipped, including for an untracked or absent file.
- **governance/*.md** → `AGENTS.md`, `AGENT_LEARNINGS.md`, `AGENT_REQUESTS.md` — agent governance; `README.md` + `CONTRIBUTING.md` — the doc-structure canon companions `AGENTS.md` links to

All files use copy-if-not-exists (won't overwrite).

## read-once hook

PreToolUse hook that prevents redundant file re-reads within a session.
Saves ~2K tokens per blocked re-read; total savings scale with how often a
session re-reads files it already has (no aggregate figure is measured).

- **Mode**: warn (default) — allows read with advisory; set `READ_ONCE_MODE=deny` to block
- **TTL**: 1200s (20 min) — cache expires after this; set `READ_ONCE_TTL` to override
- **Diff mode**: set `READ_ONCE_DIFF=1` to show diffs instead of full re-reads for changed files; snapshots skip secret-like files (`.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_*`, `*credential*`, `.netrc`, `.npmrc`, `.pgpass`; matched case-insensitively, on the requested name and on the symlink target) and files over 1 MiB. A hard link has its own name, so a hard link to a secret file under a plain name is still snapshotted
- **Cache**: per user under `claude-read-once-<uid>/<session>` in `$XDG_RUNTIME_DIR` (else `$TMPDIR`, else `/tmp`), mode 700; the hook does nothing if that dir is a symlink or not owned by you. Earlier versions used `${TMPDIR:-/tmp}/claude-read-once-<session>`, which is no longer read or cleaned up and may hold world-readable snapshots: remove those `claude-read-once-<session>` directories you own. Don't remove them with a `claude-read-once-*` glob: without `$XDG_RUNTIME_DIR` it also matches the current `claude-read-once-<uid>` base
- **PostCompact**: cache clears automatically when CC compacts context
- **Partial reads**: offset/limit reads always pass through (never cached)
- **Disable**: set `READ_ONCE_DISABLED=1`
- **Requires** `jq`, `md5sum`, `realpath` and `stat`: if one is missing the hook silently does nothing (stock macOS has no `md5sum`)

Based on [Bande-a-Bonnot/Boucle-framework](https://github.com/Bande-a-Bonnot/Boucle-framework) (MIT).

## Sandbox configuration

- `enableWeakerNestedSandbox: true` — works inside unprivileged Docker (Codespaces)
- `autoAllowBashIfSandboxed: true` — auto-approve sandboxed bash commands
- `allowUnsandboxedCommands: false` — no escape hatch
- `excludedCommands: ["docker *"]` — docker runs outside sandbox
- **Filesystem**: `/workspaces` (cross-repo writes), `.git`, `/tmp/claude-1000`
- **Network**: GitHub, npm, PyPI registries

## Install

```bash
claude plugin install workspace-sandbox@qte77-claude-code-plugins
```

For defaults without sandbox, use `workspace-setup` instead.
