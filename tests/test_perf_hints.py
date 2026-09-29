"""Tests for scripts/perf_hints.py: font preloads and hero logo priority, idempotent."""
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "perf_hints.py"
spec = importlib.util.spec_from_file_location("perf_hints", SCRIPT)
perf_hints = importlib.util.module_from_spec(spec)
spec.loader.exec_module(perf_hints)

PAGE = """<head>
<link
  rel="preload"
  href="../fonts/poppins/poppins-latin-400-normal.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
</head><body><div class="intro-container"><img
src="../images/brand/pikobit-symbol.svg"
alt="Logo Pikobit"
class="logo" width="120" height="112" /></div></body>
"""


def test_adds_600_preload_with_same_prefix_and_indent():
    out = perf_hints.update(PAGE)
    assert out.count("poppins-latin-600-normal.woff2") == 1
    assert '\n<link\n  rel="preload"\n  href="../fonts/poppins/poppins-latin-600-normal.woff2"' in out


def test_hero_logo_gets_fetchpriority_high():
    out = perf_hints.update(PAGE)
    assert 'class="logo" width="120" height="112" fetchpriority="high" />' in out


def test_idempotent():
    once = perf_hints.update(PAGE)
    assert perf_hints.update(once) == once


PAGES = sorted(
    p for p in ROOT.rglob("*.html")
    if not {"node_modules", "tests", "_site"} & set(p.relative_to(ROOT).parts)
)


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_page_preloads_both_fonts(page):
    head = page.read_text(encoding="utf-8").split("</head>")[0]
    for weight in ("400", "600"):
        assert re.search(rf'rel="preload"\s+href="[./]*fonts/poppins/poppins-latin-{weight}-normal\.woff2"', head)
