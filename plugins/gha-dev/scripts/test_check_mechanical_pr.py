"""Tests for check-mechanical-pr.py (stdlib unittest; run: python3 -m unittest discover -s plugins/gha-dev/scripts)."""

import importlib.util
import pathlib
import unittest

_SPEC = importlib.util.spec_from_file_location(
    "check_mechanical_pr", pathlib.Path(__file__).with_name("check-mechanical-pr.py")
)
assert _SPEC is not None and _SPEC.loader is not None
cmp = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cmp)


class SameMajor(unittest.TestCase):
    def test_minor_and_patch_bumps_pass(self) -> None:
        self.assertTrue(cmp.same_major("1.2.3", "1.9.0"))
        self.assertTrue(cmp.same_major("v2.0.0", "2.0.1"))

    def test_major_bump_fails(self) -> None:
        self.assertFalse(cmp.same_major("1.9.9", "2.0.0"))

    def test_zero_major_needs_same_minor(self) -> None:
        self.assertTrue(cmp.same_major("0.3.1", "0.3.9"))
        self.assertFalse(cmp.same_major("0.3.9", "0.4.0"))

    def test_unparseable_version_fails(self) -> None:
        self.assertFalse(cmp.same_major("main", "1.0.0"))


class Classifiers(unittest.TestCase):
    def test_pinned_uses_line(self) -> None:
        line = "      - uses: actions/checkout@" + "a" * 40 + " # v4.1.0"
        m = cmp.USES.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(5), "v4.1.0")
        self.assertIsNone(cmp.USES.match("      - uses: actions/checkout@v4"))


SHA_A = "a" * 40
SHA_B = "b" * 40


def uses(action: str, sha: str, tag: str) -> str:
    return f"      - uses: {action}@{sha} # {tag}"


def file_diff(path: str, *lines: str) -> str:
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n" + "\n".join(lines) + "\n"


WF = ".github/workflows/ci.yaml"
OLD = "-" + uses("actions/checkout", SHA_A, "v4.0.0")
NEW = "+" + uses("actions/checkout", SHA_B, "v4.1.0")
TAGS = {("actions/checkout", "v4.1.0"): SHA_B}


def pin_problems(diff: str, tags: dict[tuple[str, str], str]) -> list[str]:
    reasons: list[str] = []
    cmp.pin_reasons(diff, lambda action, tag: tags.get((action, tag)), reasons)
    return reasons


class PinReasons(unittest.TestCase):
    wf = ".github/workflows/ci.yaml"

    def test_same_action_sha_and_tag_change_passes(self) -> None:
        diff = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v4.0.0"), "+" + uses("actions/checkout", SHA_B, "v4.1.0")
        )
        self.assertEqual(pin_problems(diff, {("actions/checkout", "v4.1.0"): SHA_B}), [])

    def test_swap_to_a_different_action_fails(self) -> None:
        diff = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v4.0.0"), "+" + uses("evil/checkout", SHA_B, "v1")
        )
        self.assertTrue(pin_problems(diff, {("evil/checkout", "v1"): SHA_B}))

    def test_add_only_uses_line_fails(self) -> None:
        diff = file_diff(self.wf, "+" + uses("evil/action", SHA_B, "v1"))
        self.assertTrue(pin_problems(diff, {("evil/action", "v1"): SHA_B}))

    def test_sha_not_matching_tag_fails(self) -> None:
        diff = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v4.0.0"), "+" + uses("actions/checkout", SHA_B, "v4.1.0")
        )
        self.assertTrue(pin_problems(diff, {("actions/checkout", "v4.1.0"): SHA_A}))

    def test_changelog_file_is_ignored_but_source_file_is_not(self) -> None:
        pin = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v4.0.0"), "+" + uses("actions/checkout", SHA_B, "v4.1.0")
        )
        tags = {("actions/checkout", "v4.1.0"): SHA_B}
        self.assertEqual(pin_problems(pin + file_diff("changelog.d/x.md", "+Bump checkout"), tags), [])
        self.assertEqual(pin_problems(pin + file_diff("CHANGELOG.md", "+- bump"), tags), [])
        self.assertTrue(pin_problems(pin + file_diff("src/app.py", "+print(1)"), tags))


class DiffHygiene(unittest.TestCase):
    """H0 separators, H2 file operations, M1 changelog scope, M2 header-only skip."""

    def test_separator_characters_fail(self) -> None:
        for ch in ["\r", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"]:
            with self.subTest(ch=repr(ch)):
                diff = file_diff(WF, OLD, NEW + ch + "      - run: evil")
                self.assertTrue(any("control or separator" in r for r in pin_problems(diff, TAGS)))

    def test_file_operations_fail(self) -> None:
        pin = file_diff(WF, OLD, NEW)
        evil = ".github/workflows/evil.yml"
        sections = {
            "rename": f"diff --git a/changelog.d/x.md b/{evil}\nrename from changelog.d/x.md\nrename to {evil}\n",
            "copy": f"diff --git a/{evil} b/{evil}\ncopy from {evil}\ncopy to {evil}\n",
            "mode": f"diff --git a/{evil} b/{evil}\nold mode 100644\nnew mode 100755\n",
            "binary": f"diff --git a/{evil} b/{evil}\nBinary files a/{evil} and b/{evil} differ\n",
            "git binary": f"diff --git a/{evil} b/{evil}\nGIT binary patch\nliteral 1\n",
            "new workflow": f"diff --git a/{evil} b/{evil}\nnew file mode 100644\n@@ -0,0 +1 @@\n+{OLD[1:]}\n",
            "deleted": f"diff --git a/{evil} b/{evil}\ndeleted file mode 100644\n",
            "changelog to other path": "diff --git a/CHANGELOG.md b/changelog.d/x.md\n@@ -1 +1 @@\n+x\n",
        }
        for name, section in sections.items():
            with self.subTest(name=name):
                self.assertTrue(pin_problems(pin + section, TAGS))

    def test_new_changelog_fragment_may_ride_along(self) -> None:
        frag = "diff --git a/changelog.d/new.md b/changelog.d/new.md\nnew file mode 100644\n@@ -0,0 +1 @@\n+Bump\n"
        self.assertEqual(pin_problems(file_diff(WF, OLD, NEW) + frag, TAGS), [])

    def test_changelog_exemption_is_narrow(self) -> None:
        pin = file_diff(WF, OLD, NEW)
        for path in [
            "changelog.d/scriv.ini",
            "changelog.d/x/action.yml",
            "src/pkg/CHANGELOG.md",
            "changelog.d/sub/x.md",
        ]:
            with self.subTest(path=path):
                self.assertTrue(pin_problems(pin + file_diff(path, "+arbitrary: content"), TAGS))

    def test_plus_plus_content_lines_are_not_skipped(self) -> None:
        diff = file_diff(WF, OLD, NEW, "--- removed script line", "+++i; evil")
        self.assertTrue(pin_problems(diff, TAGS))


class PinPairing(unittest.TestCase):
    """M4 per-hunk pairing, M5 direction, L1 syntax."""

    def test_reindented_line_fails(self) -> None:
        diff = file_diff(WF, OLD, "+  " + NEW[1:])
        self.assertTrue(pin_problems(diff, TAGS))

    def test_swapped_pins_fail(self) -> None:
        tags = {("actions/checkout", "v4.1.0"): SHA_B, ("actions/cache", "v4.1.0"): SHA_B}
        a_old, b_old = uses("actions/checkout", SHA_A, "v4.0.0"), uses("actions/cache", SHA_A, "v4.0.0")
        diff = file_diff(
            WF,
            "-" + a_old,
            "-" + b_old,
            "+" + uses("actions/cache", SHA_B, "v4.1.0"),
            "+" + uses("actions/checkout", SHA_B, "v4.1.0"),
        )
        self.assertTrue(pin_problems(diff, tags))

    def test_in_order_pairs_in_one_hunk_pass(self) -> None:
        tags = {("actions/checkout", "v4.1.0"): SHA_B, ("actions/cache", "v4.1.0"): SHA_B}
        diff = file_diff(
            WF,
            "-" + uses("actions/checkout", SHA_A, "v4.0.0"),
            "-" + uses("actions/cache", SHA_A, "v4.0.0"),
            "+" + uses("actions/checkout", SHA_B, "v4.1.0"),
            "+" + uses("actions/cache", SHA_B, "v4.1.0"),
        )
        self.assertEqual(pin_problems(diff, tags), [])

    def test_remove_in_one_hunk_and_add_in_another_fails(self) -> None:
        diff = file_diff(WF, OLD) + "@@ -9 +9 @@\n" + NEW + "\n"
        self.assertTrue(pin_problems(diff, TAGS))

    def test_downgrade_and_major_jump_fail(self) -> None:
        for old, new in [("v5.0.0", "v4.9.0"), ("v1.0.0", "v5.0.0"), ("v4.2.0", "v4.1.0")]:
            with self.subTest(old=old, new=new):
                diff = file_diff(
                    WF, "-" + uses("actions/checkout", SHA_A, old), "+" + uses("actions/checkout", SHA_B, new)
                )
                self.assertTrue(pin_problems(diff, {("actions/checkout", new): SHA_B}))

    def test_comment_without_space_and_nbsp_indent_fail(self) -> None:
        for new in [
            f"+      - uses: actions/checkout@{SHA_B}#v4.1.0",
            "+\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0- uses: actions/checkout@" + SHA_B + " # v4.1.0",
        ]:
            with self.subTest(new=new[:30]):
                self.assertTrue(pin_problems(file_diff(WF, OLD, new), TAGS))


class Status(unittest.TestCase):
    """M3 merge state, L3 logins, H3 commits and manifests, shape choice."""

    def test_status_requires_rollup_clean_and_green(self) -> None:
        ok = [{"name": "t", "conclusion": "SUCCESS"}, {"context": "c", "state": "SUCCESS"}]
        for rollup, state in [
            ([], "CLEAN"),
            (ok, "BEHIND"),
            (ok, "BLOCKED"),
            (ok + [{"name": "x", "status": "PENDING"}], "CLEAN"),
        ]:
            with self.subTest(state=state, n=len(rollup)):
                reasons: list[str] = []
                cmp.status_reasons(rollup, state, reasons)
                self.assertTrue(reasons)
        reasons = []
        cmp.status_reasons(ok, "CLEAN", reasons)
        self.assertEqual(reasons, [])

    def test_pin_files_ok(self) -> None:
        self.assertTrue(cmp.pin_files_ok([WF, "CHANGELOG.md"]))
        for paths in ([], ["CHANGELOG.md"], ["uv.lock"], [WF, "uv.lock"], [WF, "src/a.py"]):
            self.assertFalse(cmp.pin_files_ok(paths), paths)

    def test_only_trusted_bot_logins(self) -> None:
        self.assertTrue(cmp.is_trusted_author("dependabot[bot]"))
        self.assertTrue(cmp.is_trusted_author("app/dependabot"))
        self.assertFalse(cmp.is_trusted_author("dependabot"))
        self.assertFalse(cmp.is_trusted_author("someone"))


def pr_view(**over: object) -> dict:
    view: dict = {
        "headRefOid": SHA_A,
        "files": [{"path": WF}],
        "author": {"login": "dependabot[bot]"},
        "title": "Bump actions/checkout",
        "body": "",
        "statusCheckRollup": [{"name": "t", "conclusion": "SUCCESS"}],
        "mergeStateStatus": "CLEAN",
    }
    view.update(over)
    return view


def evaluate(view: dict, diff: str) -> tuple[list[str], int]:
    return cmp.evaluate(view, lambda: diff.encode(), lambda a, t: TAGS.get((a, t)))


class Evaluate(unittest.TestCase):
    def test_pin_pr_by_trusted_bot_passes(self) -> None:
        self.assertEqual(evaluate(pr_view(), file_diff(WF, OLD, NEW)), ([], 1))

    def test_pin_pr_by_outside_author_fails(self) -> None:
        self.assertTrue(evaluate(pr_view(author={"login": "stranger"}), file_diff(WF, OLD, NEW))[0])

    def test_unclean_merge_state_fails(self) -> None:
        self.assertTrue(evaluate(pr_view(mergeStateStatus="BEHIND"), file_diff(WF, OLD, NEW))[0])

    def test_invalid_utf8_diff_fails(self) -> None:
        reasons, _ = cmp.evaluate(pr_view(), lambda: b"\xff\xfe", lambda a, t: None)
        self.assertTrue(reasons)

    def test_shape_mismatch_fails(self) -> None:
        self.assertTrue(evaluate(pr_view(files=[{"path": "src/a.py"}]), file_diff("src/a.py", "+x"))[0])


class BlockPairing(unittest.TestCase):
    """N2: a changed line cannot move across context lines inside one hunk."""

    def test_uses_line_moved_below_its_with_block_fails(self) -> None:
        tags = {("third/upload", "v1.1.0"): SHA_B}
        diff = file_diff(
            WF,
            "-" + uses("third/upload", SHA_A, "v1.0.0"),
            "         with:",
            "           path: x",
            "+" + uses("third/upload", SHA_B, "v1.1.0"),
        )
        self.assertTrue(pin_problems(diff, tags))

    def test_step_reordered_after_a_run_step_fails(self) -> None:
        tags = {("step-security/harden-runner", "v1.1.0"): SHA_B}
        diff = file_diff(
            WF,
            "-" + uses("step-security/harden-runner", SHA_A, "v1.0.0"),
            "       - run: make build",
            "+" + uses("step-security/harden-runner", SHA_B, "v1.1.0"),
        )
        self.assertTrue(pin_problems(diff, tags))

    def test_two_separate_adjacent_blocks_pass(self) -> None:
        tags = {("actions/checkout", "v4.1.0"): SHA_B, ("actions/cache", "v4.1.0"): SHA_B}
        diff = file_diff(
            WF,
            OLD,
            NEW,
            "       - run: make build",
            "-" + uses("actions/cache", SHA_A, "v4.0.0"),
            "+" + uses("actions/cache", SHA_B, "v4.1.0"),
        )
        self.assertEqual(pin_problems(diff, tags), [])

    def test_no_newline_marker_does_not_split_a_block(self) -> None:
        diff = file_diff(WF, OLD, "\\ No newline at end of file", NEW, "\\ No newline at end of file")
        self.assertEqual(pin_problems(diff, TAGS), [])


class FileSetAndHead(unittest.TestCase):
    def test_new_changelog_fragment_must_be_a_regular_file(self) -> None:
        frag = "diff --git a/changelog.d/n.md b/changelog.d/n.md\nnew file mode 120000\n@@ -0,0 +1 @@\n+x\n"
        self.assertTrue(pin_problems(file_diff(WF, OLD, NEW) + frag, TAGS))

    def test_diff_files_must_equal_the_pr_file_list(self) -> None:
        frag = "diff --git a/CHANGELOG.md b/CHANGELOG.md\n@@ -1 +1 @@\n+x\n"
        for files, ok in [({WF}, True), ({WF, "CHANGELOG.md"}, False), ({WF}, True)]:
            reasons: list[str] = []
            cmp.pin_reasons(file_diff(WF, OLD, NEW), lambda a, t: TAGS.get((a, t)), reasons, files)
            self.assertEqual(not reasons, ok, files)
        reasons = []
        cmp.pin_reasons(file_diff(WF, OLD, NEW) + frag, lambda a, t: TAGS.get((a, t)), reasons, {WF})
        self.assertTrue(reasons)

    def test_head_moved(self) -> None:
        reasons: list[str] = []
        cmp.head_reasons(SHA_A, SHA_A, reasons)
        self.assertEqual(reasons, [])
        cmp.head_reasons(SHA_A, SHA_B, reasons)
        self.assertTrue(reasons)

    def test_lock_file_prs_are_not_tier_one(self) -> None:
        view = pr_view(files=[{"path": "uv.lock"}], title="Bump foo from 1.0.0 to 1.1.0")
        reasons, _ = evaluate(view, file_diff("uv.lock", "-a", "+b"))
        self.assertTrue(any("not workflow pins" in r for r in reasons))


if __name__ == "__main__":
    unittest.main()
