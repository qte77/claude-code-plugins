# Goal Progress

How `synthesizing-cc-bigpicture` reads strategic goals and renders the **Goal Progress** section.

## Source

`goals.json` at the root of the qte77 profile repo ([qte77/qte77](https://github.com/qte77/qte77)).
Its shape (goals → key results, each KR with `id`, `statement`, `eval`, `issue`, `status`) is
documented in [qte77/qte77 `docs/goals.md`](https://github.com/qte77/qte77/blob/main/docs/goals.md) —
read it there; this skill does not restate the schema.

**Locate it locally** (the skill has no network or shell access):

1. From the discovered project paths, pick the one whose decoded path is a checkout of
   `qte77/qte77`, and Read `<path>/goals.json`.
2. If no such checkout exists, or the file is missing or invalid JSON: skip this source and say so
   in the section — never invent goals.
3. Goals are human-authored. Read them; never edit `goals.json`.

## Matching work to a goal

Goal IDs look like `G01`; KR IDs like `G01-KR1`. Attribute a session, plan or PR to a goal or KR when
its ID appears in any of:

- **Plans** — plan file body or filename (`~/.claude/plans/`, project `docs/plans/`)
- **PR labels / branch names** — as seen in session metadata and `history.jsonl` prompts
  (e.g. a `goal` label, a `G01-KR1` branch segment)
- **Memory** — project `MEMORY.md` and linked memory files
- **KR issue** — a session or PR that references the KR's `issue` number

Count only explicit ID or issue references. Topic similarity is not a match — if you suspect drift,
say so in **Signal**, don't attribute.

## Output

Render the section after **Active Plans**:

```markdown
## Goal Progress
| Goal | KR | Sessions | Plans | PRs | Signal |
|------|----|----------|-------|-----|--------|
```

- One row per KR; `Goal` repeats the goal ID.
- `Sessions` / `Plans` / `PRs` — counts of matched artifacts in the time range.
- `Signal` — `active`, `stalled` (no matched work in range), `done` (KR `status` closed), or
  `drift` (work streams active with no goal match while KRs are stalled).
- If `goals.json` has no goals, or was not found: keep the heading and write one line saying which
  (`No goals defined in goals.json` / `goals.json not found — section skipped`).
