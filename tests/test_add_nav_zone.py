"""Tests for scripts/add_nav_zone.py: "Dove lavoro" dropdown after "Servizi", idempotent."""
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "add_nav_zone.py"
spec = importlib.util.spec_from_file_location("add_nav_zone", SCRIPT)
add_nav_zone = importlib.util.module_from_spec(spec)
spec.loader.exec_module(add_nav_zone)

# Two real-world formattings: prettier (root pages) and compact (blog, crucidev).
ROOT_PAGE = """<html><body><header>
      <nav id="navbar">
        <ul class="nav-links">
          <li><a href="index.html">Home</a></li>

          <li class="dropdown">
            <a
              href="#"
              id="dropdown-toggle"
              aria-haspopup="true"
              aria-expanded="false"
              >Servizi ▼</a
            >
            <ul class="dropdown-menu">
              <li><a href="websites.html">Siti web personalizzati</a></li>
              <li>
                <a href="custom-software.html">Software gestionali su misura</a>
              </li>
            </ul>
          </li>

          <li><a href="ideas.html">Idee Innovative</a></li>
          <li><a href="contact.html">Contatti</a></li>
        </ul>
      </nav>
</header><main></main></body></html>
"""

NESTED_PAGE = """<html><body><header>
<nav id="navbar">
<ul class="nav-links">
<li><a href="../../index.html">Home</a></li>

<li class="dropdown">
<a href="#" id="dropdown-toggle" aria-haspopup="true" aria-expanded="false">Servizi ▼</a>
<ul class="dropdown-menu">
<li><a href="../../websites.html">Siti web personalizzati</a></li>
</ul>
</li>

<li><a href="../../ideas.html">Idee Innovative</a></li>
</ul>
</nav>
</header></body></html>
"""

CITY_ORDER = [
    "Monopoli", "Bari", "Polignano a Mare", "Fasano", "Conversano",
    "Castellana Grotte", "Putignano", "Casamassima", "Ostuni",
    "Brindisi", "Taranto", "Lecce",
]


def nav_of(html):
    return html[html.index("<nav") : html.index("</nav>")]


def zone_block(html):
    nav = nav_of(html)
    start = nav.index(add_nav_zone.MARKER)
    return nav[start : nav.index("</ul>", start)]


@pytest.fixture
def root_page(tmp_path):
    p = tmp_path / "index.html"
    p.write_text(ROOT_PAGE, encoding="utf-8")
    return p


@pytest.fixture
def nested_page(tmp_path):
    d = tmp_path / "crucidev" / "privacy"
    d.mkdir(parents=True)
    p = d / "index.html"
    p.write_text(NESTED_PAGE, encoding="utf-8")
    return p


def test_inserts_dropdown_right_after_servizi(root_page):
    assert add_nav_zone.process(root_page) is True
    nav = nav_of(root_page.read_text(encoding="utf-8"))
    servizi = nav.index("Servizi ▼")
    zone = nav.index("Dove lavoro ▼")
    ideas = nav.index("Idee Innovative")
    assert servizi < zone < ideas
    # the Servizi <li> is closed before the new one opens
    assert nav.count('<li class="dropdown') == 2


def test_lists_all_cities_in_order_then_all_zones(root_page):
    add_nav_zone.process(root_page)
    block = zone_block(root_page.read_text(encoding="utf-8"))
    labels = re.findall(r'<li><a href="[^"]*">([^<]+)</a></li>', block)
    assert labels == CITY_ORDER + ["Tutte le zone"]
    assert 'href="programmatore-monopoli.html"' in block
    assert 'href="programmatore-castellana-grotte.html"' in block
    assert 'href="dove-lavoro.html">Tutte le zone' in block


def test_links_use_the_page_relative_prefix(nested_page):
    add_nav_zone.process(nested_page)
    block = zone_block(nested_page.read_text(encoding="utf-8"))
    hrefs = re.findall(r'href="([^"]+)"', block)
    assert hrefs and all(h.startswith("../../") for h in hrefs)


def test_toggle_is_accessible_and_does_not_reuse_the_servizi_id(root_page):
    add_nav_zone.process(root_page)
    html = root_page.read_text(encoding="utf-8")
    assert html.count('id="dropdown-toggle"') == 1
    block = zone_block(html)
    toggle = re.search(r"<a [^>]*>Dove lavoro ▼</a>", block).group(0)
    assert 'class="dropdown-toggle"' in toggle
    assert 'aria-haspopup="true"' in toggle
    assert 'aria-expanded="false"' in toggle
    assert 'href="dove-lavoro.html"' in toggle


def test_second_run_changes_nothing(root_page, nested_page):
    for p in (root_page, nested_page):
        add_nav_zone.process(p)
        first = p.read_bytes()
        assert add_nav_zone.process(p) is False
        assert p.read_bytes() == first


def test_page_without_servizi_dropdown_is_an_error(tmp_path):
    p = tmp_path / "x.html"
    original = '<nav id="navbar"><ul><li><a href="index.html">Home</a></li></ul></nav>'
    p.write_text(original, encoding="utf-8")
    with pytest.raises(ValueError):
        add_nav_zone.process(p)
    assert p.read_text(encoding="utf-8") == original
