"""Tests for scripts/add_footer_nap.py: one identical NAP line per page, idempotent."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "add_footer_nap.py"
spec = importlib.util.spec_from_file_location("add_footer_nap", SCRIPT)
add_footer_nap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(add_footer_nap)

PAGE = """<html><body><main></main>
    <footer>
      <p>&copy; 2026 Pikobit. Tutti i diritti riservati.</p>
    </footer>
</body></html>
"""

NAP_TEXT = (
    "Pikobit · Programmatore e web designer · Monopoli (BA) · "
    "351 889 1903 · piko.bit.00@gmail.com"
)


@pytest.fixture
def page(tmp_path):
    path = tmp_path / "page.html"
    path.write_text(PAGE, encoding="utf-8")
    return path


def visible_text(html):
    import re

    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))


def test_adds_nap_inside_footer(page):
    assert add_footer_nap.process(page) is True
    html = page.read_text(encoding="utf-8")
    footer = html[html.index("<footer>") : html.index("</footer>")]
    assert html.count(add_footer_nap.MARKER) == 1
    assert add_footer_nap.MARKER in footer
    assert NAP_TEXT in visible_text(footer)
    assert 'href="tel:+393518891903"' in footer
    assert 'href="mailto:piko.bit.00@gmail.com"' in footer


def test_second_run_changes_nothing(page):
    add_footer_nap.process(page)
    first = page.read_bytes()
    assert add_footer_nap.process(page) is False
    assert page.read_bytes() == first


def test_page_without_footer_is_an_error(tmp_path):
    path = tmp_path / "nofooter.html"
    path.write_text("<html><body></body></html>", encoding="utf-8")
    with pytest.raises(ValueError):
        add_footer_nap.process(path)


def test_default_targets_cover_site_pages_and_skip_backups(tmp_path):
    (tmp_path / "blog").mkdir()
    (tmp_path / "crucidev" / "privacy").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    for rel in (
        "index.html",
        "blog/a.html",
        "crucidev/privacy/index.html",
        "old.html.backup",
        "tests/fixture.html",
    ):
        (tmp_path / rel).write_text(PAGE, encoding="utf-8")
    found = sorted(p.relative_to(tmp_path).as_posix() for p in add_footer_nap.default_targets(tmp_path))
    assert found == ["blog/a.html", "crucidev/privacy/index.html", "index.html"]
