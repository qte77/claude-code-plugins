#!/usr/bin/env python3
"""Fail when a SKILL.md nests a reserved Claude Code frontmatter field under `metadata:`.

Claude Code reads fields such as `argument-hint` and `allowed-tools` only at the top level of the
frontmatter and does not act on `metadata:` contents; the skills docs also say not to reuse
frontmatter field names as `metadata` keys (https://code.claude.com/docs/en/skills).

ENFORCED grows as each field is moved out of `metadata:` (plan 2026-09-24-0001 row 31).
Stdlib only and line-based like compute-skill-hashes.sh, so CI needs no YAML package; it accepts\nany indent, quoted keys and a flow-style `metadata: {...}`.

Usage: check-skill-frontmatter.py [SKILL.md ...]   (default: every plugin and .claude skill)
"""

import pathlib
import re
import sys

ENFORCED = ("argument-hint", "allowed-tools", "disable-model-invocation")
# Reason: tolerate any indent, quoted keys and a space before the colon, so a style change can't hide a key
KEY = re.compile(r"""^(?P<indent>[ \t]*)(?:"(?P<dq>[^"]*)"|'(?P<sq>[^']*)'|(?P<plain>[A-Za-z0-9_.-]+))[ \t]*:(?:[ \t]+(?P<value>.*))?$""")
FLOW_KEY = re.compile(r"""[{,][ \t]*(?:"([^"]*)"|'([^']*)'|([A-Za-z0-9_.-]+))[ \t]*:""")
FIX = {
    "argument-hint": "move it to the top level as a quoted string",
    "allowed-tools": "rename it metadata.intended-tools (a top-level allowed-tools pre-approves tools and "
                     "needs an owner decision)",
    "disable-model-invocation": "move it to the top level",
}


def frontmatter(text: str) -> list[str] | None:
    lines = [line.rstrip("\r") for line in text.split("\n")]
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def nested(path: pathlib.Path, n: int, key: str) -> list[str]:
    if key not in ENFORCED:
        return []
    return [f"{path}:{n}: metadata.{key} reuses a reserved frontmatter field name; {FIX[key]}"]


def check_file(path: pathlib.Path) -> list[str]:
    fm = frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{path}: no frontmatter"]
    out = []
    in_metadata = False
    child_indent = None
    for n, line in enumerate(fm, 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY.match(line)
        indent = len(line) - len(line.lstrip(" \t"))
        if indent == 0:
            in_metadata, child_indent = False, None
            if not m:
                continue
            key = m.group("dq") or m.group("sq") or m.group("plain")
            value = (m.group("value") or "").strip()
            if key == "metadata":
                in_metadata = True
                if value.startswith("{"):
                    for k in FLOW_KEY.findall(value):
                        out += nested(path, n, next(x for x in k if x))
            elif key == "argument-hint" and not value.startswith(("'", '"')):
                out.append(f"{path}:{n}: argument-hint must be a quoted string (an unquoted [x] is a YAML list)")
            continue
        if in_metadata and m:
            # Reason: only direct children of metadata count; deeper keys belong to their own parent
            child_indent = indent if child_indent is None else child_indent
            if indent == child_indent:
                out += nested(path, n, m.group("dq") or m.group("sq") or m.group("plain"))
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
