#!/usr/bin/env bash
# Regression check for read-once: each hook call is a new process, as in Claude Code.
# Usage: run.sh <hook.sh> <compact.sh>
set -uo pipefail
hook="$1" compact="$2"
export TMPDIR; TMPDIR=$(mktemp -d)
export READ_ONCE_DIFF=1   # session-wide, as a user would set it
f="$TMPDIR/sample.txt"; echo v1 > "$f"
sid="test-session-$$"
read_ev() { printf '{"session_id":"%s","tool_name":"Read","tool_input":{"file_path":"%s"}}' "$sid" "$f"; }
pass=0 fail=0
check() { if [[ "$2" == *"$3"* ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: got [$2]"; fail=$((fail+1)); fi; }

out1=$(read_ev | bash "$hook")
check "first read passes silently" "[$out1]" "[]"
out2=$(read_ev | bash "$hook")
check "second unchanged read is flagged" "$out2" "already read"

sleep 1; echo v2 > "$f"; touch -d '+2 seconds' "$f"
out3=$(read_ev | bash "$hook")
check "diff mode shows the change when blocking" "$out3" "+v2"

printf '{"session_id":"%s","hook_event_name":"PostCompact"}' "$sid" | bash "$compact"
out4=$(read_ev | bash "$hook")
check "after compaction the read passes again" "[$out4]" "[]"

dirs=$(find "$TMPDIR" -maxdepth 1 -name 'claude-read-once-*' | wc -l)
check "one cache dir per session (not per call)" "$dirs" "1"
rm -rf "$TMPDIR"
echo "pass=$pass fail=$fail"; (( fail == 0 ))
