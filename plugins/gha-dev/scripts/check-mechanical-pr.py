#!/usr/bin/env python3
"""Tier-1 check: workflow pin bumps mechanical enough to merge without an AI reviewer.

Usage: check-mechanical-pr.py OWNER/REPO NUMBER
Prints PASS and exits 0 only when all of these hold:

  - The PR author is a trusted bot (Dependabot or github-actions).
  - The changed files are workflow files or action.yml/action.yaml, optionally with the root CHANGELOG.md and
    new or edited changelog.d/*.md|rst fragments (a new fragment must be a regular file; fragments are not read).
    The files named in the diff equal the PR's file list, and that list is under 100 files.
  - In every change block (changed lines with no context line between), each removed `uses:` line pairs in order
    with an added line that is identical except for the SHA and the `# tag` comment: same indentation, action and
    path. The tag moves up within the same major version (same minor for 0.x) and each new SHA is that tag's
    commit upstream today. No `permissions:` line changes.
  - The diff has no rename, copy, mode change, binary section, or added or deleted file (a new changelog fragment
    excepted), no control or Unicode separator character in a changed line, and is valid UTF-8. It is split on
    newlines only.
  - The merge state is CLEAN, the check list is non-empty and every check is SUCCESS, SKIPPED or NEUTRAL, and the
    head did not move while the script ran.

Residuals by design: a pin with the same tag and a new SHA passes (it looks like a moved tag; the check proves the
SHA matches the tag today, not that the tag is trustworthy), and without required checks on the base branch a slow
workflow may not have registered its check yet. Lock-file and manifest bumps are not checked here; they are tier 2.

Anything else prints FAIL with reasons; the PR then needs a reviewer.
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
TRUSTED_BOTS = {"app/dependabot", "dependabot[bot]", "app/github-actions", "github-actions[bot]"}
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


def is_trusted_author(login: str) -> bool:
    return login in TRUSTED_BOTS


def version_parts(version: str) -> list[int] | None:
    m = VERSION.match(version)
    return [int(x) for x in m.group(1).split(".")] if m else None


def has_suffix(version: str) -> bool:
    """True when the version carries a prerelease or build suffix after its numbers."""
    m = VERSION.match(version)
    return bool(m and m.end(1) < len(version))


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
    read: bool = True  # False for changelog entries, which are listed but not read


def bad_char(line: str) -> bool:
    return any(unicodedata.category(c) in ("Cc", "Zl", "Zp") and c != "\t" for c in line)


class DiffParser:
    """Splits a git diff (on newlines only) into sections of change blocks.

    A new block starts at each `@@` and at each context line that follows changed lines, so a changed line cannot
    pair with a partner across context. Reasons are added for file operations, separator characters and files that
    `allowed` rejects. The ---/+++ lines are skipped in file headers only."""

    def __init__(self, allowed: Callable[[str], bool], reasons: list[str]) -> None:
        self.allowed, self.reasons = allowed, reasons
        self.sections: list[Section] = []
        self.current: Section | None = None
        self.hunk: Hunk | None = None

    def parse(self, diff: str) -> list[Section]:
        for line in diff.split("\n"):
            if line.startswith("diff --git "):
                self.start_file(line)
            elif self.hunk is None:
                self.header(line)
            elif line.startswith("@@"):
                self.new_block()
            elif line.startswith("\\"):
                continue  # "\ No newline at end of file" marker
            elif line.startswith(("+", "-")):
                self.changed(line)
            elif self.hunk.added or self.hunk.removed:
                self.new_block()  # a context line ends the block
        return self.sections

    def new_block(self) -> None:
        self.hunk = Hunk()
        if self.current is not None:
            self.current.hunks.append(self.hunk)

    def start_file(self, line: str) -> None:
        self.hunk, self.current = None, None
        m = re.match(r"diff --git a/(\S+) b/(\S+)$", line)
        if not m:
            self.reasons.append(f"unparseable file header: {line[:80]!r}")
        elif m.group(1) != m.group(2):
            self.reasons.append(f"file moved or renamed: {m.group(1)} -> {m.group(2)}")
        elif is_changelog(m.group(1)):
            self.current = Section(m.group(1), read=False)
        elif not self.allowed(m.group(2)):
            self.reasons.append(f"file is neither a workflow file nor a changelog entry:{m.group(2)}")
        else:
            self.current = Section(m.group(2))
        if self.current is not None:
            self.sections.append(self.current)

    def header(self, line: str) -> None:
        fragment = self.current is not None and not self.current.read
        if line.startswith(FILE_OPS):
            self.reasons.append(f"file operation not allowed: {line[:60]}")
        elif line.startswith("deleted file mode"):
            self.reasons.append(f"file deleted: {line}")
        elif line.startswith("new file mode") and not (fragment and line == "new file mode 100644"):
            self.reasons.append(f"file added: {line}")
        elif line.startswith("@@"):
            self.new_block()

    def changed(self, line: str) -> None:
        if self.current is None or self.hunk is None or not self.current.read:
            return
        if bad_char(line):
            self.reasons.append(f"control or separator character in a changed line: {line[:60]!r}")
        (self.hunk.added if line[0] == "+" else self.hunk.removed).append(line[1:])


def pin_reasons(
    diff: str, lookup: Callable[[str, str], str | None], reasons: list[str], files: set[str] | None = None
) -> int:
    """Pure check of a workflow diff (see the module docstring). Returns the number of pins verified.

    When `files` is given, the paths named in the diff must equal it."""
    sections = DiffParser(is_workflow, reasons).parse(diff)
    if files is not None and {s.path for s in sections} != files:
        reasons.append("files in the diff differ from the PR file list")
    if not any(h.added or h.removed for s in sections for h in s.hunks):
        reasons.append("empty diff")
    verified = 0
    for section in sections:
        if section.read and not any(h.added or h.removed for h in section.hunks):
            reasons.append(f"{section.path}: no changed line in a section that is read")
        for hunk in section.hunks:
            if len(hunk.added) != len(hunk.removed):
                reasons.append(f"{section.path}: a change block adds and removes a different number of lines")
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
    if has_suffix(new_tag) and not has_suffix(old_tag):
        reasons.append(f"{action} {old_tag} -> {new_tag} moves to a prerelease or suffixed tag (tier 2)")
        return 0
    found = lookup(action, new_tag)
    if found != sha:
        reasons.append(f"{action} {new_tag} is {str(found)[:8]}, pin is {sha[:8]}")
        return 0
    return 1


def pin_files_ok(paths: list[str]) -> bool:
    return bool(paths) and any(is_workflow(p) for p in paths) and all(is_workflow(p) or is_changelog(p) for p in paths)


def status_reasons(rollup: list[dict[str, Any]], merge_state: str, reasons: list[str]) -> None:
    if merge_state != "CLEAN":
        reasons.append(f"merge state is {merge_state}, not CLEAN")
    if not rollup:
        reasons.append("no checks reported on the head commit")
    for c in rollup:
        state = c.get("conclusion") or c.get("state") or c.get("status")
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            reasons.append(f"check {c.get('name') or c.get('context')}: {state}")


def head_reasons(before: str, now: str, reasons: list[str]) -> None:
    """The diff is read after the view; fail if the head moved in between, so PASS names a validated head."""
    if now != before:
        reasons.append(f"head moved during the check ({before[:8]} -> {now[:8]}); rerun")


def evaluate(
    view: dict[str, Any], fetch_diff: Callable[[], bytes], lookup: Callable[[str, str], str | None]
) -> tuple[list[str], int]:
    """Decide from a PR view and a lazily fetched diff. Returns (reasons, verified pin count)."""
    reasons: list[str] = []
    paths = [f["path"] for f in view["files"]]
    login = view["author"]["login"]
    count = 0
    if len(paths) >= 100:
        reasons.append("100 or more changed files; the file list may be truncated")
    if not pin_files_ok(paths):
        reasons.append("files are not workflow pins only: " + ", ".join(paths[:6]))
    elif not is_trusted_author(login):
        reasons.append(f"author {login} is not a trusted bot")
    else:
        try:
            diff = fetch_diff().decode("utf-8")
        except UnicodeDecodeError:
            reasons.append("diff is not valid UTF-8")
        else:
            count = pin_reasons(diff, lookup, reasons, set(paths))
    status_reasons(view["statusCheckRollup"], view["mergeStateStatus"], reasons)
    return reasons, count


def main() -> int:
    repo, num = sys.argv[1], sys.argv[2]
    fields = "headRefOid,statusCheckRollup,mergeStateStatus,files,author"
    view = json.loads(gh("pr", "view", num, "-R", repo, "--json", fields))
    reasons, count = evaluate(view, lambda: gh_bytes("pr", "diff", num, "-R", repo), tag_sha)
    now = json.loads(gh("pr", "view", num, "-R", repo, "--json", "headRefOid"))["headRefOid"]
    head_reasons(view["headRefOid"], now, reasons)
    if reasons:
        print(f"FAIL {repo}#{num} {view['headRefOid']}")
        for r in reasons:
            print(f"  - {r}")
        return 1
    print(f"PASS {repo}#{num} {view['headRefOid']} ({count} pin(s) verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
