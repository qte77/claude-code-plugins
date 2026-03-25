---
name: implementing-go
description: Implements idiomatic Go code matching architect specifications. Use when writing Go code, creating packages, or implementing features in Go.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebSearch, WebFetch
  argument-hint: [feature-name]
  stability: stable
  content-hash: sha256:placeholder
  last-verified-cc-version: 2.1.0
---

# Go Implementation

**Target**: $ARGUMENTS

Creates **focused, idiomatic** Go implementations following specifications
exactly. No over-engineering.

## Go Standards

See `references/go-best-practices.md` for comprehensive Go guidelines.

## Workflow

1. **Read specifications** from provided documents
2. **Validate scope** — Simple (single package) vs Complex (multi-package)
3. **Study existing patterns** in project structure
4. **Implement minimal solution** matching stated functionality
5. **Create focused tests** matching task complexity
6. **Run validation** and fix all issues

## Implementation Strategy

**Simple Tasks**: Single-package functions, standard error handling,
table-driven tests

**Complex Tasks**: Multi-package with `internal/`, custom error types,
interface-based design, comprehensive test coverage

**Always**: Use existing project patterns, pass `go vet` and `go test -race`

## Output Standards

**Simple Tasks**: Minimal Go functions with proper error returns
**Complex Tasks**: Complete packages with interfaces, tests, godoc
**All outputs**: Idiomatic, concise, no unnecessary abstraction

## Quality Checks

Before completing any task:

```bash
go vet ./...
go test -race ./...
golangci-lint run ./...
```

All checks must pass.
