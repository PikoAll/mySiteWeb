"""Nessuna pagina città, di Monopoli o di servizio resta senza link interni."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HREF = re.compile(r'<a\b[^>]*?\bhref="([^"]+)"', re.I)
SERVIZI = ["websites.html", "custom-software.html", "modern-apps.html", "creative-services.html"]


def pagine():
    return sorted(p.name for p in ROOT.glob("*.html"))


def link_di(nome):
    """Pagine radice linkate da `nome` (senza ancore, query, link esterni)."""
    testo = (ROOT / nome).read_text(encoding="utf-8")
    out = set()
    for href in HREF.findall(testo):
        if re.match(r"^[a-z]+:", href) or href.startswith("//"):
            continue
        href = href.split("#")[0].split("?")[0].lstrip("/")
        if href.startswith("./"):
            href = href[2:]
        if href in ("", "/"):
            continue
        out.add(href)
    return out


def test_ogni_pagina_citta_linkata_da_dove_lavoro():
    linkate = link_di("dove-lavoro.html")
    scoperte = [p for p in pagine() if p.startswith("programmatore-") and p not in linkate]
    assert not scoperte, f"Pagine città non linkate da dove-lavoro.html: {scoperte}"


def test_ogni_pagina_monopoli_linkata_da_almeno_due_pagine():
    monopoli = [p for p in pagine() if p.endswith("-monopoli.html")]
    assert monopoli
    link = {p: link_di(p) for p in pagine()}
    scoperte = {}
    for m in monopoli:
        da = [p for p, ls in link.items() if p != m and m in ls]
        if len(da) < 2:
            scoperte[m] = da
    assert not scoperte, f"Pagine di Monopoli con meno di 2 link in entrata (pagina: linkata da): {scoperte}"


def test_ogni_servizio_linka_una_citta_e_contatti():
    scoperte = []
    for s in SERVIZI:
        ls = link_di(s)
        if not any(l.startswith("programmatore-") for l in ls):
            scoperte.append(f"{s}: nessun link a una pagina città")
        if "contact.html" not in ls:
            scoperte.append(f"{s}: nessun link a contact.html")
    assert not scoperte, f"Pagine servizio scoperte: {scoperte}"
