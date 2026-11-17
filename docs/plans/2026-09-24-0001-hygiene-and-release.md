# 0001 — Repo hygiene, Pages deploy, release flow

## Status (read first)

**State 2026-11-17 (start here):** v3.9.0 released 2026-10-26. Shipped since the 2026-10-11 session: #265
(goals.json in bigpicture, row 15), #266 (handoff Stop hook), #267 (retire `orchestrating-parallel-workers`,
closes #157), #270 (one repo-level verified-CC-version statement, closes #187), #272 (sh-dev plugin), and #290 (read-once
hardening, closes #262, row 33). #183 closed 2026-10-11, so row 5b is done. Row 29's audit was verified on 2026-11-17: the drift is
real, item list in the row. New rows: 34 (#291, read-once TTL snapshot; shipped in the #291 PR) and 35 (#282, gha-dev SHA-pin brief skill).

**Next, in order:** row 17 → 35 → 21 → 13 → 20 (needs the owner's new name); row 14's last item (#206)
and rows 12, 24 wait on the owner; pre-stage 31/32 for the owner; 30 needs an owner OK on the settings diff.

**Shipped (v3.8.0 released 2026-09-25, first GitHub Release):** #212 · #198 · #194 · #208 · #214 Pages
deploy + release workflows · #215 cross-checking-research · #216 hash gate / MEMORY.md seed / read-once /
allow rules · #217 ghost simplify · #218 sandbox governance · #219 Makefile fail-fast · #220 13 skills
stable · #221 pip-audit env · #222 web-recon README · #223 MADR carve-out · #224 ci-status-checks rule
· #225 PR-template fallback · #226 TS strict defaults · #227 triaging-issues · #228 docs-site link ·
PR #229 bump 3.8.0 (tag `v3.8.0`, Release published, Pages redeployed).

**Session 2026-10-11 (handoff state, read first):** shipped since v3.8.0: #231 setup-uv v10 · #232 CI lints
all 229 md (was 8) + MD025 rule fix · #233 README inventory guard · #234 canon-drift SC2129. Cross-repo merged:
qte77/.github#46 (shared MD025) · doc-pipeline-engine#227 (rule re-synced; deleting it would drop the rule,
docs-governance has no deploy hook) · qte77/qte77#192 (learning → ci-status-checks link) · qte77/qte77#193
(plans-only rule canonical). Row 5b shipped (#237, closes #183). Owner decisions taken 2026-10-11: D = commit allow / push ask; F = #157
retire, #158 keep, #125 no-merge, #177/#178 defer, #185 do, #167 CodeQL stays NOT required (bump PRs from
GITHUB_TOKEN never run CodeQL). Owner branch `feat/pages-ops` (row 20) is on origin.

_The 2026-10-11 order (rows 26 → 27 → 28 → 29 → 17 → 21 → 23 → 24 → 20 → 13/14) is superseded by the 2026-11-17 order above._

**Loop:** branch per topic → fix → `make validate && make check_sync && make test_install` (fail-fast
since #219) + `bash .github/scripts/compute-skill-hashes.sh --check` + markdownlint-cli2 on every changed
`.md` incl. CHANGELOG → push → CI green → owner merges (squash; ruleset: 0 reviews, required check CodeFactor, signed commits; an
agent merge needs the owner's go-ahead) → strike the row in the same PR.
Release: dispatch Bump Version → merge the bump PR (only CodeFactor reports on GITHUB_TOKEN PRs; it is
the only required check) → Tag Release runs → dispatch Publish Release.

**Owner gates:** every merge; the plan-file rule landing in `qte77/qte77` (unblocks #207/#197/#200);
keep/cut decisions (#157, #158, #125, #177/#178, #185); #167 ruleset change.

**Commands:** local docs build:
`make docs_stage && uvx --from "mkdocs<2.0" --with mkdocs-material mkdocs build --strict`.
Bump dry-run: `uvx bump-my-version==1.5.1 bump minor --dry-run -vv --no-commit --no-tag --allow-dirty`.

**Watch-outs:** an unquoted colon followed by a space in a SKILL.md `description:` breaks YAML (bit #212). Any change under
`plugins/<name>/` needs plugin.json + marketplace.json bumps (CI-enforced). Actions must be
SHA-pinned; `qte77/.github@*` is allowlisted, `astral-sh/setup-uv` relies on `verified_allowed`
(if it `startup_failure`s, add it to `patterns_allowed`). Tags are immutable — never delete.

## Source map

| What | Where |
| --- | --- |
| Docs staging | `Makefile` `docs_stage`; `mkdocs.yml` (no nav, `exclude_docs: plans/`); `.gitignore` |
| Pages deploy | `.github/workflows/deploy-mkdocs-ghpages.yaml` (setup-uv + uvx mkdocs) |
| Root version | `.claude-plugin/marketplace.json` `metadata.version`; `.bumpversion.toml` |
| Release callers | `.github/workflows/{bump-version,tag-release,publish-release}.yaml` → `qte77/.github@613b950` |
| Plugin version gate | `.github/workflows/check-plugin-versions.yaml`; `.claude/rules/plugin-versioning.md` |
| Skill rules | `.claude/rules/skill-authoring.md`; hash script `.github/scripts/compute-skill-hashes.sh` (body only) |
| research-cross-check | removed from #198; source = #198's first commit (`plugins/cc-meta/workflows/research-cross-check.js`) |
| read-once hook | `.claude/scripts/read-once/hook.sh` (symlinked into workspace-setup/-sandbox) |
| Settings templates | `plugins/workspace-{setup,sandbox}/settings/*.json` |

## Remaining work

| # | Item | Gate | Done-when |
| --- | --- | --- | --- |
| 1 | ~~#213 Pages deploy + release workflows + README rows/badge~~ — shipped (#214) | — | — |
| 2 | ~~Verify Pages live after merge; close #213~~ — done: run 36005276222 success, site serves, #213 closed | — | — |
| 3 | ~~First release~~ — v3.8.0: bump #229 → tag `v3.8.0` on ec1e774 → Release published (first ever) | — | — |
| 4 | ~~#180: `research-cross-check.js` as its own skill + workflow, no hardcoded paths; cc-meta 1.16.0~~ — shipped (#215) | — | — |
| 5 | ~~#155, #186, #150 + #183 allow-rule part~~ — shipped (#216) | — | — |
| 5b | ~~#183: settings templates commit `allow`, push `ask` (owner chose option b)~~ — shipped (#237); #183 closed 2026-10-11 | — | — |
| 6 | ~~#184: drop ghost `simplify`; gha-dev → built-in `/simplify`~~ — shipped (#217) | — | — |
| 7 | ~~#151 remnant: workspace-sandbox governance README + CONTRIBUTING~~ — shipped (#218) | — | — |
| 7b | ~~Makefile fail-fast (`.SHELLFLAGS := -ec`)~~ — shipped (#219) | — | — |
| 8 | ~~#175: 13 mature skills `stable` + hash~~ — shipped (#220); 12 held (cc-meta ×7, creating-pr-from-branch, hardening-codebase, testing-tdd, implementing-document-indexing, verifying-design-canvas) — revisit after #157/#158/#161/#125/#187 | — | — |
| 9 | ~~security-audit `scanning-dependencies` → `uv run --with pip-audit … --skip-editable` (not bare `uvx`: audits only its own env)~~ — shipped (#221) | — | — |
| 9b | ~~web-recon README setup drift~~ — shipped (#222) | — | — |
| 10 | ~~Mechanical additions~~ — shipped: #160 (#223) · #192 (#224) · #161 (#225) · #182 (#226) · #179 (#227) | — | — |
| 11 | ~~Plan-file rule (local `/workspaces/.claude/rules/unattended-execution.md`) lands in `qte77/qte77`~~ (qte77/qte77#193); ~~then #207 close~~ (closed); #197 rework (drop handoff template, dated plan, rebase, 1.6.0), #200 rebase-or-close | owner | rule on qte77/qte77 main |
| 12 | Decisions: #157, #158, #125, #177/#178, #185, #167 | owner | decision recorded on each issue |
| 13 | #175 remainder: re-evaluate the 12 held skills once #157/#158/#161/#125/#187 are decided | agent (after 12) | each held skill either `stable` + hash or its hold reason recorded |
| 14 | P2 backlog: ~~#187 (stale `last-verified-cc-version` sweep)~~ — PR #270 (merged); #206 (Content-Signal + llms.txt check) — owner: a project-site `robots.txt` is never read (see the issue comment), needs the user-site repo or a custom domain; ~~#127 (sh-dev plugin)~~ — PR #272 (merged); ~~#126 (handoff Stop hook, after #157/#158)~~ — PR #266 (merged). Only #206 is left (open 2026-11-17) | owner (#206 needs a user-site repo or custom domain) | one PR each, green |
| 15 | Deferred (low ROI / author-deferred / spike): ~~#48 goals.json~~ — PR #265 (merged 2026-10-31), #75 cc-voice STT, #101 Graphify eval, #190 OWASP LLM tracking (explicitly YAGNI) | owner | revisit when a consumer task needs one |
| 16 | ~~Lint all markdown in CI (was root-only, 8 files) + fix 181 errors + align `make lint_md`~~ — shipped (#232) | — | — |
| 17 | Drop this repo's `.markdownlint.jsonc` + `check-markdownlint-config.py` now that qte77/.github#46 put MD025 in the shared config (CI then fetches the shared one) | agent | file + guard removed; `make lint_md` and CI markdown stay at 0 errors |
| 18 | ~~README inventory guard (counts + plugin rows vs marketplace)~~ — shipped (#233) | — | — |
| 19 | ~~canon-drift.yaml SC2129 (actionlint clean repo-wide)~~ — shipped (#234) | — | — |
| 20 | `feat/pages-ops` (WIP 32884fa): finish + rename — full scope in **#236**. Done: `syncing-design-snapshot` (patch engine + tests). To build: `examples/project.config.example.py` (placeholders: `TARGET_DIR`, `PATCHES` tuples), SKILL.md per skill, then `building-pages-site` (runtime vendoring + SRI, CSP hashes → `_headers`, minify, markdown-for-agents worker + `_routes.json`), `checking-agent-readiness` (llms.txt, `.well-known/agent-skills/` digests, content negotiation, markdown 404; cross-ref `website-audit/auditing-website-seo-geo`, do not duplicate; check overlap with #206 first), `checking-site-live` (desktop+phone: headers/CSP, console errors, failed requests, landmarks), `deploying-pages-site` (`wrangler pages deploy … --branch=main`, never preview; verify locally first, run both checks after); README, marketplace entry, version bump. Reference implementations live in a private downstream consumer (owner knows where) — **public-repo rule: no consumer names, paths, script names or IDs in this repo; use `<your-project>` placeholders.** **New name: owner to choose** (none recorded) | owner (name) → agent | renamed; 5 skills + example config; tests, validate, check_sync, lint, test_install green |
| 21 | E follow-ups: ~~close #207 (rule landed in qte77/qte77#193)~~ (closed); rework #197 (drop `handoff.template.md`, dated plan template, resync rule, rebase 4 conflicting files, 1.6.0, un-park); #200/#201: ask dntywntme to rebase onto the new rule or close | agent | #207 closed; #197 green + merged; #200/#201 resolved |
| 22 | qte77/qte77 follow-ups from #193 (in that repo): update stale `docs/unattended-execution.md` (still plan+handoff), decide on re-adding the dropped "ephemeral — mine then prune" principle, merge `docs/handoffs/{001,003,004}` into plans + rename to dated 4-digit | owner | qte77/qte77 consistent with its rule |
| 23 | F code: ~~retire `cc-meta/orchestrating-parallel-workers` (#157; drop the optional mention in `planning/triaging-issues`, README/counts, cc-meta minor bump)~~ — PR #267; write model-alias precedence docs (#185), with the cloud lane (per #262, 2026-10-26; still open) | agent | PRs merged; #157, #185 closed |
| 24 | F closes with decision recorded: #158 keep, #125 won't-do, #177/#178 deferred (not planned, reopen on consumer need), #167 won't-do (CodeQL stays not required: GITHUB_TOKEN bump PRs never run it, would stall releases) | agent | issues closed with the reason |
| 25 | ~~read-once fix (audit A): cache keyed by `$$` never hit → use hook `session_id`; PostCompact cleared the wrong dir; diff mode diffed /dev/null → snapshot + real diff~~ — shipped (#254): workspace-setup 1.7.1, workspace-sandbox 1.5.1 (main had already moved past the plan's stale 1.5.5/1.3.15 target by the time this shipped); test lives at `.claude/scripts/read-once/test.sh` (5/5 fix vs 2/5 main); README "~40% reduction" claim dropped as unverified | — | — |
| 26 | ~~python-dev (audit B): `setup-python-dev.sh:49` copies every `scaffold/workflows/*.yaml`, so `dependabot.yaml` lands in `.github/workflows/` (invalid workflow) — exclude it there (already copied correctly at :60); README "Deployed files" lists only settings.local.json — document the `.scaffold`=`python` deploy set; align plugin.json description; 2.1.4→2.1.5~~ — shipped (signed re-post of #255) | — | — |
| 27 | ~~Docs (audit C): add `plugins/readme-generator/README.md` (missing → absent from the docs site; skills + `workflows/audit-repos.js`), bump; website-audit README says WCAG 2.1 at lines 9 + 20 (skill and root README say 2.2) and omits `auditing-website-seo-geo`, bump~~ — shipped (#256) | — | — |
| 28 | ~~Settings merge, not clobber (audit D + permissions finding): python-dev, rust-dev, go-dev, typescript-dev, embedded-dev, gha-dev SessionStart hooks copy `.claude/settings.local.json` only if missing, so the first plugin wins in polyglot repos; workspace-setup/-sandbox likewise never update an existing `.claude/settings.json`, so template fixes (#216, #237) never reach existing workspaces. Merge `permissions.allow` (jq, unique) into existing files; keep copy-if-missing as the no-jq fallback; bump all touched plugins~~ — shipped (signed re-post of #257, rebased after #258: python-dev 2.1.6, workspace-setup 1.7.2, workspace-sandbox 1.5.2) | — | — |
| 29 | ~~Fix README/manifest drift (audit E, verified 2026-11-17). **Drift:** security-audit (root README, plugin README and `workflows/audit-owasp.js`) promises a Workflow fan-out, but `auditing-code-security/SKILL.md` `allowed-tools` has no `Workflow`; `plugin.json` vs `marketplace.json` descriptions differ for cpp-desktop, mas-design, docs-generator, ralph, tdd-core and security-audit; codebase-tools README line 3 mentions "context compaction" (lives in cc-meta); cc-meta README omits its MEMORY.md SessionStart hook (#201), it documents only the SessionEnd and Stop hooks. **Not drift:** versions match across the plugins (cc-voice's plugin.json lives in its own repo); every plugin has a README; root README "Full setup" lists website-audit, readme-generator and web-recon (cc-voice is external; workspace-sandbox is the "pick one" alternative). **Still to check:** web-recon README Install vs #222; docs-governance `rules/` deploy path; `designing-mas-plugins` / `securing-mas` descriptions vs skill-authoring.md~~ — shipped in the row-29 PR. Drift fixed: `auditing-code-security` `allowed-tools` gains `Workflow` (still under `metadata:`, so row 31 decides whether it takes effect); descriptions aligned (plugin.json → marketplace for mas-design, docs-generator, tdd-core, security-audit; marketplace → plugin.json for cpp-desktop and ralph, whose marketplace text named all their skills); codebase-tools README no longer claims context compaction; cc-meta README documents the MEMORY.md SessionStart seed hook. Still-to-check: web-recon README has its install line (not a bug); docs-governance `rules/frontmatter-convention.md` is never installed anywhere and the skill pointed at a path relative to itself, so the README now says it is reference material and the skill points at `../../rules/`; `designing-mas-plugins` and `securing-mas` descriptions meet skill-authoring.md (verb first, 66 and 101 characters; not a bug). Bumps: cpp-desktop 1.0.4, ralph 1.0.5, security-audit 1.2.4, codebase-tools 1.4.7, cc-meta 1.19.2, docs-governance 1.6.4 | — | — |
| 30 | Permission prompts: run `/fewer-permission-prompts`; replace one-off allow entries in `.claude/settings.local.json` with patterns (`make:*`, `uvx:*`, `npm exec:*`, `node --check:*`, `actionlint:*`, `wc:*`, `sort:*`; keep rm/mv as ask); one AGENTS.md line telling agents raw grep/cat/ls/head are denied (rtk) — use Read or python3 | owner (settings diff) → agent | subagent runs stop prompting for routine commands |
| 31 | Pre-stage owner decision — `metadata:` nesting (all 68 skills): Claude Code reads `allowed-tools`, `model`, `disable-model-invocation`, `context`, `agent`, `argument-hint` at the frontmatter TOP level; here they sit under `metadata:` and are ignored (e.g. `committing-staged-with-message` has `disable-model-invocation: true` yet is model-invocable). Hoisting changes behaviour estate-wide. Pre-stage: per-skill list of behaviour gained/lost. Before any hoist: confirm that `security-audit`'s audit workflow can't be steered to another script or path by its `args` (`args.scope`, `args.skillPath`), since hoisting makes `Workflow` pre-approved for `auditing-code-security` (from the #294 review) | agent (pre-stage) → owner | list ready; owner decides hoist/no-hoist |
| 32 | Pre-stage owner decision — overlaps: workspace-setup vs workspace-sandbox (share rules, governance, read-once, statusline, hooks.json; differ in setup script, settings template, .gitignore, link-claude-home.sh → one plugin with a sandbox option?); cc-meta's 4 session-memory skills (`handing-off-session` writes handoff files the plans-only rule forbids; ties #157 #158 #126 #201); review/security in three layers (these plugins, official code-review/security-guidance plugins, built-in /code-review /security-review) | agent (pre-stage) → owner | options + recommended default per overlap |
| 33 | ~~#262 review follow-ups: read-once cache hardening (per-user 700 cache dir, owned-and-not-symlink check, `install -m 600` snapshots skipping secret-like and >1 MiB files, same path logic in `compact.sh`, tests) + doc fixes (CONTRIBUTING secrets, python-dev settings merge wording, web-recon install line)~~ — shipped in the #262 PR | — | — |
| 34 | ~~#291 read-once follow-ups: the TTL-expired branch of `.claude/scripts/read-once/hook.sh` (about lines 101-109) rewrites the cache entry but never refreshes `$CACHE_FILE.snap`, so a later diff compares against a stale snapshot; plus the issue's doc points (hard links, legacy cache-dir glob, silent no-op without `md5sum`) and missing tests (symlink loop, relative symlink, symlink to a directory, TTL case)~~ — shipped in the #291 PR (workspace-setup 1.7.7, workspace-sandbox 1.5.7; `test.sh` 33/33) | — | — |
| 35 | #282 gha-dev: skill for the SHA-pin + grouped Dependabot brief (`plugins/gha-dev/skills/` holds only `creating-gha`) | agent | skill added per skill-authoring.md; gha-dev bumped; #282 closed |
| 36 | ~~CI never runs `.claude/scripts/read-once/test.sh` (from the #293 review); add a job that runs it on PRs touching `.claude/scripts/read-once/`~~ — shipped in the row-36 PR (`.github/workflows/test-read-once.yaml`; fails with exit 1 when a test fails, checked locally with the TTL fix reverted: 31/33) | — | — |
| — | Outside this repo (FYI, owner): the codespace's user-level plugin set — dotfiles `.claude/settings.json` enables 5 qte77 plugins but `install.sh` copies with no-clobber, so the live `~/.claude/settings.json` has none | owner | — |
| — | Excluded (other author): #199; PRs #200/#201 (see row 11) | — | — |
