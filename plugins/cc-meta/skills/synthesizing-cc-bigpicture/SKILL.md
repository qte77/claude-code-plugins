---
name: synthesizing-cc-bigpicture
description: Synthesizes a living big-picture meta-plan from Claude Code sessions, plans, tasks, and team communications. Use when orienting across projects, assessing reasoning modes, or creating a plan-to-plan overview.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob
  argument-hint: [project filter, time range, or output path]
  context: fork
---

# Big-Picture Synthesis

**Query**: $ARGUMENTS

Synthesizes a **plan to plan** — an overarching view across all Claude Code
artifacts. Not a search tool. A reasoning tool that connects sessions, plans,
tasks, and memories into a coherent narrative of what you're working on, why,
and where you're headed.

## Three Reasoning Axes

Track these per work stream to surface where you are and what shift is needed:

### Diverge / Converge

- **Diverge**: Expanding — brainstorming, exploring options, opening questions
- **Converge**: Narrowing — selecting approaches, committing, closing questions
- **Signals**: Open questions in plans = diverging. Task completion clustering = converging. Multiple branches = diverging. Merge activity = converging.
- **Alert**: Diverging for N sessions without convergence → decision debt

### Inductive / Deductive

- **Inductive** (bottom-up reasoning): Observations → patterns → principles
- **Deductive** (top-down reasoning): Principles → predictions → implementations
- **Signals**: `## Learnings` in session-memory, AGENT_LEARNINGS = inductive. PRD/plan goals driving task creation = deductive.
- **Alert**: Implementing without learning (assumptions) or learning without formalizing into plans (knowledge not actionized)

### Top-down / Bottom-up

- **Top-down**: Strategy → decomposition → tasks (PRD → architecture → implementation)
- **Bottom-up**: Details → integration → strategy (bugs reveal gaps, tests surface flaws)
- **Signals**: PRD→task flow = top-down. Blockers→plan revisions, AGENT_REQUESTS = bottom-up.
- **Alert**: All top-down (no implementation feedback) or all bottom-up (reactive without direction)

## When to Use

- Starting a work session — orient across projects
- Planning what to work on next — strategic prioritization
- Sprint/week boundary — maintain the meta-plan
- Feeling stuck — surface current reasoning mode and whether a shift is needed
- Onboarding someone to your work streams

## Do Not Use

- For searching a specific past conversation (use `/resume` or `/history`)
- For per-session context (session-memory does this automatically)
- For modifying or deleting session history
- For real-time usage monitoring (use `/insights`)

## CC Data Sources

```
~/.claude/
├── history.jsonl                              # Global prompt log
├── projects/<encoded-path>/
│   ├── sessions-index.json                    # Summaries, counts, branches, timestamps
│   ├── memory/MEMORY.md                       # Per-project persistent knowledge
│   └── <session-uuid>.jsonl                   # Full transcripts (DO NOT read in bulk)
├── plans/*.md                                 # Plan mode files
├── tasks/<session-id>/<id>.json               # Tasks (subject, status, blocks/blockedBy)
├── teams/<team-name>.json                     # Team configs
├── todos/<composite-id>.json                  # Per-session todos
└── session-memory/<session-id>.md             # Auto-extracted session notes
```

See `references/cc-entry-types.md` for JSONL entry type reference.

## Workflow

1. **Parse arguments** — Extract project filter, time range, focus area, or output
   path from `$ARGUMENTS`. Default output: `~/.claude/bigpicture.md`.

2. **Check existing** — Read output path. If bigpicture.md exists, load it for
   incremental update (preserve structure, update content).

3. **Discover projects** — Glob `~/.claude/projects/*/sessions-index.json`.
   Decode project names from path encoding (`-` → `/`). Filter if arguments
   specify project name or time range.

4. **Collect signals** (sequential, metadata-first — no subagents):
   - **Sessions**: Read `sessions-index.json` per project — summaries, timestamps, branches
   - **Plans**: Glob + Read `~/.claude/plans/*.md` — goals, open questions, decisions
   - **Tasks**: Glob + Read `~/.claude/tasks/*/*.json` — dependency graph, status
   - **Memory**: Read `~/.claude/projects/*/memory/MEMORY.md` — persistent knowledge
   - **Session memory**: Grep `~/.claude/session-memory/*.md` — learnings, errors
   - **Teams**: Read `~/.claude/teams/*.json` — active configurations

   **Critical**: Never read full session `.jsonl` transcripts in bulk. Use
   `sessions-index.json` summaries and `session-memory/*.md` notes instead.

5. **Classify reasoning modes** per work stream:
   - Count open questions vs. closed decisions in plans → diverge/converge
   - Count learning entries vs. plan-driven tasks → inductive/deductive
   - Trace flow: PRD→tasks (top-down) vs. blockers→revisions (bottom-up)
   - Flag mismatches per axis (see alerts above)

6. **Synthesize connections**:
   - Group sessions by project, then by time clusters (work streams)
   - Link plans → sessions (timestamp + project correlation)
   - Link tasks → plans (session-id in task path)
   - Identify recurring themes across project memories
   - Surface blockers: tasks with unresolved `blockedBy`
   - Detect trajectory: momentum (recent activity) vs. stale (no sessions in N days)

7. **Output** using format below. Write to output path.

## Output Format

```markdown
# Big Picture — <date>

## Reasoning Mode Summary

| Project | Phase | D/C | I/D | T/B | Alert |
|---------|-------|-----|-----|-----|-------|
| <name>  | <phase> | Diverging | Inductive | Bottom-up | <alert or —> |

Legend: D/C = Diverge/Converge, I/D = Inductive/Deductive, T/B = Top-down/Bottom-up

## Active Work Streams

### <Project Name>
- **Status:** <active/stalled/completed> — <N sessions in last 7d>
- **Current focus:** <from latest summaries + memory>
- **Reasoning mode:** <diverging+inductive = exploring> | <converging+deductive = building>
- **Key decisions:** <from plans + session memory>
- **Open questions:** <unresolved — divergence points>
- **Open tasks:** <N open> / <N total> — blockers: <list>
- **Trajectory:** <accelerating/steady/stalled>

## Cross-Project Connections
- <Project A> learning X informs <Project B> design Y (inductive→deductive bridge)
- Shared pattern: "<theme across memories>"

## Active Plans
| Plan | Project | Mode | Status | Key Goals |
|------|---------|------|--------|-----------|

## Blockers & Stale Items
- Task "<subject>" blocked since <date>
- Project "<name>" — no sessions in <N> days

## Mode Transitions Needed
- <Project>: Shift diverging → converging (enough options explored)
- <Project>: Shift top-down → bottom-up (implementation feedback needed)
- <Project>: Formalize learnings (inductive) into plan updates (deductive)
```

## Common Pitfalls

- **Data dump instead of synthesis**: If output exceeds ~200 lines, raise abstraction level. The skill interprets, not lists.
- **Stale big picture**: Only as fresh as last invocation. Not auto-updating.
- **Reading full transcripts**: Use `sessions-index.json` + `session-memory/*.md`. Never bulk-read `.jsonl` files.
- **False mode classification**: Reasoning modes are heuristic signals, not definitive judgments. Present as evidence-based assessment.
- **Spawning subagents**: Do not use Agent tool. Sequential processing within the fork context is sufficient. Only justified at extreme scale (50+ projects) with explicit user request.

## Quality Check

- Correct > Complete > Minimal (ACE-FCA)
- ~100-200 lines output (concise, not exhaustive)
- Every claim traces to a specific CC artifact (file path, session summary, plan name)
- Incremental update preserves structure, refreshes content
- No subagents spawned during normal operation

## References

See `references/cc-entry-types.md` for JSONL session entry type taxonomy.
