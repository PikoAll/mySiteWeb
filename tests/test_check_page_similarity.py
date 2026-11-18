"""Tests for scripts/check_page_similarity.py."""
import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_page_similarity.py"
spec = importlib.util.spec_from_file_location("check_page_similarity", SCRIPT)
cps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cps)

SHELL = "<html><head><script>var x = 'uno due tre quattro';</script></head><body>" \
        "<nav>menu condiviso uguale su tutte le pagine del sito</nav>" \
        "<main>{}</main><footer>footer condiviso uguale ovunque sempre</footer></body></html>"


def test_only_main_text_counts():
    text = cps.main_text(SHELL.format("<p>ciao <b>mondo</b></p>"))
    assert text.split() == ["ciao", "mondo"]


def test_clone_pages_are_identical_and_different_pages_are_not(tmp_path):
    body = "il programmatore lavora con le attività della zona e realizza siti web su misura"
    a = tmp_path / "a.html"
    b = tmp_path / "b.html"
    c = tmp_path / "c.html"
    a.write_text(SHELL.format(body + " a Bari"), encoding="utf-8")
    b.write_text(SHELL.format(body + " a Lecce"), encoding="utf-8")
    c.write_text(SHELL.format("testo completamente diverso che parla di porti navi e industria pesante"), encoding="utf-8")
    result = {(x, y): s for s, x, y in cps.pairs([a, b, c])}
    assert result[("a.html", "b.html")] > 0.8
    assert result[("a.html", "c.html")] == 0.0


def _paragraphs(html):
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    return {" ".join(re.sub(r"<[^>]+>", " ", p).lower().split())
            for p in re.findall(r"<p[ >].*?</p>", main, re.S)}


def test_every_city_page_has_a_paragraph_unique_to_it():
    files = sorted(cps.REPO_ROOT.glob("programmatore-*.html"))
    paras = {f.name: _paragraphs(f.read_text(encoding="utf-8")) for f in files}
    for name, mine in paras.items():
        others = set().union(*(p for n, p in paras.items() if n != name))
        assert mine - others, f"{name} has no paragraph that is absent from the other city pages"


def test_default_limit_is_030():
    assert cps.DEFAULT_LIMIT == 0.30


def test_real_city_pages_are_under_030():
    assert cps.main(["--max", "0.30"]) == 0


def test_exit_code_respects_limit(tmp_path):
    a = tmp_path / "a.html"
    b = tmp_path / "b.html"
    same = SHELL.format("uno due tre quattro cinque sei sette otto")
    a.write_text(same, encoding="utf-8")
    b.write_text(same, encoding="utf-8")
    assert cps.main([str(a), str(b)]) == 1
    assert cps.main(["--max", "1.0", str(a), str(b)]) == 0
