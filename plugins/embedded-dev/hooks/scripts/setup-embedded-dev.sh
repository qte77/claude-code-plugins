#!/bin/sh
set -eu

PLUGIN_DIR="$CLAUDE_PLUGIN_ROOT"
SCAFFOLD_DIR="$PLUGIN_DIR/scaffold"
deployed=0

# Deploy embedded permissions to .claude/settings.local.json (copy-if-not-exists)
if command -v gcc >/dev/null 2>&1; then
  TARGET=".claude/settings.local.json"
  if [ ! -f "$TARGET" ]; then
    mkdir -p .claude
    cp "$PLUGIN_DIR/settings/settings.local.json" "$TARGET"
    deployed=$((deployed + 1))
  fi
fi

# Deploy scaffold adapter (copy-if-not-exists)
if [ -f ".scaffold" ] && [ "$(cat .scaffold 2>/dev/null)" = "embedded" ]; then
  # Adapter script for Ralph Loop
  mkdir -p .scaffolds
  if [ ! -f ".scaffolds/embedded.sh" ]; then
    cp "$SCAFFOLD_DIR/adapter.sh" ".scaffolds/embedded.sh"
    deployed=$((deployed + 1))
  fi

  # Testing rule (copy-if-not-exists)
  if [ -d "$SCAFFOLD_DIR/rules" ]; then
    mkdir -p .claude/rules
    for rule_file in "$SCAFFOLD_DIR/rules/"*; do
      [ -f "$rule_file" ] || continue
      local_name=".claude/rules/$(basename "$rule_file")"
      if [ ! -f "$local_name" ]; then
        cp "$rule_file" "$local_name"
        deployed=$((deployed + 1))
      fi
    done
  fi
fi

# Report
if [ "$deployed" -gt 0 ]; then
  echo "# Embedded Dev Setup"
  echo ""
  echo "Deployed $deployed file(s) (settings + scaffold adapter)"
fi
