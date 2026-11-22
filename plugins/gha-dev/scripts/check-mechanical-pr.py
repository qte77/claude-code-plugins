#!/usr/bin/env python3
"""Tier-1 check: PRs mechanical enough to merge without an AI reviewer.

Usage: check-mechanical-pr.py OWNER/REPO NUMBER
Prints PASS and exits 0 only for one of these two shapes, with every check on the head SUCCESS, SKIPPED or NEUTRAL:

  A. Action pins (workflow files only): every changed line is a `uses: owner/repo[/path]@<40-hex>` line with a
     `# tag` comment, each new SHA is that tag's commit upstream, and no `permissions:` line changed.
  B. Dependabot dependency bump (lock files and manifests only): the author is Dependabot, and every version change
     named in the title or body stays within the same major version (same minor for 0.x).

Anything else prints FAIL with reasons; the PR then needs a reviewer (tier 2: major bumps, docs and lock-file
changes not by Dependabot; tier 3: hooks, permissions, rulesets, workflow triggers, tokens).
"""

import json
import os
import re
import subprocess
import sys
import urllib.parse
from collections.abc import Callable
from typing import Any

USES = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w.-]+)(/[\w./-]+)?@([0-9a-f]{40})(?:\s*#\s*(\S+))?\s*$")
LOCK_FILES = {
    "uv.lock",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Gemfile.lock",
}
LOCK_PATTERN = re.compile(r"^requirements[\w.-]*\.(txt|in)$")
BUMP = re.compile(
    r"(?:^|\n)\s*(?:Bumps|Updates|bump)\s+\[?`?([\w@./-]+?)`?\]?(?:\([^)]*\))?\s+from\s+v?([\w.+-]+?)\s+to\s+v?([\w.+-]+?)\.?(?=\s|$)",
    re.I,
)


def gh(*args: str) -> str:
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {out.stderr.strip()[:200]}")
    return out.stdout


def tag_sha(repo: str, tag: str) -> str | None:
    """Commit SHA a tag points to, dereferencing annotated tags."""
    try:
        ref = json.loads(gh("api", f"repos/{repo}/git/ref/tags/{urllib.parse.quote(tag, safe='')}"))
    except RuntimeError:
        return None
    obj = ref["object"]
    while obj["type"] == "tag":
        obj = json.loads(gh("api", f"repos/{repo}/git/tags/{obj['sha']}"))["object"]
    return str(obj["sha"])


def is_workflow(path: str) -> bool:
    return path.startswith(".github/workflows/") or os.path.basename(path) in ("action.yml", "action.yaml")


def is_changelog(path: str) -> bool:
    return os.path.basename(path) == "CHANGELOG.md" or path.startswith("changelog.d/")


def is_lock(path: str) -> bool:
    name = os.path.basename(path)
    return name in LOCK_FILES or bool(LOCK_PATTERN.match(name))


def same_major(old: str, new: str) -> bool:
    """True when old -> new keeps the major version (the minor for 0.x)."""
    o, n = re.findall(r"\d+", old)[:2], re.findall(r"\d+", new)[:2]
    if not o or not n:
        return False
    if o[0] != n[0]:
        return False
    return o[0] != "0" or (len(o) > 1 and len(n) > 1 and o[1] == n[1])


def pin_reasons(diff: str, lookup: Callable[[str, str], str | None], reasons: list[str]) -> int:
    """Pure check of a workflow diff: only pinned `uses:` lines change, each added line replaces a removed line of
    the same action and path (only SHA and tag may change), and each new SHA is its tag's commit (via `lookup`)."""
    changed: list[str] = []
    for part in re.split(r"(?m)^(?=diff --git )", diff):
        m = re.match(r"diff --git a/(\S+)", part)
        if m and is_changelog(m.group(1)):
            continue  # changelog entries are prose; the file list check already limits them to changelog files
        changed += [ln for ln in part.splitlines() if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))]
    if not changed:
        reasons.append("empty diff")
    removed: list[tuple[str, str]] = []
    added: list[tuple[str, str]] = []
    checked: dict[tuple[str, str], str | None] = {}
    for line in changed:
        body = line[1:]
        if re.search(r"^\s*permissions\s*:", body):
            reasons.append(f"permissions line changed: {body.strip()}")
            continue
        m = USES.match(body)
        if not m:
            reasons.append(f"not a pinned uses line: {body.strip()[:100]}")
            continue
        target = (m.group(1).lower(), m.group(2) or "")
        if line[0] == "-":
            removed.append(target)
            continue
        added.append(target)
        action, sha, tag = m.group(1), m.group(3), m.group(4)
        if not tag:
            reasons.append(f"{action}@{sha[:8]} has no tag comment")
            continue
        key = (action, tag)
        if key not in checked:
            checked[key] = lookup(action, tag)
        if checked[key] != sha:
            reasons.append(f"{action} {tag} is {str(checked[key])[:8]}, pin is {sha[:8]}")
    if sorted(added) != sorted(removed):
        reasons.append("added uses lines do not replace removed lines of the same action and path")
    return len(checked)


def check_pins(repo: str, num: str, reasons: list[str]) -> int:
    return pin_reasons(gh("pr", "diff", num, "-R", repo), tag_sha, reasons)


def parse_bumps(title: str, body: str, reasons: list[str]) -> dict[str, tuple[str, str]]:
    """Version changes from the title and the part of the body before Dependabot's details and notes."""
    head = re.split(r"<details>|\n---|\n>", body, maxsplit=1)[0]
    bumps: dict[str, tuple[str, str]] = {}
    for m in BUMP.finditer(title + "\n" + head):
        pkg, change = m.group(1), (m.group(2), m.group(3))
        if bumps.get(pkg, change) != change:
            reasons.append(f"{pkg} is named with two different version changes")
        bumps[pkg] = change
    return bumps


def check_bump(view: dict[str, Any], reasons: list[str]) -> int:
    if view["author"]["login"] not in ("app/dependabot", "dependabot[bot]", "dependabot"):
        reasons.append(f"lock-file change not by Dependabot (author {view['author']['login']})")
    bumps = parse_bumps(view["title"], view["body"], reasons)
    if not bumps:
        reasons.append("no 'from X to Y' version change found in title or body")
    for pkg, (old, new) in bumps.items():
        if not same_major(old, new):
            reasons.append(f"major bump {pkg} {old} -> {new} (tier 2: read the release notes)")
    return len(bumps)


def main() -> int:
    repo, num = sys.argv[1], sys.argv[2]
    reasons: list[str] = []
    view = json.loads(
        gh("pr", "view", num, "-R", repo, "--json", "headRefOid,statusCheckRollup,files,author,title,body")
    )
    paths = [f["path"] for f in view["files"]]
    if paths and any(is_workflow(p) for p in paths) and all(is_workflow(p) or is_changelog(p) for p in paths):
        shape, count = "pin(s) verified", check_pins(repo, num, reasons)
    elif paths and all(is_lock(p) for p in paths):
        shape, count = "same-major bump(s)", check_bump(view, reasons)
    else:
        shape, count = "", 0
        reasons.append("files are neither workflow pins nor lock files only: " + ", ".join(paths[:6]))
    if not view["statusCheckRollup"]:
        reasons.append("no checks reported on the head commit")
    for c in view["statusCheckRollup"]:
        state = c.get("conclusion") or c.get("state") or c.get("status")
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            reasons.append(f"check {c.get('name') or c.get('context')}: {state}")
    # The diff above was read after the view; fail if the head moved in between, so PASS names a validated head
    now = json.loads(gh("pr", "view", num, "-R", repo, "--json", "headRefOid"))["headRefOid"]
    if now != view["headRefOid"]:
        reasons.append(f"head moved during the check ({view['headRefOid'][:8]} -> {now[:8]}); rerun")
    if reasons:
        print(f"FAIL {repo}#{num} {view['headRefOid']}")
        for r in reasons:
            print(f"  - {r}")
        return 1
    print(f"PASS {repo}#{num} {view['headRefOid']} ({count} {shape})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
