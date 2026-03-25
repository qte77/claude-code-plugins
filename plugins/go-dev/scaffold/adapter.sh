#!/bin/bash
#
# Go scaffold adapter for Ralph Loop
# Deployed to .scaffolds/go.sh by go-dev plugin hook.
# Provides Go-specific implementations of adapter_* interface.
#
# Tools: go, golangci-lint, gocyclo (optional)
#

# Run tests. Output includes "FAIL" lines for baseline comparison.
_scaffold_test() {
    if [ $# -gt 0 ]; then
        go test -race -count=1 -v "$@"
    else
        go test -race -count=1 ./...
    fi
}

# Lint source files with golangci-lint (fallback to go vet + gofmt).
_scaffold_lint() {
    if command -v golangci-lint >/dev/null 2>&1; then
        if [ $# -gt 0 ]; then
            golangci-lint run "$@"
        else
            golangci-lint run ./...
        fi
    else
        go vet ./...
        gofmt -l .
    fi
}

# Static type/correctness checking with go vet.
_scaffold_typecheck() {
    go vet ./...
}

# Cyclomatic complexity analysis (requires gocyclo).
_scaffold_complexity() {
    if command -v gocyclo >/dev/null 2>&1; then
        if [ $# -gt 0 ]; then
            gocyclo -over 15 "$@"
        else
            gocyclo -over 15 .
        fi
    else
        echo "gocyclo not installed, skipping complexity check"
    fi
}

# Run tests with coverage. Output includes coverage percentage.
_scaffold_coverage() {
    go test -coverprofile=coverage.out ./...
    go tool cover -func=coverage.out
}

# Full validation sequence.
_scaffold_validate() {
    if [ -f Makefile ] && make -n validate >/dev/null 2>&1; then
        make validate
    else
        _scaffold_lint
        _scaffold_typecheck
        _scaffold_test
    fi
}

# Extract function/type signatures from a Go file.
_scaffold_signatures() {
    local filepath="$1"
    grep -nE "^(func |type |var |const )" "$filepath" 2>/dev/null || true
}

# Glob pattern for Go source files.
_scaffold_file_pattern() {
    echo "*.go"
}

# Set up Go environment.
_scaffold_env_setup() {
    export CGO_ENABLED=0
}

# Generate Go-specific application docs.
_scaffold_app_docs() {
    local src_dir="$1"
    local app_name
    app_name=$(basename "$src_dir")
    local example_path="$src_dir/example_test.go"

    cat > "$example_path" <<GOEOF
package ${app_name}_test

import (
    "fmt"
)

func Example() {
    // TODO: Add your example usage here
    fmt.Println("Example: Running $app_name")
    // Output: Example: Running $app_name
}
GOEOF
}
