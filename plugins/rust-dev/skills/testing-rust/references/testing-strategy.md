---
title: Testing Strategy (Rust)
version: 1.0
applies-to: Agents and humans
purpose: Rust-specific testing tools and when to use each
see-also: tdd-best-practices.md
---

# Testing Strategy

**Purpose**: Rust-specific testing tools and when to use each.

> Language-agnostic testing strategy (what to test, mocking, organization)
> is in the `tdd-core` plugin. This file extends it with Rust tools
> (cargo test, proptest, insta, mockall).

## Core Principles

| Principle | Testing Application |
|-----------|---------------------|
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test compiler or standard library behavior |

## What to Test

**High-Value** (test these):

1. Business logic — algorithms, calculations, decision rules
2. Error paths — `Err` variants, `None`, boundary conditions
3. Integration points — serialization contracts, external services
4. Concurrency invariants — data races, ordering guarantees

**Low-Value** (avoid these):

1. Language mechanics — `Vec::push` works, `Option::unwrap` panics
2. Trivial getters/setters — unless they encode business rules
3. Derives — `#[derive(Debug, Clone)]` is compiler-verified
4. Default zero values — unless defaults encode business invariants

### Patterns to Remove

| Pattern | Why Remove | Example |
|---------|------------|---------|
| Type checks | Type system verifies | `assert!(matches!(x, MyEnum::Variant))` for existence |
| Existence tests | Compiler ensures | `test_module_compiles()` |
| Derive behavior | Compiler handles | testing Debug output of derives |
| Over-granular | Consolidate | 6 separate tests for one struct's fields |

**Rule**: If the test wouldn't catch a real bug, remove it.

## Tool Selection Guide

| Tool | Question it answers | Use for |
|------|---------------------|---------|
| **`#[test]`** | Does this logic produce the right result? | TDD, unit, integration |
| **proptest** | Does this hold for ALL inputs? | Edge cases, parsers, math |
| **insta** | Does this output still look the same? | Serialization contracts, regressions |
| **mockall** | Does this behave correctly in isolation? | Unit tests with external deps |

**One-line rule**: `#[test]` for **logic**, proptest for **properties**, insta for **structure**, mockall for **isolation**.

## Unit Tests (Inline `mod tests`)

```rust
pub fn add(a: i32, b: i32) -> i32 { a + b }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_positive_numbers() {
        assert_eq!(add(2, 3), 5);
    }
}
```text

`#[cfg(test)]` excludes test code from release builds.

## Integration Tests (`tests/` Directory)

```text
src/
└── lib.rs
tests/
├── order_service_test.rs
└── payment_integration_test.rs
```

Integration tests have access only to the public API.

## Property-Based Testing with proptest

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_clamp_always_in_range(value in any::<i32>(), min in -1000..1000i32) {
        let max = min + 100;
        let result = clamp(value, min, max);
        prop_assert!(result >= min);
        prop_assert!(result <= max);
    }
}
```javascript

## Snapshot Testing with insta

```rust
use insta::assert_debug_snapshot;

#[test]
fn test_user_serialization() {
    let user = User { id: 1, name: "Alice".into(), role: Role::Admin };
    assert_debug_snapshot!(user);
}
```

Commands: `cargo insta review`, `cargo insta accept`

**When to use**: complex struct output, serialization regressions
**When NOT to use**: TDD Red-Green-Refactor, proptest, simple scalars

## Mocking with mockall

```rust
use mockall::{automock, predicate::*};

#[automock]
trait UserRepository {
    fn find(&self, id: u64) -> Option<User>;
}

#[test]
fn test_user_service_returns_not_found() {
    let mut mock = MockUserRepository::new();
    mock.expect_find()
        .with(eq(99u64))
        .times(1)
        .returning(|_| None);

    let service = UserService::new(mock);
    assert!(service.get_user(99).is_err());
}
```text

Always set `.times()` — unverified calls pass silently without it.

**When to mock**: external APIs, non-deterministic deps, error scenarios
**When NOT to mock**: your own structs, in-memory alternatives exist

## Mocking Strategy

- Mock external dependencies (APIs, network, filesystem)
- Mock non-deterministic values (time, random, UUIDs)
- Use real services when in-memory alternatives exist
- Always set `.times()` and `.with()` on mockall expectations
- Never mock internal functions in the same module

## Test Organization

```text
src/
└── **/*.rs         (inline mod tests for each module)
tests/
├── integration/    (full stack: DB, network)
└── common/         (shared helpers, fixtures)
```

## Naming Conventions

**Format**: `test_{module}_{component}_{behavior}`

```rust
test_order_calculator_sums_items()
test_user_parser_rejects_empty_email()
test_score_always_in_bounds()  // property test
```text

## Decision Checklist

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **compiler/library** (skip)?
4. Which tool: `#[test]` (default), proptest (any input), insta (structure), mockall (isolation)

## References

- TDD practices: `tdd-best-practices.md`
- [proptest Book](https://proptest-rs.github.io/proptest/intro.html)
- [insta Documentation](https://insta.rs/)
- [mockall Documentation](https://docs.rs/mockall/)
