"""Fail if .markdownlint.jsonc drifts from the shared qte77/.github config.

Every key in the shared config must be present locally with the same value; local-only keys
(documented overrides such as MD025) are allowed. Usage: check-markdownlint-config.py <shared-url>
"""

import json
import re
import sys
import urllib.request


def load_jsonc(text: str) -> dict:
    return json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE))


def main(url: str) -> int:
    with urllib.request.urlopen(url, timeout=20) as resp:
        shared = load_jsonc(resp.read().decode())
    with open(".markdownlint.jsonc", encoding="utf-8") as fh:
        local = load_jsonc(fh.read())
    drift = {k: (v, local.get(k)) for k, v in shared.items() if local.get(k) != v}
    if drift:
        for key, (want, got) in drift.items():
            print(f"ERROR: .markdownlint.jsonc {key} = {got!r}, shared config has {want!r}")
        print("Re-sync .markdownlint.jsonc with the shared qte77/.github config.")
        return 1
    extra = sorted(set(local) - set(shared))
    print(f".markdownlint.jsonc matches the shared config (local overrides: {', '.join(extra) or 'none'}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
