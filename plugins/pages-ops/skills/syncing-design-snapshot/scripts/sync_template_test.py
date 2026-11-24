"""Unit tests for sync_template.apply_patches's applied/carried/FAIL classification.

No test runner is configured in this repository for standalone plugin scripts, so this uses only the
standard library. Run: python3 -m unittest discover -s <this directory> -p '*_test.py'
(the default pattern, test*.py, finds no tests here).
"""

import pathlib
import unittest

from sync_template import apply_patches, load_config

EXAMPLE = pathlib.Path(__file__).resolve().parent.parent / "examples" / "project.config.example.py"


class ApplyPatchesTest(unittest.TestCase):
    def test_applies_when_original_found(self):
        files = {"a.html": "old text here"}
        failed = apply_patches(files, [("a.html", "old", "new", "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "new text here")

    def test_applies_every_occurrence(self):
        files = {"a.html": "old old old"}
        failed = apply_patches(files, [("a.html", "old", "new", "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "new new new")

    def test_carried_when_already_replaced(self):
        # old is gone, new is present: a second sync must not fail or re-touch the file.
        files = {"a.html": "new text here"}
        failed = apply_patches(files, [("a.html", "old", "new", "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "new text here")

    def test_carried_when_deletion_already_applied(self):
        # new=None deletes `old`; carried once `old` is no longer present.
        files = {"a.html": "clean text"}
        failed = apply_patches(files, [("a.html", "dirty text ", None, "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "clean text")

    def test_applied_when_replacement_contains_original(self):
        # old ("<html>\n") is a substring of new ('<html lang="en">\n'): must not be mistaken for
        # "carried" before the patch is even applied — only `old not in text` after replacement counts.
        files = {"index.html": "<html>\nbody"}
        failed = apply_patches(files, [("index.html", "<html>\n", '<html lang="en">\n', "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["index.html"], '<html lang="en">\nbody')

    def test_carried_when_replacement_contains_original_and_already_applied(self):
        files = {"index.html": '<html lang="en">\nbody'}
        failed = apply_patches(files, [("index.html", "<html>\n", '<html lang="en">\n', "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["index.html"], '<html lang="en">\nbody')

    def test_guarded_deletion_fails_when_the_claim_survives_a_restyle(self):
        # The design restyled the markup (exact original gone) but the removed claim is still there: the guard
        # phrase is present, so this must FAIL for review instead of passing as "carried".
        files = {"a.html": '<p style="font:var(--f)">Award-winning design.</p>'}
        patch = ("a.html", '<p style="font:serif">Award-winning design.</p>', None, "why", "Award-winning")
        self.assertEqual(apply_patches(files, [patch]), 1)

    def test_guarded_deletion_is_carried_once_the_claim_is_gone(self):
        files = {"a.html": "<p>Plain text.</p>"}
        patch = ("a.html", "<p>Award-winning design.</p>", None, "why", "Award-winning")
        self.assertEqual(apply_patches(files, [patch]), 0)

    def test_guarded_deletion_still_applies_the_exact_original(self):
        files = {"a.html": "<p>a</p><p>Award-winning design.</p>"}
        patch = ("a.html", "<p>Award-winning design.</p>", None, "why", "Award-winning")
        self.assertEqual(apply_patches(files, [patch]), 0)
        self.assertEqual(files["a.html"], "<p>a</p>")

    def test_fails_when_file_not_in_template(self):
        failed = apply_patches({}, [("missing.html", "old", "new", "why")])
        self.assertEqual(failed, 1)

    def test_fails_when_original_text_changed_upstream(self):
        files = {"a.html": "unrelated text"}
        failed = apply_patches(files, [("a.html", "old", "new", "why")])
        self.assertEqual(failed, 1)
        self.assertEqual(files["a.html"], "unrelated text")

    def test_counts_multiple_failures(self):
        files = {"a.html": "text"}
        failed = apply_patches(files, [("missing.html", "x", "y", "why"), ("a.html", "nope", "y", "why")])
        self.assertEqual(failed, 2)


class ExampleConfigTest(unittest.TestCase):
    """The shipped example config loads through load_config and its patches fit the engine."""

    def setUp(self):
        self.config = load_config(EXAMPLE)

    def test_defines_target_dir_and_patches(self):
        self.assertIsInstance(self.config.TARGET_DIR, str)
        self.assertTrue(self.config.PATCHES)
        for patch in self.config.PATCHES:
            self.assertIn(len(patch), (4, 5), patch)
            if len(patch) == 5:
                self.assertIsNone(patch[2], "only a deletion takes a guard")

    def test_has_a_guarded_deletion(self):
        self.assertTrue(any(len(p) == 5 and p[2] is None and p[4] for p in self.config.PATCHES))

    def test_patches_apply_to_a_template_holding_their_originals(self):
        # Each original sits in its file once, so a fresh template reads "applied" for every patch.
        files = {}
        for name, old, *_ in self.config.PATCHES:
            files[name] = files.get(name, "<body>\n") + old + "\n"
        self.assertEqual(apply_patches(files, self.config.PATCHES), 0)
        for name, old, new, *_ in self.config.PATCHES:
            self.assertNotIn(old, files[name])
            if new is not None:
                self.assertIn(new, files[name])


if __name__ == "__main__":
    unittest.main()
