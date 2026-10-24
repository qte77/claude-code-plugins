# website-audit

Website design research, usability audit, SEO/GEO audit, and WCAG accessibility audit skills.

## Skills

- **researching-website-design** — Analyzes industry websites for design patterns, layout, typography, and content strategies
- **auditing-website-usability** — Audits website usability for UX optimization, covering forms, navigation, and microcopy
- **auditing-website-accessibility** — Audits website accessibility for WCAG 2.2 AA compliance, generating findings and code fixes
- **auditing-website-seo-geo** — Audits a site's SEO and AI-search (GEO) readiness: meta tags, Open Graph/Twitter, JSON-LD, robots/llms conventions
- **verifying-design-canvas** — Pulls a Claude Design canvas straight from claude.ai/design and verifies a live deployed app matches it: theme tokens, DOM/accessibility structure, and every interactive role/tab state

## Demo

Try it out after installing:

```text
/auditing-website-accessibility https://example.com
```

This will run a WCAG 2.2 AA compliance audit against the target URL,
producing findings with severity levels and implementable code fixes.

## Install

```bash
claude plugin install website-audit@qte77-claude-code-plugins
```
