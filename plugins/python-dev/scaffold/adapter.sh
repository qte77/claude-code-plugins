#!/bin/bash
#
# Python scaffold adapter for Ralph Loop
# Deployed to .scaffolds/python.sh by python-dev plugin hook.
# Provides Python-specific implementations of adapter_* interface.
#
# Tools: uv, ruff, pyright, pytest, complexipy
# Signature extraction: Python AST via extract_signatures.py
#

# Locate extract_signatures.py (deployed alongside this adapter)
_PYTHON_EXTRACT_SIGS="$(dirname "${BASH_SOURCE[0]}")/extract_signatures.py"

# Run tests. Output includes "FAILED <test_name>" lines for baseline comparison.
_scaffold_test() {
    if [ $# -gt 0 ]; then
        uv run pytest --tb=short -q "$@"
    else
        uv run pytest --tb=no -q
    fi
}

# Format + lint source files with ruff.
_scaffold_lint() {
    if [ $# -gt 0 ]; then
        uv run ruff format "$@"
        uv run ruff check --fix "$@"
    else
        uv run ruff format --exclude tests
        uv run ruff check --fix --exclude tests
    fi
}

# Static type checking with pyright.
_scaffold_typecheck() {
    uv run pyright
}

# Cognitive complexity analysis with complexipy.
_scaffold_complexity() {
    if [ $# -gt 0 ]; then
        uv run complexipy --max-complexity 10 "$@"
    else
        uv run complexipy
    fi
}

# Run tests with coverage. Output includes "TOTAL ... XX%" line.
_scaffold_coverage() {
    uv run pytest --cov --tb=no -q
}

# Full validation sequence.
_scaffold_validate() {
    make validate
}

# Extract function/class signatures from a Python file using AST.
_scaffold_signatures() {
    local filepath="$1"
    if [ -f "$_PYTHON_EXTRACT_SIGS" ]; then
        python3 "$_PYTHON_EXTRACT_SIGS" "$filepath"
    else
        # Fallback: regex-based extraction
        grep -nE "^(class |def |    def |async def )" "$filepath" 2>/dev/null || true
    fi
}

# Glob pattern for Python source files.
_scaffold_file_pattern() {
    echo "*.py"
}

# Set up Python environment (PYTHONPATH for src/ layout).
_scaffold_env_setup() {
    export PYTHONPATH="$(pwd)/src:${PYTHONPATH:-}"
}

# Generate Python-specific application docs.
_scaffold_app_docs() {
    local src_dir="$1"
    local app_name
    app_name=$(basename "$src_dir")
    local example_path="$src_dir/example.py"

    cat > "$example_path" <<PYEOF
"""Minimal viable example demonstrating how to use this application."""

import $app_name


def main():
    """Run the application example."""
    # TODO: Add your example usage here
    print("Example: Running $app_name")


if __name__ == "__main__":
    main()
PYEOF
}
