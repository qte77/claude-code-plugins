#!/usr/bin/env bash
# Stop hook: remind the user once per session to run /handing-off-session
# when the working tree has uncommitted changes.
# Uses systemMessage (shown to the user) rather than additionalContext,
# which on Stop continues the conversation and costs a model turn.
# Disable with CC_META_HANDOFF_REMINDER=0 (e.g. in settings.local.json "env").
set -u

[ "${CC_META_HANDOFF_REMINDER:-1}" = "0" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0
command -v git >/dev/null 2>&1 || exit 0

input=$(cat)
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false')" = "true" ] && exit 0
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty' | tr -cd 'A-Za-z0-9_-')
[ -n "$session_id" ] || exit 0

marker="${TMPDIR:-/tmp}/cc-meta-handoff-reminded-$session_id"
[ -e "$marker" ] && exit 0

# Reason: only nudge when there is in-progress work to lose.
[ -n "$(git status --porcelain 2>/dev/null | head -n 1)" ] || exit 0

touch "$marker"
jq -n '{systemMessage: "Uncommitted changes in this session — consider /handing-off-session before you stop."}'
