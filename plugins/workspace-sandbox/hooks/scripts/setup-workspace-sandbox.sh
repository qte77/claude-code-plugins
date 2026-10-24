#!/bin/bash
set -euo pipefail
# Deploy workspace rules, scripts, governance, and sandbox settings (copy-if-not-exists)
# Self-contained — all CC-specific files bundled in plugin

PLUGIN_DIR="$CLAUDE_PLUGIN_ROOT"
DEPLOYED=()

# 1. Rules → .claude/rules/
mkdir -p .claude/rules
for rule in "$PLUGIN_DIR/rules/"*.md; do
  [ -f "$rule" ] || continue
  target=".claude/rules/$(basename "$rule")"
  if [ ! -f "$target" ]; then
    cp "$rule" "$target"
    DEPLOYED+=("rule: $(basename "$rule")")
  fi
done

# 2. Statusline → .claude/scripts/
mkdir -p .claude/scripts
if [ ! -f ".claude/scripts/statusline.sh" ]; then
  cp "$PLUGIN_DIR/scripts/statusline.sh" ".claude/scripts/statusline.sh"
  DEPLOYED+=("script: statusline.sh")
fi

# 3. Sandbox .gitignore → project root (hides bwrap phantom files)
if [ ! -f ".gitignore" ]; then
  cp "$PLUGIN_DIR/settings/.gitignore" ".gitignore"
  DEPLOYED+=("gitignore: .gitignore (sandbox phantoms)")
fi

# 4. Sandbox settings → .claude/settings.json (copy-if-not-exists; merge permissions.allow if present)
SETTINGS_TARGET=".claude/settings.json"
SETTINGS_SOURCE="$PLUGIN_DIR/settings/settings-sandbox.json"
if [ ! -f "$SETTINGS_TARGET" ]; then
  cp "$SETTINGS_SOURCE" "$SETTINGS_TARGET"
  DEPLOYED+=("settings: settings.json (sandbox)")
elif command -v jq >/dev/null 2>&1; then
  # Merge permissions.allow into an existing file instead of skipping it — a
  # copy-if-not-exists never reaches a workspace that already has the file.
  NEW_ALLOW=$(jq '.permissions.allow // []' "$SETTINGS_SOURCE")
  MERGED=$(jq -c --argjson new "$NEW_ALLOW" '.permissions.allow = ((.permissions.allow // []) + $new | unique)' "$SETTINGS_TARGET")
  if [ "$MERGED" != "$(jq -c '.' "$SETTINGS_TARGET")" ]; then
    echo "$MERGED" | jq '.' > "$SETTINGS_TARGET"
    DEPLOYED+=("settings: settings.json (sandbox permissions merged)")
  fi
fi

# 5. Governance files → project root
for file in "$PLUGIN_DIR/governance/"*.md; do
  [ -f "$file" ] || continue
  target="$(basename "$file")"
  if [ ! -f "$target" ]; then
    cp "$file" "$target"
    DEPLOYED+=("governance: $target")
  fi
done

# 6. Report
if [ ${#DEPLOYED[@]} -gt 0 ]; then
  echo "# Workspace Setup (Sandbox)"
  echo ""
  echo "Deployed ${#DEPLOYED[@]} file(s):"
  for item in "${DEPLOYED[@]}"; do
    echo "  - $item"
  done
fi
