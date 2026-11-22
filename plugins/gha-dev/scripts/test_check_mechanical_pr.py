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


if __name__ == "__main__":
    unittest.main()
