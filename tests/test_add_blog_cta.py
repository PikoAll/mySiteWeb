"""Tests for scripts/add_blog_cta.py: insertion, idempotency, JSON-LD untouched."""
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "add_blog_cta.py"
spec = importlib.util.spec_from_file_location("add_blog_cta", SCRIPT)
add_blog_cta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(add_blog_cta)

ARTICLE = """<!doctype html>
<html lang="it">
<head>
<script type="application/ld+json">
  {"@context": "https://schema.org", "@type": "BlogPosting", "headline": "X </main> Y"}
</script>
</head>
<body>
<main>
<section class="why-pikobit"><p>Body</p></section>
</main>
<footer><p>&copy; 2026 Pikobit.</p></footer>
</body>
</html>
"""

LD_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)


@pytest.fixture
def article(tmp_path):
    path = tmp_path / "2026-01-01-test.html"
    path.write_text(ARTICLE, encoding="utf-8")
    return path


def test_adds_box_before_main_close(article):
    assert add_blog_cta.process(article) is True
    html = article.read_text(encoding="utf-8")
    assert html.count(add_blog_cta.MARKER) == 1
    assert "Ti serve un sito o un software su misura a Monopoli?" in html
    assert html.index(add_blog_cta.MARKER) < html.rindex("</main>")
    assert html.index(add_blog_cta.MARKER) > html.index("<p>Body</p>")


def test_box_links_local_page_and_services(article):
    add_blog_cta.process(article)
    html = article.read_text(encoding="utf-8")
    for href in (
        "../programmatore-monopoli.html",
        "../websites.html",
        "../custom-software.html",
        "../modern-apps.html",
    ):
        assert f'href="{href}"' in html


def test_second_run_changes_nothing(article):
    add_blog_cta.process(article)
    first = article.read_bytes()
    assert add_blog_cta.process(article) is False
    assert article.read_bytes() == first


def test_jsonld_untouched(article):
    before = LD_RE.findall(ARTICLE)
    add_blog_cta.process(article)
    assert LD_RE.findall(article.read_text(encoding="utf-8")) == before


def test_missing_main_close_is_an_error(tmp_path):
    path = tmp_path / "broken.html"
    path.write_text("<html><body><p>no main</p></body></html>", encoding="utf-8")
    with pytest.raises(ValueError):
        add_blog_cta.process(path)
    assert path.read_text(encoding="utf-8") == "<html><body><p>no main</p></body></html>"


def test_check_mode_reports_missing_without_writing(article):
    assert add_blog_cta.main(["--check", str(article)]) == 1
    assert article.read_text(encoding="utf-8") == ARTICLE
    assert add_blog_cta.main([str(article)]) == 0
    assert add_blog_cta.main(["--check", str(article)]) == 0
