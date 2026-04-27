# Core Principles

**MANDATORY for ALL tasks.** These principles override all other guidance when
conflicts arise. Every decision optimizes for user value, clarity, and usability.

## Code Quality

- **KISS, DRY** — simplest solution that works; single source of truth.
- **AHA** — three similar lines beats a premature abstraction; extract only when the pattern is stable.
- **YAGNI** — build for the requested behavior, not for imagined future ones.

## Execution

- **Match existing patterns; ask before diverging.** Reuse what's there, validate against established conventions, clarify vague requirements before acting.
- **Touch only task-related code.** Minimal diff for the task.
- **Solve root causes, not symptoms.** Understand the "why" before patching.

## Communication

- **Clarity** — name things for what they are; state decisions and reasons plainly; prefer concrete examples over abstract framing.
- **Actionable and Concrete** — specific deliverables, measurable outcomes.

## Before Starting Any Task

- [ ] Does this serve user value?
- [ ] Is this the simplest approach?
- [ ] Am I duplicating existing work?
- [ ] Do I actually need this?
- [ ] Am I touching only relevant code?
- [ ] What's the root cause I'm solving?
- [ ] Is this clear to a reader who lacks my context?

## Post-Task Review

Before finishing, ask yourself:

- **Did we forget anything?** — check requirements thoroughly
- **High-ROI enhancements?** — suggest opportunities (don't implement)
- **Something to delete?** — remove obsolete/unnecessary code

**IMPORTANT**: Do NOT alter files based on this review. Only output
suggestions to the user.

## When in Doubt

**STOP. Ask the user.**

Don't assume, don't over-engineer, don't add complexity.
