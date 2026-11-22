#!/usr/bin/env bash
# Regression check for the SessionStart setup hooks' settings step: a git-tracked
# .claude/settings.json is never modified; the plugin's permissions.allow goes to the untracked
# .claude/settings.local.json instead. Usage: setup-settings-test.sh <plugin dir> <hook script>
#   e.g. setup-settings-test.sh plugins/workspace-setup plugins/workspace-setup/hooks/scripts/setup-workspace.sh
set -uo pipefail
plugin=$(realpath "$1") script=$(realpath "$2")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
export HOME="$work/home"; mkdir -p "$HOME"
# Reason: a developer's global git ignore (Claude Code adds **/.claude/settings.local.json to it)
# would hide what the hook does; isolate git from user and system config
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
run_hook() { (cd "$1" && bash "$script" >"$1/hook.out" 2>&1); }

# 1. No settings.json: the template is copied (unchanged behaviour)
d=$(repo fresh); run_hook "$d"
ok "missing settings.json is created from the template" "cmp -s '$d/.claude/settings.json' '$source_settings'"

# 2. Untracked settings.json: allow entries merge into it (unchanged behaviour)
d=$(repo untracked); echo '{"env":{"A":"1"}}' > "$d/.claude/settings.json"; run_hook "$d"
ok "untracked settings.json gains the plugin allow list" \
  "[ \"\$(jq -c '.permissions.allow | unique' '$d/.claude/settings.json')\" = '$want_allow' ]"
ok "untracked settings.json keeps its other keys" "[ \"\$(jq -r .env.A '$d/.claude/settings.json')\" = 1 ]"

# 3. Tracked settings.json: left byte-identical; allow entries go to settings.local.json
d=$(repo tracked); printf '{\n  "env": {"A": "1"}\n}\n' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init
run_hook "$d"
ok "tracked settings.json is not modified" "git -C '$d' diff --quiet -- .claude/settings.json"
ok "allow list lands in settings.local.json" \
  "[ \"\$(jq -c '.permissions.allow | unique' '$d/.claude/settings.local.json')\" = '$want_allow' ]"
ok "settings.local.json stays untracked" "! git -C '$d' ls-files --error-unmatch .claude/settings.local.json >/dev/null 2>&1"
ok "settings.local.json is git-ignored, so it can't be committed by accident" "git -C '$d' check-ignore -q .claude/settings.local.json"
ok "the ignore is local (.git/info/exclude), not .gitignore" "grep -qxF '**/.claude/settings.local.json' '$d/.git/info/exclude' && ! grep -qs 'settings.local.json' '$d/.gitignore'"
before=$(cat "$d/.claude/settings.local.json"); export before; run_hook "$d"
ok "a second run changes nothing and adds no second exclude line" "[ \"\$(cat '$d/.claude/settings.local.json')\" = \"\$before\" ] && [ \"\$(grep -cxF '**/.claude/settings.local.json' '$d/.git/info/exclude')\" = 1 ]"
jq '.permissions.allow += ["Bash(zzz-user-rule)"]' "$d/.claude/settings.local.json" > "$d/x" && mv "$d/x" "$d/.claude/settings.local.json"
before=$(cat "$d/.claude/settings.local.json"); export before; run_hook "$d"
ok "a rule the user appended is not re-sorted or rewritten" "[ \"\$(cat '$d/.claude/settings.local.json')\" = \"\$before\" ]"

# 4. Tracked settings.json plus an existing untracked settings.local.json: merged, other keys kept
d=$(repo local-exists); echo '{}' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init
echo '{"permissions":{"allow":["Bash(make test)"]},"model":"x"}' > "$d/.claude/settings.local.json"
run_hook "$d"
ok "existing local allow entry is kept" "jq -e '.permissions.allow | index(\"Bash(make test)\")' '$d/.claude/settings.local.json' >/dev/null"
ok "existing local keys are kept" "[ \"\$(jq -r .model '$d/.claude/settings.local.json')\" = x ]"
ok "plugin allow entries are added to the local file" \
  "[ \"\$(jq -c '[.permissions.allow[] | select(. != \"Bash(make test)\")] | unique' '$d/.claude/settings.local.json')\" = '$want_allow' ]"

# 5. Both files tracked: nothing is written, and the hook says why
d=$(repo both-tracked); echo '{}' > "$d/.claude/settings.json"; echo '{}' > "$d/.claude/settings.local.json"
git -C "$d" add -f .claude; git -C "$d" commit -qm init
run_hook "$d"
ok "tracked settings.local.json is not modified" "git -C '$d' diff --quiet -- .claude"
ok "the hook reports the skipped merge" "grep -q 'tracked' '$d/hook.out'"

# 6. Exclude file without a trailing newline: the user's last pattern stays intact
d=$(repo no-newline); echo '{}' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init
printf 'keep-me' > "$d/.git/info/exclude"; run_hook "$d"
ok "an exclude file without a final newline keeps its last pattern" "grep -qx 'keep-me' '$d/.git/info/exclude' && git -C '$d' check-ignore -q .claude/settings.local.json"

# 7. Read-only .git/info: the hook still exits 0, deploys the rest and warns
d=$(repo readonly); echo '{}' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init
chmod a-w "$d/.git/info/exclude" "$d/.git/info"; (cd "$d" && bash "$script" >"$d/hook.out" 2>&1); rc=$?; chmod u+w "$d/.git/info" "$d/.git/info/exclude"
ok "read-only .git/info: the hook exits 0" "[ $rc = 0 ]"
ok "read-only .git/info: the hook warns that the local file is not ignored" "grep -q 'not git-ignored' '$d/hook.out'"
ok "read-only .git/info: governance files are still deployed" "ls '$d'/*.md >/dev/null 2>&1 || [ -z \"\$(ls '$plugin'/governance/*.md 2>/dev/null)\" ]"

# 8. Malformed settings.local.json: left alone, the hook exits 0 and warns
d=$(repo malformed); echo '{}' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init
echo '{bad' > "$d/.claude/settings.local.json"; (cd "$d" && bash "$script" >"$d/hook.out" 2>&1); rc=$?
ok "malformed local file: the hook exits 0" "[ $rc = 0 ]"
ok "malformed local file is not rewritten" "[ \"\$(cat '$d/.claude/settings.local.json')\" = '{bad' ]"
ok "malformed local file: the hook warns" "grep -q 'not a JSON object' '$d/hook.out'"

# 9. A tracked settings.json deleted from the working tree is not recreated from the template
d=$(repo deleted); echo '{}' > "$d/.claude/settings.json"
git -C "$d" add .claude/settings.json; git -C "$d" commit -qm init; rm "$d/.claude/settings.json"
run_hook "$d"
ok "a deleted tracked settings.json stays deleted" "[ ! -e '$d/.claude/settings.json' ]"

# 10. Run from a subdirectory with its own tracked .claude: the local file is still ignored
d=$(repo subdir); mkdir -p "$d/sub/.claude"; echo '{}' > "$d/sub/.claude/settings.json"
git -C "$d" add sub/.claude/settings.json; git -C "$d" commit -qm init
run_hook "$d/sub"
ok "subdirectory: the local file there is git-ignored" "git -C '$d' check-ignore -q sub/.claude/settings.local.json"

# 11. Not a git repo: behaves as before (merge into settings.json), exit 0
d="$work/nogit"; mkdir -p "$d/.claude"; echo '{}' > "$d/.claude/settings.json"
(cd "$d" && bash "$script" >"$d/hook.out" 2>&1); rc=$?
ok "outside git: the hook exits 0 and merges into settings.json" "[ $rc = 0 ] && [ \"\$(jq -c '.permissions.allow | unique' '$d/.claude/settings.json')\" = '$want_allow' ]"

echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
