#!/usr/bin/env python3
"""Check that every internal link of the static site points to an existing file.

Scans every *.html of the repo (tests/ and .git excluded), collects href/src
values that are internal (no scheme, not mailto:/tel:/#/data:), strips query
and fragment, resolves them against the page, and reports the missing targets.
A link to a directory is valid when that directory has an index.html.
It also checks that every <loc> of sitemap.xml maps to an existing page.

Usage:
    python3 scripts/check_internal_links.py      # exit 0 no broken links, 1 otherwise
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://pikobit.it/"
SKIP_DIRS = {".git", "tests", "node_modules"}


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value.strip())


def _is_internal(href):
    parts = urlsplit(href)
    return not parts.scheme and not parts.netloc and not href.startswith("#")


def _target_exists(root, path):
    if path.is_dir():
        return (path / "index.html").is_file()
    return path.is_file() and path.resolve().is_relative_to(root.resolve())


def pages(root):
    return sorted(
        p for p in Path(root).rglob("*.html")
        if not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )


def broken_links(root):
    root = Path(root)
    broken = []
    for page in pages(root):
        parser = _LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.links:
            if not _is_internal(href):
                continue
            rel = unquote(urlsplit(href).path)
            if not rel:
                continue
            target = (root / rel.lstrip("/")) if rel.startswith("/") else (page.parent / rel)
            if not _target_exists(root, target):
                broken.append((page, href))
    return broken


def missing_sitemap_targets(root, site_url=SITE_URL):
    root = Path(root)
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        return []
    missing = []
    for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sitemap.read_text(encoding="utf-8")):
        if not loc.startswith(site_url):
            missing.append(loc)
            continue
        rel = loc[len(site_url):]
        if not _target_exists(root, root / rel if rel else root):
            missing.append(loc)
    return missing


def main():
    broken = broken_links(REPO_ROOT)
    missing = missing_sitemap_targets(REPO_ROOT)
    for page, href in broken:
        print(f"BROKEN {page.relative_to(REPO_ROOT)} -> {href}")
    for loc in missing:
        print(f"SITEMAP MISSING {loc}")
    print(f"{len(pages(REPO_ROOT))} pages scanned, {len(broken)} broken links, "
          f"{len(missing)} sitemap entries without a page")
    return 1 if broken or missing else 0


if __name__ == "__main__":
    sys.exit(main())
