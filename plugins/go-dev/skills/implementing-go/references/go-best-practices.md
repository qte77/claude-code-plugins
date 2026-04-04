---
title: Go Best Practices Reference
version: 1.0
applies-to: Agents and humans
purpose: Security-first Go coding standards with concurrency and error handling patterns
see-also: testing-strategy.md, tdd-best-practices.md
---

## Security (Non-Negotiable)

### Input Validation

Validate all external input at system boundaries:

```go
type CreateUserRequest struct {
    Email string `json:"email"`
    Age   int    `json:"age"`
}

func (r *CreateUserRequest) Validate() error {
    if r.Email == "" {
        return fmt.Errorf("email is required")
    }
    if r.Age < 0 || r.Age > 150 {
        return fmt.Errorf("age must be between 0 and 150, got %d", r.Age)
    }
    return nil
}
```

### SQL Injection Prevention

Always use parameterized queries:

```go
// GOOD
row := db.QueryRowContext(ctx, "SELECT id, name FROM users WHERE id = $1", userID)

// BAD — injection risk
row := db.QueryRow("SELECT id, name FROM users WHERE id = " + userID)
```

### Safe Deserialization

```go
dec := json.NewDecoder(r.Body)
dec.DisallowUnknownFields()
var req CreateUserRequest
if err := dec.Decode(&req); err != nil {
    return fmt.Errorf("invalid request body: %w", err)
}
```

### Secrets Management

```go
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    return fmt.Errorf("API_KEY environment variable is required")
}
```

Never hardcode credentials in source code.

## Error Handling

### Wrapping with fmt.Errorf + %w

```go
func loadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("loadConfig: read %s: %w", path, err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("loadConfig: parse %s: %w", path, err)
    }
    return &cfg, nil
}
```

### Sentinel Errors

```go
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

if errors.Is(err, ErrNotFound) {
    http.Error(w, "not found", http.StatusNotFound)
}
```

### Custom Error Types

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: %s — %s", e.Field, e.Message)
}

var ve *ValidationError
if errors.As(err, &ve) {
    log.Printf("field %s failed: %s", ve.Field, ve.Message)
}
```

Never ignore errors. When an error truly cannot occur, document why.

## Type System

### Interfaces

Define where the consumer needs them. Keep small (1-2 methods):

```go
type Reader interface {
    Read(ctx context.Context, id string) (*User, error)
}
```

### Type Assertions

Always use two-value form:

```go
if store, ok := repo.(CacheableStore); ok {
    store.Invalidate(id)
}
```

### Generics (Go 1.21+)

Use to eliminate repetitive collection functions:

```go
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}
```

Avoid generics for simple cases where concrete types suffice (YAGNI).

## Concurrency

### Goroutines and Context

Pass `context.Context` as the first parameter. Never store in a struct:

```go
func (s *Service) FetchUser(ctx context.Context, id string) (*User, error) {
    return s.db.QueryRowContext(ctx, "SELECT ...", id)
}
```

Always give goroutines a way to stop:

```go
func process(ctx context.Context, jobs <-chan Job) <-chan Result {
    out := make(chan Result)
    go func() {
        defer close(out)
        for j := range jobs {
            select {
            case <-ctx.Done():
                return
            case out <- doWork(j):
            }
        }
    }()
    return out
}
```

### sync Patterns

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()
```

Prefer channels for communication; mutexes for state protection.

## Logging (slog)

Use `log/slog` (stdlib, Go 1.21+):

```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("user created", "user_id", userID, "email", email)
logger.Error("database query failed", "err", err, "query", "SELECT users")
```

Never use `fmt.Println` or `log.Printf` for logging in production code.

## Package Organization

```text
myapp/
├── cmd/myapp/main.go     # Entry points only
├── internal/              # Business logic (compiler-enforced privacy)
│   ├── service/
│   └── store/
├── pkg/                   # Reusable packages (only if truly needed)
├── go.mod
└── go.sum
```

- `cmd/` — wires dependencies, exits on error
- `internal/` — default location; cannot be imported externally
- `pkg/` — only for stable, reusable APIs

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Ignoring errors `_ = f()` | Silent failures | Always handle or document |
| Storing `context.Context` in struct | Lifetime issues | Pass as function param |
| One-value type assertion | Panic on mismatch | Use `x, ok := v.(T)` |
| `fmt.Println` for logging | Unstructured | Use `slog` |
| Goroutine leak | Memory exhaustion | Use `ctx.Done()` or close channel |
| Hardcoded credentials | Security breach | Use `os.Getenv` |
| Concatenated SQL | Injection risk | Use parameterized queries |
| Large interfaces | Hard to mock/test | Split into 1-2 method interfaces |
| Missing `%w` in `fmt.Errorf` | Breaks `errors.Is/As` | Use `%w` for wrapping |
| Global mutable state in `init()` | Test interference | Use dependency injection |

## Pre-Commit Checklist

### Security
- [ ] No hardcoded credentials
- [ ] All user input validated at boundaries
- [ ] SQL queries use parameterized statements
- [ ] JSON decoder uses `DisallowUnknownFields()` for untrusted input

### Error Handling
- [ ] All errors handled or documented as ignored
- [ ] `fmt.Errorf("context: %w", err)` used for wrapping
- [ ] Sentinel errors for public APIs

### Concurrency
- [ ] Every goroutine has a stop signal
- [ ] `context.Context` passed as first param, not stored
- [ ] Shared state protected by mutex or channels

### Code Quality
- [ ] `slog` used for logging
- [ ] Dependencies injected via interfaces
- [ ] `go vet ./...` passes
- [ ] `golangci-lint run` passes
- [ ] Unit tests for new logic
