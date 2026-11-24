# pages-ops

Keeps a repo's static-site snapshot in sync with the Claude Design page template it comes from.
The design system owns the templates (`*.dc.html` plus shared scripts); the repo keeps a flat
snapshot of them and a short, reviewed list of its own changes. This plugin re-syncs the snapshot
and re-applies those changes. It never writes to the design system.

## Skills

- **`syncing-design-snapshot`**: fetch the template in the main session (the Artifact tool for a
  Design System artifact, `DesignSync` for a standalone claude.ai/design project), then run
  `scripts/sync_template.py` against a project config of patches. Each patch is reported
  `applied`, `carried` (the template already has it) or `FAIL` (the original text changed
  upstream). Any `FAIL` writes nothing. A deletion patch can carry a guard phrase, so a restyled
  but still present block is not reported as carried.

## Status

Draft (0.1.0). The sync engine and its unit tests are in place. Not yet included: a CI workflow
for the tests and an example project config.
