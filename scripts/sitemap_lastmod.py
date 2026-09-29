#!/usr/bin/env python3
"""Set every <lastmod> of sitemap.xml to the date the page CONTENT last changed.

Content = <title> + meta description + the visible text of <main> (same
extractor as scripts/compare_page_text.py). A commit that only touches the
<head> tags, the menu, the footer or the ?v= cache-busting is NOT a content
change, nor is a STANDARD block repeated identical on every article (the
<!-- pikobit-local-cta --> box added to all 51 articles on 2026-09-26): if it moved lastmod, every release would mark all pages as changed
and Google would learn to ignore our lastmod altogether.

Date of a page:
- untracked, or content changed in the working tree vs HEAD -> today;
- otherwise the committer date (%cs) of the newest commit whose content
  differs from its first parent's (or that created the file).

Only the text inside <lastmod> changes; URLs, order, priority stay as they are.
Needs the full git history: in a shallow clone (git clone --depth 1) every
file would date to the single commit, so the script refuses (exit 2).

Usage:
    python3 scripts/sitemap_lastmod.py [--repo DIR] [--today YYYY-MM-DD] [--check]
Exit: 0 ok (with --check: already up to date), 1 --check found changes,
2 cannot work (shallow clone, missing sitemap).
"""
import argparse
import datetime
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://pikobit.it/"

_spec = importlib.util.spec_from_file_location(
    "compare_page_text", Path(__file__).resolve().parent / "compare_page_text.py"
)
_cpt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cpt)

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.S | re.I)
# Standard blocks inside <main>, same on every page: not the page's content.
STANDARD_BLOCKS = [
    re.compile(r"<!-- pikobit-local-cta -->\s*<section\b.*?</section>", re.S),
]
URL_RE = re.compile(r"(<loc>([^<]+)</loc>\s*<lastmod>)([^<]*)(</lastmod>)")


def loc_to_path(loc):
    path = loc[len(SITE):] if loc.startswith(SITE) else loc
    return path + "index.html" if path == "" or path.endswith("/") else path


def signature(html):
    if html is None:
        return None
    parts = [m.group(1) for m in (TITLE_RE.search(html), DESC_RE.search(html)) if m]
    for block in STANDARD_BLOCKS:
        html = block.sub("", html)
    parts.append(_cpt.main_text(html))
    # Words only, lowercase: markup, block boundaries, punctuation and a
    # spelling fix like "PikoBit" -> "Pikobit" are not content.
    return " ".join(re.findall(r"\w+", " ".join(parts).lower()))


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def _show(repo, rev, path):
    res = _git(repo, "show", f"{rev}:{path}")
    return res.stdout if res.returncode == 0 else None


def last_content_change(repo, path, today):
    """(date, created): date of the last content change, and whether that
    change is the page's creation (its text never changed since)."""
    if _git(repo, "ls-files", "--error-unmatch", path).returncode != 0:
        return today, True
    work = Path(repo, path)
    if work.exists() and signature(work.read_text(encoding="utf-8")) != signature(_show(repo, "HEAD", path)):
        return today, False
    log = _git(repo, "log", "--format=%H %cs", "--", path).stdout.split("\n")
    for line in filter(None, log):
        rev, date = line.split()
        before = signature(_show(repo, f"{rev}^", path))
        if signature(_show(repo, rev, path)) != before:
            return date, before is None
    return today, False


def last_content_date(repo, path, today):
    return last_content_change(repo, path, today)[0]


def update_sitemap(xml, dates):
    return URL_RE.sub(
        lambda m: m.group(1) + dates.get(m.group(2), m.group(3)) + m.group(4), xml
    )


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--today", default=datetime.date.today().isoformat())
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo)

    if _git(repo, "rev-parse", "--is-shallow-repository").stdout.strip() != "false":
        print("sitemap_lastmod: shallow clone or not a git repo, full history needed "
              "(clone without --depth, or git fetch --unshallow)", file=sys.stderr)
        return 2
    sitemap = repo / "sitemap.xml"
    if not sitemap.exists():
        print("sitemap_lastmod: sitemap.xml not found", file=sys.stderr)
        return 2

    xml = sitemap.read_text(encoding="utf-8")
    dates = {
        m.group(2): last_content_date(repo, loc_to_path(m.group(2)), args.today)
        for m in URL_RE.finditer(xml)
    }
    new = update_sitemap(xml, dates)
    changed = sum(a != b for a, b in zip(URL_RE.findall(xml), URL_RE.findall(new)))
    if args.check:
        print(f"sitemap_lastmod: {changed} lastmod out of date")
        return 1 if changed else 0
    if new != xml:
        sitemap.write_text(new, encoding="utf-8")
    print(f"sitemap_lastmod: {changed}/{len(dates)} lastmod updated")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
