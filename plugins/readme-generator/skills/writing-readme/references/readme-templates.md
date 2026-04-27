# README templates

Template snippets for the four scopes handled by `writing-readme`.

## Repo README — GitHub Action

```markdown
# repo-name

![Version](https://img.shields.io/badge/version-X.Y.Z-8A2BE2)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Test Action](https://github.com/owner/repo/actions/workflows/test-action.yaml/badge.svg)
![CodeFactor](https://www.codefactor.io/repository/github/owner/repo/badge)
![CodeQL](https://github.com/owner/repo/actions/workflows/codeql.yaml/badge.svg)
![Dependabot](https://img.shields.io/badge/dependabot-enabled-025e8c)
<!-- Add ruff/pytest badges for Python actions, BATS badge for shell actions -->

One-line description.

## Inputs

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| ... | ... | ... | ... |

## Outputs

| Name | Description |
|------|-------------|
| ... | ... |

## Usage

\`\`\`yaml
name: Example
on: [push]
jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: owner/repo@vX
        with:
          input_name: value
\`\`\`

## What it does

1. Step one
2. Step two
3. Step three

## License

[License-Type](LICENSE)
```

**Conventions:**

- Input table columns: Name | Required | Default | Description (this order)
- Version badge immediately after H1
- Usage section has a complete, copy-pasteable workflow
- "What it does" uses numbered steps
- License links to `LICENSE` file (never `LICENSE.md`)

## Repo README — Library/Application

```markdown
# repo-name

One-line description.

## Installation

\`\`\`bash
install command
\`\`\`

## Quick Start

\`\`\`python
minimal usage example
\`\`\`

## License

[License-Type](LICENSE)
```

## Account Profile README

```markdown
# Display Name

Tagline or bio — who you are in one sentence.

### Current focus

- What you're working on now (2-3 bullets)

### Projects

- [**project-name**](url) — one-line description
- [**project-name**](url) — one-line description

### Tools & languages

Python · Rust · TypeScript · ...
```

## Organization Profile README

```markdown
# Org Name

Single-sentence mission.

Optional 2-3 sentence elaboration.

---

### What we build

**Domain 1** — brief description with inline links to
[key-repo-1](url) and [key-repo-2](url).

### Get involved

- CTA 1 → [link](url)
- Open an issue or PR on any repo.
```

**Conventions:**

- File MUST be at `.github/profile/README.md`
- 150-400 words total
- License always links to `LICENSE` (never `LICENSE.md`)
