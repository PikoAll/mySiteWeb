"""404.html: the page GitHub Pages shows for a missing address."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import site_chrome  # noqa: E402

PAGE = ROOT / "404.html"


def html():
    assert PAGE.is_file(), "404.html missing"
    return PAGE.read_text(encoding="utf-8")


def test_has_the_same_header_and_footer_as_the_site():
    text = html()
    assert site_chrome.render(PAGE, ROOT) == text


def test_is_noindex():
    assert re.search(r'<meta name="robots" content="[^"]*noindex', html())


def test_links_to_main_pages():
    main = html().split("<main", 1)[1].split("</main>", 1)[0]
    for page in ("index.html", "programmatore-monopoli.html", "dove-lavoro.html", "contact.html"):
        assert f'href="{page}"' in main, page


def test_has_a_clear_message():
    main = html().split("<main", 1)[1].split("</main>", 1)[0]
    assert re.search(r"<h1[^>]*>[^<]*(non trovata|non esiste)", main, re.I)


def test_links_work_from_any_depth():
    """GitHub Pages serves 404.html at the missing address, e.g. /blog/vecchio:
    relative links need <base href="/">."""
    assert '<base href="/" />' in html().split("</head>")[0]


def test_not_in_sitemap():
    assert "404.html" not in (ROOT / "sitemap.xml").read_text(encoding="utf-8")


def test_build_copies_it(tmp_path):
    out = tmp_path / "site"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_site.py"), "--out", str(out)],
                   check=True, capture_output=True)
    assert (out / "404.html").is_file()


def test_seo_verifica_accepts_it():
    res = subprocess.run([sys.executable, str(ROOT / "scripts/seo_head.py"), "--verifica", str(PAGE)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout
