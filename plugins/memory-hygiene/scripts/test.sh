#!/usr/bin/env bash
# Regression tests for memory-hygiene.sh: when is a consolidation pass due?
# Usage: bash plugins/memory-hygiene/scripts/test.sh
set -u

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/memory-hygiene.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

export CLAUDE_CONFIG_DIR="$TMP/claude"
export CLAUDE_PLUGIN_DATA="$TMP/data"
unset CLAUDE_PLUGIN_OPTION_SCHEDULE CLAUDE_PLUGIN_OPTION_MODE CLAUDE_CODE_DISABLE_AUTO_MEMORY

REPO="$TMP/work/my.repo"
mkdir -p "$REPO/sub" "$CLAUDE_CONFIG_DIR"
git -C "$REPO" init -q
MEM="$CLAUDE_CONFIG_DIR/projects/$(printf '%s' "$REPO" | sed 's/[^A-Za-z0-9]/-/g')/memory"
mkdir -p "$MEM"
echo "- [a](a.md) — hook" >"$MEM/MEMORY.md"
KEY=$(basename "$(dirname "$MEM")")

pass=0
fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then pass=$((pass + 1)); else
    fail=$((fail + 1))
    echo "FAIL: $1 (expected '$2', got '$3')"
  fi
}

run() { # event source [cwd] -> prints "due" or "quiet"
  local out
  out=$(jq -n --arg e "$1" --arg s "$2" --arg c "${3:-$REPO}" \
    '{hook_event_name: $e, source: $s, cwd: $c, session_id: "t", transcript_path: ""}' |
    bash "$SCRIPT" hook)
  if [ -n "$out" ]; then echo due; else echo quiet; fi
}

reset_state() { rm -rf "$CLAUDE_PLUGIN_DATA"; }

# weekly (default)
reset_state
check "weekly: due with no previous pass" due "$(run SessionStart startup)"
check "weekly: due from a subdirectory" due "$(run SessionStart startup "$REPO/sub")"
bash "$SCRIPT" "done" "$REPO" >/dev/null
check "weekly: quiet right after a pass" quiet "$(run SessionStart startup)"
touch -d '8 days ago' "$CLAUDE_PLUGIN_DATA/$KEY.last-run"
check "weekly: due after 8 days" due "$(run SessionStart resume)"
check "weekly: quiet on compact" quiet "$(run SessionStart compact)"

# daily / monthly
export CLAUDE_PLUGIN_OPTION_SCHEDULE=daily
touch -d '2 days ago' "$CLAUDE_PLUGIN_DATA/$KEY.last-run"
check "daily: due after 2 days" due "$(run SessionStart startup)"
export CLAUDE_PLUGIN_OPTION_SCHEDULE=monthly
check "monthly: quiet after 2 days" quiet "$(run SessionStart startup)"

# session-start
export CLAUDE_PLUGIN_OPTION_SCHEDULE=session-start
check "session-start: due on startup" due "$(run SessionStart startup)"
check "session-start: quiet on resume" quiet "$(run SessionStart resume)"

# session-end: the end marks it due, the next start asks
export CLAUDE_PLUGIN_OPTION_SCHEDULE=session-end
reset_state
check "session-end: quiet before any session ended" quiet "$(run SessionStart startup)"
run SessionEnd "" >/dev/null
check "session-end: due at next start" due "$(run SessionStart startup)"
bash "$SCRIPT" "done" "$REPO" >/dev/null
check "session-end: quiet after the pass" quiet "$(run SessionStart startup)"

# compact
export CLAUDE_PLUGIN_OPTION_SCHEDULE=compact
check "compact: due after compaction" due "$(run SessionStart compact)"
check "compact: quiet on startup" quiet "$(run SessionStart startup)"

# off, disabled memory, missing memory
export CLAUDE_PLUGIN_OPTION_SCHEDULE=off
check "off: quiet" quiet "$(run SessionStart startup)"
export CLAUDE_PLUGIN_OPTION_SCHEDULE=session-start
check "auto memory disabled: quiet" quiet \
  "$(CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 run SessionStart startup)"
check "no memory dir: quiet" quiet "$(run SessionStart startup "$TMP")"

# modes
out=$(jq -n --arg c "$REPO" '{hook_event_name: "SessionStart", source: "startup", cwd: $c}' | bash "$SCRIPT" hook)
check "auto: adds context for Claude" true "$(jq 'has("hookSpecificOutput")' <<<"$out")"
out=$(jq -n --arg c "$REPO" '{hook_event_name: "SessionStart", source: "startup", cwd: $c}' |
  CLAUDE_PLUGIN_OPTION_MODE=remind bash "$SCRIPT" hook)
check "remind: user message only" false "$(jq 'has("hookSpecificOutput")' <<<"$out")"

echo "memory-hygiene: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
