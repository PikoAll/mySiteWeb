"""Tests for lavori.html: the page that collects the real works of Giuseppe.

Allowed works (docs/SEO.md section 5 + the sister sites already linked in the
site): traslochimalusardi.it, Crucidev, portfolio.pikobit.it, lezioni.pikobit.it.
"""
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "lavori.html"

# work name (the h3 of its card) -> host its link must point to
WORKS = {
    "traslochimalusardi.it": "traslochimalusardi.it",
    "Crucidev": "play.google.com",
    "PienoGiusto": "apps.apple.com",
    "MentalLoad": "apps.apple.com",
    "portfolio.pikobit.it": "portfolio.pikobit.it",
    "lezioni.pikobit.it": "lezioni.pikobit.it",
}


class Cards(HTMLParser):
    """Collects the cards of the page: name (h3) and hrefs, plus h1 count."""

    def __init__(self):
        super().__init__()
        self.cards, self.h1 = [], 0
        self._in_card = self._in_h3 = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "li" and "card" in (a.get("class") or "").split():
            self.cards.append({"name": "", "hrefs": []})
            self._in_card = True
        elif tag == "h3" and self._in_card:
            self._in_h3 = True
        elif tag == "a" and self._in_card and a.get("href"):
            self.cards[-1]["hrefs"].append(a["href"])

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
        elif tag == "li":
            self._in_card = False

    def handle_data(self, data):
        if self._in_h3:
            self.cards[-1]["name"] += data


def parsed():
    p = Cards()
    p.feed(PAGE.read_text(encoding="utf-8"))
    return p


def test_page_exists_with_one_h1_and_a_valid_title():
    assert PAGE.exists()
    html = PAGE.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert len(title) <= 60 and title.endswith(" | Pikobit")
    assert parsed().h1 == 1


def test_every_listed_work_has_a_card_with_a_link_to_the_right_place():
    cards = {c["name"].strip(): c for c in parsed().cards}
    assert set(cards) == set(WORKS)
    for name, host in WORKS.items():
        hrefs = cards[name]["hrefs"]
        assert hrefs, f"{name}: card without link"
        assert any(re.match(rf"https://{re.escape(host)}(/|\?|$)", h) for h in hrefs), (name, hrefs)


def test_no_work_name_outside_the_listed_ones():
    """No other card, and no other external link in the main content."""
    p = parsed()
    assert len(p.cards) == len(WORKS)
    main = re.search(r"<main\b.*?</main>", PAGE.read_text(encoding="utf-8"), re.S).group(0)
    hosts = set(re.findall(r'href="https?://([^/"?]+)', main))
    assert hosts <= set(WORKS.values())


def test_page_is_in_the_sitemap_and_linked_from_about_and_menu():
    assert "<loc>https://pikobit.it/lavori.html</loc>" in (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for page in ("about.html", "index.html", "contact.html"):
        assert 'href="lavori.html"' in (ROOT / page).read_text(encoding="utf-8"), page
    about_main = re.search(r"<main\b.*?</main>", (ROOT / "about.html").read_text(encoding="utf-8"), re.S).group(0)
    assert 'href="lavori.html"' in about_main
