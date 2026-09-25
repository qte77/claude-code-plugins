<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- **cc-meta** (1.16.0): new `cross-checking-research` skill + bundled `workflows/research-cross-check.js`
  (#180) — bidirectional consumer-repo ↔ research-hub cross-check (pull cites/adoptions, push drafted
  findings). Paths are required args; no hardcoded repo defaults; read-only agents.
- **Release workflows**: `bump-version.yaml`, `tag-release.yaml`, `publish-release.yaml` call the
  shared `qte77/.github` reusables for the root marketplace version; `.bumpversion.toml` bumps
  `metadata.version`, the README badge, and rolls `[Unreleased]` into a dated section. See
  CONTRIBUTING.md "Releases". New `make docs_stage` target.
- **web-recon** (0.1.0): new plugin — `web-recon` skill drives the
  [web-recon-kit](https://github.com/qte77/web-recon-kit) harness for authorized web/API
  attack-surface assessment (passive enumeration, auth-posture matrix, BOLA/BFLA, cron checks),
  with a mandatory authorization gate.
- **website-audit** (1.2.3): `verifying-design-canvas` — trimmed the frontmatter description to
  the repo's 250-char cap (was 366), added a "Related skills" note distinguishing this
  verification skill from the built-in `artifact-design`/`artifact-diagramming`/
  `artifact-capabilities` creation skills, and named `polyfetch` (this repo's own e2e substrate,
  per `.claude/rules/unattended-execution.md`) explicitly instead of a generic "polyfetch-style"
  hedge.
- **website-audit** (1.2.2): `verifying-design-canvas` — added publishing comparison screenshots
  as a viewable page (embedded base64, captioned per specific claim) as an explicit technique for
  step 7 ("Report precisely"): a screenshot opened via the Read tool renders for the model only, so
  in a CLI session a human reader never sees it no matter how precisely it's described in text —
  confirmed on a real verification run this session.
- **website-audit** (1.2.1): `verifying-design-canvas` — folded in four lessons from a real
  design-fidelity run against a live canvas: `get_file`'s 256 KiB cap truncates silently (always
  fetch `.dc.html`, never the compiled bundle); Cloudflare's bot challenge blocks headless
  `claude.ai/design` access even with a captured session cookie + solved `cf_clearance`, so
  `DesignSync` is the only working path; a committed mirror draws static-analysis noise that
  should be excluded at the repo's scan config, not hand-fixed in a file that gets wholesale
  replaced; a "recently refreshed" note is not proof of current freshness.
- **website-audit** (1.2.0): new `verifying-design-canvas` skill — pulls a Claude Design canvas
  straight from `claude.ai/design` via the `DesignSync` tool and verifies a live deployed app
  actually matches it (theme tokens, accessibility-tree structure, every interactive role/tab
  state), rather than trusting a text-only diff or a possibly-stale published Artifact snapshot.
  Also covers capability-backed canvases: stub `window.claude` for a structural-only check, or
  fall back to an authenticated live render when the capability's actual content needs verifying.

### Changed

- **#175 stability sweep**: 13 mature skills now `stability: stable` + `content-hash` (guarded by
  `verify-skill-hashes`): commit-helper 1.1.2, docs-governance 1.6.1, ralph 1.0.4 (2),
  readme-generator 1.2.2, market-research 1.0.3 (8). 52 of 67 skills are now hash-guarded.
- **workspace-setup** (1.5.2): decided not to build `~/.claude.json` rebuild-persistence — closed #203.
  Warning wording updated from "no recommended fix yet" to reflect that this is final, not pending.

### Fixed

- **Makefile**: recipes now fail fast (`.SHELLFLAGS := -ec`). Under `.ONESHELL` only the last line's
  exit code counted, so `make validate` passed with a broken plugin JSON and `make check_sync`
  passed with drifted copies or broken symlinks (subshell `exit 1`, bare `diff -q`).
- **workspace-sandbox** (#151): governance now ships `README.md` + `CONTRIBUTING.md` (mirrored from
  the docs-governance canon templates by `make sync_governance`, guarded by `make check_sync`), so the
  deployed `AGENTS.md` links resolve — parity with workspace-setup.
- **marketplace** (#184): removed the ghost `simplify` entry (plugin deleted in #119; `claude plugin
  install simplify@…` failed). **gha-dev** (1.2.3): companion-plugins reference now points at the
  built-in `/simplify` instead of the removed plugin.
- **CI** (#150): `compute-skill-hashes.sh --check` now fails on stable skills with no `content-hash`
  (15 of 39 bypassed the gate), and `--update` inserts a missing hash instead of silently doing
  nothing. Backfilled: cpp-desktop 1.0.2, gha-dev 1.2.2, go-dev 1.0.2, rust-dev 1.0.2,
  security-audit 1.2.1, typescript-dev 1.0.2.
- **cc-meta** (1.16.1, #155): the SessionStart seed no longer drops an untracked `MEMORY.md` into
  git working trees.
- **workspace-setup** (1.5.3), **workspace-sandbox** (1.3.12): read-once hook degrades to a no-op when
  `jq`/`md5sum`/`realpath`/`stat` is missing instead of failing every Read (#186); the 6 dead
  `Bash(git:add:*)`-style allow rules in the settings templates now use the matching
  `Bash(git add:*)` form (#183 — the `ask` commit / `deny` push rules are left for a policy decision).
- **Pages deploy** (#213): never succeeded since it was added (0/120 runs) — `mkdocs.yml` nav pointed
  outside `docs/` and at 5 deleted analysis docs. Docs are now staged into `docs/` at build time, the
  nav is generated, and the build uses `uv`. Stale counts dropped from `site_description`.
- **README**: badge 3.6.0 -> 3.7.0 (matches `metadata.version`); added the missing
  `readme-generator` and `website-audit` rows.
- **cc-meta** (1.15.3), **docs-generator** (1.0.4): quote multi-argument `argument-hint`
  values (e.g. `"[time-range] [output-path]"`) in 7 SKILL.md files — unquoted `[a] [b]` is invalid
  YAML (`expected <block end>, but found '['`), so the frontmatter failed to parse.
- **website-audit** (1.2.4): quote the `verifying-design-canvas` description — the 1.2.3 trim
  introduced an unquoted colon followed by a space (`.dc.html): theme`), which YAML reads
  as a nested mapping.
- **workspace-setup** (1.5.1): `link-claude-home.sh` now verifies the symlink actually points at the
  configured persisted target, not just that some symlink exists at `~/.claude` — a stale link (e.g.
  after a path or account change) previously read as "already linked" and was never corrected.

### Added

- **workspace-setup** (1.5.0): `scripts/link-claude-home.sh` — copyable snippet that symlinks `~/.claude`
  to persisted storage (e.g. `/workspaces` on GitHub Codespaces) so memory, sessions, settings, and
  credentials survive a container rebuild; must run from a devcontainer's `onCreateCommand` since a
  plugin hook can't bootstrap the directory it lives inside. `SessionStart` hook now warns (non-fatal)
  when it detects `~/.claude` or `~/.claude.json` isn't linked/persisted — the latter has no recommended
  fix yet, since symlinking an individual live-rewritten file is a known-risky pattern (#199 failure
  mode 1).
- **security-audit** (1.2.0): `triaging-security-report` skill — verify an external/AI-generated
  security report against the actual code before acting; four-way verdict rubric
  (CONFIRMED / OVERSTATED / FALSE-POSITIVE / FABRICATED), deployment-context severity re-rating,
  trusted-input precedents, salvage-the-kernels close-out (#188)

<!-- Pre-#37 entries (preserved) -->

- **market-research**: New plugin with 8 skills — GTM pipeline with teams mode parallel dispatch, 2x2 strategy matrix, contradiction analysis, slide deck generation
- **python-dev**: Scaffold adapter for Ralph loop (`scaffold/adapter.sh`, project templates, GHA workflows)
- **embedded-dev**: Scaffold adapter with `find -print0 | xargs -0` safe filenames
- **commit-helper**: `creating-pr-from-branch` skill — branch analysis, PR template population, approval gate, Codespaces auth handling
- **docs-governance**: New plugin (1.0.0) with `enforcing-doc-hierarchy` and `maintaining-agents-md` skills
- **cc-meta**: `synthesizing-cc-bigpicture` skill — project filter param (`[project-name] [time-range] [output-path]`), usage examples
- **cc-meta**: Auto-resolve output path — project-filtered runs write to `<project>/docs/bigpicture.md`, unfiltered to `~/.claude/bigpicture.md`
- **cc-meta**: Project-Arching TODOs & DONEs output section (from roadmap.md, CHANGELOG.md, AGENT_REQUESTS.md)
- **cc-meta**: `stats-cache.json` and `history.jsonl` as data sources for activity trajectory and session discovery
- **cc-meta**: Team inbox parsing (`teams/*/inboxes/*.json`) and subagent transcript paths
- `examples/memory/`: MEMORY.md and claude-cowork-api.md example templates
- `CODEOWNERS`: skill file ownership for content protection
- `scaffolds.json`: scaffold registry for python-dev and embedded-dev
- CI: `check-skill-integrity.yaml` + `compute-skill-hashes.sh` for content-hash skill protection
- CI: `research-monitor` GHA for tracking upstream CC changes (#19)
- Root README: cc-meta and market-research rows in Plugins table, plugin count 12 → 13, skill count 22 → 31

#### New plugins (#38-#112)

- **gha-dev**: New plugin with `creating-gha` skill for GitHub Actions Marketplace (#39); later added security settings, uv pattern, and updated action pins (#68)
- **tdd-core**: New plugin with language-agnostic TDD methodology — Red-Green-Refactor, Arrange-Act-Assert, testing strategy, shared across language plugins (#57)
- **rust-dev**: New plugin with `implementing-rust`, `reviewing-rust`, `testing-rust` skills; cargo tool permissions via SessionStart hook (#59)
- **go-dev**: New plugin with `implementing-go`, `reviewing-go`, `testing-go` skills; go tool permissions via SessionStart hook (#59)
- **cc-voice**: Submodule for E2E voice — TTS via PTY proxy (`/speak`), STT via Moonshine (`/listen` stub, functional). Originally added as `cc-tts` (#66), renamed to `cc-voice` (#67)
- **typescript-dev**: New plugin with `implementing-typescript`, `reviewing-typescript`, `testing-typescript` skills; npm/vitest permissions via SessionStart hook (#70)
- **makefile-core**: New plugin with `creating-makefile` skill — linter script + language-neutral Makefile conventions reference (#84)
- **security-audit**: New plugin with `auditing-code-security` (OWASP Top 10), `detecting-secrets`, `scanning-dependencies` skills (#87)
- **cpp-desktop**: New plugin with C++ desktop GUI skills — `implementing-cpp`, `reviewing-cpp`, `analyzing-cpp-codebase`; covers wxWidgets, GTK, Qt (#88)
- **simplify**: New plugin packaging the `simplifying-code` skill (post-review KISS/DRY/YAGNI enforcement) (#89)
- **rag-core**: New plugin with `implementing-document-indexing` skill — heading-boundary chunking, FAISS vector store, PageIndex hybrid retrieval (#100)
- **planning**: New plugin with cherry-picked `planner` agent from `affaan-m/everything-claude-code` (MIT); detailed feature/refactor implementation plans with phased steps, file-level specificity, dependencies, risks, success criteria (#111)

#### New skills in existing plugins (#38-#112)

- **docs-governance**: `maintaining-agents-md` frontmatter convention rule (#54)
- **docs-governance**: config-drift check and markdownlint integration in `enforcing-doc-hierarchy` (#82)
- **cc-meta**: `MEMORY.md` seed template + SessionStart hook for new-project bootstrapping (#69)
- **cc-meta**: `summarizing-session-end` skill + SessionEnd hook for automated session summaries (#91)
- **cc-meta**: `handing-off-session` skill — structured cross-session handoff notes in `.claude/handoffs/` (#92)
- **cc-meta**: `orchestrating-parallel-workers` skill — fan out tasks to parallel background agents with independent context windows (#93)
- **cc-meta**: `persisting-bigpicture-learnings` skill — dated snapshots in a learnings hub for compound learning (#96)
- **cc-meta**: `mining-session-patterns` skill — extract error-fix sequences, tool failure rates, and cost signals from session JSONL (#97)
- **cc-meta**: `subagent transcripts` as `synthesizing-cc-bigpicture` data source; workflow updated with dedicated bullet (#98)
- **cc-meta**: 4-tier progressive retrieval for `synthesizing-cc-bigpicture` (metadata → summaries → deep reads → full scan) in `references/progressive-retrieval.md` (#99)
- **codebase-tools**: `hardening-codebase` skill — 7-phase quality tightening workflow (audit → tighten → fix → tests → review → refactor → ship) with language-specific lint progressions and 3-agent review framework (#102)
- **readme-generator**: `auditing-readme` batch `repos` scope can now drive a bundled dynamic workflow (`workflows/audit-repos.js`) — fans the README checklist across many repos in parallel via `Workflow({scriptPath, args})`, then runs one cross-repo consistency pass. The skill gates to the workflow when the Workflow tool is available and falls back to the inline per-repo loop otherwise; workflow agents are read-only. First demonstration that a marketplace plugin can ship a dynamic workflow (referenced by `scriptPath`, since `workflows/` is not a plugin component). Plugin version 1.0.1 → 1.1.0 (#162)
- **security-audit**: `auditing-code-security` full-codebase scope can now drive a bundled dynamic workflow (`workflows/audit-owasp.js`) — fans the ten OWASP categories (A01–A10) out across read-only agents in parallel, each returning structured findings rendered with the skill's Output Format. The skill gates to the workflow when the Workflow tool is available and falls back to the inline per-category scan otherwise. Second plugin-bundled workflow; the edited stable skill gains a `content-hash`. Plugin version 1.0.2 → 1.1.0 (#164)
- **docs-governance**: `templates/README.md` — value-first README skeleton derived verbatim from the [qte77 doc-structure canon](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md) with a `make check_sync` diff-guard; `templates/CONTRIBUTING.md` gains a `## Documentation hierarchy` statement. Plugin 1.4.0 → 1.5.0 (#170)
- **workspace-setup**: SessionStart deploy set now includes canon-derived `README.md` + `CONTRIBUTING.md` skeletons. Plugin 1.3.12 → 1.4.0 (#170)
- **Makefile / lychee**: `sync_canon` + `sync_governance` targets and `check_sync` diff-guards keep the canon-derived copies in sync with qte77/qte77; `lychee.toml` (mirrors shared `accept`) excludes skeleton/template files from link-checking (#170)
- **CI / canon-drift**: `.github/workflows/canon-drift.yaml` — weekly diff of the docs-governance derived templates against the qte77 canon, opening a sticky issue on drift (gives the local `make check_sync` guard CI teeth) (#170 follow-up)
- **CI / dependabot**: `.github/dependabot.yml` — weekly grouped SHA-bump PRs for GitHub Actions, keeping the SHA-pinned actions from #172 current
- **CONTRIBUTING.md** (repo root): canon-structured contributor guide that owns the `## Documentation hierarchy` statement; removes the `.lycheeignore` CONTRIBUTING.md forward-ref workaround

#### New agents (#38-#112)

- **codebase-tools**: `build-error-resolver` agent — cherry-picked from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT, 151k stars). Build and TypeScript error resolution specialist with minimal-diff philosophy (#104, #110)

#### New infrastructure (#38-#112)

- **workspace-setup / workspace-sandbox**: context7 MCP tool permissions via SessionStart hooks (#71)
- **workspace-sandbox**: qte77 marketplace registered in base settings (#95)
- **`.claude/rules/skill-authoring.md`**: Plugin-wide skill and agent authoring conventions — <150-line SKILL.md body cap (3.3× tighter than upstream 500-line soft cap), ≤250 char descriptions with front-loaded trigger keywords, `references/` subdir mandatory, content-hash regeneration for stable skills, plugin-scoped `agents/` layout (#109, #112)
- **docs**: `cc-entry-types.md` — tool results (detached outputs) JSONL entry type added (#53)
- **gha-dev**: `python-gha-patterns.md` reference — full Python composite action walkthrough based on gha-biorxiv-stats-action (#100)
- **gha-dev**: Scaffold split — explicit shell-based (`scripts/`) vs Python-based (`src/`) layouts in SKILL.md, with cross-reference to `python-gha-patterns.md`
- **gha-dev**: `companion-plugins.md` reference — maps companion plugins (tdd-core, python-dev, simplify, security-audit, commit-helper, makefile-core) by workflow phase, plus global rules cross-reference

### Changed

<!-- Pre-#37 entries (preserved) -->

- **cc-meta**: Simplify bigpicture skill (274→156 lines) — merge 3 reasoning axes to 2, extract project filtering to single section
- **commit-helper**: Simplify commit skill — drop mandatory diff stats/symbols, allow subject-only for small changes
- **cc-meta**: Plugin version 1.0.0 → 1.1.0 → 1.2.0 → 1.3.0
- **embedded-dev**: Plugin version 1.0.1 → 1.2.0 (scaffold adapter + hooks/settings)
- All plugins: stability metadata added to plugin.json via version bumps
- **commit-helper**: Synced SKILL.md with latest conventions (#19)
- Renamed `claude-code-research` references to `ai-agents-research` (#21)

#### Refactors and docs (#38-#112)

- **License**: Migrated to Apache-2.0 (#49)
- **docs**: Root README updated with current plugin count and table (#58)
- **docs**: Markdownlint enforcement rules added (#72)
- **docs-governance**: `enforcing-doc-hierarchy` skill rewritten — generic, KISS-oriented; no longer coupled to specific project layouts (#64)
- **docs-governance**: `enforcing-doc-hierarchy` description tightened from 295 → 179 chars per skill-authoring convention (#109)
- **workspace-setup / workspace-sandbox**: `statusline.sh` deduplicated via symlinks (#81)
- **workspace-setup / workspace-sandbox**: `statusline.sh` world-clock — opt-in via `CC_WORLD_CLOCK` env var (comma-separated IANA zones, east-to-west sunrise order recommended), renders on dedicated 4th line, invalid zones marked `?<name>`. workspace-setup 1.3.7 → 1.3.8, workspace-sandbox 1.3.6 → 1.3.7
- **workspace-setup / workspace-sandbox**: `statusline.sh` world-clock live toggle — `~/.claude/world-clock` file fallback for in-session changes (env var still wins; file picked up on next render, no CC restart needed). workspace-setup 1.3.8 → 1.3.9, workspace-sandbox 1.3.7 → 1.3.8
- **workspace-setup / workspace-sandbox**: `statusline.sh` world-clock custom labels — entries support optional `Zone=Label` syntax (e.g. `America/New_York=NYC`) for terser display; bare zones still default to the city name. workspace-setup 1.3.9 → 1.3.10, workspace-sandbox 1.3.8 → 1.3.9
- **workspace-setup / workspace-sandbox / codebase-tools / cc-meta**: Shared `.claude/rules/*.md` files (`core-principles`, `context-management`, `compound-learning`) converted from `cp`-enforced copies to symlinks pointing at the repo-root SoT — same pattern `statusline.sh` already uses. Eliminates 9 duplicate files; symlink invariants enforced by `make check_sync`. workspace-setup 1.3.10 → 1.3.11, workspace-sandbox 1.3.9 → 1.3.10, codebase-tools 1.4.2 → 1.4.3, cc-meta 1.15.1 → 1.15.2
- **python-dev**: Removed BDD, enforce TDD-only testing; reference file `bdd-best-practices.md` renamed to `bdd-best-practices-future-use.md` (parked) (#94)
- **cc-meta**: Plugin version 1.4.0 → 1.15.0 across seven successive feature merges (#91, #92, #93, #96, #97, #98, #99)
- **cc-meta**: `synthesizing-cc-bigpicture` SKILL.md 195 → 128 lines — extracted Two Reasoning Axes, CC Data Sources, Output Format into `references/reasoning-modes.md`, `references/cc-data-sources.md`, `references/output-template.md` (#108)
- **mas-design**: `securing-mas` SKILL.md 252 → 68 lines; `designing-mas-plugins` 219 → 83 lines — extracted 8 reference files total (MAESTRO checklist, plugin security checklist, common vulnerabilities, threat matrix template, security testing patterns, core principles with examples, plugin implementation template, plugin testing strategy). Plugin version 1.0.1 → 1.1.0 (#107)
- **codebase-tools**: Plugin version 1.2.0 → 1.3.0 — added agents/ subdir, description broadened to include build error resolution (#110)
- **Makefile**: `statusline.sh` added to sync targets (#60)
- **cc-voice**: Version synced to 0.4.0 in marketplace (#90)
- **`.claude/rules/skill-authoring.md`**: Agents convention section added — documents `plugins/<name>/agents/<agent-name>.md` layout, host-plugin selection, README `## Agents` section requirement, cherry-pick attribution template (#112)
- **`.claude/rules/core-principles.md`**: Tightened 73 → 55 lines — kept acronym expansions (KISS, DRY, AHA, YAGNI) and added failure-mode glosses where the name alone wasn't self-evident; folded "User-Centric Principles" into the intro; merged "Reuse and Extend" + "Resolve Ambiguity" into "Match existing patterns; ask before diverging"; preserved Consistency-and-Coherence, Rigor-and-Sufficiency, High-Impact-Quick-Wins, Clarity, Actionable-and-Concrete, Root-Cause-and-First-Principles, and Touch-only-task-related-code as named bullets. workspace-setup 1.3.11 → 1.3.12, workspace-sandbox 1.3.10 → 1.3.11.
- **`.claude/rules/skill-authoring.md`**: Resolved internal contradiction on `references/` requirement — adopted conditional reading (mandatory only when extraction is triggered by the 150-line cap), consistent with the SKILL.md body-size section.
- **market-research**: Front-loaded all 8 skill descriptions with action verbs (Assess/Map/Integrate/Score/Develop/Detect/Synthesize/Generate) per skill-authoring convention; phase labels moved to suffix so ordering info is preserved. Plugin version 1.0.1 → 1.0.2.
- **ralph**: Front-loaded `generating-interactive-userstory-md` description (verb-led "Build UserStory.md interactively..."). Plugin version 1.0.2 → 1.0.3.
- **readme-generator**: `writing-readme` SKILL.md 197 → 70 lines (under the 150-line cap); extracted four README template snippets (GitHub Action, Library/Application, Account, Organization) and per-scope conventions to `references/readme-templates.md`. Description tightened from 290 → 225 chars and front-loaded with action verb. Plugin version 1.0.0 → 1.0.1.
- **readme-generator**: `auditing-readme` + `writing-readme` rewritten to the [qte77 doc-structure canon](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md) — value-first order (Hero → Badges → What → How → Why → Refs → License → tail), badges License → Version → CI (static `blue` / native status, Version linked to `CHANGELOG.md`), `## Refs` not `## Resources`, front-door rule. Plugin 1.1.0 → 1.2.0 (#170)
- **docs-governance**: `enforcing-doc-hierarchy` discovery now points at the canon's `## Documentation hierarchy` statement (owned by `CONTRIBUTING.md`) (#170)
- **README**: dogfooded to the canon — What (Plugins) before How (Install), new `## Why`, How fragments collapsed into one section, `Resources` → `Refs`, badges fixed to static `blue` + Version linked to `CHANGELOG.md` (closes #170)
- **docs-governance**: `templates/CONTRIBUTING.md` now derived verbatim from the upstream `CONTRIBUTING.template.md` canon (provenance header + `@sync:begin` sentinel + `make check_sync` diff-guard), replacing the hand-written copy — closes the remote-drift gap left by #170; `enforcing-doc-hierarchy` opted into `stability: stable` (content-hash CI guard). Plugin 1.5.0 → 1.6.0 (#170 follow-up)
- **readme-generator**: `auditing-readme` C3 now requires the SPDX id in the License badge label (`License: Apache-2.0`, not bare `license-MIT`); batch Consistency Checks flag an unlinked Version badge; skill opted into `stability: stable`. Plugin 1.2.0 → 1.2.1 (#170 follow-up)
- **workspace-setup**: `governance/CONTRIBUTING.md` re-synced from the canon-derived template. Plugin 1.4.0 → 1.4.1 (#170 follow-up)

### Fixed

<!-- Pre-#37 entries (preserved) -->

- **cc-meta**: CC Data Sources tree — removed non-existent `sessions-index.json`, `session-memory/`, `todos/`; fixed teams structure (`config.json` + `inboxes/` not flat `.json`); added `activeForm`/`owner` task fields
- **cc-meta**: Workflow steps use real data sources (`history.jsonl`, `stats-cache.json`, team inboxes, project docs) instead of non-existent ones
- **cc-meta**: `cc-entry-types.md` reference rewritten with accurate schemas and examples
- **cc-meta**: Frontmatter aligned to agentskills.io conventions (`argument-hint` kebab-case, `Target` not `Query`)
- **cc-meta**: Project filter now applies to global sources (plans, tasks, teams) — plans filtered by content grep, tasks/teams by session allowlist correlation. Previously these leaked unfiltered data from all projects.
- Removed duplicate hooks manifest references from 4 plugins (#16)
- **check-skill-integrity.yaml**: Add `permissions: contents: read` (CodeQL alert fix)
- **embedded-dev**: `find -print0 | xargs -0` for safe filenames in scaffold adapter

#### Fixes (#38-#112)

- **marketplace**: Use github source for `cc-voice` plugin (installable from external repo, not local path) (#80)
- **marketplace**: `name` corrected `qte77-claude-code-utils` → `qte77-claude-code-plugins` to match every README / `gha-dev` install instruction; `gha-dev` `companion-plugins.md` examples updated. gha-dev 1.2.0 → 1.2.1
- **python-dev**: `testing-python/SKILL.md` content-hash drift from #94 merge — CI `verify-skill-hashes` would have blocked next PR; regenerated via `.github/scripts/compute-skill-hashes.sh --update` as part of #107
- **broken md links** (`lint / links` green): repaired cross-skill references in `mas-design` (`mas-security.md` ↔ `mas-design-principles.md` now use `../../<skill>/references/` paths); repointed `python-dev` `python-best-practices.md` testing links to `testing-python/references/` and dropped the BDD link (skill is TDD-only); removed the rotted EU Blue Guide URL from `embedded-dev` `compliance-standards.md`. Added `.lycheeignore` for the FCC page (HTTP/2 crawler error, valid for humans) and governance/template files that forward-reference consumer-repo `CONTRIBUTING.md`/`README.md`. Plugin versions: mas-design 1.1.1 → 1.1.2, python-dev 2.1.3 → 2.1.4, embedded-dev 1.2.2 → 1.2.3 (#163)

### Removed

- Stale analysis docs and compact plugin-dev reference (#62)
- `TODO.md` — completed 2026-03 phase plan (embedded-dev hooks + ralph `generating-prd-md-from-userstory-md` skill), `status: done` since 2026-03-13. Archived from repo root.

## [3.0.0] - 2026-03-01

### Added

- **embedded-dev**: New plugin with `auditing-pcb-design`, `checking-compliance`, `implementing-firmware`, and `tracing-requirements` skills
- **docs-generator**: `generating-tech-spec` and `generating-report` skills
- **website-audit**: WCAG 2.1 AA quick-reference checklist, Further Reading links, demo section
- **docs-generator**: Bundled pandoc toolchain (Makefile, run-pandoc.sh, setup-pdf-converter.sh), IEEE/APA/Chicago CSL styles, SessionStart prerequisite hook, `project-report-IMRaD` and `technical-doc` templates
- **mas-design**: MITRE ATLAS, NIST AI RMF, ISO 42001/23894 integration with unified cross-framework threat mapping
- AI security governance frameworks analysis (`docs/analysis/`)
- `.gitignore`

### Changed

- All 21 skills: `allowed-tools` moved from top-level frontmatter to `metadata.allowed-tools` (comma-separated)
- Marketplace and README updated for new plugins and skills
- **docs-generator**: Markdown writeups are core output; PDF export via pandoc is optional
- **docs-generator**: Single `template.md` replaced with `templates/project-report-IMRaD/` and `templates/technical-doc/`
- **docs-generator**: Templates restructured, redundant reference removed
- **mas-design**: Plugin description, keywords, and demo updated to reflect all four frameworks

### Removed

- **docs-generator**: `template.md` (replaced by multi-file templates), `references/pandoc-setup.md` (covered by Makefile help targets)

## [2.0.0] - 2026-03-01

### Added

- README.md for 7 plugins, PR template, `.gitmessage` in commit-helper references
- `ralph` plugin with `generating-prd-json-from-prd-md` and `generating-interactive-userstory-md` skills (extracted from docs-generator)
- Hooks declaration in plugin.json for python-dev, workspace-setup, workspace-sandbox
- CodeQL (auto lang detection) and MkDocs Material (pinned `<2.0`) GitHub Actions workflows
- `mkdocs.yml` with nav for all plugins, analysis docs, and changelog
- Design docs: stop hook session summaries, plugin enhancement analysis
- `make test_install` covers all 10 plugins with broken symlink check

### Changed

- All plugins standalone-installable (symlinks replaced with real copies, DRY via `make sync`)
- `docs-generator` narrowed to writeup-only (Ralph skills extracted to `ralph` plugin)
- Marketplace updated to 10 plugins
- workspace-sandbox owns sandbox-specific settings, workspace-setup owns base settings

### Removed

- `docs/best-practices/`, `plugins/_shared/scripts/deploy-references.sh`, mas-design hooks

## [1.0.0] - 2026-03-01

### Added

- Workspace-sandbox plugin for hardened settings
- Commit template and file permissions config
- Initial Claude Code plugin marketplace with python-dev and workspace plugins
- Core principles and context management rules
- LEARNINGS.md and README badges
- CHANGELOG.md

### Fixed

- Plugin structure: workspace config, rules migration (#2)
- Duplicate rules in top-level rules/ directory (#3)
- Branding generalization, workspace plugin consolidation, python-dev hook (#4)
- Relative paths for plugin source fields in marketplace (#5)
- Required top-level `hooks` key in hooks.json (#6)
- Statusline symlink replaced with actual file
- CodeFactor badge URL

### Changed

- README streamlined with actual repo URL and concise layout
