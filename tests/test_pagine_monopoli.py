"""MSW-012: dedicated Monopoli pages for web designer and gestionali."""
import html as htmllib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = {
    "web-designer-monopoli.html": "Web Designer",
    "gestionali-monopoli.html": "Gestionali",
    "sviluppatore-app-monopoli.html": "Sviluppatore App",
}
APP_PAGE = "sviluppatore-app-monopoli.html"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def title_of(name):
    m = re.search(r"<title>(.*?)</title>", read(name), re.S)
    return htmllib.unescape(" ".join(m.group(1).split()))


@pytest.mark.parametrize("page,keyword", PAGES.items())
def test_title_len(page, keyword):
    title = title_of(page)
    assert len(title) <= 60
    assert title.startswith(keyword)
    assert title.endswith(" | Pikobit")


@pytest.mark.parametrize("page", PAGES)
def test_description_and_canonical(page):
    html = read(page)
    desc = re.search(r'name="description"\s+content="([^"]*)"', html).group(1)
    assert len(htmllib.unescape(desc)) <= 155
    assert f'rel="canonical" href="https://pikobit.it/{page}"' in html


@pytest.mark.parametrize("page,keyword", PAGES.items())
def test_h1_unico(page, keyword):
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", read(page), re.S)
    assert len(h1) == 1
    assert keyword.lower() in h1[0].lower() and "monopoli" in h1[0].lower()


@pytest.mark.parametrize("page", PAGES)
def test_words_and_home_link(page):
    main = re.search(r"<main>(.*?)</main>", read(page), re.S).group(1)
    text = re.sub(r"<[^>]+>", " ", main)
    assert len(text.split()) >= 350
    assert re.search(r'<a href="index\.html"[^>]*>\s*programmatore a Monopoli\s*</a>', main)


@pytest.mark.parametrize("page", PAGES)
def test_in_sitemap(page):
    assert f"<loc>https://pikobit.it/{page}</loc>" in read("sitemap.xml")


@pytest.mark.parametrize("page", PAGES)
def test_linked_from_dove_lavoro(page):
    assert f'href="{page}"' in read("dove-lavoro.html")


@pytest.mark.parametrize("page", ["web-designer-monopoli.html", "gestionali-monopoli.html"])
def test_linked_from_index(page):
    assert f'href="{page}"' in read("index.html")


def test_app_page_linked_from_modern_apps():
    assert f'href="{APP_PAGE}"' in read("modern-apps.html")


def test_app_page_links_services_and_contact():
    main = re.search(r"<main>(.*?)</main>", read(APP_PAGE), re.S).group(1)
    for target in ("modern-apps.html", "contact.html"):
        assert f'href="{target}"' in main


def test_app_page_cites_only_apps_with_a_page():
    main = re.search(r"<main>(.*?)</main>", read(APP_PAGE), re.S).group(1)
    for app in ("Crucidev", "MentalLoad", "PienoGiusto"):
        if app in main:
            assert f'href="{app.lower()}/' in main, app


def test_titles_differ_from_home_and_monopoli():
    others = {title_of("index.html"), title_of("programmatore-monopoli.html")}
    assert not others & {title_of(p) for p in PAGES}


@pytest.mark.parametrize("page", PAGES)
def test_documented_in_seo_md(page):
    assert f"`{page}`" in read("docs/SEO.md")
