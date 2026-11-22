#!/usr/bin/env bash
# Regression check for statusline.sh: the context label, hostile input, field splitting and the
# opt-in world clock. Usage: statusline-test.sh <statusline.sh> <statusline-json-structure.json>
set -uo pipefail
script=$(realpath "$1") sample=$(realpath "$2")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
export HOME="$work/home"; mkdir -p "$HOME/.claude"   # no ~/.claude/world-clock unless a test writes one
unset CC_WORLD_CLOCK CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
pass=0 fail=0
has() { if [[ "$2" == *"$3"* ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: got [$2] want [$3]"; fail=$((fail+1)); fi; }
hasnt() { if [[ "$2" != *"$3"* ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: got [$2]"; fail=$((fail+1)); fi; }
no_file() { if [[ ! -e "$2" ]]; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1: $2 exists"; fail=$((fail+1)); fi; }
# Run outside any git repo so the branch field is empty and stable
render() { (cd "$work" && bash "$script"); }
# The sample JSON with one jq edit applied
sample_with() { jq "$1" "$sample"; }

# The sample uses 2000 + 15000 + 48000 of a 200000 window: 32.5% used, 68% remaining (rounded)
out=$(CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 render < "$sample")
has "context label shows used share and compact point from the override" "$out" "ctx:32% used·compact@50%"
hasnt "no imminent marker with 18% usable left" "$out" "compact@50%!"

out=$(sample_with 'del(.context_window.current_usage) | .context_window.remaining_percentage = 52' \
    | CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 render)
has "imminent marker when at most 3% usable is left" "$out" "48% used·compact@50%!"

out=$(render < "$sample")
has "without the override the observed 16.5% buffer applies" "$out" "compact@84%"

# Values reach awk only as data: a hostile value must never run, and is treated as absent.
# The payloads have no spaces, so they cannot be broken up by a whitespace split before awk sees them
marker="$work/pwned-env"
out=$(CLAUDE_AUTOCOMPACT_PCT_OVERRIDE="0;system(\"id>$marker\")" render < "$sample")
no_file "a hostile CLAUDE_AUTOCOMPACT_PCT_OVERRIDE never runs" "$marker"
marker="$work/pwned-json"
has "a non-numeric override falls back to the default buffer" "$out" "compact@84%"
out=$(sample_with "del(.context_window.current_usage) | .context_window.remaining_percentage = \"1;system(\\\"id>$marker\\\")\"" \
    | render)
no_file "a hostile remaining_percentage never runs" "$marker"
has "a non-numeric remaining_percentage reads as 100% free" "$out" "ctx:0% used"

# Only a tab splits fields: a space in the directory name must not shift the fields after it
out=$(sample_with '.workspace.current_dir = "/tmp/my project dir" | .model.id = "model-x"' | render)
has "directory name with spaces is shown whole" "$out" "dir:my project dir"
has "fields after a spaced value are not shifted" "$out" "model:model-x"
out=$(sample_with '.model.id = "a\u001b[31mb"' | render)
hasnt "control characters inside a value are scrubbed" "$out" $'a\e[31mb'

# World clock: unchanged behaviour (env var, then the ~/.claude/world-clock file)
out=$(CC_WORLD_CLOCK="UTC=Z,Not/AZone" render < "$sample")
has "world clock renders a labelled zone" "$out" "clocks: Z:"
has "world clock marks an unknown zone" "$out" "?Not/AZone"
out=$(render < "$sample")
hasnt "world clock is off by default" "$out" "clocks:"
echo "UTC" > "$HOME/.claude/world-clock"
out=$(render < "$sample")
has "world clock file is the fallback" "$out" "clocks: UTC:"

echo "passed $pass, failed $fail"
[[ $fail -eq 0 ]]
