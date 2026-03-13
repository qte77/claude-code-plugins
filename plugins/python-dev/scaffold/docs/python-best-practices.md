# Python Best Practices

## Imports

- Use absolute imports: `from src.module import Class`
- Group imports: stdlib, third-party, local (enforced by ruff isort)

## Type Hints

- Full type hints on public functions
- Use `str | None` syntax (Python 3.10+)
- Run `make type_check` to verify

## Models

- Use Pydantic for data validation
- Define models in `src/<app>/models/`

## Docstrings

- Google-style format for all public functions
- Include Args, Returns, Raises sections

## Testing

- pytest with arrange/act/assert structure
- Mock external dependencies with `@patch`
- Use `tmp_path` for filesystem isolation
- Coverage threshold: 70% (configured in pyproject.toml)

## Style

- Max line length: 100 (configured in ruff)
- Format with `make ruff` before committing
