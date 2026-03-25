# Go Testing Patterns Reference

## Table-Driven Tests

The canonical Go testing pattern. Each case is a struct; `t.Run()` creates
independent subtests that can be filtered with `-run`.

```go
tests := []struct {
    name    string
    input   string
    want    Result
    wantErr error
}{
    {"valid input", "hello", Result{OK: true}, nil},
    {"empty input", "", Result{}, ErrEmpty},
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got, err := Process(tt.input)
        if !errors.Is(err, tt.wantErr) {
            t.Fatalf("error = %v, want %v", err, tt.wantErr)
        }
        if got != tt.want {
            t.Errorf("got %v, want %v", got, tt.want)
        }
    })
}
```

## Parallel Tests

```go
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel() // Only when tests have no shared mutable state
        // ...
    })
}
```

Note: Go 1.22+ fixes loop variable capture. For pre-1.22: `tt := tt` before
`t.Parallel()`.

## Test Helpers

```go
func assertNoError(t *testing.T, err error) {
    t.Helper() // Error points to caller, not this function
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

## Fuzz Testing (Go 1.18+)

```go
func FuzzParseInput(f *testing.F) {
    f.Add("valid-seed")
    f.Fuzz(func(t *testing.T, s string) {
        _, _ = ParseInput(s) // Must not panic
    })
}
```

Run: `go test -fuzz=FuzzParseInput -fuzztime=30s`

## Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Process(input)
    }
}
```

Run: `go test -bench=. -benchmem ./...`

## Integration Tests (Build Tags)

```go
//go:build integration

package mypackage_test
```

Run: `go test -tags=integration ./...`

Keeps `go test ./...` fast for daily development.

## HTTP Testing

```go
func TestHandler(t *testing.T) {
    srv := httptest.NewServer(myHandler())
    defer srv.Close()

    resp, err := http.Get(srv.URL + "/api/v1/resource")
    // ...
}
```

No external mocking library needed for HTTP — use `net/http/httptest`.

## Mocking Strategy

- Accept interfaces, return structs
- Use `net/http/httptest` for HTTP
- Use `t.TempDir()` for filesystem
- Use `testcontainers-go` for real databases in integration tests
- Generate mocks with `gomock` or `testify/mock` when needed

## Coverage

```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out      # Summary
go tool cover -html=coverage.out      # Visual
```

Target 70-80% on critical paths. Coverage is a signal, not a target.

## Race Detector

```bash
go test -race ./...
```

Non-negotiable for concurrent code. Always enabled in CI.
