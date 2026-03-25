---
paths:
  - "**/*_test.go"
---

# Go Testing Rules

- Table-driven tests with descriptive names in `t.Run()`
- Compare errors with `errors.Is`/`errors.As`, not `==`
- Use `t.Helper()` in test helper functions
- Use `t.Parallel()` only when tests have no shared mutable state
- Use `t.TempDir()` for filesystem isolation, `testdata/` for fixtures
- Always run with `-race` flag in CI
