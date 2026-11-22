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


class BumpRegex(unittest.TestCase):
    def test_dependabot_title(self) -> None:
        m = cmp.BUMP.search("Bump requests from 2.31.0 to 2.32.3")
        self.assertIsNotNone(m)
        self.assertEqual(m.groups(), ("requests", "2.31.0", "2.32.3"))

    def test_linked_body_form(self) -> None:
        text = "Bumps [ruff](https://example.invalid/ruff) from 0.4.1 to 0.4.9.\n"
        m = cmp.BUMP.search(text)
        self.assertIsNotNone(m)
        self.assertEqual(m.groups(), ("ruff", "0.4.1", "0.4.9"))


class Classifiers(unittest.TestCase):
    def test_pinned_uses_line(self) -> None:
        line = "      - uses: actions/checkout@" + "a" * 40 + " # v4.1.0"
        m = cmp.USES.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(4), "v4.1.0")
        self.assertIsNone(cmp.USES.match("      - uses: actions/checkout@v4"))


SHA_A = "a" * 40
SHA_B = "b" * 40


def uses(action: str, sha: str, tag: str) -> str:
    return f"      - uses: {action}@{sha} # {tag}"


def file_diff(path: str, *lines: str) -> str:
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n" + "\n".join(lines) + "\n"


def pin_problems(diff: str, tags: dict[tuple[str, str], str]) -> list[str]:
    reasons: list[str] = []
    cmp.pin_reasons(diff, lambda action, tag: tags.get((action, tag)), reasons)
    return reasons


class PinReasons(unittest.TestCase):
    wf = ".github/workflows/ci.yaml"

    def test_same_action_sha_and_tag_change_passes(self) -> None:
        diff = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v3"), "+" + uses("actions/checkout", SHA_B, "v4")
        )
        self.assertEqual(pin_problems(diff, {("actions/checkout", "v4"): SHA_B}), [])

    def test_swap_to_a_different_action_fails(self) -> None:
        diff = file_diff(self.wf, "-" + uses("actions/checkout", SHA_A, "v3"), "+" + uses("evil/checkout", SHA_B, "v1"))
        self.assertTrue(pin_problems(diff, {("evil/checkout", "v1"): SHA_B}))

    def test_add_only_uses_line_fails(self) -> None:
        diff = file_diff(self.wf, "+" + uses("evil/action", SHA_B, "v1"))
        self.assertTrue(pin_problems(diff, {("evil/action", "v1"): SHA_B}))

    def test_sha_not_matching_tag_fails(self) -> None:
        diff = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v3"), "+" + uses("actions/checkout", SHA_B, "v4")
        )
        self.assertTrue(pin_problems(diff, {("actions/checkout", "v4"): SHA_A}))

    def test_changelog_file_is_ignored_but_source_file_is_not(self) -> None:
        pin = file_diff(
            self.wf, "-" + uses("actions/checkout", SHA_A, "v3"), "+" + uses("actions/checkout", SHA_B, "v4")
        )
        tags = {("actions/checkout", "v4"): SHA_B}
        self.assertEqual(pin_problems(pin + file_diff("changelog.d/x.md", "+Bump checkout"), tags), [])
        self.assertEqual(pin_problems(pin + file_diff("CHANGELOG.md", "+- bump"), tags), [])
        self.assertTrue(pin_problems(pin + file_diff("src/app.py", "+print(1)"), tags))


class ParseBumps(unittest.TestCase):
    def test_reads_title_and_head_of_body(self) -> None:
        reasons: list[str] = []
        bumps = cmp.parse_bumps("Bump requests from 2.31.0 to 2.32.3", "", reasons)
        self.assertEqual(bumps, {"requests": ("2.31.0", "2.32.3")})
        self.assertEqual(reasons, [])

    def test_ignores_lines_inside_details(self) -> None:
        body = "Bumps foo from 1.0.0 to 1.1.0.\n<details>\nBumps bar from 1.0.0 to 9.0.0\n</details>"
        reasons: list[str] = []
        self.assertEqual(cmp.parse_bumps("t", body, reasons), {"foo": ("1.0.0", "1.1.0")})

    def test_package_with_two_different_changes_is_flagged(self) -> None:
        reasons: list[str] = []
        cmp.parse_bumps("Bump foo from 1.0.0 to 1.1.0", "Bumps foo from 1.0.0 to 9.0.0", reasons)
        self.assertTrue(any("two different" in r for r in reasons))


if __name__ == "__main__":
    unittest.main()
