---
title: Rust Best Practices Reference
version: 1.0
applies-to: Agents and humans
purpose: Security-first Rust coding standards with type safety and ownership patterns
see-also: testing-strategy.md, tdd-best-practices.md
---

# Rust Best Practices

## Security (Non-Negotiable)

### No Unsafe Unless Justified

`unsafe` bypasses the borrow checker — every block needs a `// SAFETY:` comment:

```rust
// SAFETY: `ptr` is non-null and exclusively owned for the duration of this call
unsafe { std::ptr::write(ptr, value) };
```yaml

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
```text

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
```text

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
```javascript

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
```text

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
```text

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
```text

Never use `println!` for logging in production code.

## Imports and Visibility

```rust
// Order: std -> external crates -> crate-internal
use std::collections::HashMap;
use anyhow::{Context, Result};
use crate::config::AppConfig;
```

Prefer `pub(crate)` over `pub` for types used only within the crate.

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
