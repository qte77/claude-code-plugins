# python-dev

Python implementation, testing, and code review skills, deploys uv permissions via SessionStart hook.

## Skills

- **implementing-python** — Implements concise, streamlined Python code matching exact architect specifications
- **testing-python** — Writes tests following TDD (using pytest and Hypothesis) and BDD best practices
- **reviewing-code** — Provides concise, focused code reviews matching exact task complexity requirements

## Deployed files

- **settings.local.json** → `.claude/settings.local.json` — uv permissions (if uv detected, copy-if-not-exists)

When a repo's `.scaffold` file reads `python`, the SessionStart hook also deploys (all
copy-if-not-exists):

- `.scaffolds/python.sh` — Ralph Loop adapter script
- `.scaffolds/extract_signatures.py` — signature-extraction helper used by the adapter
- `.claude/rules/*.md` — testing rule(s) from `scaffold/rules/`
- `.github/workflows/{complexipy,pyright,pytest,ruff}.yaml` — CI workflows
- `.github/dependabot.yaml` — dependency update config (not a workflow, so it does not land
  under `.github/workflows/`)

## Install

```bash
claude plugin install python-dev@qte77-claude-code-plugins
```
