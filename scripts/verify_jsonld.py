#!/usr/bin/env python3
"""Verify that every blog article carries valid JSON-LD structured data.

For each blog/*.html: extract the <script type="application/ld+json"> block and
parse it with a STRICT json.loads (strict=True, the default). A literal newline
inside a JSON string — as produced when a formatter wraps prose inside the JSON
values — makes json.loads fail, which is exactly what Google's parser does too:
it silently discards the structured data for that page.

Exit code 0 only if EVERY article has exactly one JSON-LD block and all of them
parse. Non-zero otherwise, listing each offender. Meant to be run as a gate
before publishing (and reusable in CI).

Usage:
    python3 scripts/verify_jsonld.py            # scan <repo>/blog/*.html
    python3 scripts/verify_jsonld.py FILE...    # scan given files

With no arguments the blog/ directory is resolved relative to the repository
root (the parent of this scripts/ folder), NOT to the current working
directory, so the gate works when launched from anywhere (e.g. the weekly
publish guardrail runs it against a clone in a temp dir).
"""
import json
import re
import sys
from pathlib import Path

BLOCK_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S
)

# <repo>/blog, resolved from this file's location (scripts/verify_jsonld.py).
REPO_BLOG_DIR = Path(__file__).resolve().parent.parent / "blog"


def check(path):
    """Return None if OK, else an error message."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return f"cannot read file: {e}"
    blocks = BLOCK_RE.findall(src)
    if not blocks:
        return "no JSON-LD block found"
    if len(blocks) > 1:
        return f"{len(blocks)} JSON-LD blocks found (expected 1)"
    try:
        json.loads(blocks[0])  # strict=True on purpose: mirrors Google
    except json.JSONDecodeError as e:
        return f"invalid JSON: {e}"
    return None


def main(argv):
    files = argv[1:] or sorted(str(p) for p in REPO_BLOG_DIR.glob("*.html"))
    if not files:
        print("no files to check", file=sys.stderr)
        return 1
    bad = []
    for p in files:
        err = check(p)
        if err:
            bad.append((p, err))
    if bad:
        print(f"JSON-LD INVALID in {len(bad)}/{len(files)} article(s):")
        for p, err in bad:
            print(f"  - {p}: {err}")
        return 1
    print(f"JSON-LD OK: all {len(files)} article(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
