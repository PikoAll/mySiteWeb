"""Pagine servizio: sezione «Come si lavora» con link ai contatti e senza promesse (card #18)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGINE = ["websites.html", "custom-software.html", "modern-apps.html"]
PROMESSE = ["garanti", "senza sorprese", "gratuit", "entro ", "giorni", "settimane", "€", "euro"]


def sezione(pagina):
    html = (ROOT / pagina).read_text(encoding="utf-8")
    m = re.search(
        r'<section[^>]*id="come-si-lavora"[^>]*>(.*?)</section>', html, re.S
    )
    return m.group(1) if m else None


@pytest.mark.parametrize("pagina", PAGINE)
def test_sezione_come_si_lavora_esiste(pagina):
    corpo = sezione(pagina)
    assert corpo is not None, "manca la sezione id=come-si-lavora"
    assert "<h2>Come si lavora</h2>" in corpo


@pytest.mark.parametrize("pagina", PAGINE)
def test_sezione_ha_link_ai_contatti(pagina):
    corpo = sezione(pagina)
    assert corpo is not None
    assert 'href="contact.html"' in corpo


@pytest.mark.parametrize("pagina", PAGINE)
def test_sezione_senza_promesse(pagina):
    corpo = sezione(pagina)
    assert corpo is not None
    testo = corpo.lower()
    trovate = [p for p in PROMESSE if p in testo]
    assert not trovate, f"promesse non verificabili: {trovate}"
