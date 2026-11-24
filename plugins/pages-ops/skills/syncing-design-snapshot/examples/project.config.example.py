"""Example project config for sync_template.py: copy it into the site repo and edit it.

    python3 scripts/sync_template.py <fetched-dir> <project-config.py> --dry-run

TARGET_DIR is the site's snapshot folder, relative to where the script runs (usually the repo root).
PATCHES are the repo's own changes to the design's export, each with the reason it exists. List every
patch, with its reason, in the site's README too, and send each design-side fix upstream so the patch
can be dropped once the sync reports it as carried.
"""

TARGET_DIR = "packages/site/public"

PATCHES = [
    # (file, original, replacement, why)
    (
        "index.html",
        "<html>",
        '<html lang="en">',
        "the page declares its language for screen readers",
    ),
    (
        "index.html",
        'href="https://example.com/old-docs"',
        'href="https://example.com/docs"',
        "the docs moved; the design still links the old address",
    ),
    # (file, original, None, why, guard): a deletion. It counts as carried only once the guard phrase is
    # gone too, so a design that restyles this block (the exact original no longer matches) fails for
    # review instead of shipping the claim.
    (
        "index.html",
        '<p class="badge">Trusted by 10,000 teams</p>',
        None,
        "the site makes no usage claim it cannot source",
        "Trusted by 10,000 teams",
    ),
]
