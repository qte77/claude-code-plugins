#!/bin/bash
set -Eeuo pipefail
trap 'exit 0' ERR   # fail open: never error out of a hook
# read-once: PostCompact hook — clears session cache after context compaction
# Prevents stale entries from blocking legitimate re-reads after context drops older content.

# Same session key as hook.sh; a $$-keyed path never matched the cache it meant to clear.
command -v jq >/dev/null 2>&1 || exit 0
SESSION_ID=$(jq -r '.session_id // "default"' | tr -cd 'A-Za-z0-9_-') || exit 0
UID_NOW=$(id -u)
CACHE_BASE="${XDG_RUNTIME_DIR:-${TMPDIR:-/tmp}}/claude-read-once-$UID_NOW"
CACHE_DIR="$CACHE_BASE/${SESSION_ID:-default}"

# Delete only inside real dirs we own, never through a symlink.
owned_dir() {
  [ -d "$1" ] && [ ! -L "$1" ] &&
    [ "$(stat -c %u "$1" 2>/dev/null || stat -f %u "$1" 2>/dev/null)" = "$UID_NOW" ]
}
if owned_dir "$CACHE_BASE" && owned_dir "$CACHE_DIR"; then
  rm -rf "$CACHE_DIR"
fi
