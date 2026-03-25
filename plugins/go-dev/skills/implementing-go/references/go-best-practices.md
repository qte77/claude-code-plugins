# Go Best Practices Reference

## Naming

- **Packages**: short, lowercase, singular, no underscores (`user`, `auth`, `http`)
- **Exported**: PascalCase (`ValidateUser`, `ErrNotFound`)
- **Unexported**: camelCase (`writeToDB`, `maxRetries`)
- **Acronyms**: all caps (`userID`, `httpClient`, `parseURL`)
- **Receivers**: 1-2 letters matching type (`u` for `User`, `c` for `Client`)
- **Interfaces**: single-method with `-er` suffix (`Reader`, `Writer`)
- **Constants**: PascalCase exported, camelCase unexported (never `ALL_CAPS`)
- **Files**: lowercase with underscores (`user_service.go`)
- **Errors**: prefix `Err` for sentinels, suffix `Error` for types

## Error Handling

| Situation | Pattern |
|-----------|---------|
| Caller must branch on condition | Sentinel error + `errors.Is` |
| Error needs structured data | Custom type + `errors.As` |
| Adding context at boundary | `fmt.Errorf("context: %w", err)` |
| Simple message, no inspection | `errors.New(...)` |

Rules:
- Always use `%w` (not `%v`) when callers need `errors.Is`/`errors.As`
- Wrap at abstraction boundaries, not within the same layer
- Error strings: lowercase, no trailing punctuation
- Never discard errors with `_` in production code
- Never `panic` for normal error flow

## Project Layout

```
cmd/           # Thin main.go per binary (~50 lines max)
internal/      # Private packages (compiler-enforced)
pkg/           # Public reusable packages (deliberate commitment)
api/           # OpenAPI specs, protobuf definitions
testdata/      # Test fixtures (ignored by go build)
```

Dependency direction: `cmd/` → `internal/` → `pkg/`

## Context

- `context.Context` is always the first parameter
- Variable name is always `ctx`
- Never store context in a struct

## Style

- `gofmt` is non-negotiable; prefer `gofumpt` for stricter formatting
- Early returns (guard clauses) over nested `if/else`
- `goimports` for import grouping: stdlib, then third-party
- Comments explain *why*, not *what*
- Exported identifiers must have doc comments starting with the identifier name

## Security

- Passwords: `bcrypt` (cost >= 12) or Argon2id
- Random values: `crypto/rand`, never `math/rand`
- TLS: minimum 1.2, prefer 1.3
- SSRF: validate URLs, block private IP ranges, allowlist domains
- SQL: parameterized queries only
