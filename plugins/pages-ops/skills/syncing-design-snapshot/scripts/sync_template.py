"""Engine for syncing a fetched Claude Design export into a project's own site snapshot.

This pulls a design tool's page export down into the repo (the opposite direction of publishing a
repo's components up to the design system). Fetching the export itself is a main-session step this skill
does not do — point `sync()` at a directory that is already fetched (see ../SKILL.md: the Artifact tool for a
Design System artifact, `DesignSync get_file` for a standalone claude.ai/design project).

A project supplies a small config: a target directory (the site's snapshot folder, e.g.
`packages/<site>/public`) and PATCHES, a list of `(file, original, replacement, why)` tuples.
`replacement=None` deletes `original` instead of replacing it; a deletion may add a fifth element, a guard
phrase (see apply_patches). Every patch is classified:

  applied  - `original` was found in the template and replaced
  carried  - the template already contains `replacement` (safe to drop the patch)
  FAIL     - `original` is not in the template (it changed upstream; review the patch)

Any FAIL aborts the sync with nothing written. See `../../../examples/project.config.example.py` for the
config shape, and `load_config`/`main` below for running this as a CLI against that file.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

# (file, original, replacement, why) or (file, original, None, why, guard): see apply_patches.
Patch = tuple[str, ...]


def read_template(src: pathlib.Path) -> dict[str, str]:
    """Reads every file in the fetched export; a `*.dc.html` page becomes `index.html`."""
    return {
        "index.html" if f.name.endswith(".dc.html") else f.name: f.read_text(encoding="utf-8")
        for f in sorted(src.iterdir())
        if f.is_file() and not f.name.startswith(".")
    }


def apply_patches(files: dict[str, str], patches: list[Patch]) -> int:
    """Applies each (file, old, new, why[, guard]) patch to `files` in place; returns the failure count.

    A deletion may carry a guard: a phrase of the removed content. It counts as carried only once the guard is
    gone too, so content the design merely restyled (the exact original no longer matches) fails for review
    instead of shipping."""
    failed = 0
    for name, old, new, why, *rest in patches:
        guard = rest[0] if rest else None
        text = files.get(name)
        if text is None:
            print(f"FAIL     {name}: not in the template ({why})")
            failed += 1
            continue
        # Reason: "carried" needs evidence the fix is there, not just that the original text is gone (an
        # upstream rewrite also removes it, and must FAIL for review). While the original is still present it
        # is applied, unless the replacement contains it and is already in place (e.g. an added attribute);
        # a short replacement can also occur elsewhere unpatched, so it alone never means "carried" then.
        if new is None:
            carried = old not in text and (guard is None or guard not in text)
        elif old in text:
            carried = old in new and new in text
        else:
            carried = new in text
        if carried:
            print(f"carried  {name}: {why} (template already has it; drop this patch)")
        elif old in text:
            files[name] = text.replace(old, new or "")
            print(f"applied  {name}: {why}")
        else:
            print(f"FAIL     {name}: {why} (original text changed; review)")
            failed += 1
    return failed


def sync(template_dir: pathlib.Path, target_dir: pathlib.Path, patches: list[Patch], dry_run: bool = False) -> int:
    """Reads `template_dir`, applies `patches`, and writes the result to `target_dir` unless `dry_run`."""
    files = read_template(template_dir)
    failed = apply_patches(files, patches)
    if failed:
        print(f"{failed} failure(s); nothing written")
        return 1
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (target_dir / name).write_text(text, encoding="utf-8")
    print("dry run; nothing written" if dry_run else f"wrote {len(files)} files to {target_dir}")
    return 0


def load_config(path: pathlib.Path):
    """Imports a project config module (must define TARGET_DIR and PATCHES) from an arbitrary path."""
    spec = importlib.util.spec_from_file_location("project_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    template_dir, config_path = (pathlib.Path(a) for a in args)
    config = load_config(config_path)
    return sync(template_dir, pathlib.Path(config.TARGET_DIR), config.PATCHES, dry_run="--dry-run" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
