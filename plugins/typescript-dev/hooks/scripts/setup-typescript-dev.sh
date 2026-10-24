#!/bin/bash
set -euo pipefail

PLUGIN_DIR="$CLAUDE_PLUGIN_ROOT"
DEPLOYED=()

# Deploy npm/vitest permissions to .claude/settings.local.json (copy-if-not-exists)
if command -v node >/dev/null 2>&1; then
  TARGET=".claude/settings.local.json"
  SOURCE="$PLUGIN_DIR/settings/settings.local.json"
  if [ ! -f "$TARGET" ]; then
    mkdir -p .claude
    cp "$SOURCE" "$TARGET"
    DEPLOYED+=("settings: settings.local.json (npm/vitest permissions)")
  elif command -v jq >/dev/null 2>&1; then
    # Merge permissions.allow into an existing file instead of skipping it — a
    # copy-if-not-exists never reaches a workspace that already has the file.
    NEW_ALLOW=$(jq '.permissions.allow // []' "$SOURCE")
    MERGED=$(jq -c --argjson new "$NEW_ALLOW" '.permissions.allow = ((.permissions.allow // []) + $new | unique)' "$TARGET")
    if [ "$MERGED" != "$(jq -c '.' "$TARGET")" ]; then
      echo "$MERGED" | jq '.' > "$TARGET"
      DEPLOYED+=("settings: settings.local.json (npm/vitest permissions merged)")
    fi
  fi
fi

# Deploy testing rules to .claude/rules/testing.md (copy-if-not-exists)
if command -v node >/dev/null 2>&1; then
  TARGET=".claude/rules/testing.md"
  if [ ! -f "$TARGET" ]; then
    mkdir -p .claude/rules
    cp "$PLUGIN_DIR/scaffold/rules/testing.md" "$TARGET"
    DEPLOYED+=("rules: testing.md (vitest conventions)")
  fi
fi

# Report
if [ ${#DEPLOYED[@]} -gt 0 ]; then
  echo "# TypeScript Dev Setup"
  echo ""
  echo "Deployed ${#DEPLOYED[@]} file(s):"
  for item in "${DEPLOYED[@]}"; do
    echo "  - $item"
  done
fi
