"""La home ha la sezione «Servizi a Monopoli» con un link, col testo non vuoto
e una frase di descrizione, a ciascuna pagina dedicata a Monopoli."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "programmatore-monopoli.html",
    "web-designer-monopoli.html",
    "gestionali-monopoli.html",
    "sviluppo-software-monopoli.html",
    "sviluppatore-app-monopoli.html",
]
SECTION_RE = re.compile(r'<section\b[^>]*id="servizi-monopoli"[^>]*>(.*?)</section>', re.S)


def section():
    m = SECTION_RE.search((ROOT / "index.html").read_text(encoding="utf-8"))
    assert m, "sezione #servizi-monopoli mancante nella home"
    return m.group(1)


def test_section_has_visible_heading():
    assert re.search(r"<h2[^>]*>\s*Servizi a Monopoli\s*</h2>", section())


def test_each_monopoli_page_is_linked_with_text_and_description():
    body = section()
    for page in PAGES:
        m = re.search(r'<li\b[^>]*>(?:(?!</li>).)*?<a\b[^>]*href="%s"[^>]*>(.*?)</a>(.*?)</li>'
                      % re.escape(page), body, re.S)
        assert m, f"link mancante a {page}"
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        desc = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        assert text, f"testo del link vuoto per {page}"
        assert desc, f"descrizione mancante per {page}"


def test_main_page_link_text():
    assert re.search(r'<a\b[^>]*href="programmatore-monopoli.html"[^>]*>\s*Siti web a Monopoli\s*</a>', section())
