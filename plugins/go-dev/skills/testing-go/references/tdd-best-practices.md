---
title: Go TDD Best Practices
version: 1.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md
---

**Purpose**: Go-specific TDD examples with go test, testify, and rapid.

> Language-agnostic TDD principles (cycle, AAA, anti-patterns) are in
> the `tdd-core` plugin. This file extends those with Go tooling.

## Red-Green-Refactor with go test

In Go, **Red** is often a compile error — the function does not exist yet.
Write the test first, let the compiler tell you what is missing.

## AAA Structure in Go Tests

```go
func TestOrderCalculator_Total_SumsItemPrices(t *testing.T) {
    // ARRANGE
    calc := NewOrderCalculator()
    items := []Item{{Price: 10.00, Qty: 2}, {Price: 5.00, Qty: 1}}

    // ACT
    total := calc.Total(items)

    // ASSERT
    assert.Equal(t, 25.00, total)
}
```

## Go-Specific TDD: Table-Driven

Write the table first to define all expected behaviors, then implement:

**RED** — table test, function doesn't exist:

```go
func TestValidateAge(t *testing.T) {
    tests := []struct {
        name    string
        age     int
        wantErr bool
    }{
        {name: "valid adult", age: 25, wantErr: false},
        {name: "negative age", age: -1, wantErr: true},
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
```

**GREEN** — minimal implementation:

```go
func ValidateAge(age int) error {
    if age < 0 {
        return fmt.Errorf("age must be non-negative, got %d", age)
    }
    if age > 150 {
        return fmt.Errorf("age must be <= 150, got %d", age)
    }
    return nil
}
```

**REFACTOR** — extract constants, improve messages — tests still pass.

## TDD with Interface Injection

Design the interface in the test, then implement:

```go
// RED: test defines what the service needs
func TestNotificationService_SendsEmailOnOrder(t *testing.T) {
    mailer := &fakeMailer{}
    svc := NewNotificationService(mailer)

    svc.OrderPlaced(ctx, Order{ID: "123", CustomerEmail: "alice@example.com"})

    require.Len(t, mailer.sent, 1)
    assert.Equal(t, "alice@example.com", mailer.sent[0])
}

type fakeMailer struct{ sent []string }
func (f *fakeMailer) Send(_ context.Context, to string) error {
    f.sent = append(f.sent, to)
    return nil
}
```

The failing test tells you exactly what interface is needed.

## Anti-Patterns

### Testing unexported implementation details

```go
// BAD — tests internal structure
func TestService_usesCache(t *testing.T) {
    assert.NotNil(t, svc.cache)  // unexported field
}

// GOOD — tests observable behavior
func TestService_ReturnsCachedResult(t *testing.T) {
    first := svc.Fetch(ctx, "key")
    second := svc.Fetch(ctx, "key")
    assert.Equal(t, first, second)
}
```

### Constructing real dependencies in unit tests

```go
// BAD — slow, requires network/DB
db, _ := sql.Open("postgres", realDSN)
svc := NewOrderService(db)

// GOOD — inject fake, fast and isolated
store := &fakeOrderStore{}
svc := NewOrderService(store)
```

### Untyped fakes (accepting wrong calls silently)

```go
// Add compile-time interface check to every fake
var _ EmailSender = (*fakeEmailSender)(nil)
```

### Shared mutable state between subtests

Each subtest should be fully isolated. Fresh state per `t.Run`.

## When to Use TDD in Go

**Use TDD for**: Business logic, HTTP handlers, data transformations,
error handling paths, interface-driven components

**Consider alternatives for**: Exploratory prototypes, simple CRUD wrappers,
generated code

## Running Tests During TDD

```bash
go test -v -run TestValidateAge ./...    # Single test, verbose
go test ./...                            # All tests
go test -race ./...                      # With race detector
go test -race ./... && go vet ./...      # Pre-commit
```
