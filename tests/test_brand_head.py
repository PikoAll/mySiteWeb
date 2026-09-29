"""Tests for scripts/brand_head.py and a site-wide check of the brand <head> tags."""
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "brand_head.py"
spec = importlib.util.spec_from_file_location("brand_head", SCRIPT)
brand_head = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand_head)

OG_IMAGE = "https://pikobit.it/images/brand/og-pikobit-1200x630.jpg"
LOGO = "https://pikobit.it/images/brand/pikobit-logo-512.png"

# Two real-world formattings: prettier (root pages) and compact (blog).
ROOT_PAGE = """<html><head>
    <link rel="canonical" href="https://pikobit.it/" />
    <meta property="og:type" content="website" />
    <meta property="og:image" content="https://pikobit.it/images/banner.webp" />
    <meta property="og:url" content="https://pikobit.it/" />
    <link rel="icon" href="./images/logo.webp" type="image/png" />
    <script type="application/ld+json">
      {
        "@type": "ProfessionalService",
        "image": "https://pikobit.it/images/logo.webp",
        "telephone": "+39"
      }
    </script>
</head><body><main><h1>Ciao</h1></main></body></html>
"""

BLOG_PAGE = """<html><head>
<meta property="og:type" content="article" />
<meta property="og:image"
content="https://pikobit.it/images/banner.webp" />
<link rel="icon" href="../images/logo.webp" type="image/png">
<link rel="icon" href="../images/logo.webp" type="image/png">
</head><body></body></html>
"""


def test_favicon_block_replaces_old_webp_icon():
    out = brand_head.update_head(ROOT_PAGE)
    assert "logo.webp" not in out.split("<script")[0]
    assert '<link rel="icon" href="/favicon.ico" sizes="any" />' in out
    assert 'href="/images/brand/favicon-32.png"' in out
    assert 'href="/images/brand/favicon-192.png"' in out
    assert '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />' in out
    assert '<link rel="manifest" href="/site.webmanifest" />' in out
    assert '<meta name="theme-color" content="#0d0f12" />' in out


def test_duplicate_old_icon_links_collapse_into_one_block():
    out = brand_head.update_head(BLOG_PAGE)
    assert out.count('href="/favicon.ico"') == 1
    assert "logo.webp" not in out


def test_og_image_and_social_tags():
    for page in (ROOT_PAGE, BLOG_PAGE):
        out = brand_head.update_head(page)
        assert "banner.webp" not in out
        assert f'<meta property="og:image" content="{OG_IMAGE}" />' in out
        assert '<meta property="og:image:width" content="1200" />' in out
        assert '<meta property="og:image:height" content="630" />' in out
        assert 'property="og:image:alt"' in out
        assert '<meta property="og:locale" content="it_IT" />' in out
        assert '<meta property="og:site_name" content="Pikobit" />' in out
        assert '<meta name="twitter:card" content="summary_large_image" />' in out
        assert f'<meta name="twitter:image" content="{OG_IMAGE}" />' in out


def test_jsonld_image_becomes_square_logo_imageobject():
    out = brand_head.update_head(ROOT_PAGE)
    data = json.loads(re.search(r'ld\+json">(.*?)</script>', out, re.S).group(1))
    for key in ("image", "logo"):
        assert data[key] == {"@type": "ImageObject", "url": LOGO, "width": 512, "height": 512}
    assert data["telephone"] == "+39"


def test_idempotent():
    for page in (ROOT_PAGE, BLOG_PAGE):
        once = brand_head.update_head(page)
        assert brand_head.update_head(once) == once


def test_body_untouched():
    out = brand_head.update_head(ROOT_PAGE)
    assert out.split("</head>")[1] == ROOT_PAGE.split("</head>")[1]


# --- site-wide check on the real pages ------------------------------------

PAGES = sorted(
    p for p in ROOT.rglob("*.html")
    if not {"node_modules", "tests", "_site"} & set(p.relative_to(ROOT).parts)
)


def _attr(html, attr_name, attr_value, target):
    m = re.search(
        rf'<(?:meta|link)\s+{attr_name}="{re.escape(attr_value)}"\s+{target}="([^"]*)"',
        html,
    )
    return m.group(1) if m else None


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_page_has_brand_head(page):
    html = page.read_text(encoding="utf-8")
    head = re.sub(r"\s+", " ", html.split("</head>")[0])
    assert '<link rel="icon" href="/favicon.ico" sizes="any" />' in head
    assert '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />' in head
    assert '<link rel="manifest" href="/site.webmanifest" />' in head
    assert '<meta name="theme-color" content="#0d0f12" />' in head
    assert _attr(head, "property", "og:image", "content") == OG_IMAGE
    assert _attr(head, "name", "twitter:card", "content") == "summary_large_image"
    canonical = _attr(head, "rel", "canonical", "href")
    assert canonical and _attr(head, "property", "og:url", "content") == canonical
    if page.parent.name == "blog":
        assert _attr(head, "property", "og:type", "content") == "article"
    for old in ("logo.webp", "banner.webp", "filigrana.webp"):
        assert old not in html
