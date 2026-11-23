"""Card #69: l'articolo Ferrari FTM deve essere collegato da index.html e da
un'altra pagina della radice (non resources.html), con testo descrittivo."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "blog/2026-07-31-ferrari-ftm-aerodinamica-f1.html"
GENERIC = {"clicca qui", "qui", "leggi", "leggi di più", "scopri di più", "link"}
LINK_RE = re.compile(r'<a\b[^>]*\bhref="' + re.escape(TARGET) + r'"[^>]*>(.*?)</a>', re.S)


def link_texts(page):
    html = (ROOT / page).read_text(encoding="utf-8")
    return [re.sub(r"<[^>]+>", "", t).strip() for t in LINK_RE.findall(html)]


def test_index_links_the_ferrari_article_with_descriptive_text():
    texts = link_texts("index.html")
    assert texts
    assert all(len(t.split()) >= 3 and t.lower() not in GENERIC for t in texts)


def test_another_root_page_links_the_ferrari_article():
    others = [p.name for p in ROOT.glob("*.html")
              if p.name not in ("index.html", "resources.html") and link_texts(p.name)]
    assert others
    for name in others:
        assert all(len(t.split()) >= 3 and t.lower() not in GENERIC for t in link_texts(name))


def test_no_blog_2026_article_is_modified():
    for base in ("origin/main", "main"):
        out = subprocess.run(["git", "diff", "--name-only", base],
                             cwd=ROOT, capture_output=True, text=True)
        if out.returncode == 0:
            changed = [f for f in out.stdout.split() if f.startswith("blog/2026-")]
            assert changed == []
            return
