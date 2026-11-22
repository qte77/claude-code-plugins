#!/bin/bash
set -euo pipefail
# Deploy workspace rules, scripts, governance, and sandbox settings (copy-if-not-exists)
# Self-contained — all CC-specific files bundled in plugin

PLUGIN_DIR="$CLAUDE_PLUGIN_ROOT"
DEPLOYED=()
WARNINGS=()

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
tracked() { git ls-files --error-unmatch "$1" >/dev/null 2>&1; }
if [ ! -f "$SETTINGS_TARGET" ]; then
  if tracked "$SETTINGS_TARGET"; then
    WARNINGS+=("settings: $SETTINGS_TARGET is tracked but deleted in the working tree; not recreated")
  else
    cp "$SETTINGS_SOURCE" "$SETTINGS_TARGET"
    DEPLOYED+=("settings: settings.json (sandbox)")
  fi
elif command -v jq >/dev/null 2>&1; then
  # Merge permissions.allow instead of skipping, since a copy-if-not-exists never reaches a
  # workspace that already has the file.
  # Reason: a git-tracked settings.json is shared project config. Writing personal
  # pre-approvals into it dirties the repo and can get them committed, so they go to the
  # untracked settings.local.json; if that file is tracked too, nothing is written.
  MERGE_TARGET="$SETTINGS_TARGET"
  if tracked "$SETTINGS_TARGET"; then
    MERGE_TARGET=".claude/settings.local.json"
    if tracked "$MERGE_TARGET"; then
      MERGE_TARGET=""
      WARNINGS+=("settings: permissions merge skipped (settings.json and settings.local.json are git-tracked)")
    fi
  fi
  CURRENT='{}'
  if [ -n "$MERGE_TARGET" ] && [ -f "$MERGE_TARGET" ]; then
    if ! CURRENT=$(jq -c 'if type == "object" then . else error("not an object") end' "$MERGE_TARGET" 2>/dev/null); then
      WARNINGS+=("settings: $MERGE_TARGET is not a JSON object; permissions merge skipped")
      MERGE_TARGET=""
    fi
  fi
  if [ -n "$MERGE_TARGET" ]; then
    NEW_ALLOW=$(jq '.permissions.allow // []' "$SETTINGS_SOURCE")
    # Append only missing entries, so the user's own order is kept and nothing is rewritten
    MERGED=$(jq -c --argjson new "$NEW_ALLOW" '(.permissions.allow // []) as $have | .permissions.allow = ($have + [$new[] | select(. as $x | $have | index([$x]) | not)])' <<<"$CURRENT")
    if [ "$MERGED" != "$CURRENT" ]; then
      echo "$MERGED" | jq '.' > "$MERGE_TARGET"
      DEPLOYED+=("settings: $(basename "$MERGE_TARGET") (sandbox permissions merged)")
    fi
    # Keep the local file out of commits with a local-only ignore; the same pattern Claude
    # Code adds to the global excludes file. Never fatal.
    if [ "$MERGE_TARGET" != "$SETTINGS_TARGET" ] && [ -f "$MERGE_TARGET" ] \
      && ! git check-ignore -q "$MERGE_TARGET" 2>/dev/null; then
      if ! { EXCLUDE=$(git rev-parse --git-path info/exclude 2>/dev/null) \
        && mkdir -p "$(dirname "$EXCLUDE")" 2>/dev/null \
        && { [ ! -s "$EXCLUDE" ] || [ -z "$(tail -c1 "$EXCLUDE")" ] || echo; } >> "$EXCLUDE" 2>/dev/null \
        && echo '**/.claude/settings.local.json' >> "$EXCLUDE" 2>/dev/null; }; then
        WARNINGS+=("settings: $MERGE_TARGET is not git-ignored (could not write .git/info/exclude); do not commit it")
      fi
    fi
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
if [ ${#DEPLOYED[@]} -gt 0 ] || [ ${#WARNINGS[@]} -gt 0 ]; then
  echo "# Workspace Setup (Sandbox)"
  echo ""
  if [ ${#DEPLOYED[@]} -gt 0 ]; then
    echo "Deployed ${#DEPLOYED[@]} file(s):"
    for item in "${DEPLOYED[@]}"; do
      echo "  - $item"
    done
  fi
  if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo ""
    echo "Warnings:"
    for w in "${WARNINGS[@]}"; do
      echo "  - $w"
    done
  fi
fi
