---
title: Go Testing Strategy
version: 1.0
applies-to: Agents and humans
purpose: Go-specific testing tools and when to use each
see-also: tdd-best-practices.md
---

# Testing Strategy

**Purpose**: Go-specific testing tools and when to use each.

> Language-agnostic testing strategy (what to test, mocking, organization)
> is in the `tdd-core` plugin. This file extends it with Go tools
> (go test, testify, rapid, gomock, golden files).

## Core Principles

| Principle | Testing Application |
|-----------|---------------------|
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test stdlib or framework behavior |

## What to Test

**High-Value** (test these):

1. Business logic — algorithms, calculations, decision rules
2. Integration points — HTTP handlers, database operations
3. Edge cases — empty inputs, error propagation, boundaries
4. Contracts — API response shapes, data transformations

**Low-Value** (avoid these):

1. Stdlib behavior — `json.Marshal`, `http.NewRequest`, etc.
2. Trivial getters/setters — unless they encode business rules
3. Default zero values — unless defaults encode business rules
4. Type existence — the compiler handles these

### Patterns to Remove

| Pattern | Why Remove | Example |
|---------|------------|---------|
| Struct field existence | Compiler validates | `assert user.Name != ""` |
| Interface satisfaction | Compile-time check | `var _ Reader = (*Store)(nil)` in test |
| Default zero values | Testing `0 == 0` | `assert cfg.Timeout == 0` |
| Over-granular | Consolidate to table | 8 separate test functions |

**Rule**: If the test wouldn't catch a real bug, remove it.

## Tool Selection Guide

| Tool | Question it answers | Use for |
|------|---------------------|---------|
| **go test + stdlib** | Does this logic produce the right result? | TDD, unit, integration |
| **testify/assert** | Is failure message readable? | When `t.Error` is unclear |
| **testify/require** | Is this prerequisite met? | Setup validation, nil checks |
| **rapid** | Does this hold for ALL inputs? | Math, parsers, invariants |
| **golden files** | Does output still look the same? | Large text/JSON regressions |
| **gomock** | Does call sequence match? | When call count/order matters |

**One-line rule**: `go test` for **logic**, testify for **readability**,
rapid for **properties**, golden files for **regressions**, gomock for **interaction**.

## Table-Driven Tests (Go Idiom)

```go
func TestValidateAge(t *testing.T) {
    tests := []struct {
        name    string
        age     int
        wantErr bool
    }{
        {name: "valid", age: 25, wantErr: false},
        {name: "negative", age: -1, wantErr: true},
        {name: "over max", age: 151, wantErr: true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateAge(tt.age)
            if tt.wantErr {
                require.Error(t, err)
            } else {
                require.NoError(t, err)
            }
        })
    }
}
```text

## testify: assert vs require

- **assert** — records failure, test continues (independent checks)
- **require** — stops test immediately (prerequisites)

```go
func TestProcessOrder(t *testing.T) {
    order, err := ProcessOrder(ctx, input)
    require.NoError(t, err)       // stop if fails
    require.NotNil(t, order)      // stop if nil

    assert.Equal(t, "pending", order.Status)
    assert.Greater(t, order.Total, 0.0)
}
```

## Property-Based Testing with rapid

```go
import "pgregory.net/rapid"

func TestParseRoundTrip(t *testing.T) {
    rapid.Check(t, func(t *rapid.T) {
        price := rapid.Float64Range(0.01, 9999.99).Draw(t, "price")
        qty := rapid.IntRange(1, 1000).Draw(t, "qty")

        item := Item{Price: price, Qty: qty}
        encoded, _ := json.Marshal(item)
        var decoded Item
        json.Unmarshal(encoded, &decoded)

        if decoded.Price != item.Price || decoded.Qty != item.Qty {
            t.Fatalf("round-trip mismatch")
        }
    })
}
```text

## Mocking with Interfaces (No Framework)

```go
type EmailSender interface {
    Send(ctx context.Context, to, subject, body string) error
}

// Fake in test file
type fakeEmailSender struct {
    sent []string
    err  error
}
func (f *fakeEmailSender) Send(_ context.Context, to, _, _ string) error {
    f.sent = append(f.sent, to)
    return f.err
}

// Compile-time interface check
var _ EmailSender = (*fakeEmailSender)(nil)
```

Prefer interface fakes; use gomock only when call count/order is the behavior under test.

## Test Organization

```text
mypackage/
├── service.go
├── service_test.go      # same package or _test suffix
└── testdata/            # golden files, fixtures
```text

Use `t.Helper()` in test helpers so failures point to callers.

## Naming Conventions

**Format**: `Test{Type}_{Method}_{Behavior}`

```go
TestUserService_Create_ReturnsIDOnSuccess
TestUserService_Create_RejectsEmptyEmail
TestValidateEmail_MissingAt
```

## Decision Checklist

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **stdlib** (skip)?
4. Which tool: go test (default), testify (readability), rapid (any input), golden files (regression), gomock (interaction)

## References

- TDD practices: `tdd-best-practices.md`
- [rapid Documentation](https://pkg.go.dev/pgregory.net/rapid)
- [testify Documentation](https://pkg.go.dev/github.com/stretchr/testify)
