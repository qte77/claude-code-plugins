<!-- DERIVED — do not hand-edit. Source of truth:
     https://raw.githubusercontent.com/qte77/qte77/main/docs/templates/README.template.md
     Regenerate with 'make sync'; verify with 'make check_sync'. Tracking: qte77/claude-code-plugins#170 -->
<!-- @sync:begin (content below mirrors the SoT verbatim) -->
<!--
  Canonical README skeleton for qte77 repos. Copy to your repo root and fill in.
  Contract & rules: https://github.com/qte77/qte77/blob/main/docs/doc-structure.md
  Order is fixed (value-first): Hero → Badges → What → How → Why → Refs → License → <tail>.
  Keep it a front door — each section answers its one question; link depth out to docs/.
-->

# name

> name is what-it-does for who — one-line positioning.

<!-- Hero: H1 + one-line tagline required. A theme-aware wordmark is optional — if used,
     replace the H1 with a <picture> (self-hosted at assets/images/, dark + light). -->

<!-- Badges: License → Version → CI/status (SSOT: paperverse). Static (License, Version) = shields.io blue;
     status badges = native color. Left-aligned, consecutive lines, no <p align="center">. Only sanctioned external images. -->
[![License](https://img.shields.io/badge/license-SPDX-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-X.Y.Z-blue.svg)](CHANGELOG.md)
[![CI](https://github.com/ORG/REPO/actions/workflows/CI.yaml/badge.svg)](https://github.com/ORG/REPO/actions/workflows/CI.yaml)

## What

<!-- ≤ ~7 tight bullets: what it does FOR THE READER. Build internals → docs/architecture.md. -->

- capability
- capability
- capability

<!-- Optional screenshots: theme-aware, self-hosted at assets/images/, collapsed, bottom of What.
     Keep the blank lines inside <details>/<picture> so GitHub renders the nested markdown. -->
<details>
<summary>Screenshots</summary>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/images/name-dark.png" />
  <img alt="describe the screenshot" src="assets/images/name-light.png" />
</picture>

</details>

## How

<!-- One minimal example to get running. Full reference → docs/. -->

```bash
install && run
```

See [docs/quickstart.md](docs/quickstart.md) for full setup.

## Why

<!-- 2–4 lines, deferred here on purpose. Pattern: incumbent pioneered X → gap Y → we differ: Z.
     Link the spec if there is one (docs/PRD.md, docs/UserStory.md). -->

The problem and what makes this different.

## Refs

<!-- Links only, no prose. -->

- [docs/architecture.md](docs/architecture.md) — how it's built
- [CONTRIBUTING.md](CONTRIBUTING.md) — workflow
- [CHANGELOG.md](CHANGELOG.md) — changes

## License

<!-- SPDX + LICENSE link; attribute bundled third-party in NOTICE. -->

SPDX-id — see [LICENSE](LICENSE).

<!-- <tail>: one repo-type section, after License or folded into What.
     profile → Tools · Posts   |   plugin → Plugins table · Install   |   engine → API link -->
