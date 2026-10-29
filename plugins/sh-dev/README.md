# sh-dev

Shell scripting skills for Bash scripts that hooks, CI and setup flows depend on.

## Skills

- `implementing-shell` — Write and review Bash scripts: strict mode, argument parsing, usage
  messages, exit codes, `DRY_RUN`, dependency checks, ShellCheck clean.
- `testing-shell` — BATS tests: `@test` blocks, `setup`/`teardown`, `run` with `$status`/`$output`
  assertions, stubbing external commands on `PATH`, CI wiring with ShellCheck.

## Companions

- `tdd-core` — the Red-Green-Refactor methodology `testing-shell` follows
- `gha-dev` — GitHub Action scaffolding; its shell-based actions use these skills for BATS and ShellCheck
- `makefile-core` — `scaffold-shell.md` for a Makefile wrapping lint and test recipes

## Install

```bash
claude plugin install sh-dev@qte77-claude-code-plugins
```
