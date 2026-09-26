#!/usr/bin/env python3
"""Put the same NAP line (Name, Address, Phone) in the footer of every page.

Local SEO wants name, place and phone written identically everywhere and
identical to the Google Business Profile. The address is the city only: the
business is a service-area business with a hidden street address, so no street
must ever appear here.

The line is inserted right after the opening <footer> tag and marked with
MARKER; a page that already has it is left byte-for-byte unchanged
(idempotent). *.backup files and tests/ are never touched.

Usage:
    python3 scripts/add_footer_nap.py            # every page of the site
    python3 scripts/add_footer_nap.py FILE...    # only the given files

Exit code: 0 ok, 2 a page could not be processed (e.g. no <footer>).
"""
import re
import sys
from pathlib import Path

MARKER = 'class="nap"'

NAP = (
    '<p class="nap">Pikobit · Programmatore e web designer · Monopoli (BA) · '
    '<a href="tel:+393518891903">351 889 1903</a> · '
    '<a href="mailto:piko.bit.00@gmail.com">piko.bit.00@gmail.com</a></p>'
)

FOOTER_RE = re.compile(r"<footer[^>]*>")
REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "tests", "node_modules"}


def default_targets(root):
    root = Path(root)
    return sorted(
        p
        for p in root.rglob("*.html")
        if not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )


def process(path):
    """Insert the NAP line in path. Return True if the file changed."""
    path = Path(path)
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return False
    m = FOOTER_RE.search(html)
    if not m:
        raise ValueError(f"{path}: no <footer> found")
    html = html[: m.end()] + "\n" + NAP + html[m.end() :]
    path.write_text(html, encoding="utf-8")
    return True


def main(argv):
    files = [Path(a) for a in argv] or default_targets(REPO_ROOT)
    changed, errors = 0, []
    for f in files:
        try:
            changed += process(f)
        except (OSError, ValueError) as e:
            errors.append(str(e))
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print(f"{changed} changed, {len(files) - changed - len(errors)} already ok, {len(errors)} errors")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
