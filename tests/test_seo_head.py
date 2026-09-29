"""Tests for scripts/seo_head.py plus site-wide checks of structured data and
SEO meta tags (one Pikobit entity, same sameAs everywhere, breadcrumbs, blog
dates, robots, approved favicons)."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("seo_head", ROOT / "scripts" / "seo_head.py")
seo_head = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_head)

BUSINESS = "https://pikobit.it/#business"
PERSON = "https://pikobit.it/#giuseppe"
BLOCK_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
BRAND_DIR = Path.home() / "Scrivania/PikBitAvatar/brand-approvato/favicon"

BLOG = """<!doctype html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Titolo - Blog PikoBit</title>
<meta
name="description"
content="Descrizione &amp; altro"
/>
<link
rel="canonical"
href="
https://pikobit.it/blog/2026-09-04-prova.html
"
/>
<meta property="og:type" content="article" />
<meta
property="og:title"
content="Titolo lungo
su due righe"
/>
<meta property="og:description" content="Descrizione &amp; altro" />
<meta property="og:image" content="https://pikobit.it/images/brand/og-pikobit-1200x630.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta
property="og:url"
content="
https://pikobit.it/blog/2026-09-04-prova.html
"
/>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Titolo lungo",
  "description": "Descrizione",
  "datePublished": "2026-09-04",
  "author": {"@type": "Person", "name": "PikoBit", "sameAs": ["https://www.youtube.com/@pikobit01"]}
}
</script>
</head>
<body><main><h1>Titolo lungo</h1><p>Testo.</p></main></body>
</html>
"""

SERVICE = """<html lang="it"><head>
    <meta name="viewport" content="width=device-width" />
    <title>Siti Web - Pikobit</title>
    <meta name="description" content="Siti vetrina su misura." />
    <link rel="canonical" href="https://pikobit.it/websites.html" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Siti Web - Pikobit" />
    <meta property="og:description" content="Siti vetrina." />
    <meta name="twitter:card" content="summary_large_image" />
    <!-- Dati strutturati -->
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Siti Web - Pikobit",
        "author": {"@type": "Person", "name": "Pikobit", "sameAs": ["https://www.youtube.com/@pikobit01"]}
      }
    </script>
</head><body><main><h1>Siti web su misura</h1></main></body></html>
"""

PRIVACY = """<html lang="it"><head>
  <meta name="viewport" content="width=device-width" />
  <title>Privacy</title>
  <meta name="robots" content="noindex, follow" />
  <link rel="canonical" href="https://pikobit.it/privacy.html" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Privacy" />
  <meta property="og:description" content="Informativa" />
</head><body><main><h1>Privacy</h1></main></body></html>
"""


def graph(html):
    blocks = BLOCK_RE.findall(html.split("</head>")[0])
    assert len(blocks) == 1
    return json.loads(blocks[0])["@graph"]


def by_type(nodes, t):
    return [n for n in nodes if n.get("@type") == t]


@pytest.fixture
def dates(monkeypatch):
    monkeypatch.setattr(seo_head, "modified_date", lambda rel, published, existing: "2026-09-10")


# --- unit: one page at a time ---------------------------------------------

def test_blog_gets_entity_dates_breadcrumb_and_meta(dates):
    out = seo_head.update_page(BLOG, "blog/2026-09-04-prova.html")
    nodes = graph(out)
    assert by_type(nodes, "ProfessionalService")[0] == seo_head.BUSINESS_NODE
    assert by_type(nodes, "Person")[0] == seo_head.PERSON_NODE
    post = by_type(nodes, "BlogPosting")[0]
    assert post["dateModified"] == "2026-09-10"
    assert post["datePublished"] == "2026-09-04"
    assert post["author"] == {"@id": PERSON}
    assert post["publisher"] == {"@id": BUSINESS}
    assert post["image"] == seo_head.OG_IMAGE
    assert post["mainEntityOfPage"] == {"@id": "https://pikobit.it/blog/2026-09-04-prova.html"}
    crumbs = by_type(nodes, "BreadcrumbList")[0]["itemListElement"]
    assert [c["name"] for c in crumbs] == ["Home", "Blog", "Titolo lungo"]
    assert crumbs[1]["item"] == "https://pikobit.it/resources.html"
    assert '<meta property="article:published_time" content="2026-09-04" />' in out
    assert '<meta property="article:modified_time" content="2026-09-10" />' in out
    assert 'href="https://pikobit.it/blog/2026-09-04-prova.html"' in out
    assert 'content="https://pikobit.it/blog/2026-09-04-prova.html"' in out
    assert '<meta name="twitter:title" content="Titolo lungo su due righe" />' in out
    assert '<meta name="twitter:description" content="Descrizione &amp; altro" />' in out
    assert seo_head.ROBOTS_TAG in out


def test_idempotent(dates):
    for html, rel in ((BLOG, "blog/2026-09-04-prova.html"), (SERVICE, "websites.html"),
                      (PRIVACY, "privacy.html")):
        once = seo_head.update_page(html, rel)
        assert seo_head.update_page(once, rel) == once


def test_visible_text_and_title_untouched(dates):
    out = seo_head.update_page(BLOG, "blog/2026-09-04-prova.html")
    assert out.split("<body>")[1] == BLOG.split("<body>")[1]
    assert "<title>Titolo - Blog Pikobit</title>" in out  # only the brand suffix


def test_service_page_gets_service_and_breadcrumb(dates):
    nodes = graph(seo_head.update_page(SERVICE, "websites.html"))
    svc = by_type(nodes, "Service")[0]
    assert svc["name"] == "Siti web su misura"
    assert svc["description"] == "Siti vetrina su misura."
    assert svc["provider"] == {"@id": BUSINESS}
    assert len(svc["areaServed"]) == 13
    page = by_type(nodes, "WebPage")[0]
    assert page["author"] == {"@id": PERSON}
    crumbs = by_type(nodes, "BreadcrumbList")[0]["itemListElement"]
    assert [c["name"] for c in crumbs] == ["Home", "Siti web personalizzati"]


def test_privacy_keeps_noindex_and_gets_jsonld(dates):
    out = seo_head.update_page(PRIVACY, "privacy.html")
    assert seo_head.ROBOTS_TAG not in out
    assert '<meta name="robots" content="noindex, follow" />' in out
    assert by_type(graph(out), "BreadcrumbList")


def test_verify_flags_a_raw_page():
    problems = seo_head.verify_page(BLOG, "blog/2026-09-04-prova.html")
    joined = "\n".join(problems)
    for needle in ("dateModified", "BreadcrumbList", "robots", "canonical", "twitter:title"):
        assert needle in joined


def test_verify_accepts_an_updated_page(dates):
    out = seo_head.update_page(BLOG, "blog/2026-09-04-prova.html")
    assert seo_head.verify_page(out, "blog/2026-09-04-prova.html") == []


def test_business_entity_content():
    b = seo_head.BUSINESS_NODE
    assert b["@id"] == BUSINESS
    assert b["sameAs"] == [
        "https://www.google.com/maps?cid=16391512325002463359",
        "https://www.instagram.com/pikobit_it/",
        "https://www.youtube.com/@pikobit01",
    ]
    assert b["hasMap"] == "https://www.google.com/maps?cid=16391512325002463359"
    assert set(b["address"]) == {"@type", "addressLocality", "addressRegion", "postalCode", "addressCountry"}
    assert b["geo"]["@type"] == "GeoCoordinates"
    assert b["founder"] == {"@id": PERSON}
    assert "aggregateRating" not in b and "review" not in b
    assert len(b["areaServed"]) == 13
    p = seo_head.PERSON_NODE
    assert p["name"] == "Giuseppe Alaimo"
    assert "https://www.linkedin.com/in/giuseppe-alaimo-aba40b226" in p["sameAs"]
    assert any("superprof.it" in s for s in p["sameAs"])


# --- site-wide: the pages in the working tree ------------------------------

PAGES = seo_head.pages()


def test_page_count():
    assert len(PAGES) >= 75  # every page but crucidev/privacy (an app's policy)


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_site_page_is_conform(page):
    rel = str(page.relative_to(ROOT))
    assert seo_head.verify_page(page.read_text(encoding="utf-8"), rel) == []


def test_same_id_same_data_across_site():
    seen = {}
    for page in PAGES:
        for node in graph(page.read_text(encoding="utf-8")):
            if "@id" in node and len(node) > 1:
                key = node["@id"]
                assert seen.setdefault(key, node) == node, f"{key} differs in {page.name}"


def test_site_is_idempotent(monkeypatch):
    monkeypatch.setattr(seo_head, "modified_date", lambda rel, published, existing: existing or published)
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        assert seo_head.update_page(html, str(page.relative_to(ROOT))) == html, page.name


@pytest.mark.skipif(not BRAND_DIR.exists(), reason="brand folder not on this machine")
@pytest.mark.parametrize("site, approved", [
    ("favicon.ico", "favicon.ico"),
    ("images/brand/favicon-32.png", "favicon-32.png"),
])
def test_favicon_is_the_approved_file(site, approved):
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(ROOT / site) == digest(BRAND_DIR / approved)


def test_favicon_ico_has_16_32_48():
    from PIL import Image
    assert Image.open(ROOT / "favicon.ico").info["sizes"] >= {(16, 16), (32, 32), (48, 48)}


# --- review fixes (2026-09-29, second round) --------------------------------

def test_jsonld_escapes_script_breakout(dates):
    html = SERVICE.replace("<h1>Siti web su misura</h1>", "<h1>Siti &lt;/script&gt;&lt;b&gt; web</h1>")
    html = html.replace("<title>Siti Web - Pikobit</title>", "<title>A &lt;/script&gt;&lt;script&gt;alert(1) &amp; B</title>")
    out = seo_head.update_page(html, "websites.html")
    block = BLOCK_RE.findall(out.split("</head>")[0])[0]
    assert "<" not in block and ">" not in block and "&" not in block
    nodes = json.loads(block)["@graph"]
    assert by_type(nodes, "Service")[0]["name"] == "Siti </script><b> web"
    assert by_type(nodes, "WebPage")[0]["name"] == "A </script><script>alert(1) & B"


def test_untouched_article_is_modified_when_published(monkeypatch):
    monkeypatch.setattr(seo_head, "_history_available", lambda: True)
    monkeypatch.setattr(seo_head._lastmod, "last_content_change", lambda *a: ("2026-07-29", True))
    assert seo_head.modified_date("blog/x.html", "2026-07-28", None) == "2026-07-28"
    monkeypatch.setattr(seo_head._lastmod, "last_content_change", lambda *a: ("2026-09-10", False))
    assert seo_head.modified_date("blog/x.html", "2026-07-28", None) == "2026-09-10"


@pytest.mark.parametrize("bad, needle", [
    ('<img src="images/logo.webp" alt="">', "logo.webp"),
    ('<div style="background:url(../images/filigrana.webp)"></div>', "filigrana.webp"),
    ('<link rel="icon" href="/images/brand/favicon-99.png" />', "favicon-99.png"),
    ('<link rel="manifest" href="/manca.webmanifest" />', "manca.webmanifest"),
])
def test_verify_flags_retired_or_missing_images(dates, bad, needle):
    out = seo_head.update_page(SERVICE, "websites.html").replace("</head>", bad + "\n</head>")
    assert any(needle in p for p in seo_head.verify_page(out, "websites.html"))


def test_verify_flags_missing_og_image(dates):
    out = seo_head.update_page(SERVICE, "websites.html").replace(
        "</head>", '<meta property="og:image" content="https://pikobit.it/images/nope.jpg" />\n</head>')
    assert any("nope.jpg" in p for p in seo_head.verify_page(out, "websites.html"))


def test_offer_catalog_references_service_pages():
    items = seo_head.BUSINESS_NODE["hasOfferCatalog"]["itemListElement"]
    assert all(set(i["itemOffered"]) == {"@id"} for i in items)
    assert {"@id": "https://pikobit.it/websites.html#service"} in [i["itemOffered"] for i in items]


CITY = """<html lang="it"><head>
    <meta name="viewport" content="width=device-width" />
    <title>Programmatore a Bari - Pikobit</title>
    <meta name="description" content="Siti e gestionali per Bari." />
    <link rel="canonical" href="https://pikobit.it/programmatore-bari.html" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Programmatore a Bari - Pikobit" />
    <meta property="og:description" content="Siti e gestionali per Bari." />
</head><body><main><h1>Programmatore e web designer a Bari</h1></main></body></html>
"""


def test_city_page_gets_its_own_service(dates):
    nodes = graph(seo_head.update_page(CITY, "programmatore-bari.html"))
    svc = by_type(nodes, "Service")[0]
    assert svc["@id"] == "https://pikobit.it/programmatore-bari.html#service"
    assert svc["provider"] == {"@id": BUSINESS}
    assert svc["areaServed"] == {"@type": "City", "name": "Bari", "addressCountry": "IT"}
    assert svc["name"] == "Realizzazione siti web, software e app a Bari"
    assert svc["description"] == "Siti e gestionali per Bari."


@pytest.mark.parametrize("html, rel, needle", [
    (BLOG.replace('"@type": "BlogPosting"', '"@type": "Article"'), "blog/2026-09-04-prova.html", "BlogPosting"),
    (re.sub(r"<link\s+rel=\"canonical\".*?/>", "", SERVICE, flags=re.S), "websites.html", "canonical"),
    (PRIVACY.replace('<meta name="viewport" content="width=device-width" />', "")
             .replace("<title>", "<!-- x --><title>"), "privacy.html", "viewport"),
])
def test_broken_page_gives_a_clear_error(tmp_path, capsys, monkeypatch, html, rel, needle):
    monkeypatch.setattr(seo_head, "ROOT", tmp_path)
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    assert seo_head.main([str(target)]) == 1
    err = capsys.readouterr().err
    assert rel in err and needle in err


def test_missing_file_gives_a_clear_error(capsys):
    assert seo_head.main(["non-esiste.html"]) == 1
    assert "non-esiste.html" in capsys.readouterr().err


def test_jsonld_follows_title_h1_and_description(dates):
    once = seo_head.update_page(CITY, "programmatore-bari.html")
    changed = (once.replace("<title>Programmatore a Bari - Pikobit</title>", "<title>Nuovo titolo | Pikobit</title>")
               .replace('content="Siti e gestionali per Bari." />', 'content="Nuova descrizione." />', 1)
               .replace("<h1>Programmatore e web designer a Bari</h1>", "<h1>Nuovo h1 a Bari</h1>"))
    nodes = graph(seo_head.update_page(changed, "programmatore-bari.html"))
    svc = by_type(nodes, "Service")[0]
    assert svc["description"] == "Nuova descrizione."
    service = seo_head.update_page(SERVICE, "websites.html").replace("<h1>Siti web su misura</h1>", "<h1>Nuovo h1</h1>")
    assert by_type(graph(seo_head.update_page(service, "websites.html")), "Service")[0]["name"] == "Nuovo h1"
    page = by_type(nodes, "WebPage")
    assert not page or (page[0]["name"], page[0]["description"]) == ("Nuovo titolo | Pikobit", "Nuova descrizione.")


def test_brand_name_is_pikobit_in_titles(dates):
    html = SERVICE.replace("Siti Web - Pikobit", "Siti Web - PikoBit")
    out = seo_head.update_page(html, "websites.html")
    assert "<title>Siti Web - Pikobit</title>" in out
    assert '<meta property="og:title" content="Siti Web - Pikobit" />' in out
    assert "PikoBit" in seo_head.update_page(SERVICE.replace("<main>", "<main><p>PikoBit</p>"), "websites.html").split("<main>")[1]
    blog = seo_head.update_page(BLOG, "blog/2026-09-04-prova.html")
    assert "<title>Titolo - Blog Pikobit</title>" in blog


def test_verify_flags_pikobit_spelling(dates):
    out = seo_head.update_page(SERVICE, "websites.html").replace("<title>Siti Web - Pikobit", "<title>Siti Web - PikoBit")
    assert any("PikoBit" in p for p in seo_head.verify_page(out, "websites.html"))


# --- pre-merge polish (2026-09-29, third round) ------------------------------

def test_blog_suffix_fixed_across_line_breaks(dates):
    html = BLOG.replace("<title>Titolo - Blog PikoBit</title>", "<title>\nTitolo lungo - Blog\nPikoBit\n</title>")
    out = seo_head.update_page(html, "blog/2026-09-04-prova.html")
    assert "PikoBit" not in out.split("</head>")[0].split("<title>")[1].split("</title>")[0]
    assert "Blog\nPikobit" in out
    bad = out.replace("Blog\nPikobit", "Blog\nPikoBit")
    assert any("PikoBit" in p for p in seo_head.verify_page(bad, "blog/2026-09-04-prova.html"))


def test_city_service_is_named_by_the_service(dates):
    svc = by_type(graph(seo_head.update_page(CITY, "programmatore-bari.html")), "Service")[0]
    assert svc["name"] == "Realizzazione siti web, software e app a Bari"
    assert svc["serviceType"] == seo_head.CITY_SERVICE_TYPE


@pytest.mark.parametrize("title, ok", [
    ("Siti Web - Pikobit", False),
    ("Pikobit - Siti Web", False),
    ("Siti Web | Pikobit", True),
    ("Un titolo davvero troppo lungo per stare nei risultati | Pikobit", False),
])
def test_verify_title_format(dates, title, ok):
    out = seo_head.update_page(SERVICE, "websites.html").replace("<title>Siti Web - Pikobit</title>", f"<title>{title}</title>")
    flagged = any("title" in p and ("| Pikobit" in p or "60" in p) for p in seo_head.verify_page(out, "websites.html"))
    assert flagged is not ok


def test_verify_description_length(dates):
    long = "x" * 156
    out = seo_head.update_page(SERVICE, "websites.html").replace('content="Siti vetrina su misura."', f'content="{long}"', 1)
    assert any("155" in p for p in seo_head.verify_page(out, "websites.html"))
    blog = seo_head.update_page(BLOG.replace("Descrizione &amp; altro", long, 1), "blog/2026-09-04-prova.html")
    assert not any("155" in p for p in seo_head.verify_page(blog, "blog/2026-09-04-prova.html"))


def test_og_and_twitter_description_follow_the_meta_description(dates):
    out = seo_head.update_page(SERVICE, "websites.html")  # og says "Siti vetrina."
    assert '<meta property="og:description" content="Siti vetrina su misura." />' in out
    assert '<meta name="twitter:description" content="Siti vetrina su misura." />' in out
    bad = out.replace('<meta property="og:description" content="Siti vetrina su misura." />',
                      '<meta property="og:description" content="Altro." />')
    assert any("og:description" in p for p in seo_head.verify_page(bad, "websites.html"))


def test_person_knows_the_confirmed_technologies_only():
    # Confirmed by Giuseppe on 2026-09-29: nothing else goes here.
    assert seo_head.PERSON_NODE["knowsAbout"] == [
        "Java", "Spring Boot", "Python", "C", "C++", "Flutter", "Dart", "Kotlin",
        "Android Studio", "Angular", "React", "HTML", "CSS", "JavaScript", "WordPress",
        "PostgreSQL", "MySQL", "Clean Architecture", "Design pattern", "Test automatici",
    ]
