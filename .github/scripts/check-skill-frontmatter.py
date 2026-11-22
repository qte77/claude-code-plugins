#!/usr/bin/env python3
"""Fail when a SKILL.md nests a reserved Claude Code frontmatter field under `metadata:`.

Claude Code reads fields such as `argument-hint` and `allowed-tools` only at the top level of the
frontmatter and does not act on `metadata:` contents; the skills docs also say not to reuse
frontmatter field names as `metadata` keys (https://code.claude.com/docs/en/skills).

ENFORCED grows as each field is moved out of `metadata:` (plan 2026-09-24-0001 row 31).
Stdlib only, line-based like compute-skill-hashes.sh, so CI needs no YAML package.

Usage: check-skill-frontmatter.py [SKILL.md ...]   (default: every plugin and .claude skill)
"""

import pathlib
import re
import sys

ENFORCED = ("argument-hint", "allowed-tools")
TOP_KEY = re.compile(r"^([A-Za-z0-9_-]+):(.*)$")
NESTED_KEY = re.compile(r"^  ([A-Za-z0-9_-]+):")


def frontmatter(text: str) -> list[str] | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def check_file(path: pathlib.Path) -> list[str]:
    fm = frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{path}: no frontmatter"]
    out = []
    in_metadata = False
    for n, line in enumerate(fm, 2):
        top = TOP_KEY.match(line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            in_metadata = key == "metadata"
            if key == "argument-hint" and not value.startswith(("'", '"')):
                out.append(f"{path}:{n}: argument-hint must be a quoted string (an unquoted [x] is a YAML list)")
            continue
        nested = NESTED_KEY.match(line)
        if in_metadata and nested and nested.group(1) in ENFORCED:
            out.append(f"{path}:{n}: metadata.{nested.group(1)} is a reserved top-level field; "
                       "move it to the top level or rename it")
    return out


def main(argv: list[str]) -> int:
    root = pathlib.Path(__file__).resolve().parents[2]
    files = [pathlib.Path(a) for a in argv] or sorted(
        [*root.glob("plugins/*/skills/*/SKILL.md"), *root.glob(".claude/skills/*/SKILL.md")]
    )
    problems = [p for f in files for p in check_file(f)]
    for p in problems:
        print(p)
    print(f"{len(files)} SKILL.md checked, {len(problems)} problem(s); enforced: {', '.join(ENFORCED)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
