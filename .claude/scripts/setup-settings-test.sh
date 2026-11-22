#!/usr/bin/env bash
# Regression check for the SessionStart setup hooks' settings step: a git-tracked
# .claude/settings.json is never touched and nothing else is written for it, and the check fails
# closed (any git problem counts as tracked). Untracked, missing or outside-git settings.json keeps
# the old merge behaviour. Usage: setup-settings-test.sh <plugin dir> <hook script>
#   e.g. setup-settings-test.sh plugins/workspace-setup plugins/workspace-setup/hooks/scripts/setup-workspace.sh
set -uo pipefail
plugin=$(realpath "$1") script=$(realpath "$2")
work=$(mktemp -d)
trap 'chmod -R u+w "$work" 2>/dev/null; rm -rf "$work"' EXIT
export HOME="$work/home"; mkdir -p "$HOME"
# Reason: isolate git from the developer's user and system config
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1; unset XDG_CONFIG_HOME
export CLAUDE_PLUGIN_ROOT="$plugin"
source_settings=$(ls "$plugin"/settings/settings-*.json)
want_allow=$(jq -c '.permissions.allow | unique' "$source_settings")
pass=0 fail=0
ok() { if eval "$2"; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1"; fail=$((fail+1)); fi; }

# A fresh git repo in its own folder; $1 = name
repo() {
  local d="$work/$1"; mkdir -p "$d/.claude"
  git -C "$d" init -q
  git -C "$d" config user.email t@example.invalid; git -C "$d" config user.name t
  git -C "$d" config commit.gpgsign false
  echo "$d"
}
# Commit a one-line settings.json at $2 (default .claude/settings.json) in repo $1
commit_settings() {
  mkdir -p "$(dirname "$1/${2:-.claude/settings.json}")"
  printf '{"env":{"A":"1"}}\n' > "$1/${2:-.claude/settings.json}"
  git -C "$1" add "${2:-.claude/settings.json}"; git -C "$1" commit -qm init
}
run_hook() { (cd "$1" && bash "$script" >"$1/hook.out" 2>&1); }
# Nothing settings-related besides settings.json may appear, and no exclude entry
no_side_files() { [ -z "$(find "$1" -name 'settings.local.json' -not -path '*/.git/*' 2>/dev/null)" ] && ! grep -qs 'settings' "$1/.git/info/exclude"; }

# 1. No settings.json: the template is copied (unchanged behaviour)
d=$(repo fresh); run_hook "$d"
ok "missing settings.json is created from the template" "cmp -s '$d/.claude/settings.json' '$source_settings'"

# 2. Untracked settings.json: allow entries merge into it (unchanged behaviour)
d=$(repo untracked); echo '{"env":{"A":"1"}}' > "$d/.claude/settings.json"; run_hook "$d"
ok "untracked settings.json gains the plugin allow list" \
  "[ \"\$(jq -c '.permissions.allow | unique' '$d/.claude/settings.json')\" = '$want_allow' ]"
ok "untracked settings.json keeps its other keys" "[ \"\$(jq -r .env.A '$d/.claude/settings.json')\" = 1 ]"

# 3. Tracked settings.json: untouched, nothing else written, one informational line
d=$(repo tracked); commit_settings "$d"; cp "$d/.claude/settings.json" "$work/tracked.before"
run_hook "$d"
ok "tracked settings.json is byte-identical" "cmp -s '$d/.claude/settings.json' '$work/tracked.before' && git -C '$d' diff --quiet -- .claude/settings.json"
ok "tracked: no settings.local.json and no exclude entry are written" "no_side_files '$d'"
ok "tracked: the hook says it skipped the merge" "grep -q 'tracked' '$d/hook.out'"
run_hook "$d"
ok "tracked: a second run still changes nothing" "cmp -s '$d/.claude/settings.json' '$work/tracked.before' && no_side_files '$d'"

# 4. Tracked settings.json plus an existing settings.local.json: both untouched
d=$(repo local-exists); commit_settings "$d"
echo '{"permissions":{"allow":["Bash(make test)"]}}' > "$d/.claude/settings.local.json"; cp "$d/.claude/settings.local.json" "$work/local.before"
run_hook "$d"
ok "an existing settings.local.json is not touched" "cmp -s '$d/.claude/settings.local.json' '$work/local.before'"

# 5. Staged but never committed counts as tracked
d=$(repo staged); echo '{}' > "$d/.claude/settings.json"; git -C "$d" add .claude/settings.json
run_hook "$d"
ok "staged settings.json is left alone" "[ \"\$(cat '$d/.claude/settings.json')\" = '{}' ]"

# 6. A tracked settings.json deleted from the working tree is not recreated
d=$(repo deleted); commit_settings "$d"; rm "$d/.claude/settings.json"
run_hook "$d"
ok "a deleted tracked settings.json stays deleted" "[ ! -e '$d/.claude/settings.json' ]"

# 7. Subdirectory with its own tracked .claude
d=$(repo subdir); commit_settings "$d" sub/.claude/settings.json; cp "$d/sub/.claude/settings.json" "$work/sub.before"
run_hook "$d/sub"
ok "subdirectory: tracked settings.json untouched" "cmp -s '$d/sub/.claude/settings.json' '$work/sub.before'"

# 8. Not a git repo: behaves as before (merge into settings.json), exit 0
d="$work/nogit"; mkdir -p "$d/.claude"; echo '{}' > "$d/.claude/settings.json"
(cd "$d" && bash "$script" >"$d/hook.out" 2>&1); rc=$?
ok "outside git: exit 0 and settings.json is merged" "[ $rc = 0 ] && [ \"\$(jq -c '.permissions.allow | unique' '$d/.claude/settings.json')\" = '$want_allow' ]"

# 9. Git errors fail closed: inside a repo, any answer but a clean "not tracked" means skip
d=$(repo dubious); commit_settings "$d"; cp "$d/.claude/settings.json" "$work/dubious.before"
(cd "$d" && GIT_TEST_ASSUME_DIFFERENT_OWNER=1 bash "$script" >"$d/hook.out" 2>&1); rc=$?
ok "dubious ownership: exit 0, tracked file untouched, nothing else written" "[ $rc = 0 ] && cmp -s '$d/.claude/settings.json' '$work/dubious.before' && no_side_files '$d'"
d=$(repo dubious-del); commit_settings "$d"; rm "$d/.claude/settings.json"
(cd "$d" && GIT_TEST_ASSUME_DIFFERENT_OWNER=1 bash "$script" >"$d/hook.out" 2>&1)
ok "dubious ownership: a deleted tracked file is not recreated" "[ ! -e '$d/.claude/settings.json' ]"
d=$(repo dubious-untracked); echo '{}' > "$d/.claude/settings.json"
(cd "$d" && GIT_TEST_ASSUME_DIFFERENT_OWNER=1 bash "$script" >"$d/hook.out" 2>&1)
ok "dubious ownership: even an untracked file is left alone (state unknown)" "[ \"\$(cat '$d/.claude/settings.json')\" = '{}' ]"
d=$(repo corrupt); commit_settings "$d"; cp "$d/.claude/settings.json" "$work/corrupt.before"
echo garbage > "$d/.git/index"; run_hook "$d"; rc=$?
ok "corrupt index: tracked file untouched, nothing else written" "cmp -s '$d/.claude/settings.json' '$work/corrupt.before' && no_side_files '$d'"
# git missing from PATH (the repo is still there)
bin="$work/nogit-bin"; mkdir -p "$bin"
for t in bash jq cp mkdir dirname basename realpath ls cat tr sed grep env cmp tail head find rm mv; do
  p=$(command -v "$t" 2>/dev/null) && [ -x "$p" ] && ln -sf "$p" "$bin/$t"
done
d=$(repo no-git-binary); commit_settings "$d"; cp "$d/.claude/settings.json" "$work/ngb.before"
(cd "$d" && PATH="$bin" bash "$script" >"$d/hook.out" 2>&1); rc=$?
ok "git missing from PATH: exit 0 and tracked file untouched" "[ $rc = 0 ] && cmp -s '$d/.claude/settings.json' '$work/ngb.before' && no_side_files '$d'"

# 10. Symlinks: the path is resolved before asking git
d=$(repo symdir); mkdir -p "$d/cfg"; rmdir "$d/.claude"; commit_settings "$d" cfg/settings.json; ln -s cfg "$d/.claude"
cp "$d/cfg/settings.json" "$work/symdir.before"; run_hook "$d"
ok ".claude symlinked to a tracked in-repo dir: file untouched" "cmp -s '$d/cfg/settings.json' '$work/symdir.before' && git -C '$d' diff --quiet"
d=$(repo symfile); commit_settings "$d" cfg/settings.json; ln -s ../cfg/settings.json "$d/.claude/settings.json"
cp "$d/cfg/settings.json" "$work/symfile.before"; run_hook "$d"
ok "settings.json symlinked to a tracked file: target untouched" "cmp -s '$d/cfg/settings.json' '$work/symfile.before'"
d=$(repo symdir-untracked); mkdir -p "$d/cfg"; rmdir "$d/.claude"; echo '{}' > "$d/cfg/settings.json"; ln -s cfg "$d/.claude"; run_hook "$d"
ok ".claude symlinked to an untracked in-repo dir: merged as before" "[ \"\$(jq -c '.permissions.allow | unique' '$d/cfg/settings.json')\" = '$want_allow' ]"
d="$work/outside-repo"; mkdir -p "$d/real" "$work/elsewhere"; echo '{}' > "$work/elsewhere/settings.json"; ln -s "$work/elsewhere" "$d/.claude"
git -C "$d" init -q; run_hook "$d"
ok ".claude symlinked outside the repo, target not in any repo: merged as before" "[ \"\$(jq -c '.permissions.allow | unique' '$work/elsewhere/settings.json')\" = '$want_allow' ]"

echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
