"""Tests for scripts/compare_page_text.py: no sentence of <main> lost in a restyling."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "compare_page_text.py"
spec = importlib.util.spec_from_file_location("compare_page_text", SCRIPT)
cpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpt)

BEFORE = """<html><body><header><nav>Idee Innovative</nav></header>
<main><h1>Titolo</h1><p>Prima frase. Seconda
   frase lunga!</p><ul><li><strong>Voce</strong>: testo della voce.</li></ul>
<script>var x = "not text";</script></main>
<footer>Zone</footer></body></html>"""


def test_same_text_in_new_markup_is_not_a_loss():
    after = """<main><section class="cards"><h1>Titolo</h1>
    <div class="card"><h3><strong>Voce</strong>: testo della voce.</h3></div>
    <p>Prima frase.</p><p>Seconda frase lunga!</p></section></main>"""
    assert cpt.lost_sentences(BEFORE, after) == []


def test_a_removed_sentence_is_reported():
    after = "<main><h1>Titolo</h1><p>Prima frase.</p><p>Voce: testo della voce.</p></main>"
    assert cpt.lost_sentences(BEFORE, after) == ["Seconda frase lunga!"]


def test_only_main_counts_and_scripts_are_ignored():
    sentences = cpt.sentences(cpt.main_text(BEFORE))
    assert "Idee Innovative" not in " ".join(sentences)
    assert "not text" not in " ".join(sentences)


def test_list_item_turned_into_a_card_title_and_text_is_not_a_loss():
    before = "<main><ul><li><strong>Siti vetrina:</strong> Ideali per presentare la tua attività.</li></ul></main>"
    after = '<main><div class="card"><h3>Siti vetrina</h3><p>Ideali per presentare la tua attività.</p></div></main>'
    assert cpt.lost_sentences(before, after) == []


def test_a_changed_word_is_a_loss():
    before = "<main><p>Il preventivo è gratuito.</p></main>"
    after = "<main><p>Il preventivo è gratis.</p></main>"
    assert cpt.lost_sentences(before, after) == ["Il preventivo è gratuito."]


def test_punctuation_only_sentence_is_never_lost():
    # "informativa privacy. *": the split leaves a sentence "*" with no word.
    html = "<main><p>Ho letto l'informativa privacy. *</p></main>"
    assert cpt.lost_sentences(html, html) == []
