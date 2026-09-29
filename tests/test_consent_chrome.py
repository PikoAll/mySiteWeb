"""Tests for the cookie-consent part of scripts/site_chrome.py.

Google Analytics must never be loaded straight from a page: every page loads
scripts/consent.js instead (it loads gtag.js only after "Accetta"), and every
footer links the privacy page and the "Preferenze cookie" switch.
"""
import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "site_chrome.py"
spec = importlib.util.spec_from_file_location("site_chrome", SCRIPT)
site_chrome = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_chrome)

ROOT = SCRIPT.parent.parent

# The three real-world GA snippets found in the repo (prettier, blog, compact).
GA_PRETTIER = """    <!-- Google tag (gtag.js) -->
    <script
      async
      src="https://www.googletagmanager.com/gtag/js?id=G-TVGN1XBX7H"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {
        dataLayer.push(arguments);
      }
      gtag("js", new Date());

      gtag("config", "G-TVGN1XBX7H");
    </script>
"""
GA_BLOG = """<!-- Google tag (gtag.js) -->
<script
async
src="
https://www.googletagmanager.com/gtag/js?id=G-TVGN1XBX7H
"
></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag() {
dataLayer.push(arguments);
}
gtag("js", new Date());

gtag("config", "G-TVGN1XBX7H");
</script>
"""
GA_COMPACT = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-TVGN1XBX7H"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-TVGN1XBX7H');
</script>
"""


def page(ga, script_src="scripts/script.js?v=4.3.1.0"):
    return f"""<!doctype html><html><head>
<title>T</title>
<script defer src="{script_src}"></script>
<script type="application/ld+json">{{"a": 1}}</script>
{ga}</head><body>
<header><nav id="navbar"></nav></header>
<main><h1>Titolo</h1></main>
<footer>
<p class="nap">Pikobit</p>
<p>&copy; 2026 Pikobit.</p>
</footer>
</body></html>
"""


def write(tmp_path, rel, text):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_every_ga_snippet_is_replaced_by_consent_js(tmp_path):
    for i, ga in enumerate((GA_PRETTIER, GA_BLOG, GA_COMPACT)):
        p = write(tmp_path, f"p{i}.html", page(ga))
        site_chrome.process(p, tmp_path)
        html = p.read_text(encoding="utf-8")
        assert "googletagmanager" not in html, i
        assert "gtag(" not in html and "Google tag" not in html, i
        assert html.count('scripts/consent.js') == 1, i


def test_consent_js_is_in_head_with_the_site_version(tmp_path):
    p = write(tmp_path, "blog/x.html", page(GA_BLOG, "../scripts/script.js?v=4.3.1.0"))
    site_chrome.process(p, tmp_path)
    html = p.read_text(encoding="utf-8")
    head = html[: html.index("</head>")]
    assert '<script defer src="../scripts/consent.js?v=4.3.1.0"></script>' in head


def test_page_without_ga_gets_consent_js_too(tmp_path):
    p = write(tmp_path, "crucidev/privacy/index.html", page("", "../../scripts/script.js"))
    site_chrome.process(p, tmp_path)
    assert '<script defer src="../../scripts/consent.js"></script>' in p.read_text(encoding="utf-8")


def test_an_existing_consent_tag_is_kept_as_is(tmp_path):
    """update_versions.py may bump its ?v= independently: never rewrite it."""
    tag = '<script defer src="scripts/consent.js?v=9.9.9.9"></script>\n'
    p = write(tmp_path, "a.html", page(tag))
    site_chrome.process(p, tmp_path)
    html = p.read_text(encoding="utf-8")
    assert html.count("consent.js") == 1 and "consent.js?v=9.9.9.9" in html


def footer_of(html):
    return re.search(r"<footer\b.*?</footer>", html, re.S).group(0)


def test_footer_links_privacy_and_cookie_preferences(tmp_path):
    p = write(tmp_path, "blog/x.html", page(GA_BLOG))
    site_chrome.process(p, tmp_path)
    foot = footer_of(p.read_text(encoding="utf-8"))
    assert '<a href="../privacy.html">Privacy</a>' in foot
    prefs = re.search(r"<a [^>]*data-cookie-prefs[^>]*>Preferenze cookie</a>", foot)
    assert prefs and 'href="../privacy.html#cookie"' in prefs.group(0)
    # after the NAP and the Zone line, before the copyright
    assert foot.index('class="nap"') < foot.index("footer-zone") < foot.index("footer-legal") < foot.index("&copy;")


def test_second_run_changes_nothing(tmp_path):
    for i, ga in enumerate((GA_PRETTIER, GA_BLOG, GA_COMPACT, "")):
        p = write(tmp_path, f"q{i}.html", page(ga))
        assert site_chrome.process(p, tmp_path) is True
        first = p.read_bytes()
        assert site_chrome.process(p, tmp_path) is False
        assert p.read_bytes() == first
        assert footer_of(first.decode()).count("footer-legal") == 1


def test_no_real_page_loads_google_analytics_directly():
    """Guard for pages added later (e.g. the weekly blog script): a hardcoded
    gtag.js would track before consent. Fix: python3 scripts/site_chrome.py."""
    offenders, missing = [], []
    for p in site_chrome.default_targets(ROOT):
        html = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(ROOT))
        if "googletagmanager.com" in html or "google-analytics.com" in html:
            offenders.append(rel)
        if "scripts/consent.js" not in html or "data-cookie-prefs" not in html:
            missing.append(rel)
    assert offenders == [] and missing == []


def test_no_page_has_placeholders_left():
    """privacy.html had "[DA COMPLETARE: ...]" markers: none may go online."""
    left = [str(p.relative_to(ROOT)) for p in site_chrome.default_targets(ROOT)
            if "DA COMPLETARE" in p.read_text(encoding="utf-8")]
    assert left == []


def test_privacy_states_the_ga_retention():
    html = (ROOT / "privacy.html").read_text(encoding="utf-8")
    stats = html[html.index('id="statistiche"'): html.index('id="cookie"')]
    assert "I dati di Google Analytics sono conservati per 2 mesi." in " ".join(stats.split())
