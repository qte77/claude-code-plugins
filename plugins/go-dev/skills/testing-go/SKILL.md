---
name: testing-go
description: Writes Go tests following TDD with table-driven tests, subtests, fuzz testing, and benchmarks. Use when writing unit tests, integration tests, or benchmarks.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob, Edit, Write, Bash
  argument-hint: [test-scope or package-name]
  stability: stable
  content-hash: sha256:placeholder
  last-verified-cc-version: 2.1.0
---

# Go Testing

**Target**: $ARGUMENTS

Writes **focused, behavior-driven tests** following Go testing conventions.

## Quick Reference

**Full documentation**: `references/go-testing-patterns.md`

## Quick Decision

**TDD (default)**: Table-driven tests with `t.Run()` subtests.
**Fuzz**: Use `testing.F` for parser/validator inputs.
**Benchmark**: Use `testing.B` for performance-critical paths.
**Integration**: Guard with `//go:build integration` tag.

## TDD Essentials

**Cycle**: RED (failing test) → GREEN (minimal pass) → REFACTOR (clean up)

**Structure**: Table-driven with Arrange-Act-Assert

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    int
        want    int
        wantErr error
    }{
        {"positive division", 10, 2, 5, nil},
        {"divide by zero", 10, 0, 0, ErrDivideByZero},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if !errors.Is(err, tt.wantErr) {
                t.Errorf("Divide(%d, %d) error = %v; want %v", tt.a, tt.b, err, tt.wantErr)
            }
            if got != tt.want {
                t.Errorf("Divide(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

## What to Test

**High-Value**: Business logic, error paths, integration points, edge cases

**Avoid**: Library behavior, trivial assertions, implementation details

## Naming Convention

**Format**: `Test{Function}_{scenario}` or descriptive table entry names

```go
func TestValidateUser_EmptyEmailReturnsError(t *testing.T) { ... }
```

## Execution

```bash
go test ./...                          # All tests
go test -race ./...                    # With race detector
go test -run TestUser ./...            # Filter by name
go test -tags=integration ./...        # Integration tests
go test -fuzz=FuzzParse -fuzztime=30s  # Fuzz testing
go test -bench=. -benchmem ./...       # Benchmarks
go test -coverprofile=c.out ./...      # Coverage
```

## Quality Gates

- [ ] All tests pass (`go test -race ./...`)
- [ ] TDD Red-Green-Refactor followed
- [ ] Table-driven structure with `t.Run()` subtests
- [ ] Descriptive test names explaining the scenario
- [ ] `errors.Is`/`errors.As` for error comparison
- [ ] `t.Helper()` in shared test helpers
- [ ] `t.TempDir()` for filesystem isolation
- [ ] No shared mutable state with `t.Parallel()`
