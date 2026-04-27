---
title: TDD Best Practices (Rust)
version: 1.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md
---

# TDD Best Practices

**Purpose**: Rust-specific TDD examples with cargo test, proptest, and mockall.

> Language-agnostic TDD principles (cycle, AAA, anti-patterns) are in
> the `tdd-core` plugin. This file extends those with Rust tooling.

## Red-Green-Refactor with cargo test

In Rust, the RED phase often starts with a **compilation error** — the
function does not exist yet. That is intentional. Write the test first,
let the compiler tell you what is missing.

## AAA Structure in Rust Tests

```rust
#[test]
fn test_order_calculator_sums_item_prices() {
    // ARRANGE
    let items = vec![Item { price: 10, qty: 2 }, Item { price: 5, qty: 1 }];
    let calculator = OrderCalculator::new();

    // ACT
    let total = calculator.total(&items);

    // ASSERT
    assert_eq!(total, 25);
}
```javascript

## Rust-Specific TDD: Newtype with Validation

**RED** — write the test, it won't compile:

```rust
#[test]
fn test_email_rejects_missing_at_sign() {
    let result = Email::parse("notanemail");
    assert!(result.is_err());
}
```

**GREEN** — minimal implementation:

```rust
pub struct Email(String);

impl Email {
    pub fn parse(s: &str) -> Result<Self, AppError> {
        if s.contains('@') {
            Ok(Email(s.to_owned()))
        } else {
            Err(AppError::InvalidInput("missing @".into()))
        }
    }
}
```javascript

**REFACTOR** — improve without breaking tests.

## Property-Based TDD

Start with a specific test, then generalize with proptest:

```rust
// Step 1 — specific TDD test
#[test]
fn test_discount_never_exceeds_original_price() {
    let price = Money::new(100);
    let discounted = apply_discount(price, 0.2);
    assert!(discounted <= price);
}

// Step 2 — generalize with proptest
proptest! {
    #[test]
    fn test_discount_always_lte_original(
        price in 1u64..1_000_000,
        rate in 0.0f64..=1.0,
    ) {
        let p = Money::new(price);
        prop_assert!(apply_discount(p, rate) <= p);
    }
}
```

## Anti-Patterns

### Testing implementation details

```rust
// BAD — tests internal structure
fn test_cache_uses_hashmap() {
    assert!(cache.inner.capacity() > 0);
}

// GOOD — tests observable behavior
fn test_cache_returns_stored_value() {
    cache.insert("key", "value");
    assert_eq!(cache.get("key"), Some("value"));
}
```javascript

### unwrap() masking failures

```rust
// BAD — unhelpful panic message
let user = service.get_user(id).unwrap();

// GOOD — descriptive failure
let user = service.get_user(id).expect("user should exist for valid id");
```

### Shared mutable state

Rust tests run in parallel. Shared state (`static Mutex`, env vars) causes flaky tests. Use dependency injection instead.

### Over-mocking your own code

Mock only external dependencies. Use real types for your own structs/services.

## When to Use TDD in Rust

**Use TDD for**: Business logic, error handling paths, async service logic,
parser/serializer correctness, trait implementations

**Consider alternatives for**: Simple data structs (compiler verifies derives),
FFI/unsafe (use property tests + sanitizers), exploratory prototypes

## Running Tests During TDD

```bash
cargo watch -x test                              # Watch mode
cargo test test_email_rejects_missing_at_sign     # Single test
cargo test -- --nocapture                         # Show output
cargo test && cargo clippy -- -D warnings         # Pre-commit
```text
