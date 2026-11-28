"""Home: sezione «Le nostre app» con CruciDev, PienoGiusto e MentalLoad."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = (ROOT / "index.html").read_text(encoding="utf-8")


def _sezione():
    m = re.search(r'<section[^>]*id="le-nostre-app".*?</section>', HOME, re.S)
    assert m, "sezione #le-nostre-app mancante nella home"
    return m.group(0)


def test_titolo_e_tre_app():
    s = _sezione()
    assert "<h2" in s and "Le nostre app" in s
    for nome in ("CruciDev", "PienoGiusto", "MentalLoad"):
        assert re.search(rf"<h3[^>]*>(?:<[^>]+>)*\s*{nome}", s, re.I), nome


def test_link_alle_pagine_e_badge():
    s = _sezione()
    assert 'href="app-pienogiusto.html"' in s
    assert 'href="app-mentalload.html"' in s
    assert "https://apps.apple.com/it/app/pienogiusto/id6837226724" in s
    assert "https://apps.apple.com/it/app/mentalload/id6837226677" in s
    assert "https://play.google.com/store/apps/details?id=it.pikobit.crucidev" in s
    assert s.count("presto su Google Play") == 2


def test_screenshot_con_alt_e_dimensioni_e_lazy():
    s = _sezione()
    imgs = re.findall(r"<img\b[^>]*>", s)
    shots = [i for i in imgs if "badge" not in i]
    assert len(shots) >= 4
    for i in shots:
        assert re.search(r'alt="[^"]+"', i) and "width=" in i and "height=" in i
        assert 'loading="lazy"' in i
        src = re.search(r'src="([^"]+)"', i).group(1)
        assert (ROOT / src).exists(), src


def test_senza_eyebrow_e_card_annidate():
    s = _sezione()
    assert "eyebrow" not in s and "kicker" not in s
    assert 'class="card' not in s
