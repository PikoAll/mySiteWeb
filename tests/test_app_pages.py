"""Pagine schede delle app realizzate: PienoGiusto e MentalLoad."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

APPS = {
    "app-pienogiusto.html": ("PienoGiusto", "https://apps.apple.com/it/app/pienogiusto/id6837226724", "pienogiusto"),
    "app-mentalload.html": ("MentalLoad", "https://apps.apple.com/it/app/mentalload/id6837226677", "mentalload"),
}


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_each_app_page_has_title_description_h1_and_store_link():
    for page, (name, link, _) in APPS.items():
        html = read(page)
        title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
        desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html, re.S).group(1)
        assert len(title) <= 60 and title.endswith(" | Pikobit") and name in title, (page, title)
        assert 70 <= len(desc) <= 155, (page, len(desc))
        assert len(re.findall(r"<h1\b", html)) == 1, page
        assert f'href="{link}"' in html, page
        assert "presto su Google Play" in html, page
        assert "badge-app-store-it.svg" in html, page


def test_each_app_page_has_real_screenshots_that_exist_with_alt_and_size():
    for page, (_, _, slug) in APPS.items():
        html = read(page)
        shots = re.findall(rf'<img[^>]+src="(images/apps/{slug}-(?!icona)[^"]+)"[^>]*>', html)
        assert len(shots) >= 4, page
        for tag in re.findall(r"<img[^>]+>", html):
            assert 'alt="' in tag and "width=" in tag and "height=" in tag, tag
        for src in shots:
            assert (ROOT / src).exists(), src


def test_app_pages_have_no_personal_data():
    for page in APPS:
        low = read(page).lower()
        for bad in ("alaimo", "giuseppe a", "@gmail", "+39", "via "):
            main = re.search(r"<main\b.*?</main>", low, re.S).group(0)
            assert bad not in main, (page, bad)


def test_app_pages_are_in_sitemap_and_linked_from_lavori():
    sm = read("sitemap.xml")
    lav = read("lavori.html")
    for page in APPS:
        assert f"<loc>https://pikobit.it/{page}</loc>" in sm, page
        assert f'href="{page}"' in lav, page


def test_pagine_app_og_description_e_lazy():
    import pathlib
    for f in ("app-mentalload.html", "app-pienogiusto.html"):
        s = (pathlib.Path(__file__).resolve().parent.parent / f).read_text()
        assert 'property="og:description"' in s
        assert s.count('loading="lazy"') == 4
