#!/usr/bin/env python3
"""Check that no page of the built site is heavier than the budget.

For every *.html of the built site (default _site/) the weight is the size of
the HTML plus every local resource it loads, each counted once: stylesheets,
scripts, images (img/source src and srcset, link icons, preloads, manifest)
and the files referenced by url(...) in those stylesheets (fonts, images).
External resources are ignored. Scenes loaded lazily by scripts are not counted.

The budget is scripts/page_weight_budget.json: {"max_page_bytes": N}
(heaviest real page at the time of writing, plus 10%).

Usage:
    python3 scripts/check_page_weight.py [--root _site] [--budget FILE]
Exit: 0 every page within budget, 1 otherwise.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUDGET = REPO_ROOT / "scripts" / "page_weight_budget.json"
CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
CSS_IMPORT_RE = re.compile(r"""@import\s+["']([^"']+)["']""")


class _Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("img", "script", "source", "video", "audio") and a.get("src"):
            self.refs.append(a["src"])
        if tag == "link" and a.get("href") and "canonical" not in (a.get("rel") or ""):
            self.refs.append(a["href"])
        if tag in ("img", "source") and a.get("srcset"):
            self.refs += [c.strip().split()[0] for c in a["srcset"].split(",") if c.strip()]


def _resolve(root, base, ref):
    parts = urlsplit(ref.strip())
    if parts.scheme or parts.netloc or not parts.path:
        return None
    rel = unquote(parts.path)
    target = (root / rel.lstrip("/")) if rel.startswith("/") else (base.parent / rel)
    try:
        target = target.resolve()
        target.relative_to(root.resolve())
    except (ValueError, OSError):
        return None
    return target if target.is_file() else None


def _css_refs(css):
    text = css.read_text(encoding="utf-8", errors="ignore")
    return [r for r in CSS_URL_RE.findall(text) + CSS_IMPORT_RE.findall(text) if not r.startswith("data:")]


def page_files(root, page):
    root, page = Path(root), Path(page)
    parser = _Refs()
    parser.feed(page.read_text(encoding="utf-8"))
    seen = {page.resolve()}
    queue = [(page, r) for r in parser.refs]
    while queue:
        base, ref = queue.pop()
        target = _resolve(root, base, ref)
        if target is None or target in seen:
            continue
        seen.add(target)
        if target.suffix == ".css":
            queue += [(target, r) for r in _css_refs(target)]
    return seen


def page_weight(root, page):
    return sum(f.stat().st_size for f in page_files(root, page))


def over_budget(root, max_bytes):
    root = Path(root)
    result = []
    for page in sorted(root.rglob("*.html")):
        weight = page_weight(root, page)
        if weight > max_bytes:
            result.append((page, weight))
    return result


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    opts = {"--root": REPO_ROOT / "_site", "--budget": DEFAULT_BUDGET}
    while args:
        if len(args) < 2 or args[0] not in opts:
            print(__doc__)
            return 2
        opts[args[0]] = Path(args[1])
        args = args[2:]
    root = opts["--root"]
    max_bytes = json.loads(Path(opts["--budget"]).read_text(encoding="utf-8"))["max_page_bytes"]
    over = over_budget(root, max_bytes)
    for page, weight in over:
        print(f"OVER BUDGET {page.relative_to(root)}: {weight} bytes > {max_bytes}")
    pages = len(list(root.rglob("*.html")))
    print(f"{pages} pages scanned, {len(over)} over the budget of {max_bytes} bytes")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
