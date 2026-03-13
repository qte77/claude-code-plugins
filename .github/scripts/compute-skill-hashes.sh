#!/usr/bin/env bash
# compute-skill-hashes.sh
#
# Usage:
#   --check   (default) Verify content-hash in stable SKILL.md files matches body SHA256
#   --update  Recompute and write content-hash into each stable SKILL.md frontmatter
#
# Exit codes:
#   0  All stable skills pass hash verification (--check), or all hashes updated (--update)
#   1  One or more hash mismatches found (--check)

set -euo pipefail

MODE="${1:---check}"

if [[ "$MODE" != "--check" && "$MODE" != "--update" ]]; then
  echo "Usage: $0 [--check|--update]" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL_PATTERN="${REPO_ROOT}/plugins/*/skills/*/SKILL.md"

mismatches=0

# Extract the body of a SKILL.md file: everything after the closing --- of frontmatter.
# The closing --- is the second occurrence of a line containing only ---.
extract_body() {
  local file="$1"
  awk '
    /^---$/ { delim_count++; if (delim_count == 2) { found=1; next } }
    found { print }
  ' "$file"
}

# Extract a frontmatter value by key.
# Returns the value portion after "key: " on the matching line.
extract_frontmatter_value() {
  local file="$1"
  local key="$2"
  awk -v key="$key" '
    /^---$/ { delim_count++ }
    delim_count == 2 { exit }
    delim_count >= 1 && $0 ~ "^" key ": " {
      sub("^" key ": ", ""); print; exit
    }
  ' "$file"
}

# Check whether frontmatter contains a given key: value pair.
frontmatter_has_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  awk -v key="$key" -v val="$value" '
    /^---$/ { delim_count++ }
    delim_count == 2 { exit }
    delim_count >= 1 && $0 == key ": " val { found=1; exit }
    END { exit !found }
  ' "$file"
}

# Replace content-hash line inside frontmatter.
update_content_hash() {
  local file="$1"
  local new_hash="$2"
  local tmp
  tmp="$(mktemp)"

  awk -v new_hash="sha256:${new_hash}" '
    /^---$/ { delim_count++ }
    delim_count <= 2 && /^  content-hash: / {
      sub(/^  content-hash: .*/, "  content-hash: " new_hash)
    }
    { print }
  ' "$file" > "$tmp"

  mv "$tmp" "$file"
}

for skill_file in $SKILL_PATTERN; do
  [[ -f "$skill_file" ]] || continue

  # Check stability field inside metadata block.
  # We look for "  stability: stable" (two-space indent, inside metadata: block).
  stability=""
  in_frontmatter=0
  delim_count=0
  while IFS= read -r line; do
    if [[ "$line" == "---" ]]; then
      (( delim_count++ )) || true
      [[ $delim_count -eq 1 ]] && in_frontmatter=1
      [[ $delim_count -eq 2 ]] && break
      continue
    fi
    if [[ $in_frontmatter -eq 1 && "$line" =~ ^[[:space:]]*stability:[[:space:]]*(.+)$ ]]; then
      stability="${BASH_REMATCH[1]}"
    fi
  done < "$skill_file"

  if [[ "$stability" != "stable" ]]; then
    continue
  fi

  # Compute SHA256 of body content.
  body="$(extract_body "$skill_file")"
  actual_hash="$(printf '%s' "$body" | sha256sum | awk '{print $1}')"

  if [[ "$MODE" == "--update" ]]; then
    update_content_hash "$skill_file" "$actual_hash"
    echo "Updated: $skill_file"
    echo "  hash: sha256:${actual_hash}"
    continue
  fi

  # --check mode: read declared hash and compare.
  declared=""
  while IFS= read -r line; do
    if [[ "$line" == "---" ]]; then
      (( delim_count++ )) || true
      [[ $delim_count -eq 2 ]] && break
      continue
    fi
    if [[ "$line" =~ ^[[:space:]]*content-hash:[[:space:]]*(.+)$ ]]; then
      declared="${BASH_REMATCH[1]}"
    fi
  done < <(awk '/^---$/{c++} c==2{exit} {print}' "$skill_file")

  # Strip "sha256:" prefix if present.
  declared_hash="${declared#sha256:}"

  if [[ "$declared_hash" == "PENDING" || -z "$declared_hash" ]]; then
    echo "SKIP (no hash yet): $skill_file"
    continue
  fi

  if [[ "$actual_hash" != "$declared_hash" ]]; then
    echo "MISMATCH: $skill_file"
    echo "  declared: sha256:${declared_hash}"
    echo "  actual:   sha256:${actual_hash}"
    (( mismatches++ )) || true
  else
    echo "OK: $skill_file"
  fi
done

if [[ "$MODE" == "--check" ]]; then
  if [[ $mismatches -gt 0 ]]; then
    echo ""
    echo "ERROR: ${mismatches} stable SKILL.md file(s) have mismatched content hashes."
    echo "If you intentionally changed a stable skill, update its content-hash by running:"
    echo "  bash .github/scripts/compute-skill-hashes.sh --update"
    exit 1
  else
    echo ""
    echo "All stable skill hashes verified successfully."
  fi
fi
