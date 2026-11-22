"""Tests for check-skill-frontmatter.py (stdlib unittest; run: python3 -m unittest discover -s .github/scripts)."""

import importlib.util
import pathlib
import tempfile
import unittest

_SPEC = importlib.util.spec_from_file_location(
    "check_skill_frontmatter", pathlib.Path(__file__).with_name("check-skill-frontmatter.py")
)
csf = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(csf)


def problems(frontmatter: str) -> list[str]:
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "SKILL.md"
        p.write_text(f"---\n{frontmatter}---\n\n# Body\n")
        return csf.check_file(p)


class CheckSkillFrontmatter(unittest.TestCase):
    def test_nested_argument_hint_is_reported(self):
        out = problems("name: x\ndescription: y\nmetadata:\n  argument-hint: \"[a]\"\n")
        self.assertEqual(len(out), 1)
        self.assertIn("metadata.argument-hint", out[0])

    def test_nested_allowed_tools_is_reported(self):
        out = problems("name: x\nmetadata:\n  allowed-tools: Read, Grep\n")
        self.assertIn("metadata.allowed-tools", out[0])

    def test_unquoted_top_level_argument_hint_is_reported(self):
        # Reason: YAML reads an unquoted [a] as a list, not the string the docs expect
        out = problems("name: x\nargument-hint: [a]\n")
        self.assertIn("argument-hint must be a quoted string", out[0])

    def test_quoted_top_level_argument_hint_passes(self):
        self.assertEqual(problems("name: x\nargument-hint: \"[a] [b]\"\nmetadata:\n  stability: stable\n"), [])

    def test_keys_not_yet_enforced_may_stay_nested(self):
        self.assertEqual(problems("name: x\nmetadata:\n  context: fork\n  content-hash: sha256:ab\n"), [])

    def test_renamed_nested_key_passes(self):
        self.assertEqual(problems("name: x\nmetadata:\n  intended-tools: Read, Bash\n"), [])

    def test_file_without_frontmatter_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "SKILL.md"
            p.write_text("# no frontmatter\n")
            self.assertIn("no frontmatter", csf.check_file(p)[0])


if __name__ == "__main__":
    unittest.main()
