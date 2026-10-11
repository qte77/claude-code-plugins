"""Unit tests for sync_template.apply_patches's applied/carried/FAIL classification.

No test runner is configured in this repository for standalone plugin scripts, so this uses only the
standard library. Run: python3 -m unittest discover -s <this directory>
"""

import unittest

from sync_template import apply_patches


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


if __name__ == "__main__":
    unittest.main()
