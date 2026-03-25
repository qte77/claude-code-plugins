# go-dev

Go implementation, testing, and code review skills with scaffold adapter for
the Ralph loop.

## Skills

| Skill | Trigger |
|-------|---------|
| `implementing-go` | Writing Go code, creating packages, implementing features |
| `testing-go` | Writing tests, TDD, table-driven tests, fuzz testing, benchmarks |
| `reviewing-go` | Code review for quality, security, idiomatic style |

## Scaffold Adapter

Provides Go-specific implementations of the Ralph loop adapter interface:

- `_scaffold_test()` — `go test -race -count=1 ./...`
- `_scaffold_lint()` — `golangci-lint run` (fallback: `go vet` + `gofmt`)
- `_scaffold_typecheck()` — `go vet ./...`
- `_scaffold_complexity()` — `gocyclo -over 15`
- `_scaffold_coverage()` — `go test -coverprofile=coverage.out ./...`
- `_scaffold_validate()` — `make validate` or lint+typecheck+test sequence

## CI Workflow Templates

Deployed to `.github/workflows/` when `.scaffold == "go"`:

- `go-test.yaml` — tests with race detector and coverage
- `golangci-lint.yaml` — linting via golangci-lint-action v6
- `govulncheck.yaml` — vulnerability scanning
- `dependabot.yaml` — automated Go module updates

## Settings

Grants Bash permissions for: `go build`, `go test`, `go vet`, `go mod`,
`go generate`, `golangci-lint`, `govulncheck`.
