export const meta = {
  name: 'security-audit-owasp',
  description: 'OWASP Top 10 audit: fan the ten categories out across read-only agents in parallel, return structured findings.',
  phases: [
    { title: 'Audit', detail: 'one read-only agent per OWASP category (A01-A10) scans the scope' },
  ],
}

// `args` arrives as a JSON string on the skill->Workflow path — parse defensively.
const a = typeof args === 'string' ? JSON.parse(args) : (args ?? {})
const scope = a.scope || '.'
const skillPath = a.skillPath || ''

// The ten OWASP categories are fixed, so coverage is deterministic every run.
const OWASP = [
  ['A01', 'Injection'],
  ['A02', 'Broken Authentication'],
  ['A03', 'Cross-Site Scripting (XSS)'],
  ['A04', 'Insecure Direct Object References'],
  ['A05', 'Security Misconfiguration'],
  ['A06', 'Sensitive Data Exposure'],
  ['A07', 'Missing Function-Level Access Control'],
  ['A08', 'Cross-Site Request Forgery (CSRF)'],
  ['A09', 'Using Components with Known Vulnerabilities'],
  ['A10', 'Server-Side Request Forgery (SSRF)'],
]

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['category', 'findings'],
  properties: {
    category: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'location', 'description', 'remediation'],
        properties: {
          severity: { 'enum': ['Critical', 'High', 'Medium', 'Low', 'Info'] },
          location: { type: 'string' },     // file:line
          description: { type: 'string' },
          remediation: { type: 'string' },
        },
      },
    },
  },
}

// Single source of truth for the checklist is the SKILL.md; agents read it when a
// resolved path is passed in. Falls back to general OWASP knowledge otherwise.
phase('Audit')
const perCategory = (await parallel(OWASP.map(([id, name]) => () => {
  const checklistRef = skillPath
    ? `Apply the ${id} checklist exactly as written in ${skillPath}.`
    : `Apply the standard OWASP ${id} (${name}) checklist.`
  return agent(
    `Audit the code under "${scope}" for OWASP ${id} (${name}) vulnerabilities. ${checklistRef} ` +
    `Search read-only with Grep/Glob/Read, limited to files within "${scope}" — never modify any file. For each issue, report severity ` +
    `(Critical/High/Medium/Low/Info), location as file:line, a one-line description, and a remediation. ` +
    `Return an empty findings array if the category has no issues in scope.`,
    { label: `owasp:${id}`, phase: 'Audit', schema: FINDINGS_SCHEMA },
  )
}))).filter(Boolean)

return { scope, perCategory }
