---
title: Rust Best Practices Reference
version: 1.0
applies-to: Agents and humans
purpose: Security-first Rust coding standards with type safety and ownership patterns
see-also: testing-strategy.md, tdd-best-practices.md
---

## Security (Non-Negotiable)

### No Unsafe Unless Justified

`unsafe` bypasses the borrow checker — every block needs a `// SAFETY:` comment:

```rust
// SAFETY: `ptr` is non-null and exclusively owned for the duration of this call
unsafe { std::ptr::write(ptr, value) };
```

Prefer safe abstractions (`Vec`, `Box`, `Arc`) over raw pointers. Run `cargo clippy` and `cargo audit` on every build.

### Secrets Management

```rust
use std::env;

struct AppConfig {
    api_key: String,
    db_url: String,
}

impl AppConfig {
    pub fn from_env() -> Result<Self, AppError> {
        Ok(Self {
            api_key: env::var("API_KEY").map_err(|_| AppError::MissingEnv("API_KEY"))?,
            db_url: env::var("DATABASE_URL").map_err(|_| AppError::MissingEnv("DATABASE_URL"))?,
        })
    }
}
```

Never hardcode credentials in source code.

### Input Validation

Validate all external input at system boundaries using strong types:

```rust
use std::str::FromStr;

struct Email(String);

impl FromStr for Email {
    type Err = AppError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.contains('@') && s.len() <= 254 {
            Ok(Email(s.to_owned()))
        } else {
            Err(AppError::InvalidInput("invalid email".into()))
        }
    }
}
```

## Type System

### Newtype Pattern

Wrap primitives to enforce domain invariants at compile time:

```rust
struct UserId(u64);
struct OrderId(u64);

// Compiler rejects: process_order(user_id) when order_id expected
fn process_order(id: OrderId) -> Result<(), AppError> { ... }
```

### Enums for State Machines

Model exclusive states as enums — the compiler enforces exhaustive handling:

```rust
enum ConnectionState {
    Disconnected,
    Connecting { host: String, port: u16 },
    Connected { stream: TcpStream },
    Failed { reason: String },
}
```

### Option and Result Instead of Null/Exceptions

```rust
fn find_user(id: UserId) -> Option<User> { ... }
fn parse_config(path: &Path) -> Result<Config, AppError> { ... }
```

## Error Handling

### thiserror for Libraries

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO operation failed")]
    Io(#[from] std::io::Error),

    #[error("failed to parse config: {0}")]
    Parse(String),

    #[error("missing environment variable: {0}")]
    MissingEnv(&'static str),

    #[error("invalid input: {0}")]
    InvalidInput(String),
}
```

### anyhow for Binaries

```rust
use anyhow::{Context, Result};

fn run() -> Result<()> {
    let config = load_config(Path::new("config.toml"))
        .context("failed to load application config")?;
    start_server(config).context("server startup failed")?;
    Ok(())
}
```

Use `thiserror` in library crates (callers match variants); `anyhow` in binary crates (errors reported, not matched).

## Ownership and Borrowing

```rust
// Borrow when you only need to read
fn display_user(user: &User) { println!("{}", user.name); }

// Take ownership when you need to store or consume
fn store_user(user: User) { self.users.push(user); }

// Clone only when ownership transfer is genuinely needed
let owned = user.name.clone();
spawn(async move { use_owned(owned).await });
```

## Traits

```rust
// Generics — monomorphized, zero runtime overhead
fn process<T: DataSource>(source: T) -> Result<Data, AppError> { ... }

// Trait objects — dynamic dispatch, heterogeneous collections
fn process(source: &dyn DataSource) -> Result<Data, AppError> { ... }
```

Use generics by default; `dyn Trait` when you need runtime polymorphism.

## Async (Tokio)

### Concurrent Execution

```rust
use tokio::task::JoinSet;

let mut set = JoinSet::new();
for item in items {
    set.spawn(async move { process(item).await });
}
while let Some(res) = set.join_next().await {
    handle(res?);
}
```

### Timeout Handling

```rust
use tokio::time::{timeout, Duration};

async fn fetch_with_timeout(url: &str) -> Result<Response, AppError> {
    timeout(Duration::from_secs(30), fetch(url))
        .await
        .map_err(|_| AppError::Timeout)?
        .map_err(AppError::Io)
}
```

CPU-bound work must use `spawn_blocking`, not run directly in async fn.

## Logging (tracing)

```rust
use tracing::{info, warn, error, instrument};

#[instrument(skip(password), fields(user_id = %user.id))]
async fn login(user: &User, password: &str) -> Result<Token, AppError> {
    info!("login attempt");
    let token = authenticate(user, password).await?;
    info!(token_expiry = %token.expires_at, "login successful");
    Ok(token)
}
```

Never use `println!` for logging in production code.

## Imports and Visibility

```rust
// Order: std -> external crates -> crate-internal
use std::collections::HashMap;
use anyhow::{Context, Result};
use crate::config::AppConfig;
```

Prefer `pub(crate)` over `pub` for types used only within the crate.

## Lints in the Manifest

Set lint levels once in `Cargo.toml` (`[lints]`, or `[workspace.lints]` plus `lints.workspace = true`)
instead of attributes in every crate root. A strict set for code that must not crash:

```toml
[lints.rust]
unsafe_code = "deny"      # "forbid" only if the crate has no FFI or wasm exports

[lints.clippy]
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
```

Tests may opt out with `#![cfg_attr(test, allow(clippy::unwrap_used))]`. Run
`cargo clippy --all-targets -- -D warnings` and `cargo fmt --check` in CI, and keep `rustfmt.toml` and
`clippy.toml` in the repo root so editors and CI agree.

## Hostile Input

Treat file, network and parameter input as hostile: use `get()` over indexing, clamp sizes, bound
recursion and loops, and return errors instead of panicking. Keep one test that feeds junk (empty,
huge, malformed, boundary values) to every public entry point and asserts "no panic", and add a
regression test for every crash fixed. For parsers and replay formats, add a fuzz target
(`cargo fuzz`) once the format has real users.

## Dependencies

Run `cargo audit` (RustSec advisories). For a repo-level policy consider `cargo deny`: an allowed
licence list, `unknown-registry = "deny"`, `unknown-git = "deny"`, and git sources pinned by
revision. Commit `Cargo.lock` for binaries and for anything that ships a build artifact. Add these
checks when the first dependency arrives, not before.

## WebAssembly and Determinism

For a simulation that must give identical results on every engine, native and in the browser:

- Keep replayed state integer-only (fixed point). If floats are unavoidable, avoid threads and
  relaxed SIMD and canonicalise NaNs; the Rust Reference does not specify NaN bit patterns or
  cross-platform float results, so do not assume them.
- Never iterate a `HashMap`/`HashSet` in simulation code (order varies); use `BTreeMap` or a sorted `Vec`.
- Seed one explicit RNG per simulation; never read the clock or OS entropy inside a step.
- Prove it with one golden result (a hash after N seeded steps) checked by both the native Rust
  test and a test that runs the built `.wasm`.
- `u64`/`i64` arguments and results cross to JavaScript as `BigInt`, and a `u64` result arrives
  signed unless reinterpreted (`BigInt.asUintN(64, x)`). Test at least one value above `i64::MAX`.
- Exports use `#[unsafe(no_mangle)]` in edition 2024, and the `unsafe_code` lint flags that
  attribute (checked with `deny`). Use `deny` and allow it on the small exports module only; `forbid`
  cannot be overridden.
- The Rust and WebAssembly book is no longer maintained (its working group was sunset); prefer
  current `wasm-bindgen` and `wasm32-unknown-unknown` documentation and verify tool versions.

## Canonical Sources

| Topic | Source |
|---|---|
| API design | Rust API Guidelines (rust-lang.github.io/api-guidelines) |
| Formatting | Rust Style Guide (doc.rust-lang.org/style-guide) |
| Lints | Clippy book (doc.rust-lang.org/clippy) and the Cargo `[lints]` reference |
| Unsafe | The Rustonomicon (doc.rust-lang.org/nomicon; self-described as incomplete) |
| Performance | The Rust Performance Book (nnethercote.github.io/perf-book) |
| Dependencies | RustSec advisory database (rustsec.org) and cargo-deny docs |
| Fuzzing | Rust Fuzz Book (rust-fuzz.github.io/book) |
| Broad pragmatic guidance | Microsoft Pragmatic Rust Guidelines (microsoft.github.io/rust-guidelines) |

Link these; do not paste their text into a project.

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Hardcoded secrets | Security breach | Load via `env::var()` |
| `unwrap()` in production | Panic at runtime | Use `?` or handle explicitly |
| Unnecessary `.clone()` | Performance regression | Borrow instead (`&T`) |
| `unsafe` without `// SAFETY:` | Unsound code | Always document the invariant |
| `Box<dyn Error>` in library | Callers can't match | Use `thiserror` enum |
| `anyhow` in library crate | Opaque errors | Reserve for binaries |
| Blocking in async context | Stalls runtime | Use `spawn_blocking` |
| `println!` for logging | No structured output | Use `tracing` |
| Over-public API | Semver breakage risk | Use `pub(crate)` |

## Pre-Commit Checklist

### Security

- [ ] No hardcoded secrets or credentials
- [ ] All external input validated at boundaries
- [ ] Every `unsafe` block has `// SAFETY:` comment
- [ ] `cargo audit` passes
- [ ] Junk-input test covers every public entry point (no panics)
- [ ] Deterministic code: no `HashMap` iteration, clock or OS entropy; golden hash checked native and in wasm

### Type Safety

- [ ] Newtypes used for domain IDs and values
- [ ] `Option`/`Result` used, no sentinel values
- [ ] `thiserror` (library) or `anyhow` (binary) for errors

### Code Quality

- [ ] No `unwrap()`/`expect()` in production paths
- [ ] `?` used for error propagation
- [ ] No unnecessary `.clone()`
- [ ] `pub(crate)` for crate-internal types
- [ ] `tracing` used for logging

### Testing and Validation

- [ ] Unit tests for new logic
- [ ] `cargo test` passes
- [ ] `cargo clippy -- -D warnings` passes
- [ ] `cargo fmt --check` passes
