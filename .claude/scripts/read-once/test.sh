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
# check = exact match; has = substring match (a "0" must not pass on "10")
check() { if [[ "$2" == "$3" ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: got [$2] want [$3]"; fail=$((fail+1)); fi; }
has() { if [[ "$2" == *"$3"* ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: got [$2]"; fail=$((fail+1)); fi; }

out1=$(read_ev | bash "$hook")
check "first read passes silently" "[$out1]" "[]"
out2=$(read_ev | bash "$hook")
has "second unchanged read is flagged" "$out2" "already read"

sleep 1; echo v2 > "$f"; touch -d '+2 seconds' "$f"
out3=$(read_ev | bash "$hook")
has "diff mode shows the change when blocking" "$out3" "+v2"

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
for name in .env.local server.pem id_ed25519 aws-credentials.json .NPMRC .netrc .pgpass cert.p12 cert.PFX; do
  f="$TMPDIR/$name"; echo secret > "$f"; read_ev | bash "$hook" >/dev/null
done
f="$TMPDIR/big.bin"; head -c 1048577 /dev/zero > "$f"; read_ev | bash "$hook" >/dev/null
snaps=$(find "$base" -name '*.snap' | wc -l)
check "secret-like and >1 MiB files are not snapshotted" "$snaps" "1"
f="$TMPDIR/sample.txt"

# A symlink to a secret-named file is judged by its target: no snapshot, and an old one is removed.
echo secret > "$TMPDIR/.env"; f="$TMPDIR/notes.txt"; ln -sf "$TMPDIR/.env" "$f"
rm -rf "$base"; mkdir -p "$base/$sid"; chmod 700 "$base" "$base/$sid"
key=$(echo -n "$(realpath "$f")" | md5sum | cut -d' ' -f1)
echo old > "$base/$sid/$key.snap"   # cache entry absent: first-read path
read_ev | bash "$hook" >/dev/null
check "symlink to a secret file: old snapshot removed" "$(find "$base" -name '*.snap' | wc -l | tr -d ' ')" "0"
rm -rf "$base"; read_ev | bash "$hook" >/dev/null
check "symlink to a secret file: not snapshotted" "$(find "$base" -name '*.snap' | wc -l | tr -d ' ')" "0"
rm -f "$f"; f="$TMPDIR/sample.txt"

# --- #291 ---
snap_of() { echo "$base/$sid/$(echo -n "$(realpath "$1")" | md5sum | cut -d' ' -f1).snap"; }
snaps_now() { find "$base" -name '*.snap' 2>/dev/null | wc -l | tr -d ' '; }

# TTL expiry refreshes the snapshot, so a later diff is against the content just read.
rm -rf "$base"; f="$TMPDIR/ttl.txt"; echo v1 > "$f"
read_ev | bash "$hook" >/dev/null
echo v2 > "$f"; touch -d '+2 seconds' "$f"
read_ev | READ_ONCE_TTL=0 bash "$hook" >/dev/null
check "TTL expiry refreshes the snapshot" "$(cat "$(snap_of "$f")" 2>/dev/null)" "v2"
echo v3 > "$f"; touch -d '+4 seconds' "$f"
out7=$(read_ev | bash "$hook")
has "diff after TTL expiry is against the refreshed snapshot" "$out7" "-v2"

# A relative symlink is resolved from its own dir: to a secret it is skipped, to a file it is kept.
rm -rf "$base"; mkdir "$TMPDIR/rel"; echo secret > "$TMPDIR/rel/.env"; echo ok > "$TMPDIR/rel/plain.txt"
f="$TMPDIR/rel/a.txt"; (cd "$TMPDIR/rel" && ln -s .env a.txt); read_ev | bash "$hook" >/dev/null
check "relative symlink to a secret file: not snapshotted" "$(snaps_now)" "0"
f="$TMPDIR/rel/b.txt"; (cd "$TMPDIR/rel" && ln -s plain.txt b.txt); read_ev | bash "$hook" >/dev/null
check "relative symlink to a plain file: snapshotted" "$(cat "$(snap_of "$f")" 2>/dev/null)" "ok"

# A symlink loop or a symlink to a directory passes through: exit 0, no output, nothing cached.
for kind in loop dir; do
  rm -rf "$base"; f="$TMPDIR/$kind-link"
  if [ "$kind" = loop ]; then ln -s "$f" "$f"; else mkdir "$TMPDIR/somedir"; ln -s "$TMPDIR/somedir" "$f"; fi
  out=$(read_ev | bash "$hook"); rc=$?
  check "symlink $kind: exits 0 silently" "${rc}[$out]" "0[]"
  check "symlink $kind: nothing cached" "$(find "$base" -type f 2>/dev/null | wc -l | tr -d ' ')" "0"
done
f="$TMPDIR/sample.txt"

# Fail open: bad input and write failures exit 0 and write nothing.
rm -rf "$base"
printf 'not json' | bash "$hook" >/dev/null 2>&1; rc=$?
check "hook: invalid input exits 0" "$rc" "0"
check "hook: invalid input writes nothing" "$(find "$base" 2>/dev/null | wc -l | tr -d ' ')" "0"
mkdir -m 700 "$base" "$base/$sid"; echo keep > "$base/$sid/x"
printf 'not json' | bash "$compact" >/dev/null 2>&1; rc=$?
check "compact: invalid input exits 0" "$rc" "0"
check "compact: invalid input deletes nothing" "$(cat "$base/$sid/x")" "keep"
rm -rf "$base"
fstub="$TMPDIR/failstub"; mkdir "$fstub"
for cmd in chmod install; do printf '#!/bin/sh\nexit 1\n' > "$fstub/$cmd"; chmod +x "$fstub/$cmd"; done
read_ev | PATH="$fstub:$PATH" bash "$hook" >/dev/null 2>&1; rc=$?
check "failing install/chmod: hook exits 0" "$rc" "0"
check "failing install/chmod: no snapshot" "$(find "$base" -name '*.snap' 2>/dev/null | wc -l | tr -d ' ')" "0"
rm -rf "$base"; mkdir -m 700 "$base"; read_ev | bash "$hook" >/dev/null   # real dirs
rm -rf "${base:?}/$sid"; printf '#!/bin/sh\nexit 1\n' > "$fstub/chmod"; rm -f "$fstub/install"
read_ev | PATH="$fstub:$PATH" bash "$hook" >/dev/null 2>&1; rc=$?
check "failing chmod only: hook exits 0" "$rc" "0"
check "failing chmod only: nothing cached" "$(find "$base" -type f 2>/dev/null | wc -l | tr -d ' ')" "0"

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
