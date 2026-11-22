#!/bin/bash
set -euo pipefail
# Deploy workspace rules, scripts, governance, and base settings (copy-if-not-exists)
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

# 3. Base settings → .claude/settings.json (copy-if-not-exists; merge permissions.allow if present)
SETTINGS_TARGET=".claude/settings.json"
SETTINGS_SOURCE="$PLUGIN_DIR/settings/settings-base.json"
# Reason: a git-tracked settings.json is shared project config. Merging personal pre-approvals
# into it dirties the repo every session and can get them committed, so a tracked file is left
# alone and nothing else is written for it. The check fails closed: only "no repository above the
# file" or a clean "not tracked" answer from git allows a write; any other git problem (missing
# git, dubious ownership, corrupt index, path outside the work tree) counts as tracked.
# The path is resolved first, so a symlinked .claude or settings.json is checked at its target.
settings_tracked_or_unknown() {
  local real dir
  # Reason: these variables can point git at another repository, index or work tree, so its answer
  # about this file cannot be trusted; treat as tracked and skip
  [ -z "${GIT_DIR:-}${GIT_WORK_TREE:-}${GIT_INDEX_FILE:-}" ] || return 0
  real=$(realpath -m -- "$1" 2>/dev/null) || return 0
  dir=$(dirname "$real")
  # No .git (dir or file) at or above the target: not a repository, so not tracked
  local up="$dir"
  while [ ! -e "$up/.git" ]; do
    [ "$up" = "/" ] && return 1
    up=$(dirname "$up")
  done
  command -v git >/dev/null 2>&1 || return 0
  [ -d "$dir" ] || return 0
  local err rc=0
  err=$(LC_ALL=C git -C "$dir" ls-files --error-unmatch -- "$(basename "$real")" 2>&1 >/dev/null) || rc=$?
  [ "$rc" -eq 0 ] && return 0
  # 1 plus git's "did not match" message is the one clean "not tracked" answer
  if [ "$rc" -eq 1 ] && [[ "$err" == *"did not match any file(s) known to git"* ]]; then
    return 1
  fi
  return 0
}
SKIP_SETTINGS=false
if settings_tracked_or_unknown "$SETTINGS_TARGET"; then
  SKIP_SETTINGS=true
  WARNINGS+=("settings: $SETTINGS_TARGET is git-tracked (or its tracking state could not be read); left unchanged, base permissions not merged")
fi
if [ "$SKIP_SETTINGS" = true ]; then
  :
elif [ ! -f "$SETTINGS_TARGET" ]; then
  cp "$SETTINGS_SOURCE" "$SETTINGS_TARGET"
  DEPLOYED+=("settings: settings.json (base)")
elif command -v jq >/dev/null 2>&1; then
  # Merge permissions.allow into an existing file instead of skipping it — a
  # copy-if-not-exists never reaches a workspace that already has the file.
  NEW_ALLOW=$(jq '.permissions.allow // []' "$SETTINGS_SOURCE")
  MERGED=$(jq -c --argjson new "$NEW_ALLOW" '.permissions.allow = ((.permissions.allow // []) + $new | unique)' "$SETTINGS_TARGET")
  if [ "$MERGED" != "$(jq -c '.' "$SETTINGS_TARGET")" ]; then
    echo "$MERGED" | jq '.' > "$SETTINGS_TARGET"
    DEPLOYED+=("settings: settings.json (base permissions merged)")
  fi
fi

# 4. Governance files → project root
for file in "$PLUGIN_DIR/governance/"*.md; do
  [ -f "$file" ] || continue
  target="$(basename "$file")"
  if [ ! -f "$target" ]; then
    cp "$file" "$target"
    DEPLOYED+=("governance: $target")
  fi
done

# 5. Drift check: ~/.claude should be a symlink to persisted storage (rebuild
# survival). This hook can't fix it — see scripts/link-claude-home.sh for why.
if [ ! -L "$HOME/.claude" ]; then
  WARNINGS+=("~/.claude is not a symlink to persisted storage — memory, sessions, credentials, and settings will not survive a container rebuild. Run scripts/link-claude-home.sh from your devcontainer's onCreateCommand (this hook runs too late to fix it itself).")
fi
# ~/.claude.json (sibling file: project trust state, marketplace/onboarding
# flags) has no persistence mechanism here — decided not to build one (#203).
# Claude Code config writes are not verified atomic-rename-safe for every path
# (see #199 failure mode 1), so symlinking a single file is known-risky, and
# the value (re-approving trust dialogs) didn't clear the bar against that
# and the file's unresolved redaction question (it carries oauthAccount).
if [ ! -L "$HOME/.claude.json" ]; then
  WARNINGS+=("~/.claude.json is not persisted — per-project trust approvals and marketplace/onboarding state will not survive a container rebuild. Accepted limitation, not being fixed (see qte77/claude-code-plugins#203).")
fi

# 6. Report
if [ ${#DEPLOYED[@]} -gt 0 ] || [ ${#WARNINGS[@]} -gt 0 ]; then
  echo "# Workspace Setup"
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
