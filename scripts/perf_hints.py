#!/usr/bin/env python3
"""Loading hints on every page. Idempotent.

- preload of Poppins 600 next to the 400 one: headings (h1 in the hero) use
  it on every page, but only index.html preloaded it, so the other pages
  discovered it late from the CSS (text swap and layout shift).
- fetchpriority="high" on the hero logo (<img class="logo">), above the fold.

Usage:
    python3 scripts/perf_hints.py            # every page of the site
    python3 scripts/perf_hints.py FILE...    # given pages only
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRELOAD_400_RE = re.compile(
    r'([ \t]*)<link\s+rel="preload"\s+href="([./]*)fonts/poppins/poppins-latin-400-normal\.woff2"'
    r'[^>]*/?>'
)
LOGO_RE = re.compile(r'(<img\b[^>]*class="logo"[^>]*?)(\s*/?>)', re.S)


def update(html):
    if "poppins-latin-600-normal.woff2" not in html.split("</head>")[0]:
        def add_600(m):
            tag = m.group(0)
            return tag + "\n" + tag.replace("-400-", "-600-")
        html = PRELOAD_400_RE.sub(add_600, html, count=1)

    def priority(m):
        if "fetchpriority" in m.group(1):
            return m.group(0)
        return m.group(1) + ' fetchpriority="high"' + m.group(2)

    return LOGO_RE.sub(priority, html, count=1)


def pages():
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not {"node_modules", "tests", "_site"} & set(p.relative_to(ROOT).parts)
    )


def main(argv):
    targets = [Path(a) for a in argv] or pages()
    changed = 0
    for page in targets:
        html = page.read_text(encoding="utf-8")
        new = update(html)
        if new != html:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"perf_hints: {changed}/{len(targets)} pages updated")


if __name__ == "__main__":
    main(sys.argv[1:])
