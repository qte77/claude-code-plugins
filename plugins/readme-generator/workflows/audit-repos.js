export const meta = {
  name: 'readme-audit-repos',
  description: 'Batch README audit: fan a per-repo checklist across many repos in parallel, then cross-check consistency.',
  phases: [
    { title: 'Discover', detail: 'resolve owner/pattern to a repo list (skipped when repos are passed explicitly)' },
    { title: 'Audit', detail: 'one read-only agent per repo runs the SKILL.md checklist' },
    { title: 'Consistency', detail: 'one agent cross-checks convention drift across all repos' },
  ],
}

// `args` arrives as a JSON string on the skill->Workflow path — parse defensively.
const a = typeof args === 'string' ? JSON.parse(args) : (args ?? {})

// Single source of truth for the checklist is the SKILL.md; agents read it when a
// resolved path is passed in. Falls back to general README best practices otherwise.
const skillPath = a.skillPath || ''
const checklistRef = skillPath
  ? `Read the audit checklist tables (Base Repo R1-R7, GHA Extension G1-G5) from ${skillPath} and apply them verbatim.`
  : 'Apply the standard Base Repo checklist (title, description, badges, install/usage, license, valid internal links, LICENSE filename) plus a GHA inputs/outputs/usage check when action.yml or action.yaml exists.'

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['repo', 'isGHA', 'checks', 'requiredPass', 'recommendedPass', 'topIssue'],
  properties: {
    repo: { type: 'string' },
    isGHA: { type: 'boolean' },
    checks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'level', 'status'],
        properties: {
          id: { type: 'string' },
          level: { 'enum': ['required', 'recommended'] },
          status: { 'enum': ['pass', 'fail', 'na'] },
          note: { type: 'string' },
        },
      },
    },
    requiredPass: { type: 'string' },     // "X/Y"
    recommendedPass: { type: 'string' },  // "Z/W"
    topIssue: { type: 'string' },         // worst failing required check, or "none"
  },
}

// Phase 1 — resolve the concrete repo list.
phase('Discover')
let repos = Array.isArray(a.repos) ? a.repos.filter(Boolean) : []
if (!repos.length && a.owner) {
  const pattern = a.pattern || '*'
  const discovered = await agent(
    `List GitHub repositories owned by "${a.owner}" whose name matches the glob "${pattern}" (treat * as wildcard). ` +
    `Run read-only: gh repo list ${a.owner} --no-archived --limit 200 --json name,nameWithOwner. ` +
    `Return the matching repos as full "owner/name" strings. Do not modify anything.`,
    {
      label: 'discover-repos',
      phase: 'Discover',
      schema: { type: 'object', required: ['repos'], properties: { repos: { type: 'array', items: { type: 'string' } } } },
    },
  )
  repos = (discovered && discovered.repos) || []
}

if (!repos.length) {
  log('No targets — pass args.repos: ["owner/repo", ...] or args.owner + args.pattern.')
  return { repos: [], perRepo: [], consistency: [], note: 'no-targets' }
}
log(`Auditing ${repos.length} repo(s): ${repos.join(', ')}`)

// Phase 2 — fan out one read-only audit agent per repo.
phase('Audit')
const perRepo = (await parallel(repos.map(repo => () =>
  agent(
    `Audit the README.md of GitHub repo "${repo}" against the readme-generator checklist. ${checklistRef}\n` +
    `Fetch the README read-only: gh api repos/${repo}/contents/README.md --jq '.content' | base64 -d. ` +
    `Detect GHA by probing for action.yml/action.yaml via gh api repos/${repo}/contents/<file>. ` +
    `Evaluate every applicable check with status pass/fail/na and a short note; compute requiredPass and ` +
    `recommendedPass as "X/Y" counts; set topIssue to the single most important failing required check (or "none"). ` +
    `Strictly read-only — never modify any file or repo.`,
    { label: `audit:${repo}`, phase: 'Audit', schema: FINDINGS_SCHEMA },
  )
))).filter(Boolean)

if (!perRepo.length) {
  return { repos, perRepo: [], consistency: [], note: 'all-audits-failed' }
}

// Phase 3 — one cross-repo consistency pass (the genuinely cross-cutting reasoning).
phase('Consistency')
const consistency = await agent(
  `README audit findings across ${perRepo.length} repos:\n${JSON.stringify(perRepo)}\n\n` +
  `Report cross-repo CONSISTENCY drift only (not per-repo issues): (1) input-table column order, ` +
  `(2) badge style/placement, (3) section naming, (4) license format (LICENSE vs LICENSE.md). ` +
  `Each observation must name the repos that diverge. Read-only.`,
  {
    label: 'consistency',
    phase: 'Consistency',
    schema: { type: 'object', required: ['observations'], properties: { observations: { type: 'array', items: { type: 'string' } } } },
  },
)

return { repos, perRepo, consistency: (consistency && consistency.observations) || [] }
