export const meta = {
  name: 'research-cross-check',
  description: 'Bidirectional cross-check between a consumer repo and the ai-agents-research hub: pull concepts to cite/adopt, push findings to contribute, and draft the contributions',
  phases: [
    { title: 'Scan', detail: "read the consumer's decisions/findings + the hub's landscape/learnings" },
    { title: 'Diff', detail: 'pull candidates (cite/adopt) + push candidates (contribute)' },
    { title: 'Draft', detail: 'draft top contributions in the hub format' },
  ],
}

// args: a consumer-repo path string, OR { consumer, research?, focus? }.
const A = typeof args === 'object' && args ? args : {}
const CONSUMER =
  A.consumer || (typeof args === 'string' && args.trim()) || '/workspaces/qte77/claude-azure-workflows-gui'
const RESEARCH = A.research || '/workspaces/qte77/ai-agents-research'
const CONSUMER_NAME = CONSUMER.replace(/\/+$/, '').split('/').pop()
const FOCUS = A.focus ? `\n\nFOCUS this cross-check on: ${A.focus}.` : ''

const OURS_SCHEMA = {
  type: 'object',
  properties: {
    decisions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          summary: { type: 'string' },
          sources_cited: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'title'],
      },
    },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          topic: { type: 'string' },
          summary: { type: 'string' },
          evidence: { type: 'string' },
        },
        required: ['topic', 'summary'],
      },
    },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['decisions', 'findings'],
}

const THEIRS_SCHEMA = {
  type: 'object',
  properties: {
    concepts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          doc: { type: 'string' },
          summary: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'doc'],
      },
    },
    tools: {
      type: 'array',
      items: {
        type: 'object',
        properties: { name: { type: 'string' }, doc: { type: 'string' }, note: { type: 'string' } },
        required: ['name'],
      },
    },
    contribution_targets: {
      type: 'object',
      properties: {
        per_repo_learnings_dir: { type: 'string' },
        agent_requests: { type: 'string' },
        cross_repo_digest: { type: 'string' },
        per_repo_format_note: { type: 'string' },
      },
    },
  },
  required: ['concepts', 'contribution_targets'],
}

const PULL_SCHEMA = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          their_concept: { type: 'string' },
          their_doc: { type: 'string' },
          why: { type: 'string' },
          target_our_file: { type: 'string' },
          action: { type: 'string', description: 'cite | adopt-via-new-ADR | evaluate' },
          priority: { type: 'string', description: 'high | medium | low' },
        },
        required: ['their_concept', 'target_our_file', 'action'],
      },
    },
  },
  required: ['candidates'],
}

const PUSH_SCHEMA = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          key: { type: 'string' },
          our_finding: { type: 'string' },
          target_their_file: { type: 'string' },
          rationale: { type: 'string' },
          provenance: { type: 'string' },
          priority: { type: 'string', description: 'high | medium | low' },
        },
        required: ['key', 'our_finding', 'target_their_file'],
      },
    },
  },
  required: ['candidates'],
}

const DRAFT_SCHEMA = {
  type: 'object',
  properties: {
    target_path: { type: 'string', description: 'path relative to the ai-agents-research repo root' },
    title: { type: 'string' },
    content_markdown: { type: 'string' },
    pr_note: { type: 'string' },
  },
  required: ['target_path', 'content_markdown'],
}

phase('Scan')

const [ours, theirs] = await Promise.all([
  agent(
    `Read the consumer project at ${CONSUMER} and summarize what it has DECIDED and FOUND, to cross-check against the ai-agents-research catalog.${FOCUS}

Read (use Read, don't guess) whatever exists: docs/decisions/*.md (ADRs), docs/plans/*.md, AGENTS.md / CLAUDE.md, README.md, CHANGELOG.md, and key design docs (architecture, roadmap, evaluation).

Return: the project's key DECISIONS (id, title, 1-line summary, external sources each cites) and its notable reusable FINDINGS/learnings (anything another repo could adopt — methodology, tooling, gotchas, comparisons) with brief evidence. Note open questions.`,
    { label: 'scan:ours', phase: 'Scan', schema: OURS_SCHEMA },
  ),
  agent(
    `Read the ai-agents-research catalog at ${RESEARCH} and catalog concepts/tools relevant to the consumer project (${CONSUMER_NAME}).${FOCUS}

Read (use Read, don't guess): the index/README, then the landscape docs under docs/sdlc-lcm/, docs/cc-community/, and docs/non-cc/ that match the consumer's domain. Also read one file under docs/learnings/per-repo/ (e.g. agents-eval.md) as a FORMAT TEMPLATE, and note the contribution receptacles: docs/learnings/per-repo/ (dir), AGENT_REQUESTS.md, docs/learnings/cross-repo-digest.md.

Return: relevant concepts (name, source doc path, 1-line summary, cited URLs), tools, and contribution_targets (the receptacle paths + a note on the per-repo-learnings file format).`,
    { label: 'scan:theirs', phase: 'Scan', schema: THEIRS_SCHEMA },
  ),
])

phase('Diff')

const [pull, push] = await Promise.all([
  agent(
    `PULL (hub research -> consumer). Given OURS and THEIRS (JSON), list THEIR concepts/tools/sources the consumer has NOT yet applied or cited, each mapped to the target file in the CONSUMER repo that should cite/adopt it (a specific ADR or plan), with a concrete action (cite | adopt-via-new-ADR | evaluate) and priority. Skip anything already cited.

OURS:\n${JSON.stringify(ours)}\n\nTHEIRS:\n${JSON.stringify(theirs)}`,
    { label: 'diff:pull', phase: 'Diff', schema: PULL_SCHEMA, effort: 'high' },
  ),
  agent(
    `PUSH (consumer -> hub research). Given OURS and THEIRS (JSON), list the consumer's findings/learnings NOT yet captured in THEIRS, each with the target file in the HUB repo (a new docs/learnings/per-repo/${CONSUMER_NAME}.md, a specific landscape doc to extend, or AGENT_REQUESTS.md), a rationale, and provenance. Prioritise high-value, first-party-sourced items.

OURS:\n${JSON.stringify(ours)}\n\nTHEIRS:\n${JSON.stringify(theirs)}`,
    { label: 'diff:push', phase: 'Diff', schema: PUSH_SCHEMA, effort: 'high' },
  ),
])

phase('Draft')

const top = (push.candidates || []).slice(0, 4)
const drafts = await parallel(
  top.map((c, i) => () =>
    agent(
      `Draft a contribution for the ai-agents-research hub, ready to drop into the repo, matching their per-repo-learnings format (What it is -> How it works -> Adoption/relevance -> Action items; first-party sources cited; a provenance footer noting source repo "${CONSUMER_NAME}" + a {{DATE}} placeholder). Item: ${JSON.stringify(c)}.

Return target_path (relative to the hub repo root), title, the full content_markdown, and a one-paragraph pr_note. Keep it tight and accurate — do NOT invent facts unsupported by OURS.\n\nOURS context:\n${JSON.stringify(ours)}`,
      { label: `draft:${c.key || i}`, phase: 'Draft', schema: DRAFT_SCHEMA },
    ),
  ),
)

return { consumer: CONSUMER_NAME, pull, push, drafts: drafts.filter(Boolean) }
