#!/usr/bin/env python3
"""Check that every internal link of the static site points to an existing file.

Scans every *.html of the repo (tests/ and .git excluded), collects href/src
values that are internal (no scheme, not mailto:/tel:/#/data:), strips query
and fragment, resolves them against the page, and reports the missing targets.
A link to a directory is valid when that directory has an index.html.
It also checks that every <loc> of sitemap.xml maps to an existing page, and
the assets referenced outside the HTML: url(...) in the CSS, the icons of
site.webmanifest, and for every data-fx="scene" the scripts the loader of
scripts/script.js will fetch (scripts/fx/<scene>.js, scripts/fx/core.js,
styles/fx.css).

Usage:
    python3 scripts/check_internal_links.py              # the repo
    python3 scripts/check_internal_links.py --root _site # the built site
Exit: 0 no broken reference, 1 otherwise.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://pikobit.it/"
SKIP_DIRS = {".git", "tests", "node_modules", "_site"}  # _site: built copy, see build_site.py


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


CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
FX_RE = re.compile(r'data-fx="([a-z-]+)"')


def _files(root, pattern):
    return sorted(
        p for p in Path(root).rglob(pattern)
        if not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )


def broken_assets(root):
    """(file, reference) for assets referenced outside the HTML links."""
    root = Path(root)
    broken = []
    for css in _files(root, "*.css"):
        for ref in CSS_URL_RE.findall(css.read_text(encoding="utf-8")):
            if ref.startswith("data:") or not _is_internal(ref):
                continue
            rel = unquote(urlsplit(ref).path)
            target = (root / rel.lstrip("/")) if rel.startswith("/") else (css.parent / rel)
            if not _target_exists(root, target):
                broken.append((css, ref))
    manifest = root / "site.webmanifest"
    if manifest.is_file():
        for icon in json.loads(manifest.read_text(encoding="utf-8")).get("icons", []):
            src = icon.get("src", "")
            if _is_internal(src) and not _target_exists(root, root / src.lstrip("/")):
                broken.append((manifest, src))
    scenes = {m for page in pages(root) for m in FX_RE.findall(page.read_text(encoding="utf-8"))}
    needed = [f"scripts/fx/{scene}.js" for scene in sorted(scenes)]
    needed += ["scripts/fx/core.js", "styles/fx.css"] if scenes else []
    broken += [(root, f) for f in needed if not (root / f).is_file()]
    return broken


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[1]) if args[:1] == ["--root"] and len(args) == 2 else REPO_ROOT
    broken = broken_links(root)
    missing = missing_sitemap_targets(root)
    assets = broken_assets(root)
    for page, href in broken:
        print(f"BROKEN {page.relative_to(root)} -> {href}")
    for loc in missing:
        print(f"SITEMAP MISSING {loc}")
    for where, ref in assets:
        print(f"ASSET MISSING {where} -> {ref}")
    print(f"{len(pages(root))} pages scanned, {len(broken)} broken links, "
          f"{len(missing)} sitemap entries without a page, {len(assets)} missing assets")
    return 1 if broken or missing or assets else 0


if __name__ == "__main__":
    sys.exit(main())
