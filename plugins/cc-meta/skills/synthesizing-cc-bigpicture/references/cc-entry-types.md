# Claude Code JSONL Entry Types

Reference for parsing `~/.claude/projects/<path>/<session-uuid>.jsonl` files.

Source: `randlee/claude-history` entry type taxonomy + CC filesystem documentation.

## Session Transcript Entries

Each line in a session `.jsonl` file is a JSON object with a `type` field:

| Type | Description | Key Fields |
|------|-------------|------------|
| `user` | User messages (prompts or tool results) | `uuid`, `parentUuid`, `timestamp`, `message` |
| `assistant` | Claude responses with text and tool_use | `uuid`, `parentUuid`, `timestamp`, `message` |
| `system` | System events and hook summaries | `timestamp`, `event` |
| `queue-operation` | Subagent spawn triggers | `agentId`, `sessionId` |
| `progress` | Status updates during processing | `timestamp`, `status` |
| `file-history-snapshot` | Git state captured at session start | `staged`, `unstaged`, `untracked` |
| `summary` | Conversation summaries (from auto-compaction) | `timestamp`, `content` |
| `result` | Session completion markers | `timestamp`, `status` |

## Sessions Index

`~/.claude/projects/<path>/sessions-index.json` — metadata cache per project:

- Auto-generated summaries per session
- Message counts
- Git branch at time of session
- Creation and last-update timestamps
- Session UUIDs (link to `.jsonl` files)

**Prefer this over reading individual .jsonl files** — it's the metadata-first
approach for discovering what sessions contain.

## Plans

`~/.claude/plans/*.md` — plain markdown files with plan names as filenames
(often auto-generated whimsical names like `tingly-weaving-kite.md`).

## Tasks

`~/.claude/tasks/<session-id>/<id>.json` — structured objects:

```json
{
  "id": "3",
  "subject": "Task title",
  "description": "Task details",
  "status": "in_progress",
  "blocks": ["4", "5"],
  "blockedBy": ["1"]
}
```

The `blocks`/`blockedBy` arrays create a dependency graph within a task list.

## Teams

`~/.claude/teams/<team-name>.json` — team configuration including model
assignments per role.

## Session Memory

`~/.claude/session-memory/<session-id>.md` — auto-extracted notes with sections:
Current State, Task Specification, Files and Functions, Workflow, Errors &
Corrections, Learnings, Key Results.

## Project Memory

`~/.claude/projects/<path>/memory/MEMORY.md` — persistent per-project knowledge
loaded at conversation start.

## Path Encoding

Project paths are URL-encoded with dashes:
- `/home/user/myapp` → `-home-user-myapp`
- `C:\Users\name\project` → `C--Users-name-project`
