#!/usr/bin/env bash
# Regression check for read-once: each hook call is a new process, as in Claude Code.
# Usage: run.sh <hook.sh> <compact.sh>
set -uo pipefail
hook="$1" compact="$2"
export TMPDIR; TMPDIR=$(mktemp -d)
unset XDG_RUNTIME_DIR   # the cache base falls back to TMPDIR
base="$TMPDIR/claude-read-once-$(id -u)"
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

dirs=$(find "$base" -mindepth 1 -maxdepth 1 -type d | wc -l)
check "one cache dir per session (not per call)" "$dirs" "1"

# --- hardening (#262) ---
mode() { stat -c %a "$1" 2>/dev/null || stat -f %Lp "$1"; }
check "per-user cache base is mode 700" "$(mode "$base")" "700"
check "session cache dir is mode 700" "$(mode "$base/$sid")" "700"
snap=$(find "$base/$sid" -name '*.snap' | head -1)
check "snapshot is mode 600" "$(mode "$snap")" "600"

# A stale base from an earlier run with loose permissions is tightened.
rm -rf "$base"; mkdir -m 755 "$base"
read_ev | bash "$hook" >/dev/null
check "existing loose base is tightened to 700" "$(mode "$base")" "700"

# Secret-like and oversized files are never snapshotted.
for name in .env.local server.pem id_ed25519 aws-credentials.json; do
  f="$TMPDIR/$name"; echo secret > "$f"; read_ev | bash "$hook" >/dev/null
done
f="$TMPDIR/big.bin"; head -c 1048577 /dev/zero > "$f"; read_ev | bash "$hook" >/dev/null
snaps=$(find "$base" -name '*.snap' | wc -l)
check "secret-like and >1 MiB files are not snapshotted" "$snaps" "1"
f="$TMPDIR/sample.txt"

# A symlinked base: the hook does nothing (never blocks) and writes nothing through it.
rm -rf "$base"; elsewhere="$TMPDIR/elsewhere"; mkdir -m 700 "$elsewhere"; ln -s "$elsewhere" "$base"
read_ev | bash "$hook" >/dev/null; out5=$(read_ev | bash "$hook")
check "symlinked base: second read not flagged" "[$out5]" "[]"
check "symlinked base: nothing written through it" "$(find "$elsewhere" -mindepth 1 | wc -l)" "0"
rm -f "$base"

# A base owned by someone else (simulated with an id stub): the hook does nothing.
stub="$TMPDIR/stub"; mkdir "$stub"; printf '#!/bin/sh\necho 4242\n' > "$stub/id"; chmod +x "$stub/id"
foreign="$TMPDIR/claude-read-once-4242"; mkdir -m 700 "$foreign"
PATH="$stub:$PATH" bash "$hook" < <(read_ev) >/dev/null; out6=$(read_ev | PATH="$stub:$PATH" bash "$hook")
check "foreign-owned base: second read not flagged" "[$out6]" "[]"
check "foreign-owned base: nothing written into it" "$(find "$foreign" -mindepth 1 | wc -l)" "0"

# Compaction never deletes through a symlinked session dir.
mkdir -m 700 "$base"; target="$TMPDIR/keep"; mkdir "$target"; touch "$target/file"; ln -s "$target" "$base/$sid"
printf '{"session_id":"%s","hook_event_name":"PostCompact"}' "$sid" | bash "$compact"
check "compaction leaves a symlink target alone" "$(ls "$target")" "file"
rm -rf "$TMPDIR"
echo "pass=$pass fail=$fail"; (( fail == 0 ))
