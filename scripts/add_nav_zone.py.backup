#!/usr/bin/env python3
"""Add the "Dove lavoro" dropdown to the navigation bar of every page.

The dropdown is inserted right after the <li class="dropdown"> of "Servizi"
and lists the city pages plus the hub dove-lavoro.html. Links are written with
the same relative prefix the page already uses for its Home link ("", "../",
"../../"), so the same script serves root pages, blog/ and crucidev/privacy/.

The toggle uses class="dropdown-toggle", never id="dropdown-toggle" (that id
belongs to "Servizi" and must stay unique); scripts/script.js handles every
.dropdown by class. A page that already carries MARKER is left byte-for-byte
unchanged (idempotent). *.backup files and tests/ are never touched.

Usage:
    python3 scripts/add_nav_zone.py            # every page of the site
    python3 scripts/add_nav_zone.py FILE...    # only the given files

Exit code: 0 ok, 2 a page could not be processed.
"""
import re
import sys
from pathlib import Path

MARKER = 'class="dropdown nav-zone"'

# (label, page) in menu order; Monopoli first because it is the main page.
CITIES = [
    ("Monopoli", "programmatore-monopoli.html"),
    ("Bari", "programmatore-bari.html"),
    ("Polignano a Mare", "programmatore-polignano-a-mare.html"),
    ("Fasano", "programmatore-fasano.html"),
    ("Conversano", "programmatore-conversano.html"),
    ("Castellana Grotte", "programmatore-castellana-grotte.html"),
    ("Putignano", "programmatore-putignano.html"),
    ("Casamassima", "programmatore-casamassima.html"),
    ("Ostuni", "programmatore-ostuni.html"),
    ("Brindisi", "programmatore-brindisi.html"),
    ("Taranto", "programmatore-taranto.html"),
    ("Lecce", "programmatore-lecce.html"),
]
HUB = ("Tutte le zone", "dove-lavoro.html")

NAV_RE = re.compile(r"<nav\b.*?</nav>", re.S)
HOME_RE = re.compile(r'href="([./]*)index\.html"\s*>\s*Home')
REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "tests", "node_modules"}


def block(prefix):
    items = "\n".join(
        f'<li><a href="{prefix}{page}">{label}</a></li>' for label, page in CITIES + [HUB]
    )
    return (
        f"\n\n<li {MARKER}>\n"
        f'<a href="{prefix}{HUB[1]}" class="dropdown-toggle" aria-haspopup="true" '
        f'aria-expanded="false">Dove lavoro ▼</a>\n'
        f'<ul class="dropdown-menu">\n{items}\n</ul>\n</li>'
    )


def _servizi_end(nav):
    """Index in nav right after the </li> that closes the Servizi dropdown."""
    start = nav.find('<li class="dropdown">')
    if start == -1:
        return -1
    menu_end = nav.find("</ul>", start)
    li_end = nav.find("</li>", menu_end) if menu_end != -1 else -1
    return li_end + len("</li>") if li_end != -1 else -1


def process(path):
    """Insert the dropdown in path. Return True if the file changed."""
    path = Path(path)
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return False
    nav_m = NAV_RE.search(html)
    if not nav_m:
        raise ValueError(f"{path}: no <nav> found")
    nav = nav_m.group(0)
    home = HOME_RE.search(nav)
    end = _servizi_end(nav)
    if not home or end == -1:
        raise ValueError(f"{path}: Home link or Servizi dropdown not found in <nav>")
    new_nav = nav[:end] + block(home.group(1)) + nav[end:]
    path.write_text(html[: nav_m.start()] + new_nav + html[nav_m.end() :], encoding="utf-8")
    return True


def default_targets(root):
    root = Path(root)
    return sorted(
        p for p in root.rglob("*.html")
        if not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )


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
