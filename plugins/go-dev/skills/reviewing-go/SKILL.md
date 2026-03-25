---
name: reviewing-go
description: Provides focused Go code reviews for quality, security, and idiomatic style. Use when reviewing Go code or when the user asks for code review.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob, WebFetch, WebSearch
  argument-hint: [file-or-directory]
  stability: stable
  content-hash: sha256:placeholder
  last-verified-cc-version: 2.1.0
---

# Review Context

- Changed files: !`git diff --name-only HEAD~1 2>/dev/null || echo "No recent commits"`
- Staged files: !`git diff --staged --name-only`

## Go Code Review

**Scope**: $ARGUMENTS

Delivers **focused, idiomatic** Go code reviews matching stated task
requirements exactly. No over-analysis.

## Go Standards

See `references/go-review-checklist.md` for comprehensive review guidelines.

## Workflow

1. **Read task requirements** to understand expected scope
2. **Check `go vet` and `go test -race`** pass before detailed review
3. **Match review depth** to task complexity
4. **Validate requirements** — does implementation match task scope exactly?
5. **Issue focused feedback** with specific file paths and line numbers

## Review Strategy

**Simple Tasks**: Security, error handling correctness, naming, requirements
match

**Complex Tasks**: Above plus architecture, interface design, concurrency
safety, performance

**Always**: Check error wrapping, naming conventions, test coverage

## Review Checklist

**Security & Correctness**:

- [ ] No security vulnerabilities (SSRF, injection, path traversal)
- [ ] `crypto/rand` not `math/rand` for security values
- [ ] Errors wrapped with `%w` at boundaries, checked with `errors.Is`/`errors.As`
- [ ] `go vet` and `go test -race` pass

**Idiomatic Go**:

- [ ] Naming follows Go conventions (PascalCase exports, camelCase internal)
- [ ] Acronyms all-caps (`ID`, `URL`, `HTTP`)
- [ ] `context.Context` as first parameter
- [ ] Interfaces are small (1-2 methods)
- [ ] Early returns over nested `if/else`

**Code Quality**:

- [ ] Implements exactly what was requested
- [ ] No over-engineering or scope creep
- [ ] Tests cover stated functionality with table-driven pattern

**Structural Health**:

- [ ] No function exceeds cyclomatic complexity 15
- [ ] No copy-paste duplication across methods
- [ ] Package names are descriptive (no `utils`, `common`, `helpers`)

## Output Standards

**Simple Tasks**: CRITICAL issues only, clear approval when requirements met
**Complex Tasks**: CRITICAL/WARNINGS/SUGGESTIONS with specific fixes
**All reviews**: Concise, actionable, no unnecessary analysis
