# Go Review Checklist Reference

## Recommended golangci-lint Linters

```yaml
version: "2"
linters:
  enable:
    - errcheck       # Unchecked errors
    - govet          # go vet checks
    - staticcheck    # Deep static analysis
    - gosimple       # Code simplification
    - ineffassign    # Ineffectual assignments
    - unused         # Unused code
    - revive         # Style linting (replaces golint)
    - gosec          # Security checks
    - goimports      # Import formatting
    - misspell       # Spelling in comments/strings
    - gocyclo        # Cyclomatic complexity
    - bodyclose      # HTTP response body close
    - errname        # Error naming (Err prefix, Error suffix)
    - errorlint      # Correct errors.Is/As usage
    - wrapcheck      # External errors wrapped
```

## Common Anti-Patterns

| Anti-Pattern | Correct Alternative |
|---|---|
| `err == ErrNotFound` with wrapped errors | `errors.Is(err, ErrNotFound)` |
| `fmt.Errorf("ctx: %v", err)` when unwrap needed | `fmt.Errorf("ctx: %w", err)` |
| Log and continue on error inside function | Return error, let caller decide |
| `math/rand` for tokens/nonces | `crypto/rand` |
| MD5/SHA-1 for security hashes | SHA-256+ for integrity, bcrypt/Argon2id for passwords |
| `utils`, `helpers`, `common` packages | Descriptive domain-specific names |
| Bare `go test ./...` in CI | `go test -race ./...` |
| Storing `context.Context` in struct | Pass as first function parameter |
| Giant interfaces (5+ methods) | Small interfaces (1-2 methods) |
| `panic` for normal error flow | Return error values |

## Security Review Points

### SSRF Prevention
- URL scheme: only `http`/`https`
- Resolved IP: block private ranges (127.x, 10.x, 172.16-31.x, 192.168.x, 169.254.x)
- Domain allowlist over blocklist
- No automatic redirect following without re-validation

### Crypto
- Passwords: `bcrypt` cost >= 12 or Argon2id
- Random: `crypto/rand` only
- TLS: minimum 1.2, prefer 1.3, AEAD cipher suites only
- Never hardcode secrets

### Input Validation
- Parameterized SQL queries only
- File paths: reject `..` and URL-encoded variants
- HTML: `html/template` not `text/template`

## Module Hygiene

- `go.mod` version matches actual minimum Go requirement
- `go.sum` committed alongside `go.mod`
- `go mod tidy` produces no diff
- No `replace` directives in published libraries
- `govulncheck ./...` passes
