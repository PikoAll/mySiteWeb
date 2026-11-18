"""Limiti SEO di docs/SEO.md sulle pagine fisse (.html in radice, blog escluso):
title <= 60, description <= 155, una parola chiave principale per pagina."""
import html as htmllib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TITLE_MAX, DESCRIPTION_MAX = 60, 155

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', re.S | re.I)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)

# Tabella di docs/SEO.md: pagina -> frase chiave (minuscola) in title e h1.
KEYWORDS = {
    "programmatore-monopoli.html": "siti web a monopoli",
    "web-designer-monopoli.html": "web designer a monopoli",
    "gestionali-monopoli.html": "gestionali su misura a monopoli",
    "sviluppo-software-monopoli.html": "sviluppo software a monopoli",
    "sviluppatore-app-monopoli.html": "sviluppatore app a monopoli",
    "websites.html": "siti web in puglia",
    "custom-software.html": "in puglia",
    "modern-apps.html": "in puglia",
}


def _clean(s):
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", "", s)).split())


def title_of(html):
    m = TITLE_RE.search(html)
    return _clean(m.group(1)) if m else ""


def description_of(html):
    m = DESC_RE.search(html)
    return _clean(m.group(1)) if m else ""


def h1_of(html):
    m = H1_RE.search(html)
    return _clean(m.group(1)) if m else ""


def fixed_pages():
    return sorted(ROOT.glob("*.html"))


def title_problem(html):
    t = title_of(html)
    return len(t) > TITLE_MAX or not t


def description_problem(html):
    d = description_of(html)
    return len(d) > DESCRIPTION_MAX or not d


BAD = (
    "<html><head><title>" + "T" * 61 + "</title>"
    '<meta name="description" content="' + "d" * 156 + '"></head></html>'
)
GOOD = (
    "<html><head><title>Corto | Pikobit</title>"
    '<meta name="description" content="Breve"></head></html>'
)


def test_title_troppo_lungo_rilevato():
    assert title_problem(BAD)
    assert not title_problem(GOOD)


def test_description_troppo_lunga_rilevata():
    assert description_problem(BAD)
    assert not description_problem(GOOD)


def test_pagine_fisse_trovate():
    assert len(fixed_pages()) >= 20


@pytest.mark.parametrize("page", fixed_pages(), ids=lambda p: p.name)
def test_title_entro_60(page):
    t = title_of(page.read_text(encoding="utf-8"))
    assert t and len(t) <= TITLE_MAX, f"{page.name}: title di {len(t)} caratteri"


@pytest.mark.parametrize("page", fixed_pages(), ids=lambda p: p.name)
def test_description_entro_155(page):
    d = description_of(page.read_text(encoding="utf-8"))
    assert d and len(d) <= DESCRIPTION_MAX, f"{page.name}: description di {len(d)} caratteri"


@pytest.mark.parametrize("name,keyword", sorted(KEYWORDS.items()))
def test_parola_chiave_in_title_e_h1(name, keyword):
    html = (ROOT / name).read_text(encoding="utf-8")
    assert keyword in title_of(html).lower(), f"{name}: manca '{keyword}' nel title"
    assert keyword in h1_of(html).lower(), f"{name}: manca '{keyword}' nell'h1"


def test_title_unici_tra_pagine_fisse():
    seen = {}
    for p in fixed_pages():
        t = title_of(p.read_text(encoding="utf-8"))
        assert t not in seen, f"{p.name} e {seen[t]} hanno lo stesso title"
        seen[t] = p.name
