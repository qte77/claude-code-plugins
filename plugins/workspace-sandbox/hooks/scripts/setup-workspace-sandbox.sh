#!/bin/bash
set -euo pipefail
# Deploy workspace rules and sandbox settings (copy-if-not-exists)

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

# 2. Sandbox .gitignore → project root (hides bwrap phantom files)
if [ ! -f ".gitignore" ]; then
  cp "$PLUGIN_DIR/settings/.gitignore" ".gitignore"
  DEPLOYED+=("gitignore: .gitignore (sandbox phantoms)")
fi

# 3. Sandbox settings → .claude/settings.json (only if missing)
if [ ! -f ".claude/settings.json" ]; then
  cp "$PLUGIN_DIR/settings/settings-sandbox.json" ".claude/settings.json"
  DEPLOYED+=("settings: settings.json (sandbox)")
fi

# 4. Report
if [ ${#DEPLOYED[@]} -gt 0 ]; then
  echo "# Workspace Setup (Sandbox)"
  echo ""
  echo "Deployed ${#DEPLOYED[@]} file(s):"
  for item in "${DEPLOYED[@]}"; do
    echo "  - $item"
  done
fi
