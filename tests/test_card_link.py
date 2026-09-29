"""Guard for the card classes: a card that is a link (its h3 link covers the
whole card) carries .card--link, and only those do. The hover glow, the
pointer and the "Scopri di più" arrow hang on that class, so a card that is
not clickable never looks like a button."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "tests", "node_modules", "_site"}
CARD_RE = re.compile(r'<li class="(card(?:\s[^"]*)?)">(.*?)</li>', re.S)


def pages():
    return sorted(p for p in ROOT.rglob("*.html")
                  if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts))


def test_card_link_class_matches_the_stretched_link():
    wrong = []
    for page in pages():
        for classes, body in CARD_RE.findall(page.read_text(encoding="utf-8")):
            linked = re.search(r"<h3>\s*<a\b", body) is not None
            if linked != ("card--link" in classes.split()):
                wrong.append(f"{page.relative_to(ROOT)}: {classes} {body.strip()[:60]!r}")
    assert wrong == []


def test_some_cards_are_links_and_some_are_not():
    """The regex above must keep matching the real markup (not pass on zero cards)."""
    classes = [c for p in pages() for c, _ in CARD_RE.findall(p.read_text(encoding="utf-8"))]
    assert any("card--link" in c for c in classes)
    assert any("card--link" not in c for c in classes)


CHIPS_RE = re.compile(r'<ul class="city-grid">(.*?)</ul>', re.S)


def test_city_chip_is_clickable_iff_it_holds_a_link():
    wrong = []
    for page in pages():
        for ul in CHIPS_RE.findall(page.read_text(encoding="utf-8")):
            for attrs, body in re.findall(r"<li\b([^>]*)>(.*?)</li>", ul, re.S):
                if ("<a " in body) != ('class="card--link"' in attrs):
                    wrong.append(f"{page.relative_to(ROOT)}: {body.strip()[:60]!r}")
    assert wrong == []
