---
name: verifying-design-canvas
description: Pull a Claude Design canvas (.dc.html) straight from claude.ai/design and verify a live deployed app actually matches it — theme tokens, DOM/accessibility structure, and every interactive role/tab state, not just the default view. Use when asked "does the site match the design", "is the design source stale", or before/after building a UI from a design-refs canvas.
---

# Verifying a design canvas against a live app

Use this whenever someone asks whether a deployed app matches its Claude Design source, or
whether a repo's committed `docs/design-refs/*.dc.html` mirror has drifted from the live canvas.
Learned the hard way: a text-level or default-state-only diff misses real gaps — an interactive
canvas can mock an entire screen that only appears in a non-default state (a role selection, a
tab, a toggle), and a document diff alone won't render it.

## 1. Pull the canvas straight from source (not a stale local copy)

The `DesignSync` tool reads `claude.ai/design` projects directly — the URL form is
`claude.ai/design/p/<projectId>?file=<name>`.

```
DesignSync(method: "get_project", projectId: "<uuid>")   # confirms access + canEdit
DesignSync(method: "list_files", projectId: "<uuid>")    # find the exact filename (often several:
                                                          # "X.dc.html" the editable source,
                                                          # "X -export-.dc.html" a frozen export,
                                                          # "X.html" a compiled/flattened view —
                                                          # read the .dc.html one, it's the source)
DesignSync(method: "get_file", projectId: "<uuid>", path: "<exact filename>")
```

If a published Artifact URL (`claude.ai/code/artifact/<id>`) is given instead of a `design/p/`
project URL, `Artifact(action: "read", url: ...)` works too, but it's a **snapshot at publish
time** — a "Bundled Page" with the canvas's HTML/CSS/JS inlined into one self-contained file. Only
trust it as current if you also pull the live project and confirm the two match (see step 2); a
canvas can be edited after an Artifact was published and the snapshot goes stale silently.

## 2. Diff against the repo's committed mirror first (cheap, catches drift)

If the repo keeps its own copy (e.g. `docs/design-refs/*.dc.html`), byte-compare it against what
`get_file` just returned before doing anything else — this is free and tells you immediately
whether "the design changed" or "the repo's copy is stale" before you spend effort on a live-app
render comparison.

Don't stop at a whole-file diff if they differ — split by section markers (canvas HTML often has
`<!-- ═══ SCREEN NAME ═══ -->` dividers) and diff each section, since large aggregate diffs are
often dominated by the trailing `<script>` block (sample data, unrelated to markup) while every
actual screen section is untouched, or vice versa.

## 3. Render BOTH sides for real — screenshots + accessibility tree + computed CSS

A text diff of markup only tells you the *source* matches; it does not tell you the *rendered app*
matches, and it cannot see runtime-only differences (a role toggle, a live matchMedia fork, a
loading/empty state). Drive a real headless browser (Patchright, Playwright, or a polyfetch-style
scripting substrate that exposes the live `Page`) for:

- **Screenshots** — full-page, at every distinct viewport/breakpoint the app forks on.
- **The accessibility tree** (`page.locator("body").aria_snapshot()` on Patchright/Playwright) —
  diff this between the canvas render and the live app render: same headings, same roles
  (`button`/`tab`/`link`), same labels, same nesting for equivalent sections. Catches structural
  drift that a screenshot alone can blur past.
- **Computed CSS** via `page.evaluate(...) -> getComputedStyle(...)` for the specific design
  tokens claimed (background color, accent color, font-family, border-radius) — read the actual
  CSS custom properties (`--primary`, `data-theme`, `data-variant` attributes) where the app
  exposes them; more authoritative than scanning one element's resolved style.

A canvas artifact/`.dc.html` renders standalone: if it's a self-contained "Bundled Page" (from
`Artifact read`), open it via a plain `file://` URL — it self-unpacks (wait for the "Unpacking..."
overlay to clear, several seconds) with no network dependency. A raw `.dc.html` from
`DesignSync.get_file` is a live-editor source format (`<sc-if>`/`<sc-for>`/`{{ }}` template
tags, an inline `<script type="text/x-dc">`) — it is generally NOT directly openable as a static
page; prefer comparing it at the text/section level (step 2) plus reading its embedded script for
sample-data intent, rather than trying to render it raw.

## 4. Handle capability-backed canvases separately from pure-mockup ones

Some canvases declare a runtime **capability** (live/connected data, saved state, a viewer-count,
an ask-Claude question — anything backed by `window.claude.*` calls, per the platform's own
capability list). A bare local render (the `file://` "Bundled Page" from step 3) has no
`window.claude` object at all — those calls either throw, or, if the canvas defensively guards
them, silently fall back to an empty/loading state. Either way, that section is **not** rendering
its real content in a local-only comparison.

Check for this before trusting a local-render screenshot as a full substitute:

- **Scan the pulled source first** (step 1/2's `get_file`/`Artifact read` output) for a
  `capabilities` declaration or `window.claude.` calls. None found → the local `file://` render
  from step 3 is a complete substitute, skip the rest of this step.
- **Some found, and only structural fidelity matters** (layout, spacing, typography, DOM/aria
  shape) — inject a no-op polyfill before the page's own scripts run
  (`page.add_init_script(...)` on Patchright/Playwright: define `window.claude` with stub
  `getData`/`setData`/`complete`/etc. that resolve to `null`/no-op) so capability-driven sections
  render their empty/default state instead of crashing. Good enough for the accessibility-tree and
  computed-CSS checks in step 3; the capability region's actual *content* is still unverified.
- **The capability-populated content itself needs verifying** (not just structure around it) —
  only the real backend can serve that, so fall back to an authenticated `claude.ai` session
  driving the live hosted canvas/Artifact URL for that specific region. Scope this to the
  capability-bearing section only; keep using the local render for everything else — the auth
  overhead isn't worth paying for the whole page when most of it doesn't need it.

Carry this distinction into step 7's report: state plainly whether a capability region was
structure-checked only (stubbed) or content-verified (live), don't let a stubbed pass read as a
full match.

## 5. Exercise every interactive state, not just the default render

**This is the step that's easy to skip and easy to get burned by.** A canvas with a role
picker, tab bar, or mode toggle can mock a COMPLETELY different screen per state — read the
canvas's own script for state branches (e.g. `role==='X' ? screenA : screenB`,
`isSupply = role==='host' || role==='sponsor'`) and render/screenshot each one live, not just
whatever's on screen by default. A "looks fine" verdict from two passes that only checked the
default state can still miss a whole screen mocked behind a non-default toggle.

## 6. Judge sample data on its own terms — real substitute vs. no substitute

Canvas scripts routinely carry realistic-looking but 100% fake sample data (per-role `hooks`/
`fit`/`prep` text, hardcoded metrics, a `toast(...)` call with no real backend behind it even in
the mockup). Before treating a visual gap as a "missing feature to build," check the canvas's own
handler code for that interaction:

- If the interaction has **no real logic behind it even in the design tool** (a static toast
  string, a hardcoded reference to one sample record) — there is nothing to "import and wire up."
  Building it for real requires new backing data/capability that doesn't exist yet. File it as an
  issue (cross-repo if the missing capability lives in a different service) rather than shipping
  fabricated UI.
- If a **real substitute already exists or is buildable** (e.g. a ranking engine can replace fake
  per-role copy with a genuine score), build against that instead of porting the sample text
  verbatim — this is the normal "don't fabricate content" rule, not a new one.

## 7. Report precisely

State exactly what was compared (which URLs/files, which viewports, which interactive states),
give the concrete matching/mismatching values (not "looks the same" — the actual computed color,
the actual aria diff), and separate **real gaps** (a screen state exists in the design with no
live equivalent and no real data to back it) from **correct, deliberate omissions** (fake content
properly left out, matching a no-fabrication discipline). Conflating the two either overstates a
bug or understates a real gap.
