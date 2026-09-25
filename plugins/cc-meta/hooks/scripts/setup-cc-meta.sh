#!/bin/bash
set -euo pipefail
# Deploy MEMORY.md seed template (copy-if-not-exists)

PLUGIN_DIR="$CLAUDE_PLUGIN_ROOT"
DEPLOYED=()

# The target is relative to the session cwd, so inside a git repo this would drop an
# untracked MEMORY.md into the working tree (#155). Claude Code's own project memory lives
# elsewhere and uses a different format, so skip rather than redirect. Retirement: #201/#158.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# MEMORY.md seed template
TARGET="MEMORY.md"
if [ ! -f "$TARGET" ]; then
  cp "$PLUGIN_DIR/examples/memory/MEMORY.md" "$TARGET"
  DEPLOYED+=("memory: MEMORY.md (seed template)")
fi

# Report
if [ ${#DEPLOYED[@]} -gt 0 ]; then
  echo "# CC Meta Setup"
  echo ""
  echo "Deployed ${#DEPLOYED[@]} file(s):"
  for item in "${DEPLOYED[@]}"; do
    echo "  - $item"
  done
fi
