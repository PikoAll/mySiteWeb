"""Le pagine privacy di MentalLoad e PienoGiusto hanno la sezione «Su iPhone»."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGINE = {
    "mentalload": "nessun tracciamento",
    "pienogiusto": "solo quando chiedi un percorso",
}


def _leggi(app):
    return (ROOT / app / "privacy" / "index.html").read_text(encoding="utf-8")


def _sezione_iphone(html):
    m = re.search(r"<h2>Su iPhone</h2>\s*<div class=\"article-body\">\s*<p>(.*?)</p>", html, re.S)
    assert m, "manca <h2>Su iPhone</h2> seguito da un paragrafo"
    return m.group(1)


def test_frase_chiave_nella_sezione_iphone():
    for app, frase in PAGINE.items():
        assert frase in _sezione_iphone(_leggi(app)), app


def test_json_ld_android_ios_e_data():
    for app in PAGINE:
        html = _leggi(app)
        assert '"operatingSystem": "Android, iOS"' in html, app
        assert '"dateModified": "2026-11-20"' in html, app
        assert "<strong>Ultimo aggiornamento:</strong> 20 novembre 2026" in html, app
