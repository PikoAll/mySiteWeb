"""Tests for scripts/site_chrome.py: one header/menu/footer-zone for every page, idempotent."""
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "site_chrome.py"
spec = importlib.util.spec_from_file_location("site_chrome", SCRIPT)
site_chrome = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_chrome)

# Old chrome, two real-world formattings: prettier (root pages) and compact
# (blog, crucidev), with the "Dove lavoro" dropdown of the previous release.
ROOT_PAGE = """<html><head>
<link rel="icon" href="./images/logo.webp" type="image/png" />
<script type="application/ld+json">{"image": "https://pikobit.it/images/logo.webp"}</script>
</head><body>
    <header>
      <img
        src="./images/banner.webp"
        alt="Pikobit Banner"
        class="banner"
        width="1024"
        height="587"
      />
      <div class="hamburger" id="hamburger-menu" role="button" tabindex="0" aria-label="Apri menu di navigazione" aria-expanded="false">
        <svg class="icon-svg" viewBox="0 0 448 512" aria-hidden="true"><path d="M0 96z"/></svg>
      </div>
      <div class="overlay" id="overlay"></div>
      <nav id="navbar">
        <ul class="nav-links">
          <li><a href="index.html">Home</a></li>
          <li class="dropdown">
            <a href="#" id="dropdown-toggle" aria-haspopup="true" aria-expanded="false">Servizi ▼</a>
            <ul class="dropdown-menu">
              <li><a href="websites.html">Siti web personalizzati</a></li>
            </ul>
          </li>
<li class="dropdown nav-zone">
<a href="dove-lavoro.html" class="dropdown-toggle" aria-haspopup="true" aria-expanded="false">Dove lavoro ▼</a>
<ul class="dropdown-menu">
<li><a href="programmatore-monopoli.html">Monopoli</a></li>
</ul>
</li>
          <li><a href="ideas.html">Idee Innovative</a></li>
          <li><a href="resources.html">Risorse</a></li>
          <li><a href="contact.html">Contatti</a></li>
        </ul>
      </nav>
    </header>
    <main>
      <section class="intro">
        <div class="intro-container">
          <img
            src="./images/logo.webp"
            alt="Logo Pikobit - Tutorial e Progetti di Programmazione"
            class="logo"
            width="671"
            height="752"
          />
          <h1>Titolo</h1>
        </div>
      </section>
    </main>
    <footer>
<p class="nap">Pikobit · Monopoli (BA)</p>
      <p>&copy; 2026 Pikobit.</p>
    </footer>
</body></html>
"""

NESTED_PAGE = """<html><body>
<header>
<img src="../../images/banner.webp" alt="Pikobit Banner" class="banner" width="1024" height="587" />
<nav id="navbar">
<ul class="nav-links">
<li><a href="../../index.html">Home</a></li>
<li><a href="../../contact.html">Contatti</a></li>
</ul>
</nav>
</header>
<main><div class="intro-container"><img src="../../images/logo.webp" alt="Logo Pikobit" class="logo" width="671" height="752" /></div></main>
<footer>
<p class="nap">Pikobit</p>
</footer>
</body></html>
"""

MENU = ["Home", "Servizi ▼", "Dove lavoro", "Progetti &amp; idee", "Chi sono", "Blog", "Contatti"]
CITY_ORDER = [
    "Monopoli", "Bari", "Polignano a Mare", "Fasano", "Conversano",
    "Castellana Grotte", "Putignano", "Turi", "Casamassima", "Ostuni",
    "Brindisi", "Taranto", "Lecce",
]


def write(tmp_path, rel, text):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def header_of(html):
    return re.search(r"<header\b.*?</header>", html, re.S).group(0)


def footer_of(html):
    return re.search(r"<footer\b.*?</footer>", html, re.S).group(0)


def top_level_labels(header):
    ul = header[header.index('class="nav-links"'):]
    # drop the Servizi submenu, keep only the first-level entries
    ul = re.sub(r'<ul class="dropdown-menu">.*?</ul>', "", ul, flags=re.S)
    return [re.sub(r"\s+", " ", t).strip() for t in re.findall(r"<a\b[^>]*>(.*?)</a>", ul, re.S)]


@pytest.fixture
def root_page(tmp_path):
    return write(tmp_path, "index.html", ROOT_PAGE)


@pytest.fixture
def nested_page(tmp_path):
    return write(tmp_path, "crucidev/privacy/index.html", NESTED_PAGE)


def test_menu_has_the_approved_entries_in_order(root_page):
    assert site_chrome.process(root_page, root_page.parent) is True
    header = header_of(root_page.read_text(encoding="utf-8"))
    assert top_level_labels(header) == MENU


def test_dove_lavoro_is_a_plain_link_without_dropdown(root_page):
    site_chrome.process(root_page, root_page.parent)
    header = header_of(root_page.read_text(encoding="utf-8"))
    assert "nav-zone" not in header
    assert "programmatore-" not in header
    assert re.search(r'<a href="dove-lavoro.html"[^>]*>Dove lavoro</a>', header)
    assert header.count('<li class="dropdown">') == 1  # only Servizi


def test_renamed_entries_keep_the_same_urls(root_page):
    site_chrome.process(root_page, root_page.parent)
    header = header_of(root_page.read_text(encoding="utf-8"))
    assert re.search(r'href="ideas.html"[^>]*>Progetti &amp; idee<', header)
    assert re.search(r'href="resources.html"[^>]*>Blog<', header)


def test_contatti_is_the_highlighted_button(root_page):
    site_chrome.process(root_page, root_page.parent)
    header = header_of(root_page.read_text(encoding="utf-8"))
    assert re.search(r'<li class="nav-cta"><a href="contact.html"[^>]*>Contatti</a></li>', header)


def test_header_is_vector_no_raster_banner(root_page):
    site_chrome.process(root_page, root_page.parent)
    html = root_page.read_text(encoding="utf-8")
    header = header_of(html)
    assert "banner.webp" not in header
    assert '<svg class="wordmark"' in header
    assert 'aria-label="Pikobit, vai alla home"' in header


def test_hamburger_is_a_real_button(root_page):
    site_chrome.process(root_page, root_page.parent)
    header = header_of(root_page.read_text(encoding="utf-8"))
    button = re.search(r'<button[^>]*id="hamburger-menu"[^>]*>', header).group(0)
    assert 'type="button"' in button
    assert 'aria-expanded="false"' in button
    assert 'aria-controls="navbar"' in button
    assert header.count('id="dropdown-toggle"') == 1


def test_links_use_the_page_relative_prefix(nested_page, tmp_path):
    site_chrome.process(nested_page, tmp_path)
    html = nested_page.read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"#]+)"', header_of(html) + footer_of(html))
    local = [h for h in hrefs if not h.startswith("https://")]
    assert local and all(h.startswith("../../") for h in local)


def test_footer_lists_all_cities_in_order(root_page):
    site_chrome.process(root_page, root_page.parent)
    footer = footer_of(root_page.read_text(encoding="utf-8"))
    zone = re.search(r'<nav class="footer-zone".*?</nav>', footer, re.S).group(0)
    links = re.findall(r'<a href="(programmatore-[a-z-]+\.html)">([^<]+)</a>', zone)
    assert [label for _, label in links] == CITY_ORDER
    assert ("programmatore-castellana-grotte.html", "Castellana Grotte") in links
    # the zone line sits right after the NAP line
    assert footer.index('class="nap"') < footer.index('class="footer-zone"')


def test_intro_logo_becomes_the_vector_mark_with_the_same_alt(root_page):
    site_chrome.process(root_page, root_page.parent)
    html = root_page.read_text(encoding="utf-8")
    main = html[html.index("<main>"):html.index("</main>")]
    img = re.search(r'<img[^>]*class="logo"[^>]*>', main).group(0)
    assert 'src="./images/brand/pikobit-symbol.svg"' in img
    assert 'alt="Logo Pikobit - Tutorial e Progetti di Programmazione"' in img
    assert 'width="120"' in img and 'height="112"' in img
    # favicon and JSON-LD keep the raster logo
    assert 'rel="icon" href="./images/logo.webp"' in html
    assert '"image": "https://pikobit.it/images/logo.webp"' in html


def test_current_page_is_marked(tmp_path):
    about = write(tmp_path, "about.html", ROOT_PAGE)
    post = write(tmp_path, "blog/2026-09-26-x.html", NESTED_PAGE.replace("../../", "../"))
    city = write(tmp_path, "programmatore-bari.html", ROOT_PAGE)
    for p in (about, post, city):
        site_chrome.process(p, tmp_path)
    assert re.search(r'href="about.html" aria-current="page">Chi sono', about.read_text(encoding="utf-8"))
    assert header_of(about.read_text(encoding="utf-8")).count("aria-current") == 1


def test_child_pages_mark_the_parent_section_not_the_current_page(tmp_path):
    """A city page is a child of "Dove lavoro", a post a child of "Blog": the
    parent gets the light .nav-parent style, never aria-current (that would
    announce and paint it as the page you are on)."""
    post = write(tmp_path, "blog/2026-09-26-x.html", NESTED_PAGE.replace("../../", "../"))
    city = write(tmp_path, "programmatore-bari.html", ROOT_PAGE)
    for p in (post, city):
        site_chrome.process(p, tmp_path)
    assert re.search(r'href="../resources.html" class="nav-parent">Blog', post.read_text(encoding="utf-8"))
    assert re.search(r'href="dove-lavoro.html" class="nav-parent">Dove lavoro', city.read_text(encoding="utf-8"))
    for p in (post, city):
        assert "aria-current" not in header_of(p.read_text(encoding="utf-8"))


BREADCRUMB = """<nav class="breadcrumb" aria-label="Percorso">
        <a href="index.html">Home</a> ›
        <a href="dove-lavoro.html">Dove lavoro</a> ›
        <span aria-current="page">{}</span>
      </nav>"""


def test_city_page_gets_the_breadcrumb_right_after_main(tmp_path):
    city = write(tmp_path, "programmatore-polignano-a-mare.html", ROOT_PAGE)
    site_chrome.process(city, tmp_path)
    html = city.read_text(encoding="utf-8")
    assert "<main>\n      " + BREADCRUMB.format("Polignano a Mare") in html
    assert html.count('class="breadcrumb"') == 1


def test_city_breadcrumb_replaces_a_stale_one(tmp_path):
    stale = ROOT_PAGE.replace("<main>", '<main>\n      <nav class="breadcrumb" aria-label="Percorso"><a href="index.html">Home</a> › Bari</nav>')
    city = write(tmp_path, "programmatore-bari.html", stale)
    site_chrome.process(city, tmp_path)
    html = city.read_text(encoding="utf-8")
    assert BREADCRUMB.format("Bari") in html
    assert html.count('class="breadcrumb"') == 1


def test_other_pages_get_no_breadcrumb(root_page):
    site_chrome.process(root_page, root_page.parent)
    assert 'class="breadcrumb"' not in root_page.read_text(encoding="utf-8")


def test_every_city_breadcrumb_matches_its_jsonld():
    """Visible breadcrumb and BreadcrumbList JSON-LD say the same thing."""
    import json
    root = SCRIPT.parent.parent
    for label, page in site_chrome.CITIES:
        html = (root / page).read_text(encoding="utf-8")
        assert BREADCRUMB.format(label) in html, page
        graph = []
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            data = json.loads(block)
            graph += data.get("@graph", [data])
        crumbs = [n for n in graph if n.get("@type") == "BreadcrumbList"]
        assert len(crumbs) == 1, page
        names = [i["name"] for i in crumbs[0]["itemListElement"]]
        assert names == ["Home", "Dove lavoro", label], page


def test_second_run_changes_nothing(root_page, nested_page, tmp_path):
    for p, root in ((root_page, root_page.parent), (nested_page, tmp_path)):
        site_chrome.process(p, root)
        first = p.read_bytes()
        assert site_chrome.process(p, root) is False
        assert p.read_bytes() == first


def test_page_without_header_or_footer_is_an_error(tmp_path):
    original = '<nav id="navbar"><ul><li><a href="index.html">Home</a></li></ul></nav>'
    p = write(tmp_path, "x.html", original)
    with pytest.raises(ValueError):
        site_chrome.process(p, tmp_path)
    assert p.read_text(encoding="utf-8") == original


def test_every_real_page_already_carries_the_current_chrome():
    """Guard: a page added later (e.g. by the weekly blog script) with a stale
    header fails here; running scripts/site_chrome.py fixes it."""
    root = SCRIPT.parent.parent
    stale = [str(p.relative_to(root)) for p in site_chrome.default_targets(root)
             if site_chrome.render(p, root) != p.read_text(encoding="utf-8")]
    assert stale == []


def test_wordmark_file_has_the_same_drawing_as_the_header():
    """images/brand/pikobit-wordmark.svg (brand kit) and the inline header
    wordmark must not drift apart: same paths, same viewBox."""
    kit = (SCRIPT.parent.parent / "images" / "brand" / "pikobit-wordmark.svg").read_text(encoding="utf-8")
    inner = lambda s: re.search(r"<svg\b[^>]*>(.*)</svg>", s, re.S).group(1)
    box = lambda s: re.search(r'viewBox="([^"]+)"', s).group(1)
    assert inner(kit) == inner(site_chrome.WORDMARK)
    assert box(kit) == box(site_chrome.WORDMARK)


MAPS = "https://www.google.com/maps?cid=16391512325002463359"


def test_footer_links_the_google_business_profile(root_page):
    site_chrome.process(root_page, root_page.parent)
    legal = re.search(r'<p class="footer-legal">.*?</p>', footer_of(root_page.read_text(encoding="utf-8")), re.S).group(0)
    assert f'<a href="{MAPS}" target="_blank" rel="noopener">Trovami su Google Maps</a>' in legal
