#!/bin/bash
set -euo pipefail
# read-once: PostCompact hook — clears session cache after context compaction
# Prevents stale entries from blocking legitimate re-reads after context drops older content.

# Same session key as hook.sh; a $$-keyed path never matched the cache it meant to clear.
command -v jq >/dev/null 2>&1 || exit 0
SESSION_ID=$(jq -r '.session_id // "default"' | tr -cd 'A-Za-z0-9_-')
CACHE_DIR="${TMPDIR:-/tmp}/claude-read-once-${SESSION_ID:-default}"

if [ -d "$CACHE_DIR" ]; then
  rm -rf "$CACHE_DIR"
fi
