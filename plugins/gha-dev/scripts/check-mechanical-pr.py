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
    r"(?:^|\n)\s*(?:Bumps|Updates|bump)\s+\[?`?([\w@./-]+?)`?\]?(?:\([^)]*\))?"
    r"\s+from\s+v?([\w.+-]+?)\s+to\s+v?([\w.+-]+?)\.?(?=\s|$)",
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
        ref = json.loads(gh("api", f"repos/{repo}/git/ref/tags/{tag}"))
    except RuntimeError:
        return None
    obj = ref["object"]
    while obj["type"] == "tag":
        obj = json.loads(gh("api", f"repos/{repo}/git/tags/{obj['sha']}"))["object"]
    return obj["sha"]


def is_workflow(path: str) -> bool:
    return path.startswith(".github/workflows/") or os.path.basename(path) in ("action.yml", "action.yaml")


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


def check_pins(repo: str, num: str, reasons: list[str]) -> int:
    diff = gh("pr", "diff", num, "-R", repo)
    changed = [ln for ln in diff.splitlines() if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))]
    if not changed:
        reasons.append("empty diff")
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
        if line[0] == "+":
            action, sha, tag = m.group(1), m.group(3), m.group(4)
            if not tag:
                reasons.append(f"{action}@{sha[:8]} has no tag comment")
                continue
            key = (action, tag)
            if key not in checked:
                checked[key] = tag_sha(action, tag)
            if checked[key] != sha:
                reasons.append(f"{action} {tag} is {str(checked[key])[:8]}, pin is {sha[:8]}")
    return len(checked)


def check_bump(view: dict, reasons: list[str]) -> int:
    if view["author"]["login"] not in ("app/dependabot", "dependabot[bot]", "dependabot"):
        reasons.append(f"lock-file change not by Dependabot (author {view['author']['login']})")
    bumps = {m.group(1): (m.group(2), m.group(3)) for m in BUMP.finditer(view["title"] + "\n" + view["body"])}
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
    if paths and all(is_workflow(p) for p in paths):
        shape, count = "pin(s) verified", check_pins(repo, num, reasons)
    elif paths and all(is_lock(p) for p in paths):
        shape, count = "same-major bump(s)", check_bump(view, reasons)
    else:
        shape, count = "", 0
        reasons.append("files are neither workflow pins nor lock files only: " + ", ".join(paths[:6]))
    for c in view["statusCheckRollup"]:
        state = c.get("conclusion") or c.get("state") or c.get("status")
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            reasons.append(f"check {c.get('name') or c.get('context')}: {state}")
    if reasons:
        print(f"FAIL {repo}#{num} {view['headRefOid']}")
        for r in reasons:
            print(f"  - {r}")
        return 1
    print(f"PASS {repo}#{num} {view['headRefOid']} ({count} {shape})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
