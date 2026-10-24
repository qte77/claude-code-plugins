#!/bin/bash
set -euo pipefail
# read-once: PreToolUse hook for Read tool deduplication
# Prevents redundant file re-reads within a session, saving ~2K tokens per blocked read.
# Source: Bande-a-Bonnot/Boucle-framework (MIT)

MODE="${READ_ONCE_MODE:-warn}"
TTL="${READ_ONCE_TTL:-1200}"
DIFF_ENABLED="${READ_ONCE_DIFF:-0}"
DIFF_MAX="${READ_ONCE_DIFF_MAX:-40}"

[ "${READ_ONCE_DISABLED:-0}" = "1" ] && exit 0

# Degrade to a no-op (never block Read) on hosts missing a required binary.
for bin in jq md5sum realpath stat; do
  command -v "$bin" >/dev/null 2>&1 || exit 0
done

# Parse tool input from stdin
INPUT=$(cat)

# Reason: each hook call is a new process, so a $$-keyed cache was empty on every
# Read and never caught a repeat. Key the cache by the session instead.
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "default"' | tr -cd 'A-Za-z0-9_-')
CACHE_DIR="${TMPDIR:-/tmp}/claude-read-once-${SESSION_ID:-default}"
mkdir -p "$CACHE_DIR"

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
HAS_OFFSET=$(echo "$INPUT" | jq -r '.tool_input.offset // empty')
HAS_LIMIT=$(echo "$INPUT" | jq -r '.tool_input.limit // empty')

# Partial reads always pass through
[ -n "$HAS_OFFSET" ] || [ -n "$HAS_LIMIT" ] && exit 0

# No file path = pass through
[ -z "$FILE_PATH" ] && exit 0

# File doesn't exist = pass through (let Read tool handle the error)
[ ! -f "$FILE_PATH" ] && exit 0

# Cache key: hash of absolute path
CACHE_KEY=$(echo -n "$(realpath "$FILE_PATH")" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/$CACHE_KEY"

# Current mtime
CURRENT_MTIME=$(stat -c %Y "$FILE_PATH" 2>/dev/null || stat -f %m "$FILE_PATH" 2>/dev/null)

if [ -f "$CACHE_FILE" ]; then
  CACHED_MTIME=$(sed -n '1p' "$CACHE_FILE")
  CACHED_TIME=$(sed -n '2p' "$CACHE_FILE")
  NOW=$(date +%s)

  # TTL expired = allow and refresh
  if [ $((NOW - CACHED_TIME)) -ge "$TTL" ]; then
    echo "$CURRENT_MTIME" > "$CACHE_FILE"
    echo "$NOW" >> "$CACHE_FILE"
    exit 0
  fi

  # File changed since last read
  if [ "$CURRENT_MTIME" != "$CACHED_MTIME" ]; then
    echo "$CURRENT_MTIME" > "$CACHE_FILE"
    echo "$NOW" >> "$CACHE_FILE"

    # Diff mode: answer with the diff against the snapshot taken at the last read,
    # instead of the full file, when the diff is small enough.
    if [ "$DIFF_ENABLED" = "1" ] && [ -f "$CACHE_FILE.snap" ]; then
      DIFF=$(diff -u "$CACHE_FILE.snap" "$FILE_PATH" 2>/dev/null || true)
      cp "$FILE_PATH" "$CACHE_FILE.snap"
      if [ -n "$DIFF" ] && [ "$(printf '%s\n' "$DIFF" | wc -l)" -le "$DIFF_MAX" ]; then
        jq -cn --arg d "$DIFF" --arg f "$FILE_PATH" \
          '{decision:"block",reason:("read-once: \($f) changed since your last read. Diff only:\n" + $d)}'
        exit 0
      fi
    fi
    exit 0
  fi

  # File unchanged = redundant read
  if [ "$MODE" = "deny" ]; then
    echo "{\"decision\":\"block\",\"reason\":\"read-once: $FILE_PATH already in context (unchanged). Use Edit directly.\"}"
    exit 0
  fi

  # Warn mode: allow but advise
  echo "{\"decision\":\"allow\",\"reason\":\"read-once: $FILE_PATH already read and unchanged. Consider skipping redundant reads.\"}"
  exit 0
fi

# First read: cache and allow
NOW=$(date +%s)
echo "$CURRENT_MTIME" > "$CACHE_FILE"
echo "$NOW" >> "$CACHE_FILE"
[ "$DIFF_ENABLED" = "1" ] && cp "$FILE_PATH" "$CACHE_FILE.snap"
exit 0
