"""SEO #61: the home links lezioni.pikobit.it with the anchor text «ripetizioni di informatica»."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_home_links_lezioni_with_keyword_anchor():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<a\b[^>]*href="https://lezioni\.pikobit\.it/"[^>]*>\s*ripetizioni di informatica\s*</a>', html)
    assert m, "link a lezioni.pikobit.it con testo «ripetizioni di informatica» mancante nella home"
