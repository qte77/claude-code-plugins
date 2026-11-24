"""Unit tests for sync_template: patch classification, reading the export, sync and the CLI.

No test runner is configured in this repository for standalone plugin scripts, so this uses only the
standard library. Run: python3 -m unittest discover -s <this directory> -p '*_test.py'
(the default pattern, test*.py, finds no tests here).
"""

import contextlib
import io
import os
import pathlib
import tempfile
import unittest

from sync_template import apply_patches, load_config, main, read_template, sync

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
        # old ("foo") is inside new ("foo bar"). Before the patch the text holds old but not new, so it is
        # applied, not mistaken for "carried".
        files = {"a.html": "<p>foo</p>"}
        failed = apply_patches(files, [("a.html", "foo", "foo bar", "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "<p>foo bar</p>")

    def test_carried_when_replacement_contains_original_and_already_applied(self):
        # The text holds new, and so old as well: carried, and the file is not patched a second time.
        files = {"a.html": "<p>foo bar</p>"}
        failed = apply_patches(files, [("a.html", "foo", "foo bar", "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], "<p>foo bar</p>")

    def test_applied_when_replacement_also_occurs_elsewhere(self):
        # old is still present and new (which does not contain old) also occurs elsewhere: the patch is
        # still needed, so it is applied, not read as "carried".
        files = {"a.html": '<a href="/old">x</a> <a href="/new">y</a>'}
        failed = apply_patches(files, [("a.html", 'href="/old"', 'href="/new"', "why")])
        self.assertEqual(failed, 0)
        self.assertEqual(files["a.html"], '<a href="/new">x</a> <a href="/new">y</a>')

    def test_guarded_deletion_fails_when_a_second_copy_survives(self):
        # The exact original is deleted, but a restyled second copy (say, a phone layout) still holds the
        # guard phrase: FAIL, since the content would ship.
        files = {"a.html": '<p>Claim X.</p><p class="r">Claim X.</p>'}
        patch = ("a.html", "<p>Claim X.</p>", None, "why", "Claim X")
        self.assertEqual(apply_patches(files, [patch]), 1)

    def test_guard_on_a_replacement_fails(self):
        # A guard only has a meaning for a deletion; on a replacement it would be silently ignored.
        files = {"a.html": "old"}
        self.assertEqual(apply_patches(files, [("a.html", "old", "new", "why", "old")]), 1)

    def test_empty_original_fails(self):
        files = {"a.html": "abc"}
        self.assertEqual(apply_patches(files, [("a.html", "", "X", "why")]), 1)
        self.assertEqual(files["a.html"], "abc")

    def test_empty_guard_fails(self):
        files = {"a.html": "<p>a</p>"}
        self.assertEqual(apply_patches(files, [("a.html", "<p>a</p>", None, "why", "")]), 1)

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


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args, **kwargs)


class SyncTest(unittest.TestCase):
    """read_template, sync and main against a temporary fetched export and target."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        self.src = self.root / "fetched"
        self.src.mkdir()
        (self.src / "page.dc.html").write_text("<html><p>old</p></html>", encoding="utf-8")
        (self.src / "shared.js").write_text("x()", encoding="utf-8")
        self.target = self.root / "site" / "public"

    def test_read_template_renames_the_page_to_index(self):
        self.assertEqual(sorted(read_template(self.src)), ["index.html", "shared.js"])

    def test_read_template_skips_symlinks(self):
        (self.root / "outside.txt").write_text("secret", encoding="utf-8")
        os.symlink(self.root / "outside.txt", self.src / "link.txt")
        self.assertNotIn("link.txt", read_template(self.src))

    def test_clean_run_writes_the_patched_page(self):
        rc = _quiet(sync, self.src, self.target, [("index.html", "old", "new", "why")])
        self.assertEqual(rc, 0)
        self.assertEqual((self.target / "index.html").read_text(encoding="utf-8"), "<html><p>new</p></html>")
        self.assertTrue((self.target / "shared.js").is_file())

    def test_a_fail_writes_nothing(self):
        rc = _quiet(sync, self.src, self.target, [("index.html", "absent", "new", "why")])
        self.assertEqual(rc, 1)
        self.assertFalse(self.target.exists())

    def test_dry_run_writes_nothing(self):
        rc = _quiet(sync, self.src, self.target, [("index.html", "old", "new", "why")], dry_run=True)
        self.assertEqual(rc, 0)
        self.assertFalse(self.target.exists())

    def test_two_pages_mapping_to_index_abort(self):
        (self.src / "other.dc.html").write_text("<html>2</html>", encoding="utf-8")
        rc = _quiet(sync, self.src, self.target, [])
        self.assertEqual(rc, 1)
        self.assertFalse(self.target.exists())

    def _config(self):
        config = self.root / "project_config.py"
        config.write_text(f"TARGET_DIR = {str(self.target)!r}\nPATCHES = []\n", encoding="utf-8")
        return config

    def test_main_rejects_an_unknown_flag_and_writes_nothing(self):
        rc = _quiet(main, [str(self.src), str(self._config()), "--dryrun"])
        self.assertEqual(rc, 2)
        self.assertFalse(self.target.exists())

    def test_main_dry_run_writes_nothing(self):
        rc = _quiet(main, [str(self.src), str(self._config()), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertFalse(self.target.exists())

    def test_main_writes_with_a_valid_config(self):
        rc = _quiet(main, [str(self.src), str(self._config())])
        self.assertEqual(rc, 0)
        self.assertTrue((self.target / "index.html").is_file())

    def test_main_rejects_a_config_that_is_not_python(self):
        config = self.root / "config.txt"
        config.write_text("TARGET_DIR = 'x'\n", encoding="utf-8")
        rc = _quiet(main, [str(self.src), str(config)])
        self.assertEqual(rc, 2)
        self.assertFalse(self.target.exists())


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
