"""Fail if README.md's inventory drifts from the marketplace.

Checks, for every local plugin registered in .claude-plugin/marketplace.json whose directory exists:
- README's "N plugins, M skills, K agents" line matches the counts on disk;
- README's plugin table has a `| **<name>** |` row.
External plugins (non-string `source`, e.g. cc-voice) are not counted.
"""

import json
import re
import sys
from pathlib import Path


def main() -> int:
    market = json.loads(Path(".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    local = [p for p in market["plugins"] if isinstance(p["source"], str) and Path(p["source"]).is_dir()]
    skills = sum(len(list(Path(p["source"]).glob("skills/*/SKILL.md"))) for p in local)
    agents = sum(len(list(Path(p["source"]).glob("agents/*.md"))) for p in local)
    readme = Path("README.md").read_text(encoding="utf-8")

    errors = []
    m = re.search(r"(\d+) plugins, (\d+) skills, (\d+) agents", readme)
    if not m:
        errors.append('README has no "N plugins, M skills, K agents" line')
    elif tuple(map(int, m.groups())) != (len(local), skills, agents):
        errors.append(
            f"README says {m.group(0)!r}; actual: {len(local)} plugins, {skills} skills, {agents} agents"
        )
    rows = set(re.findall(r"^\| \*\*([a-z0-9-]+)\*\*", readme, re.MULTILINE))
    errors += [f"README plugin table has no row for '{p['name']}'" for p in local if p["name"] not in rows]

    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        return 1
    print(f"README inventory OK: {len(local)} plugins, {skills} skills, {agents} agents, all rows present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
