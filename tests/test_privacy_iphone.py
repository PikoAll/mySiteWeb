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


DATE = {
    "mentalload": ("2026-11-21", "21 novembre 2026"),
    "pienogiusto": ("2026-11-20", "20 novembre 2026"),
}


def test_json_ld_android_ios_e_data():
    for app in PAGINE:
        html = _leggi(app)
        iso, esteso = DATE[app]
        assert '"operatingSystem": "Android, iOS"' in html, app
        assert f'"dateModified": "{iso}"' in html, app
        assert f"<strong>Ultimo aggiornamento:</strong> {esteso}" in html, app


def test_mentalload_copia_automatica_e_niente_background_su_iphone():
    html = _leggi("mentalload")
    assert "backup automatico di Android è disattivato" not in html
    assert (
        "<strong>Copia automatica</strong>: parte spenta. Se la accendi tu, una copia "
        "cifrata dei tuoi dati passa dal backup di Google (Android) o di iCloud (iPhone) "
        "e si apre solo con la tua frase di recupero. Lo sviluppatore non la vede mai."
    ) in html
    assert (
        "Su iPhone non c'è nessun controllo periodico in background: "
        "gli avvisi si aggiornano quando apri l'app."
    ) in _sezione_iphone(html)
