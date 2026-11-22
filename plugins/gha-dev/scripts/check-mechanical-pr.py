#!/usr/bin/env python3
"""Tier-1 check: PRs mechanical enough to merge without an AI reviewer.

Usage: check-mechanical-pr.py OWNER/REPO NUMBER
Prints PASS and exits 0 only when the PR author is a trusted bot, the head commit is CLEAN with a non-empty list of
checks that are all SUCCESS, SKIPPED or NEUTRAL, the head did not move while the script ran, and the PR has one of
these two shapes:

  A. Action pins: the changed files are workflow files or action.yml/action.yaml (plus the root CHANGELOG.md and new
     or edited changelog.d/*.md|rst fragments, which are not read). In every hunk, each removed line pairs in order
     with an added line that is identical except for the SHA and the `# tag` comment: same indentation, action and
     path. The tag only moves up within the same major version (same minor for 0.x), and each new SHA is that tag's
     commit upstream. No `permissions:` line changes. Authors: Dependabot or github-actions.
  B. Dependabot bump: only lock files and manifests change. Every commit is authored by dependabot[bot] with a
     verified signature. Every version change in the title, package table and `Updates` lines (release notes are
     ignored) stays within the same major (same minor for 0.x), and a "with N updates" group parses N packages.
     Lock files are not read line by line. A manifest line may only change the version of a package named in the
     bumps (old version replaced by the new one, nothing else).

The diff is rejected if it renames, copies, changes the mode of, adds or deletes (except a new changelog fragment) or
is binary for any file, if a changed line holds a control or Unicode separator character, if the diff is not valid
UTF-8, or if it touches a file that does not fit the shape. The diff is split on newlines only.

Anything else prints FAIL with reasons; the PR then needs a reviewer (tier 2: major bumps, docs and lock-file
changes not by Dependabot; tier 3: hooks, permissions, rulesets, workflow triggers, tokens).
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

USES = re.compile(
    r"^( *(?:- +)?)uses:[ ]+([\w.-]+/[\w.-]+)(/[\w./-]+)?@([0-9a-f]{40})(?:[ \t]+#[ \t]*(\S+))?[ \t]*$", re.ASCII
)
LOCK_FILES = {
    "uv.lock",
    "poetry.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
    "go.sum",
    "Gemfile.lock",
}
MANIFEST_FILES = {"pyproject.toml", "package.json", "Cargo.toml", "go.mod"}
MANIFEST_PATTERN = re.compile(r"^requirements[\w.-]*\.(txt|in)$")
DEPENDABOT = {"app/dependabot", "dependabot[bot]"}
TRUSTED_BOTS = DEPENDABOT | {"app/github-actions", "github-actions[bot]"}
FILE_OPS = (
    "rename from",
    "rename to",
    "similarity index",
    "dissimilarity index",
    "copy from",
    "copy to",
    "old mode",
    "new mode",
    "Binary files",
    "GIT binary patch",
)
BUMP = re.compile(
    r"(?:^|\n)\s*(?:Bumps|Updates|bump)\s+\[?`?([\w@./-]+?)`?\]?(?:\([^)]*\))?\s+from\s+v?([\w.+-]+?)\s+to\s+v?([\w.+-]+?)\.?(?=\s|$)",
    re.I,
)
TABLE_ROW = re.compile(
    r"^\|\s*\[?`?([\w@./-]+?)`?\]?(?:\([^)]*\))?\s*\|\s*`?v?([\w.+-]+?)`?\s*\|\s*`?v?([\w.+-]+?)`?\s*\|\s*$", re.M
)
VERSION = re.compile(r"^v?(\d+(?:\.\d+)*)(?:[-+._].*)?$", re.ASCII)


def gh_bytes(*args: str) -> bytes:
    out = subprocess.run(["gh", *args], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {out.stderr.decode(errors='replace').strip()[:200]}")
    return out.stdout


def gh(*args: str) -> str:
    return gh_bytes(*args).decode("utf-8")


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
    """Root CHANGELOG.md, or a markdown or rst fragment directly under changelog.d/."""
    return path == "CHANGELOG.md" or bool(re.fullmatch(r"changelog\.d/[\w.-]+\.(md|rst)", path, re.ASCII))


def is_manifest(path: str) -> bool:
    name = os.path.basename(path)
    return name in MANIFEST_FILES or bool(MANIFEST_PATTERN.match(name))


def is_lock(path: str) -> bool:
    return os.path.basename(path) in LOCK_FILES or is_manifest(path)


def is_trusted_author(login: str, allowed: set[str] = TRUSTED_BOTS) -> bool:
    return login in allowed


def version_parts(version: str) -> list[int] | None:
    m = VERSION.match(version)
    return [int(x) for x in m.group(1).split(".")] if m else None


def same_major(old: str, new: str) -> bool:
    """True when old -> new keeps the major version (the minor for 0.x)."""
    o, n = version_parts(old), version_parts(new)
    if not o or not n or o[0] != n[0]:
        return False
    return o[0] != 0 or (len(o) > 1 and len(n) > 1 and o[1] == n[1])


def not_lower(old: str, new: str) -> bool:
    o, n = version_parts(old), version_parts(new)
    if not o or not n:
        return False
    width = max(len(o), len(n))
    return n + [0] * (width - len(n)) >= o + [0] * (width - len(o))


@dataclass
class Hunk:
    removed: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)


@dataclass
class Section:
    path: str
    hunks: list[Hunk] = field(default_factory=list)


def bad_char(line: str) -> bool:
    return any(unicodedata.category(c) in ("Cc", "Zl", "Zp") and c != "\t" for c in line)


def parse_diff(diff: str, allowed: Callable[[str], bool], reasons: list[str]) -> list[Section]:
    """Split a git diff on newlines only into sections with per-hunk removed and added lines.

    Fails (adds reasons) on renames, copies, mode changes, binary sections, new or deleted files other than a
    new changelog fragment, files that `allowed` rejects, and changed lines holding control or separator characters.
    Changelog sections (same path on both sides) are dropped unread.
    The ---/+++ lines are skipped in file headers only."""
    sections: list[Section] = []
    current: Section | None = None
    hunk: Hunk | None = None
    fragment = False  # the current file is a changelog entry (same path both sides): its content is not read
    for line in diff.split("\n"):
        if line.startswith("diff --git "):
            hunk, current, fragment = None, None, False
            m = re.match(r"diff --git a/(\S+) b/(\S+)$", line)
            if not m:
                reasons.append(f"unparseable file header: {line[:80]!r}")
            elif m.group(1) != m.group(2):
                reasons.append(f"file moved or renamed: {m.group(1)} -> {m.group(2)}")
            elif is_changelog(m.group(1)):
                fragment = True
            elif not allowed(m.group(2)):
                reasons.append(f"file not allowed in this shape: {m.group(2)}")
            else:
                current = Section(m.group(2))
                sections.append(current)
        elif hunk is None:  # file header: extended header lines and the ---/+++ paths
            if line.startswith(FILE_OPS):
                reasons.append(f"file operation not allowed: {line[:60]}")
            elif line.startswith("deleted file mode") or (line.startswith("new file mode") and not fragment):
                reasons.append(f"file added or deleted: {line}")
            elif line.startswith("@@"):
                hunk = Hunk()
                if current is not None:
                    current.hunks.append(hunk)
        elif line.startswith("@@"):
            hunk = Hunk()
            if current is not None:
                current.hunks.append(hunk)
        elif line.startswith(("+", "-")) and current is not None:
            if bad_char(line):
                reasons.append(f"control or separator character in a changed line: {line[:60]!r}")
            (hunk.added if line[0] == "+" else hunk.removed).append(line[1:])
    return sections


def pin_reasons(diff: str, lookup: Callable[[str, str], str | None], reasons: list[str]) -> int:
    """Pure check of a workflow diff (see the module docstring, shape A). Returns the number of pins verified."""
    sections = parse_diff(diff, is_workflow, reasons)
    if not any(h.added or h.removed for s in sections for h in s.hunks):
        reasons.append("empty diff")
    verified = 0
    for section in sections:
        for hunk in section.hunks:
            if len(hunk.added) != len(hunk.removed):
                reasons.append(f"{section.path}: a hunk adds and removes a different number of lines")
                continue
            for old, new in zip(hunk.removed, hunk.added, strict=True):
                verified += pair_reasons(old, new, lookup, reasons)
    return verified


def pair_reasons(old: str, new: str, lookup: Callable[[str, str], str | None], reasons: list[str]) -> int:
    for body in (old, new):
        if re.search(r"^\s*permissions\s*:", body):
            reasons.append(f"permissions line changed: {body.strip()}")
            return 0
    o, n = USES.match(old), USES.match(new)
    if not o or not n:
        reasons.append(f"not a pinned uses line: {(new if o else old).strip()[:100]}")
        return 0
    if o.group(1, 2, 3) != n.group(1, 2, 3):
        reasons.append(f"added line is not the removed line with a new SHA and tag: {n.group(2)}{n.group(3) or ''}")
        return 0
    action, sha, old_tag, new_tag = n.group(2), n.group(4), o.group(5), n.group(5)
    if not old_tag or not new_tag:
        reasons.append(f"{action} pin lacks a tag comment")
        return 0
    if not same_major(old_tag, new_tag) or not not_lower(old_tag, new_tag):
        reasons.append(f"{action} {old_tag} -> {new_tag} is a major bump or a downgrade (tier 2)")
        return 0
    found = lookup(action, new_tag)
    if found != sha:
        reasons.append(f"{action} {new_tag} is {str(found)[:8]}, pin is {sha[:8]}")
        return 0
    return 1


def parse_bumps(title: str, body: str, reasons: list[str]) -> dict[str, tuple[str, str]]:
    """Version changes from the title, Dependabot's package table and its `Updates x from a to b` lines.

    Release notes inside <details> blocks and quoted lines are dropped first. A grouped PR ("with N updates") must
    yield exactly N packages, so a body format this parser does not understand fails instead of passing."""
    text = re.sub(r"(?is)<details>.*?</details>", "", body)
    text = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(">"))
    bumps: dict[str, tuple[str, str]] = {}
    found = [(m.group(1), (m.group(2), m.group(3))) for m in BUMP.finditer(title + "\n" + text)]
    found += [
        (m.group(1), (m.group(2), m.group(3)))
        for m in TABLE_ROW.finditer(text)
        if m.group(1).lower() != "package" and not set(m.group(1)) <= set("-:")
    ]
    for pkg, change in found:
        if bumps.get(pkg, change) != change:
            reasons.append(f"{pkg} is named with two different version changes")
        bumps[pkg] = change
    group = re.search(r"with (\d+) updates?", title + "\n" + text)
    if group and int(group.group(1)) != len(bumps):
        reasons.append(f"group says {group.group(1)} updates but {len(bumps)} were parsed")
    return bumps


def commit_reasons(commits: list[dict[str, Any]], reasons: list[str]) -> None:
    """Every PR commit must be authored by Dependabot with a verified signature."""
    if not commits:
        reasons.append("no commits listed for the PR")
    for c in commits:
        login = (c.get("author") or {}).get("login")
        if login != "dependabot[bot]":
            reasons.append(f"commit not authored by dependabot[bot] (author {login})")
        if not ((c.get("commit") or {}).get("verification") or {}).get("verified"):
            reasons.append("commit signature is not verified")


def manifest_reasons(diff: str, bumps: dict[str, tuple[str, str]], reasons: list[str]) -> None:
    """Lock files are not read. A manifest line may only swap the old version of a named package for the new one."""
    for section in parse_diff(diff, is_lock, reasons):
        if not is_manifest(section.path):
            continue
        for hunk in section.hunks:
            if len(hunk.added) != len(hunk.removed):
                reasons.append(f"{section.path}: a hunk adds and removes a different number of lines")
                continue
            for old, new in zip(hunk.removed, hunk.added, strict=True):
                ok = any(
                    pkg.lower() in old.lower() and v_old in old and old.replace(v_old, v_new) == new
                    for pkg, (v_old, v_new) in bumps.items()
                )
                if not ok:
                    reasons.append(f"{section.path}: not a version-only change of a bumped package: {new.strip()[:80]}")


def bump_reasons(view: dict[str, Any], commits: list[dict[str, Any]], diff: str, reasons: list[str]) -> int:
    bumps = parse_bumps(view["title"], view["body"], reasons)
    if not bumps:
        reasons.append("no 'from X to Y' version change found in title or body")
    for pkg, (old, new) in bumps.items():
        if not same_major(old, new):
            reasons.append(f"major bump {pkg} {old} -> {new} (tier 2: read the release notes)")
    commit_reasons(commits, reasons)
    manifest_reasons(diff, bumps, reasons)
    return len(bumps)


def choose_shape(paths: list[str]) -> str | None:
    if paths and any(is_workflow(p) for p in paths) and all(is_workflow(p) or is_changelog(p) for p in paths):
        return "pins"
    if paths and all(is_lock(p) for p in paths):
        return "bump"
    return None


def status_reasons(rollup: list[dict[str, Any]], merge_state: str, reasons: list[str]) -> None:
    if merge_state != "CLEAN":
        reasons.append(f"merge state is {merge_state}, not CLEAN")
    if not rollup:
        reasons.append("no checks reported on the head commit")
    for c in rollup:
        state = c.get("conclusion") or c.get("state") or c.get("status")
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            reasons.append(f"check {c.get('name') or c.get('context')}: {state}")


def evaluate(
    view: dict[str, Any],
    fetch_diff: Callable[[], bytes],
    fetch_commits: Callable[[], list[dict[str, Any]]],
    lookup: Callable[[str, str], str | None],
) -> tuple[list[str], str, int]:
    """Decide from a PR view and lazily fetched diff and commits. Returns (reasons, shape, verified count)."""
    reasons: list[str] = []
    paths = [f["path"] for f in view["files"]]
    shape = choose_shape(paths)
    login = view["author"]["login"]
    if len(paths) >= 100:
        reasons.append("100 or more changed files; the file list may be truncated")
    count = 0
    if shape is None:
        reasons.append("files are neither workflow pins nor lock files only: " + ", ".join(paths[:6]))
    elif not is_trusted_author(login, DEPENDABOT if shape == "bump" else TRUSTED_BOTS):
        reasons.append(f"author {login} is not a trusted bot for this shape")
    else:
        try:
            diff = fetch_diff().decode("utf-8")
        except UnicodeDecodeError:
            reasons.append("diff is not valid UTF-8")
        else:
            if shape == "pins":
                count = pin_reasons(diff, lookup, reasons)
            else:
                count = bump_reasons(view, fetch_commits(), diff, reasons)
    status_reasons(view["statusCheckRollup"], view["mergeStateStatus"], reasons)
    return reasons, shape or "", count


def main() -> int:
    repo, num = sys.argv[1], sys.argv[2]
    view = json.loads(
        gh(
            "pr",
            "view",
            num,
            "-R",
            repo,
            "--json",
            "headRefOid,statusCheckRollup,mergeStateStatus,files,author,title,body",
        )
    )
    reasons, shape, count = evaluate(
        view,
        lambda: gh_bytes("pr", "diff", num, "-R", repo),
        lambda: json.loads(gh("api", f"repos/{repo}/pulls/{num}/commits?per_page=100")),
        lambda action, tag: tag_sha(action, tag),
    )
    # The diff above was read after the view; fail if the head moved in between, so PASS names a validated head
    now = json.loads(gh("pr", "view", num, "-R", repo, "--json", "headRefOid"))["headRefOid"]
    if now != view["headRefOid"]:
        reasons.append(f"head moved during the check ({view['headRefOid'][:8]} -> {now[:8]}); rerun")
    if reasons:
        print(f"FAIL {repo}#{num} {view['headRefOid']}")
        for r in reasons:
            print(f"  - {r}")
        return 1
    print(f"PASS {repo}#{num} {view['headRefOid']} ({count} {'pin(s) verified' if shape == 'pins' else 'bump(s)'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
