# web-recon

Authorized **web/API reconnaissance & attack-surface assessment** for Claude Code. Drives the
[web-recon-kit][kit] harness (config-driven via `scope.toml`) through recon → API testing → authz
(BOLA/BFLA) → verified report.

## Skill

- **web-recon** — end-to-end authorized recon/assessment workflow. Authorization-gated; the
  underlying runners are read-only (GET/OPTIONS), throttled, and never trigger cron/mutation.

## Requires

- A [web-recon-kit][kit] checkout (the Python engine).
- A [polyfetch-scrape][poly] checkout for the browser tier (consumed via the
  `uv run --directory` env-borrow contract).

See the web-recon-kit README for setup and the per-target `scope.toml` schema. Abbreviations
(BOLA, BFLA, IDOR, RBAC, …) are expanded in the skill and in the harness `docs/glossary.md`.

[kit]: https://github.com/qte77/web-recon-kit
[poly]: https://github.com/qte77/polyfetch-scrape
