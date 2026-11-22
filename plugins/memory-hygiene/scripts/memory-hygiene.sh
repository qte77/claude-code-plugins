#!/usr/bin/env bash
# memory-hygiene: decide when the auto-memory consolidation pass is due.
#
#   memory-hygiene.sh hook          SessionStart / SessionEnd hook (hook JSON on stdin)
#   memory-hygiene.sh paths [DIR]   print the memory dir and state files for DIR (default: $PWD)
#   memory-hygiene.sh done  [DIR]   record a finished pass for DIR
#
# Schedule (plugin option `schedule`, env CLAUDE_PLUGIN_OPTION_SCHEDULE):
#   weekly (default) | daily | monthly  due once the interval since the last pass has passed
#   session-start                        due at every new or cleared session
#   session-end                          a session end marks it due; it runs at the next session start
#   compact                              due right after each compaction (auto or manual)
#   off                                  never
# Mode (plugin option `mode`, env CLAUDE_PLUGIN_OPTION_MODE):
#   auto (default)  ask Claude to run the skill (adds context, costs a subagent run)
#   remind          only show the user a reminder (no model cost)
#
# Hooks cannot run a model or a skill themselves: this script only decides and asks.
set -u

STATE_DIR="${CLAUDE_PLUGIN_DATA:-${XDG_STATE_HOME:-$HOME/.local/state}/memory-hygiene}"
CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILL="/memory-hygiene:consolidating-memory"

# The auto-memory dir is derived from the git repository (worktrees share it), or the
# directory itself outside git; `autoMemoryDirectory` in user settings overrides it.
memory_dir() {
  local dir="$1" custom common root
  # Already a memory dir (`done`/`paths` from the skill): use it as given.
  if is_memory_dir "$dir"; then
    printf '%s\n' "$dir"
    return
  fi
  custom=$(jq -r '.autoMemoryDirectory // empty' "$CONFIG_DIR/settings.json" 2>/dev/null)
  if [ -n "$custom" ]; then
    printf '%s\n' "${custom/#\~/$HOME}"
    return
  fi
  common=$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
  if [ -n "$common" ]; then root=$(dirname "$common"); else root="$dir"; fi
  printf '%s/projects/%s/memory\n' "$CONFIG_DIR" "$(printf '%s' "$root" | sed 's/[^A-Za-z0-9]/-/g')"
}

# True when DIR is <config>/projects/<key>/memory, compared on resolved paths
# (the config dir is often reached through a symlink).
is_memory_dir() {
  local real config
  real=$(cd "$1" 2>/dev/null && pwd -P) || return 1
  config=$(cd "$CONFIG_DIR" 2>/dev/null && pwd -P) || return 1
  [ "$(basename "$real")" = memory ] && [ "$(dirname "$(dirname "$real")")" = "$config/projects" ]
}

state_key() { basename "$(dirname "$1")" | tr -cd 'A-Za-z0-9_-'; }

interval_seconds() {
  case "$1" in
    daily) echo 86400 ;;
    weekly) echo 604800 ;;
    monthly) echo 2592000 ;;
    *) echo 0 ;;
  esac
}

cmd_paths() {
  local mem key
  mem=$(memory_dir "${1:-$PWD}")
  key=$(state_key "$mem")
  printf 'memory_dir=%s\nlast_run=%s/%s.last-run\npending=%s/%s.pending\n' \
    "$mem" "$STATE_DIR" "$key" "$STATE_DIR" "$key"
}

cmd_done() {
  local mem key
  mem=$(memory_dir "${1:-$PWD}")
  key=$(state_key "$mem")
  mkdir -p "$STATE_DIR"
  touch "$STATE_DIR/$key.last-run"
  rm -f "$STATE_DIR/$key.pending"
  echo "recorded pass for $mem"
}

cmd_hook() {
  command -v jq >/dev/null 2>&1 || exit 0
  [ "${CLAUDE_CODE_DISABLE_AUTO_MEMORY:-0}" = "1" ] && exit 0
  local schedule mode input event src cwd transcript mem key last_run pending due=0 last age
  schedule="${CLAUDE_PLUGIN_OPTION_SCHEDULE:-weekly}"
  mode="${CLAUDE_PLUGIN_OPTION_MODE:-auto}"
  [ "$schedule" = "off" ] && exit 0

  input=$(cat)
  event=$(jq -r '.hook_event_name // empty' <<<"$input")
  src=$(jq -r '.source // empty' <<<"$input")
  cwd=$(jq -r '.cwd // empty' <<<"$input")
  transcript=$(jq -r '.transcript_path // empty' <<<"$input")
  [ -n "$cwd" ] || cwd="$PWD"

  mem=$(memory_dir "$cwd")
  # Fall back to the transcript's project dir when the derived path has no memory.
  if [ ! -f "$mem/MEMORY.md" ] && [ -n "$transcript" ]; then
    mem="$(dirname "$transcript")/memory"
  fi
  [ -f "$mem/MEMORY.md" ] || exit 0

  key=$(state_key "$mem")
  mkdir -p "$STATE_DIR"
  last_run="$STATE_DIR/$key.last-run"
  pending="$STATE_DIR/$key.pending"

  if [ "$event" = "SessionEnd" ]; then
    [ "$schedule" = "session-end" ] && touch "$pending"
    exit 0
  fi
  [ "$event" = "SessionStart" ] || exit 0

  case "$schedule:$src" in
    compact:compact) due=1 ;;
    session-start:startup | session-start:clear) due=1 ;;
    session-end:startup | session-end:clear | session-end:resume) [ -e "$pending" ] && due=1 ;;
    daily:startup | daily:clear | daily:resume | weekly:startup | weekly:clear | weekly:resume | \
      monthly:startup | monthly:clear | monthly:resume)
      last=$(stat -c %Y "$last_run" 2>/dev/null || echo 0)
      age=$(($(date +%s) - last))
      [ "$age" -ge "$(interval_seconds "$schedule")" ] && due=1
      ;;
  esac
  [ "$due" = 1 ] || exit 0

  local when="never"
  [ -e "$last_run" ] && when=$(date -u -d "@$(stat -c %Y "$last_run")" +%Y-%m-%d)
  local note="Memory consolidation is due for this project (schedule: $schedule, last pass: $when)."
  if [ "$mode" = "remind" ]; then
    jq -n --arg m "$note Run $SKILL when convenient." '{systemMessage: $m}'
    exit 0
  fi
  jq -n --arg m "$note Claude will run $SKILL in the background." \
    --arg c "$note When you reach a natural break, invoke the $SKILL skill. It runs in a background subagent and only touches this project's auto-memory directory ($mem). Don't interrupt the user's task for it." \
    '{systemMessage: $m, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
}

case "${1:-}" in
  hook) cmd_hook ;;
  paths) cmd_paths "${2:-}" ;;
  done) cmd_done "${2:-}" ;;
  *)
    echo "usage: $0 hook|paths [DIR]|done [DIR]" >&2
    exit 2
    ;;
esac
