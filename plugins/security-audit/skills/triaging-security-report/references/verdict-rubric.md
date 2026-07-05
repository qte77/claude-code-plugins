# Verdict Rubric — classifying security-report findings

Four mutually exclusive verdicts. When torn between two, verify deeper — the boundary cases
are where reports mislead.

## CONFIRMED

The claimed pattern exists in the code and is a real weakness in this deployment.

- Verify the *pattern*, not the cited line — report line numbers drift across commits.
- Record the verified file:line and the concrete exposure path.
- Still re-rate severity (see Severity-context rules) — CONFIRMED ≠ the report's severity.

## OVERSTATED

The pattern exists, but the report's severity ignores the deployment context.

Common downgrades:

- **Secrets in process argv on GitHub-hosted runners** — ephemeral single-tenant VM,
  `GITHUB_TOKEN` auto-revokes at job end and is log-masked; the only reader is a process the
  same job spawned. HIGH → LOW/MEDIUM (rises again on self-hosted/multi-job runners).
- **Unvalidated input** that is operator-controlled (CLI flag, env var, checked-in config).
- **Missing hardening** presented as an active vulnerability.

## FALSE-POSITIVE

The flagged pattern is present but is not a vulnerability.

Recurring scanner myths:

- `json.loads` / `JSON.parse` as "insecure deserialization" — JSON parsing executes no code;
  CWE-502 needs pickle/yaml.load/ObjectInputStream-class primitives.
- "SSRF" where the URL's **host and protocol** are not attacker-controlled (config-authored
  URLs, hardcoded API hosts with only a path/slug parameter). Path-only control is not SSRF.
- Hardcoded **non-secret** constants (default keyword lists, endpoint templates) as "data
  exposure".
- Missing rate limiting / DoS on operator-run CLI tools — resource exhaustion is a different
  review, not a code vulnerability.
- Regex "injection"/ReDoS on linear patterns (a single `.*` cannot backtrack catastrophically).

## FABRICATED

The report describes code that does not exist, or flags the defense as the flaw.

Two observed shapes:

- **Phantom code**: a command/function/file the repo simply doesn't contain (claimed Makefile
  `sed` with untrusted input — the Makefile had no `sed` at all). Grep the whole repo before
  concluding; then record "absent" as the verified location.
- **Mitigation flagged as vulnerability**: the XXE-safe parser (`defusedxml.fromstring`)
  reported as "no XXE protection"; a path-traversal *sanitizer* (`safe_slug` collapsing
  non-alphanumerics) reported as "potential path traversal". Read the flagged function's
  body — if it *is* the guard, the correct action is usually a **regression test pinning the
  guard**, not a code change.

FABRICATED findings' remediations are dangerous by construction (e.g. "replace the hardcoded
defaults with empty lists" — would break the tool out of the box). Never apply them.

## Severity-context rules (trusted-input precedents)

Inputs assumed trusted unless the threat model says otherwise:

- Environment variables and CLI flags (attacker who sets these already owns the process)
- Checked-in configuration files and operator-authored local files
- UUIDs (unguessable; no validation needed)

Exposure-context modifiers:

- Ephemeral, single-tenant CI runners shrink local-attacker windows
- Auto-revoking, log-masked tokens cap secret-exposure impact
- Client-side JS needs no authz checks (the server is the boundary)
- A strict same-origin CSP + vendored assets materially mitigates XSS-class findings on
  static dashboards — credit existing controls before accepting an "unsanitized output" claim

## Architecture-gap findings ("missing control X")

Score them against the components that exist:

1. Map the claimed control to the component it would protect.
2. If the component isn't in this codebase (LLM calls, tool dispatch, RAG store living in a
   different system), the finding is **out of scope** — record the architectural reason.
3. If the component exists and the control is genuinely absent, treat as CONFIRMED-hardening
   (usually MEDIUM at most unless an exploit path is demonstrated).

## Report-metadata smells (step-1 checklist)

- Headline rating vs the report's own confirmed count (HIGH with `0 confirmed` = hypotheses)
- Per-finding confidence markers: `unconfirmed`, `memory_hint`, `inferred`, `not_tested`
- Attack chains where every required edge is unproven
- Uniform scores across findings (0.50/0.50 everywhere = no per-finding analysis happened)
- Remediation advice that contradicts the finding (or would break documented behavior)
