# memory-hygiene

Keeps Claude Code's auto memory small and correct. `MEMORY.md` loads into every session, so a
bloated or wrong index costs tokens on every request and carries mistakes forward. This plugin
runs a clean-up pass on a schedule you choose.

## What it does

- **Skill `consolidating-memory`** runs in a background subagent. It backs up the project's
  auto-memory directory, checks each memory against the repo, git history and recent sessions,
  fixes wrong facts, merges duplicates, deletes obsolete entries, flags what it can't verify, and
  rewrites `MEMORY.md` as a one-line-per-memory index. It reports what changed. Owner
  instructions (`feedback`, `user` memories) are kept; contradictions are flagged, not resolved.
- **Hook** (`SessionStart` and `SessionEnd`) decides when a pass is due. A hook can't run a model,
  so it only asks: in `auto` mode it tells Claude to run the skill at a natural break, in
  `remind` mode it only shows you a reminder.

Run it by hand any time with `/memory-hygiene:consolidating-memory`.

## Options

Set when you enable the plugin, or later in `/config`.

| Option | Values | Default |
| --- | --- | --- |
| `schedule` | `weekly`, `daily`, `monthly`: due once the interval since the last pass has passed. `session-start`: every new or cleared session. `session-end`: a session end marks it due and it runs at the next session start (a session-end hook has about 1.5 seconds and can't run a model). `compact`: right after each compaction, auto or manual. `off`. | `weekly` |
| `mode` | `auto`: Claude runs the skill in a background subagent (costs one subagent run per pass). `remind`: a reminder only, no model cost. | `auto` |

Schedules are tracked per project in the plugin's data directory (`${CLAUDE_PLUGIN_DATA}`), which
also holds the last 3 backups per project.

## Notes

- The memory directory follows Claude Code's rule: one per git repository (worktrees share it),
  or `autoMemoryDirectory` from user settings. Nothing runs when auto memory is off
  (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`) or the project has no `MEMORY.md`.
- Tests: `bash plugins/memory-hygiene/scripts/test.sh`.
- Background: the "dreaming" idea in
  [Components of agent memory](https://www.anthropic.com/research/components-of-agent-memory).
