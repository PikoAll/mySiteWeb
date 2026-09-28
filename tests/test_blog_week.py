"""Blog "last week" grouping (scripts/blog-week.js) against the real resources.html.

The weekly publishing script adds <div class="article-box"> cards (usually at
the top of the list) and its guardrail counts them: the grouping must work on
that markup as it is, with the date read from the card link. The JS is run
with node, the same code the browser runs.
"""
import datetime as dt
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "scripts" / "blog-week.js"
RESOURCES = ROOT / "resources.html"
CARD = '<div class="article-box">'
OPEN = '<section class="articles-section">'


def recent_flags(hrefs):
    node = shutil.which("node")
    assert node, "node is required to run scripts/blog-week.js"
    code = (
        f"const {{recentFlags}} = require({json.dumps(str(JS))});"
        f"console.log(JSON.stringify(recentFlags({json.dumps(hrefs)})));"
    )
    return json.loads(subprocess.run([node, "-e", code], check=True, capture_output=True, text=True).stdout)


def card_hrefs(html):
    """First link of each article-box, in page order (as the browser sees them)."""
    boxes = html.split(CARD)[1:]
    return [re.search(r'href="([^"]+)"', b).group(1) for b in boxes]


def date_of(href):
    """Date of a blog link, None for the old external links without one."""
    m = re.search(r"blog/(\d{4}-\d{2}-\d{2})-", href)
    return dt.date.fromisoformat(m.group(1)) if m else None


def newest_of(hrefs):
    return max(d for d in map(date_of, hrefs) if d)


def pipeline_adds_on_top(html, slug_date):
    card = (
        f'\n                {CARD}\n'
        f"                    <h3>Articolo nuovo</h3>\n"
        f"                    <p>Aggiunto dallo script del venerdi.</p>\n"
        f'<a href="blog/{slug_date.isoformat()}-articolo-nuovo.html">Leggi di più</a>\n'
        f"                </div>"
    )
    return html.replace(OPEN, OPEN + card, 1)


@pytest.fixture
def html():
    return RESOURCES.read_text(encoding="utf-8")


def test_all_cards_are_in_the_articles_section_with_a_link(html):
    section = html[html.index(OPEN):]
    assert section.count(CARD) == html.count(CARD) > 0
    hrefs = card_hrefs(html)
    assert len(hrefs) == html.count(CARD)
    # every article of the blog/ folder carries its date in the link
    assert all(date_of(h) for h in hrefs if h.startswith("blog/"))


def test_old_external_links_without_a_date_are_older():
    assert recent_flags(["blog/2026-09-26-a.html", "https://datapizza.tech/blog/0evp"]) == [True, False]
    assert recent_flags(["https://example.com/a", "https://example.com/b"]) == [True, True]


def test_today_the_last_seven_days_before_the_newest_article_are_shown(html):
    hrefs = card_hrefs(html)
    flags = recent_flags(hrefs)
    newest = newest_of(hrefs)
    for href, shown in zip(hrefs, flags):
        d = date_of(href)
        assert shown == (d is not None and d > newest - dt.timedelta(days=7)), href
    assert any(flags) and not all(flags)


def test_card_added_by_the_pipeline_on_top_lands_in_the_last_week(html):
    newest = newest_of(card_hrefs(html))
    friday = newest + dt.timedelta(days=7)
    after = pipeline_adds_on_top(html, friday)
    assert after.count(CARD) == html.count(CARD) + 1  # the guardrail sees one more
    hrefs = card_hrefs(after)
    flags = recent_flags(hrefs)
    assert hrefs[0].startswith(f"blog/{friday.isoformat()}-") and flags[0] is True
    # the previous week moved to "older": only the new card is shown
    assert flags[1:] == [False] * (len(hrefs) - 1)


def test_same_week_card_joins_the_shown_ones(html):
    hrefs = card_hrefs(html)
    before = recent_flags(hrefs)
    newest = newest_of(hrefs)
    flags = recent_flags(card_hrefs(pipeline_adds_on_top(html, newest + dt.timedelta(days=1))))
    assert flags[0] is True
    # cards from 7 days before the new one fall out, the rest stays as it was
    cutoff = newest + dt.timedelta(days=1) - dt.timedelta(days=7)
    assert flags[1:] == [shown and date_of(h) > cutoff for h, shown in zip(hrefs, before)]
