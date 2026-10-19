# Claim Verification

**Promoted from `AGENT_LEARNINGS.md` 2026-07-30 after nine occurrences in one session.**
Every one was caught by the user or an adversarial subagent — none by self-check. That is a scheduling
failure, not a knowledge failure: the verification step exists, it just was not run before writing.

## The gate

**Before anything outward-facing is published, every load-bearing factual claim in it is verified at
source in the same turn.** Outward-facing = anything a human other than you will act on: an issue, a PR
body, a comment, an email, a plan row, a design doc.

- Vendor behaviour → the vendor's own docs, fetched now. Not memory.
- Current state of a system → query the current state. Not an aggregate view.
- Someone's stated position → their actual words, read now.

**A claim that cannot be verified is removed, or marked unverified in the artifact itself** — not merely
hedged in conversation.

**Never label a step "safe", "risk-free" or "no risk" while any dependency it rests on is unconfirmed.**

## Five failure modes this prevents

**1 · Assertion from partial evidence.** Never generalise from one sample. One file is not a corpus, one
function is not a codebase, one commit is not a history. If the claim is about "all", check all — or say
how many were checked.

**2 · Search artifact — the tool answered a different question.** A grep, glob or find that returns
nothing has not proven absence; it has proven that pattern did not match that scope.

- Aggregate views show what was **ever** true, never what **is** true. Read migrations, commits and
  config chronologically — last write wins.
- Binary files (`.xlsx`, `.pdf`, images) are invisible to text search. Absence of a grep hit across them
  means nothing.
- Before reporting "not found", state what was searched and how; a wrong scope is the usual cause.

**3 · Hedge decay.** Uncertainty stated while thinking must survive into the artifact. If the analysis
said "strong inference, worth confirming", the published version says so too. Hedges that exist only in
conversation are lost the moment the artifact is read by anyone else.

**4 · Acting on a known unknown.** Flagging a dependency as unresolved and then building on it anyway is
worse than not flagging it — it produces a plan that looks verified. Either resolve it, or mark every
step that rests on it as conditional.

**5 · Deference without verification.** A correction from the user or a teammate is a hypothesis, not a
source. Check it against the system before adopting it. Being told something plausible is not evidence.

## Before replying to a person

**Read what they actually said, in full, first.** Check for replies on any thread before adding to it.
Answering around an unread reply wastes both sides' effort and reads as not listening.

## Verify hardest where it costs most

Order of care: security findings · legal or contractual claims · anything instructing someone to take an
irreversible action (a transfer, a deletion, a purchase, a deploy) · severity ratings.

**Severity is a claim like any other.** "Critical" and "moderate" both need the access path traced, not
assumed from the mechanism found first.
