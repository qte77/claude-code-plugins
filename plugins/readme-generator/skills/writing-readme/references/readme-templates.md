# README templates

Template snippets for the four scopes handled by `writing-readme`. Repo READMEs
follow the [qte77 doc-structure canon](https://github.com/qte77/qte77/blob/main/docs/doc-structure.md)
(SoT) — derive from it, never redefine it here.

- **Canon repo order (value-first):** Hero → Badges → What → How → Why → Refs → License → \<tail\>.
- **Badges:** License → Version → CI; License & Version are shields.io static `blue` (Version
  linked to `CHANGELOG.md`); status badges keep the service's native color; left-aligned on
  consecutive lines, no `<p align="center">`.
- **Front-door rule:** each section answers its one question; depth links out to `docs/`, never inlined.
- **Screenshots (optional):** collapsed `<details>` at the bottom of What, theme-aware, self-hosted
  at `assets/images/`.

## Repo README — canon skeleton (library / application / generic)

```markdown
# repo-name

> repo-name is what-it-does for who — one-line positioning.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-X.Y.Z-blue.svg)](CHANGELOG.md)
[![CI](https://github.com/owner/repo/actions/workflows/ci.yaml/badge.svg)](https://github.com/owner/repo/actions/workflows/ci.yaml)

## What

- capability for the reader
- capability
- capability

## How

\`\`\`bash
install && run
\`\`\`

See [docs/](docs/) for full setup.

## Why

The problem and what makes this different (incumbent → gap → how we differ).

## Refs

- [docs/architecture.md](docs/architecture.md) — how it's built
- [CONTRIBUTING.md](CONTRIBUTING.md) — workflow
- [CHANGELOG.md](CHANGELOG.md) — changes

## License

SPDX-id — see [LICENSE](LICENSE).
```

## Repo README — GitHub Action (tail variant)

Same canon order; the Action's Inputs/Outputs/Usage are the repo-type `<tail>` under How.

```markdown
# repo-name

> repo-name is what-it-does for who — one-line positioning.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-X.Y.Z-blue.svg)](CHANGELOG.md)
[![CI](https://github.com/owner/repo/actions/workflows/test-action.yaml/badge.svg)](https://github.com/owner/repo/actions/workflows/test-action.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/owner/repo/badge)](https://www.codefactor.io/repository/github/owner/repo)
<!-- status badges use native color; add CodeQL / ruff / BATS after CI as applicable -->

## What

- what the action does, for the reader (1–3 bullets)

## How

\`\`\`yaml
- uses: owner/repo@vX
  with:
    input_name: value
\`\`\`

### Inputs

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| ... | ... | ... | ... |

### Outputs

| Name | Description |
|------|-------------|
| ... | ... |

## Refs

- [CHANGELOG.md](CHANGELOG.md) — changes

## License

SPDX-id — see [LICENSE](LICENSE).
```

**Conventions:** Input table columns `Name | Required | Default | Description` (this order); badges
License → Version → CI (static `blue` / native status); License links to `LICENSE` (never `LICENSE.md`).

## Account Profile README

Profile repos use the profile `<tail>` (focus · projects · tools); no version/CI badges — a License
badge only, or omit the badge row.

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
