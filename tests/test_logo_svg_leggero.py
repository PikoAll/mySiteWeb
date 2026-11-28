"""Il simbolo Pikobit e' nell'header di ogni pagina: deve restare leggero."""
import os
import re

SVG = os.path.join(os.path.dirname(__file__), "..", "images", "brand", "pikobit-symbol.svg")
LIMITE = 30000  # byte; prima 43455


def test_logo_sotto_il_limite():
    assert os.path.getsize(SVG) <= LIMITE


def test_logo_mantiene_viewbox_e_un_solo_percorso():
    s = open(SVG, encoding="utf8").read()
    assert 'viewBox="22 23 2446 2275"' in s
    assert len(re.findall(r"<path\b", s)) == 2
