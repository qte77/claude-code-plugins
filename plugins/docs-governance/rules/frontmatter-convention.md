---
paths:
  - "**/*.md"
---

# Frontmatter Convention

Every markdown file MUST have YAML frontmatter unless it is an exempt file.

## Required Fields

```yaml
---
title: Descriptive Title
purpose: One-line purpose statement
created: YYYY-MM-DD
updated: YYYY-MM-DD
validated_links: YYYY-MM-DD
---
```

- `title` — descriptive, matches the `# H1` heading
- `purpose` — one line, used for relevance matching and context decisions
- `created` — date of first commit
- `updated` — bump on every content edit
- `validated_links` — date when URLs were last verified working

## Optional Fields

- `source` — primary URL the doc is based on
- `category` — `technical`, `requirements`, `implementation`, `landscape`

## Exempt Files

These follow their own conventions — no YAML frontmatter required:

### Well-Known Project Files

`README.md`, `CHANGELOG.md`, `LICENSE.md`, `CONTRIBUTING.md`, `AGENTS.md`,
`CODE_OF_CONDUCT.md`, `SECURITY.md`, `TODO.md`, `LEARNINGS.md`, `REQUESTS.md`,
`CODEOWNERS`, `.gitmessage`

### GitHub Templates

Files in `.github/` — issue templates, PR templates, and workflow files use
their own YAML frontmatter format (`name`, `description`, `labels`, etc.).

### Build/Config Markdown

`mkdocs.yml`-referenced nav files, `docs/index.md` (if auto-generated).

## Rules

- No `sources:` key in frontmatter — sources go in the Sources section at end of file
- `<!-- markdownlint-disable MD013 -->` at file top only (not inline around tables)
- Sources section uses reference-style links (`[key]: url` at bottom)
