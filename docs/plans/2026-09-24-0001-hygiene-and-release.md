# 0001 — Repo hygiene, Pages deploy, release flow

## Status (read first)

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

**Next, in order:** row 25 (read-once, local commit ready) → 26 → 27 → 28 → 29 → 17 → 21 → 23 → 24 → 20
(needs the owner's new name) → 13/14; pre-stage 31/32 for the owner; 30 needs an owner OK on the settings diff.

**Loop:** branch per topic → fix → `make validate && make check_sync && make test_install` (fail-fast
since #219) + `bash .github/scripts/compute-skill-hashes.sh --check` + markdownlint-cli2 on every changed
`.md` incl. CHANGELOG → push → CI green → owner merges (`gh pr merge N --squash --delete-branch`; ruleset: 0
reviews, required check CodeFactor, signed commits; the Claude Code auto-mode classifier blocks agent
merge-without-review, so it needs a normal permission prompt) → strike the row in the same PR.
Release: dispatch Bump Version → merge the bump PR (only CodeFactor reports on GITHUB_TOKEN PRs; it is
the only required check) → Tag Release runs → dispatch Publish Release.

**Owner gates:** every merge; the plan-file rule landing in `qte77/qte77` (unblocks #207/#197/#200);
keep/cut decisions (#157, #158, #125, #177/#178, #185); #167 ruleset change.

**Commands:** gh needs `env -u GH_TOKEN -u GITHUB_TOKEN` (stale env token). Local docs build:
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
| 5b | #183: settings templates commit `allow`, push `ask` (owner chose option b) — branch `fix/settings-commit-push-policy`, PR open | agent | PR merged; close #183 (governance points: keep both deny classes; generic rules user-level; rules SSOT = this repo) |
| 6 | ~~#184: drop ghost `simplify`; gha-dev → built-in `/simplify`~~ — shipped (#217) | — | — |
| 7 | ~~#151 remnant: workspace-sandbox governance README + CONTRIBUTING~~ — shipped (#218) | — | — |
| 7b | ~~Makefile fail-fast (`.SHELLFLAGS := -ec`)~~ — shipped (#219) | — | — |
| 8 | ~~#175: 13 mature skills `stable` + hash~~ — shipped (#220); 12 held (cc-meta ×7, creating-pr-from-branch, hardening-codebase, testing-tdd, implementing-document-indexing, verifying-design-canvas) — revisit after #157/#158/#161/#125/#187 | — | — |
| 9 | ~~security-audit `scanning-dependencies` → `uv run --with pip-audit … --skip-editable` (not bare `uvx`: audits only its own env)~~ — shipped (#221) | — | — |
| 9b | ~~web-recon README setup drift~~ — shipped (#222) | — | — |
| 10 | ~~Mechanical additions~~ — shipped: #160 (#223) · #192 (#224) · #161 (#225) · #182 (#226) · #179 (#227) | — | — |
| 11 | Plan-file rule (local `/workspaces/.claude/rules/unattended-execution.md`) lands in `qte77/qte77`; then #207 close, #197 rework (drop handoff template, dated plan, rebase, 1.6.0), #200 rebase-or-close | owner | rule on qte77/qte77 main |
| 12 | Decisions: #157, #158, #125, #177/#178, #185, #167 | owner | decision recorded on each issue |
| 13 | #175 remainder: re-evaluate the 12 held skills once #157/#158/#161/#125/#187 are decided | agent (after 12) | each held skill either `stable` + hash or its hold reason recorded |
| 14 | P2 backlog: #187 (stale `last-verified-cc-version` sweep), #206 (Content-Signal + llms.txt check), #127 (sh-dev plugin), #126 (handoff Stop hook, after #157/#158) | agent | one PR each, green |
| 15 | Deferred (low ROI / author-deferred / spike): #48 goals.json, #75 cc-voice STT, #101 Graphify eval, #190 OWASP LLM tracking (explicitly YAGNI) | owner | revisit when a consumer task needs one |
| 16 | ~~Lint all markdown in CI (was root-only, 8 files) + fix 181 errors + align `make lint_md`~~ — shipped (#232) | — | — |
| 17 | Drop this repo's `.markdownlint.jsonc` + `check-markdownlint-config.py` now that qte77/.github#46 put MD025 in the shared config (CI then fetches the shared one) | agent | file + guard removed; `make lint_md` and CI markdown stay at 0 errors |
| 18 | ~~README inventory guard (counts + plugin rows vs marketplace)~~ — shipped (#233) | — | — |
| 19 | ~~canon-drift.yaml SC2129 (actionlint clean repo-wide)~~ — shipped (#234) | — | — |
| 20 | `feat/pages-ops` (WIP 32884fa): finish + rename — full scope in **#236**. Done: `syncing-design-snapshot` (patch engine + tests). To build: `examples/project.config.example.py` (placeholders: `TARGET_DIR`, `PATCHES` tuples), SKILL.md per skill, then `building-pages-site` (runtime vendoring + SRI, CSP hashes → `_headers`, minify, markdown-for-agents worker + `_routes.json`), `checking-agent-readiness` (llms.txt, `.well-known/agent-skills/` digests, content negotiation, markdown 404; cross-ref `website-audit/auditing-website-seo-geo`, do not duplicate; check overlap with #206 first), `checking-site-live` (desktop+phone: headers/CSP, console errors, failed requests, landmarks), `deploying-pages-site` (`wrangler pages deploy … --branch=main`, never preview; verify locally first, run both checks after); README, marketplace entry, version bump. Reference implementations live in a private downstream consumer (owner knows where) — **public-repo rule: no consumer names, paths, script names or IDs in this repo; use `<your-project>` placeholders.** **New name: owner to choose** (none recorded) | owner (name) → agent | renamed; 5 skills + example config; tests, validate, check_sync, lint, test_install green |
| 21 | E follow-ups: close #207 (rule landed in qte77/qte77#193); rework #197 (drop `handoff.template.md`, dated plan template, resync rule, rebase 4 conflicting files, 1.6.0, un-park); #200/#201: ask dntywntme to rebase onto the new rule or close | agent | #207 closed; #197 green + merged; #200/#201 resolved |
| 22 | qte77/qte77 follow-ups from #193 (in that repo): update stale `docs/unattended-execution.md` (still plan+handoff), decide on re-adding the dropped "ephemeral — mine then prune" principle, merge `docs/handoffs/{001,003,004}` into plans + rename to dated 4-digit | owner | qte77/qte77 consistent with its rule |
| 23 | F code: retire `cc-meta/orchestrating-parallel-workers` (#157; drop the optional mention in `planning/triaging-issues`, README/counts, cc-meta minor bump); write model-alias precedence docs (#185) | agent | PRs merged; #157, #185 closed |
| 24 | F closes with decision recorded: #158 keep, #125 won't-do, #177/#178 deferred (not planned, reopen on consumer need), #167 won't-do (CodeQL stays not required: GITHUB_TOKEN bump PRs never run it, would stall releases) | agent | issues closed with the reason |
| 25 | read-once fix (audit A): cache keyed by `$$` never hit → use hook `session_id`; PostCompact cleared the wrong dir; diff mode diffed /dev/null → snapshot + real diff. Local-only commit 6d40662 on `fix/read-once-session-cache` (worktree `ccp-audit-fixes`); rebase on main, bump workspace-setup 1.5.5→**1.5.6**, workspace-sandbox 1.3.15→**1.3.16** (#237 already took .5/.15); CHANGELOG Fixed; decide where the regression test (`.read-once-test.sh`, 5/5 fix vs 2/5 main) lives; recheck README's "~40% token reduction" claim | agent | PR green |
| 26 | python-dev (audit B): `setup-python-dev.sh:49` copies every `scaffold/workflows/*.yaml`, so `dependabot.yaml` lands in `.github/workflows/` (invalid workflow) — exclude it there (already copied correctly at :60); README "Deployed files" lists only settings.local.json — document the `.scaffold`=`python` deploy set; align plugin.json description; 2.1.4→2.1.5 | agent | PR green; a scaffold run puts no dependabot.yaml under workflows/ |
| 27 | Docs (audit C): add `plugins/readme-generator/README.md` (missing → absent from the docs site; skills + `workflows/audit-repos.js`), bump; website-audit README says WCAG 2.1 at lines 9 + 20 (skill and root README say 2.2) and omits `auditing-website-seo-geo`, bump | agent | PR green; `make docs_stage` includes readme-generator |
| 28 | Settings merge, not clobber (audit D + permissions finding): python-dev, rust-dev, go-dev, typescript-dev, embedded-dev, gha-dev SessionStart hooks copy `.claude/settings.local.json` only if missing, so the first plugin wins in polyglot repos; workspace-setup/-sandbox likewise never update an existing `.claude/settings.json`, so template fixes (#216, #237) never reach existing workspaces. Merge `permissions.allow` (jq, unique) into existing files; keep copy-if-missing as the no-jq fallback; bump all touched plugins | agent | each hook verified on a repo that already has the file |
| 29 | Verify, then fix or record not-a-bug (audit E, unverified): web-recon README Install (vs #222); root README "Full setup" list missing website-audit, readme-generator, web-recon, cc-voice; cc-voice STT status README vs marketplace.json; description drift plugin.json vs marketplace.json (ralph, mas-design, cpp-desktop); codebase-tools README mentions "context compaction" (lives in cc-meta); cc-meta README omits its MEMORY.md SessionStart hook (#201); docs-governance `rules/` has no deploy path; security-audit README promises Workflow fan-out but `Workflow` is not in that skill's allowed-tools; `designing-mas-plugins` / `securing-mas` descriptions vs skill-authoring.md | agent | each item fixed or recorded as not-a-bug |
| 30 | Permission prompts: run `/fewer-permission-prompts`; replace one-off allow entries in `.claude/settings.local.json` with patterns (`make:*`, `uvx:*`, `npm exec:*`, `node --check:*`, `actionlint:*`, `wc:*`, `sort:*`; keep rm/mv as ask); one AGENTS.md line telling agents raw grep/cat/ls/head are denied (rtk) — use Read or python3 | owner (settings diff) → agent | subagent runs stop prompting for routine commands |
| 31 | Pre-stage owner decision — `metadata:` nesting (all 68 skills): Claude Code reads `allowed-tools`, `model`, `disable-model-invocation`, `context`, `agent`, `argument-hint` at the frontmatter TOP level; here they sit under `metadata:` and are ignored (e.g. `committing-staged-with-message` has `disable-model-invocation: true` yet is model-invocable). Hoisting changes behaviour estate-wide. Pre-stage: per-skill list of behaviour gained/lost | agent (pre-stage) → owner | list ready; owner decides hoist/no-hoist |
| 32 | Pre-stage owner decision — overlaps: workspace-setup vs workspace-sandbox (share rules, governance, read-once, statusline, hooks.json; differ in setup script, settings template, .gitignore, link-claude-home.sh → one plugin with a sandbox option?); cc-meta's 4 session-memory skills (`handing-off-session` writes handoff files the plans-only rule forbids; ties #157 #158 #126 #201); review/security in three layers (these plugins, official code-review/security-guidance plugins, built-in /code-review /security-review) | agent (pre-stage) → owner | options + recommended default per overlap |
| — | Outside this repo (FYI, owner): the codespace's user-level plugin set — dotfiles `.claude/settings.json` enables 5 qte77 plugins but `install.sh` copies with no-clobber, so the live `~/.claude/settings.json` has none | owner | — |
| — | Excluded (other author): #199; PRs #200/#201 (see row 11) | — | — |
