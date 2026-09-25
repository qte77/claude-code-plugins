# 0001 — Repo hygiene, Pages deploy, release flow

## Status (read first)

**Shipped:** #212 (verifying-design-canvas description ≤250, polyfetch named) · #198 (argument-hint
quoting in 7 skills + verifying-design-canvas description quoting; cc-meta 1.15.3, docs-generator
1.0.4, website-audit 1.2.4) · #194 (web-recon plugin 0.1.0) · #208 (dependabot GHA group) · the
Pages deploy fix + release workflows + README rows (#214).

**Next, in order:** the remaining-work table below, top to bottom. Phase A (agent) rows first;
owner rows are batched into one sitting.

**Loop:** branch per topic → fix → `make validate && make check_sync` +
`bash .github/scripts/compute-skill-hashes.sh --check` + YAML-parse all SKILL.md frontmatter →
push → CI green → owner squash-merges (`gh pr merge N --squash --delete-branch --admin`; branch
protection needs 1 review and the Claude Code classifier blocks agent merge-without-review) →
strike the row in the same PR.

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
| 3 | First release: dispatch Bump Version (minor → 3.8.0), merge PR, confirm tag, dispatch Publish Release | owner | `gh release view v3.8.0` exists |
| 4 | ~~#180: `research-cross-check.js` as its own skill + workflow, no hardcoded paths; cc-meta 1.16.0~~ — shipped (#215) | — | — |
| 5 | ~~#155, #186, #150 + #183 allow-rule part~~ — shipped (#216) | — | — |
| 5b | #183 remainder: decide policy for `ask` git:commit and `deny` git:push (fixing the syntax activates them for fresh consumers) + the issue's governance decision points | owner | policy recorded on #183, then a syntax PR |
| 6 | ~~#184: drop ghost `simplify`; gha-dev → built-in `/simplify`~~ — shipped (#217) | — | — |
| 7 | ~~#151 remnant: workspace-sandbox governance README + CONTRIBUTING~~ — shipped (#218) | — | — |
| 7b | ~~Makefile fail-fast (`.SHELLFLAGS := -ec`)~~ — shipped (#219) | — | — |
| 8 | ~~#175: 13 mature skills `stable` + hash~~ — shipped (#220); 12 held (cc-meta ×7, creating-pr-from-branch, hardening-codebase, testing-tdd, implementing-document-indexing, verifying-design-canvas) — revisit after #157/#158/#161/#125/#187 | — | — |
| 9 | ~~security-audit `scanning-dependencies` → `uv run --with pip-audit … --skip-editable` (not bare `uvx`: audits only its own env)~~ — shipped (#221) | — | — |
| 9b | ~~web-recon README setup drift~~ — shipped (#222) | — | — |
| 10 | Mechanical additions: ~~#160~~ (#223) · ~~#192~~ (#224) · ~~#161~~ (#225) · ~~#182~~ (PR_NUM) · #179 | agent | one PR each, green |
| 11 | Plan-file rule (local `/workspaces/.claude/rules/unattended-execution.md`) lands in `qte77/qte77`; then #207 close, #197 rework (drop handoff template, dated plan, rebase, 1.6.0), #200 rebase-or-close | owner | rule on qte77/qte77 main |
| 12 | Decisions: #157, #158, #125, #177/#178, #185, #167 | owner | decision recorded on each issue |
