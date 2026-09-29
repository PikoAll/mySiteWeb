#!/usr/bin/env python3
"""Verify that every page of the site carries valid JSON-LD structured data.

For each page (root *.html, blog/*.html, crucidev/privacy/index.html): extract the <script type="application/ld+json"> block and
parse it with a STRICT json.loads (strict=True, the default). A literal newline
inside a JSON string — as produced when a formatter wraps prose inside the JSON
values — makes json.loads fail, which is exactly what Google's parser does too:
it silently discards the structured data for that page.

Beyond the syntax, on every node of every @graph:
- each node has an @type;
- a BreadcrumbList numbers its items 1..n, each with name and item;
- across ALL the checked pages, a node @id that carries data has the same
  data everywhere (Google merges nodes by @id: two versions contradict).

Exit code 0 only if EVERY page has exactly one JSON-LD block and all of them
pass. Non-zero otherwise, listing each offender. Meant to be run as a gate
before publishing (and reusable in CI).

Usage:
    python3 scripts/verify_jsonld.py            # scan every page of <repo>
    python3 scripts/verify_jsonld.py FILE...    # scan given files

With no arguments the pages are resolved relative to the repository
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

# <repo>, resolved from this file's location (scripts/verify_jsonld.py).
REPO = Path(__file__).resolve().parent.parent


def repo_pages():
    return sorted(
        [str(p) for p in REPO.glob("*.html")]
        + [str(p) for p in (REPO / "blog").glob("*.html")]
        + [str(p) for p in (REPO / "crucidev").rglob("*.html")]
    )


def nodes_of(data):
    items = data.get("@graph", [data]) if isinstance(data, dict) else data
    return [n for n in items if isinstance(n, dict)]


def check_nodes(nodes):
    """Schema sanity of one page's nodes: None if OK, else an error message."""
    for node in nodes:
        if "@type" not in node:
            return f"node without @type: {json.dumps(node, ensure_ascii=False)[:80]}"
        if node["@type"] == "BreadcrumbList":
            items = node.get("itemListElement", [])
            if [i.get("position") for i in items] != list(range(1, len(items) + 1)):
                return "BreadcrumbList positions are not 1..n"
            if not all(i.get("name") and i.get("item") for i in items):
                return "BreadcrumbList item without name or item"
    return None


def check(path, ids=None):
    """Return None if OK, else an error message. `ids` collects @id -> (data,
    path) across calls, to catch the same @id with different data."""
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
        data = json.loads(blocks[0])  # strict=True on purpose: mirrors Google
    except json.JSONDecodeError as e:
        return f"invalid JSON: {e}"
    nodes = nodes_of(data)
    err = check_nodes(nodes)
    if err or ids is None:
        return err
    for node in nodes:
        if "@id" in node and len(node) > 1:
            first = ids.setdefault(node["@id"], (node, path))
            if first[0] != node:
                return f"@id {node['@id']} has different data than in {first[1]}"
    return None


def main(argv):
    files = argv[1:] or repo_pages()
    if not files:
        print("no files to check", file=sys.stderr)
        return 1
    bad = []
    ids = {}
    for p in files:
        err = check(p, ids)
        if err:
            bad.append((p, err))
    if bad:
        print(f"JSON-LD INVALID in {len(bad)}/{len(files)} page(s):")
        for p, err in bad:
            print(f"  - {p}: {err}")
        return 1
    print(f"JSON-LD OK: all {len(files)} page(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
