"""Regression test for the Gmail-corrupted links (fixed in 8d3d9b6, 2e9c295, fce0b1d).

Blog articles pasted from a Gmail draft came with every link wrapped in Gmail's
redirect (`https://www.google.com/url?q=...&source=gmail...`), sometimes with a
double scheme (`http://https://...`). It happened three times in two days
(2026-07-29/30) and each time it was fixed by hand with fix_gmail_links.py.
Red on fce0b1d^ (4 articles of 2026-07-30), green after the fix.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "tests", "node_modules", "_site", "test-results", "playwright-report"}

GMAIL_REDIRECT = re.compile(r"google\.com/url\?q=|[?&](?:amp;)?source=gmail")
DOUBLE_SCHEME = re.compile(r"https?://https?://")


def site_pages():
    for path in sorted(REPO_ROOT.rglob("*.html")):
        if not SKIP_DIRS.intersection(path.relative_to(REPO_ROOT).parts):
            yield path


def offending_links(pattern):
    found = []
    for page in site_pages():
        for n, line in enumerate(page.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern.search(line):
                found.append(f"{page.relative_to(REPO_ROOT)}:{n}")
    return found


def test_the_site_has_pages_to_scan():
    assert len(list(site_pages())) > 10


def test_no_link_wrapped_in_the_gmail_redirect():
    assert offending_links(GMAIL_REDIRECT) == []


def test_no_link_with_a_double_scheme():
    assert offending_links(DOUBLE_SCHEME) == []
