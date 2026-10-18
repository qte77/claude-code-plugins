# Unattended E2E Execution (arc template)

**Goal: long-running, e2e hands-off unattended sessions with minimal supervision and
intervention.** These constraints generalize across projects and repos; apply each section per the
use case (e.g. the UI-e2e section applies when the project ships a UI).

## Plan artifact (one per arc)

- Save ONE file per arc: `docs/plans/YYYY-MM-DD-NNNN-slug.md` (creation date, 4-digit sequence =
  next free number — never reuse or renumber — kebab slug). No separate handoff files or
  `handoffs/` folders: merge any existing handoff into its plan. No separate
  onboarding file, and no dedicated "handoff" ritual or section name either — the plan document
  itself opens with the current status (what shipped, what's next in order, the loop, owner-gates,
  commands, watch-outs), then the rest of the plan (source map, approach, remaining-work table). A
  single file per arc is easier to keep in sync than two that can drift, and a plain "read the plan"
  is easier to follow than "read the plan, then also read its handoff."
- **The plan's opening MUST onboard the next session to it and how to handle it**: what shipped,
  what's next (in order), the loop, owner-gates, commands, watch-outs.
- **The plan MUST contain a code/file/source map** (exact files, functions, line refs, external
  refs, reference blueprints) so the next session does **not** have to map or gather context again.
- Keep the plan (its opening status included) + memory in sync at every milestone. Close an arc by
  marking shipped items and migrating the entire remainder to the next arc's plan — never leave work
  stranded in a closed arc.
- **EXACTLY ONE remaining-work table per plan.** One section lists what is still open, one row per
  item, with a **gate** column (`agent` / `owner` / `data`) and a **done-when**. Source maps, design
  sections, and execution orders may describe HOW an item is done — they must NEVER re-list WHAT is
  open; they point at the table. Two lists of open work always drift into disagreement, and the
  next session then re-does shipped items because it trusted the stale copy.
- **Strike the row in the SAME PR that ships it** — not in a later docs PR. A merged PR whose plan
  row still reads "remaining" is an incomplete PR.
- **No orphans: every plan item ends in exactly one state** — shipped (with its PR number), deferred
  (with the gate + the reason), or a live row in the table. An item that is described in the plan
  but appears in none of the three is a doc bug; audit for orphans at every arc close.

## Non-blocked phase shape (structure every arc this way)

- **Phase A — agent-only:** front-load EVERY agent-runnable slice; never interleave owner-gated
  items mid-sequence.
- **Pre-stage every gate during Phase A:** migration SQL (PR'd, unapplied), remediation scripts,
  dry-run reports — so gates become approvals, not work sessions.
- **Phase B — ONE owner sitting:** batch all gates (migrations, DB mutations, spend) into a single
  pre-staged checkpoint.
- **Phase C — activation:** agent resumes (verify, activate gated features, e2e, deploy).
- **Decide-by-default:** every open decision in the plan carries a recommended default; proceed
  with the default unattended; the owner overrides at the checkpoint.
- **Done-when per item:** each backlog item states its verification so the agent self-verifies and
  moves on.
- **Build-behind-gate:** ship data-dependent features dormant behind their gate; they activate when
  the data lands — code never waits on data.
- **Arc-start access checklist:** list the credentials/grants the arc needs in the plan; the owner
  provisions once up front (no mid-run credential stalls).
- **Bounded write budgets:** pre-approve capped, backup-first data writes (dry-run shown) instead
  of gating every small write.

## Per-milestone discipline (after every major milestone / merged PR)

- **Git:** new branch per topic; commits by topic (`feat`/`fix`/`test`/`docs`/`chore`); push +
  squash-merge ONLY if all CI + test items pass; delete stale remote AND local branches.
- **Docs & issues audit:** CHANGELOG · root README · architecture/ADRs · roadmap · userstory ·
  registries · consumer-facing contract/interface doc (e.g. `docs/CONTRACT.md`, a design-token
  source doc) if the repo has one — updates needed? New **URLs / env vars / CLI switches**
  documented (README tables + CHANGELOG)? Issues to **open/update/close** (close shipped features;
  advance — never auto-close — multi-item trackers)? If a CI test asserts the contract doc against
  the live source (the pattern to prefer over a purely hand-maintained doc), does it still pass?
- **Progress report (concise):** what **shipped** · what's **next** · **overall % of the plan** ·
  **blocked/deferred** (+ what's pre-staged for each).

## Quality gates (always)

- **Strict TDD: first model the expected and desired behavior** (RED first). Only non-trivial
  tests, only where necessary — for modules, never for simple scripts/config;
  rendering/wiring = e2e is the test.
- Run the EXACT CI gate locally before pushing (the repo's make/npm validate target incl. format
  checks) — never à la carte. Run the audit (dependency/security) target too.
- Assume strict lint + typing + security always.

## UI e2e verification (when the project ships a UI)

- Use **polyfetch + its patchright chromium** for e2e UI tests, **locally AND against the remote
  deploy**.
- Vary the **viewport + device emulation**; **click buttons, dropdowns, and other interactive
  elements** to verify functionality *and* appearance — not just render presence.
- Take **screenshots and (opt-in) videos in horizontal and vertical orientation**.
- Use the patchright/chromium **devtools**: capture **console errors** (fail the run on app console
  errors) and failed network requests.

## Context economy (see context-management.md)

- Delegate discovery/search/audits/long-running ops to **subagents**; the main thread keeps
  conclusions, not dumps.
- **Compact at phase/milestone boundaries**; durable facts belong in the plan or memory, not only
  in-conversation.
- **Enforcing compaction in long runs:** the model cannot trigger `/compact`; set
  `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=<pct>` (e.g. 50) to fire auto-compact earlier (main +
  subagents); in SDK/headless runs `/compact [instructions]` can be sent as a prompt input. Shape
  WHAT survives via a "what to preserve" section in CLAUDE.md (plan state, shipped list, next
  steps, branch/PR state); a `PreCompact` hook may archive/block but never trigger or rewrite.
- Redirect verbose command output to files; read back only the relevant slice.
- **What to preserve during compaction** (the compactor reads this): the current arc + its state
  (newest `docs/plans/` file, items done/in-flight) · this session's shipped list
  (PR numbers + one-liners) · the ordered next steps + done-whens · branch/PR/CI state + anything
  uncommitted · parked owner-gated items + their pre-staged artifacts · unresolved decisions + the
  defaults being applied. **Drop** raw command output, file dumps, and search results already
  distilled into the above.
