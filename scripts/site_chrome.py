#!/usr/bin/env python3
"""Write the same header, menu and footer "Zone" line on every page.

Single source of the site chrome (it replaces add_nav_zone.py):
- <header>: circuit band (images/brand/header-circuit.svg, from gen_header_circuit.py)
  with the PIKOBIT wordmark as inline SVG, the hamburger <button>, the menu
  Home · Servizi ▼ · Dove lavoro · Progetti & idee · Chi sono · Blog · Contatti.
  The whole <header> is rewritten from the template below, so an old or
  hand-edited header is brought back in line.
- footer: after the NAP line, a <nav class="footer-zone"> linking the 12 city
  pages (they left the menu, the internal links stay on every page).
- intro logo: <img class="logo" src=".../logo.webp"> becomes the vector mark
  images/brand/pikobit-symbol.svg, same alt. Favicon and JSON-LD are scripts/brand_head.py's job.
- menu state: the page itself gets aria-current="page"; a child page (city
  page under "Dove lavoro", blog post under "Blog") marks its parent entry
  with class="nav-parent" (light style), never aria-current.
- city pages: a visible breadcrumb Home › Dove lavoro › <city> right after
  <main>, same names as their BreadcrumbList JSON-LD.
- cookie consent: the hardcoded Google tag (gtag.js) is removed and
  <script defer src=".../scripts/consent.js"> goes in <head> instead (it loads
  Google Analytics only after "Accetta"); the footer gets a line with
  "Privacy" and "Preferenze cookie" (data-cookie-prefs reopens the banner,
  without JS the link just opens privacy.html#cookie).

Links get the prefix of the page depth ("", "../", "../../"), so the same
script serves root pages, blog/ and crucidev/privacy/. Running it twice
changes nothing (idempotent). *.backup files and tests/ are never touched.

Usage:
    python3 scripts/site_chrome.py            # every page of the site
    python3 scripts/site_chrome.py FILE...    # only the given files

Exit code: 0 ok, 2 a page could not be processed.
"""
import re
import sys
from pathlib import Path

# (label, page) in menu order; Monopoli first because it is the main page.
CITIES = [
    ("Monopoli", "programmatore-monopoli.html"),
    ("Bari", "programmatore-bari.html"),
    ("Polignano a Mare", "programmatore-polignano-a-mare.html"),
    ("Fasano", "programmatore-fasano.html"),
    ("Conversano", "programmatore-conversano.html"),
    ("Castellana Grotte", "programmatore-castellana-grotte.html"),
    ("Putignano", "programmatore-putignano.html"),
    ("Turi", "programmatore-turi.html"),
    ("Casamassima", "programmatore-casamassima.html"),
    ("Ostuni", "programmatore-ostuni.html"),
    ("Brindisi", "programmatore-brindisi.html"),
    ("Taranto", "programmatore-taranto.html"),
    ("Lecce", "programmatore-lecce.html"),
]

SERVICES = [
    ("Siti web personalizzati", "websites.html"),
    ("Applicazioni moderne", "modern-apps.html"),
    ("Software gestionali su misura", "custom-software.html"),
    ("Servizi Creativi e Soluzioni Complete", "creative-services.html"),
    ("Lezioni e tutorial", "lessons.html"),
]

# First-level entries after Servizi: (label, page, css class of the <li>)
MENU = [
    ("Dove lavoro", "dove-lavoro.html", ""),
    ("Progetti &amp; idee", "ideas.html", ""),
    ("Chi sono", "about.html", ""),
    ("Blog", "resources.html", ""),
    ("Contatti", "contact.html", "nav-cta"),
]

# PIKOBIT lettering of the round logo, redrawn as vector over a trace of
# images/logo.webp. Letters white, the dot in the O is the logo light blue.
WORDMARK = (
    '<svg class="wordmark" viewBox="-3 -4 553 109" aria-hidden="true" focusable="false">'
    '<g fill="#fff" stroke="#fff" stroke-width="3" stroke-linejoin="round">'
    '<path d="M0 0H50C68 0 82 14 82 33C82 52 68 66 50 66H21V100H0V44H50C55 44 60 40 60 33'
    'C60 26 55 22 50 22H21V30H0Z"/>'
    '<path d="M96 0H117V100H96Z"/>'
    '<path d="M134 0H155V35L188 0H217L178 45L220 100H192L162 58L155 65V100H134Z"/>'
    '<path fill-rule="evenodd" d="M275.5-1.5a51.5 51.5 0 1 0 .01 0ZM275.5 19a31 31 0 1 1-.01 0Z"/>'
    '<path fill-rule="evenodd" d="M341 0H389C405 0 417 9 417 21C417 30 413 36 407 40'
    'C417 45 423 54 423 68C423 86 411 100 393 100H341V40H388C393 40 396 36 396 31'
    'C396 26 393 22 388 22H362V30H341ZM362 60H393C399 60 402 64 402 69C402 74 399 78 393 78H362Z"/>'
    '<path d="M437 0H458V100H437Z"/>'
    '<path d="M473 0H547V22H520.5V100H499.5V22H473Z"/></g>'
    '<circle cx="275.5" cy="50" r="11.5" fill="none" stroke="#9ad8f3" stroke-width="9"/></svg>'
)

HAMBURGER_ICON = (
    '<svg class="icon-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path d="M3 6h18M3 12h18M3 18h18" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round"/></svg>'
)

HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.S)
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.S)
ZONE_RE = re.compile(r'\n?<nav class="footer-zone".*?</nav>', re.S)
NAP_RE = re.compile(r'<p class="nap">.*?</p>', re.S)
BREADCRUMB_RE = re.compile(r'\s*<nav class="breadcrumb"[^>]*>.*?</nav>', re.S)
MAIN_RE = re.compile(r"<main\b[^>]*>")
# The Google tag in any of its formattings (prettier, blog, compact), with the
# comment above it and the leading whitespace.
GA_RE = re.compile(
    r"[ \t]*(?:<!--\s*Google tag \(gtag\.js\)\s*-->\s*)?"
    r"<script\s+async\s+src=\"\s*https://www\.googletagmanager\.com/gtag/js\?[^\"]*\"\s*>\s*</script>"
    r"\s*<script>\s*window\.dataLayer.*?</script>[ \t]*\n?",
    re.S,
)
CONSENT_RE = re.compile(r'<script defer src="(?:\.\./)*scripts/consent\.js[^"]*"></script>')
SCRIPT_VERSION_RE = re.compile(r'scripts/script\.js(\?v=[\d.]+)"')
LEGAL_RE = re.compile(r'\n?<p class="footer-legal">.*?</p>', re.S)
LOGO_RE = re.compile(r'<img\b(?=[^>]*\bclass="logo")(?=[^>]*logo\.webp)[^>]*>', re.S)
REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "tests", "node_modules", "_site"}  # _site: built copy, see build_site.py


def _current(rel):
    """(page, attribute) marking the menu entry of the page at rel."""
    if rel.startswith("blog/"):
        return "resources.html", ' class="nav-parent"'
    if rel.startswith("programmatore-"):
        return "dove-lavoro.html", ' class="nav-parent"'
    return rel, ' aria-current="page"'


def _link(prefix, page, label, current):
    cur = current[1] if current[0] == page else ""
    return f'<a href="{prefix}{page}"{cur}>{label}</a>'


def header(prefix, rel):
    cur = _current(rel)
    services = "\n".join(
        f"<li>{_link(prefix, page, label, cur)}</li>" for label, page in SERVICES
    )
    entries = "\n".join(
        (f'<li class="{cls}">' if cls else "<li>") + _link(prefix, page, label, cur) + "</li>"
        for label, page, cls in MENU
    )
    return (
        '<header class="site-header" id="site-header">\n'
        '<div class="brand-band">\n'
        f'<a class="brand" href="{prefix}index.html" aria-label="Pikobit, vai alla home">{WORDMARK}</a>\n'
        '<button class="hamburger" id="hamburger-menu" type="button" '
        'aria-label="Apri menu di navigazione" aria-expanded="false" aria-controls="navbar">'
        f"{HAMBURGER_ICON}</button>\n"
        "</div>\n"
        '<div class="overlay" id="overlay"></div>\n'
        '<nav id="navbar" aria-label="Menu principale">\n'
        '<ul class="nav-links">\n'
        f"<li>{_link(prefix, 'index.html', 'Home', cur)}</li>\n"
        '<li class="dropdown">\n'
        '<a href="#" id="dropdown-toggle" aria-haspopup="true" aria-expanded="false">Servizi ▼</a>\n'
        f'<ul class="dropdown-menu">\n{services}\n</ul>\n'
        "</li>\n"
        f"{entries}\n"
        "</ul>\n"
        "</nav>\n"
        "</header>"
    )


def footer_zone(prefix):
    links = " · ".join(f'<a href="{prefix}{page}">{label}</a>' for label, page in CITIES)
    return f'\n<nav class="footer-zone" aria-label="Zone in cui lavoro"><p>Zone: {links}</p></nav>'


# The Google Business profile: site and profile point at each other.
MAPS = "https://www.google.com/maps?cid=16391512325002463359"


def footer_legal(prefix):
    return (
        f'\n<p class="footer-legal"><a href="{prefix}privacy.html">Privacy</a> · '
        f'<a href="{prefix}privacy.html#cookie" data-cookie-prefs>Preferenze cookie</a> · '
        f'<a href="{MAPS}" target="_blank" rel="noopener">Trovami su Google Maps</a></p>'
    )


def _consent_script(html, prefix):
    """Drop the hardcoded Google tag, make sure consent.js is loaded in <head>.

    An existing consent.js tag is kept as it is (update_versions.py owns its
    ?v=); a new one takes the version of script.js on the same page."""
    html = GA_RE.sub("", html)
    if CONSENT_RE.search(html):
        return html
    version = SCRIPT_VERSION_RE.search(html)
    tag = f'<script defer src="{prefix}scripts/consent.js{version.group(1) if version else ""}"></script>'
    at = html.find("</head>")
    if at == -1:
        at = html.rfind("</body>")
    line = html.rfind("\n", 0, at) + 1  # same indentation as </head>
    indent = html[line:at] if not html[line:at].strip() else ""
    at = line if indent or line == at else at
    return html[:at] + indent + tag + "\n" + html[at:]


def breadcrumb(label):
    return (
        '<nav class="breadcrumb" aria-label="Percorso">\n'
        '        <a href="index.html">Home</a> ›\n'
        '        <a href="dove-lavoro.html">Dove lavoro</a> ›\n'
        f'        <span aria-current="page">{label}</span>\n'
        "      </nav>"
    )


def _city_breadcrumb(html, rel):
    label = dict((page, label) for label, page in CITIES).get(rel)
    main = MAIN_RE.search(html)
    if not label or not main:
        return html
    head, body = html[: main.end()], html[main.end():]
    body = BREADCRUMB_RE.sub("", body, count=1) if BREADCRUMB_RE.match(body) else body
    return head + "\n      " + breadcrumb(label) + body


def _logo(tag):
    tag = tag.replace("logo.webp", "brand/pikobit-symbol.svg")
    tag = re.sub(r'width="\d+"', 'width="120"', tag)
    return re.sub(r'height="\d+"', 'height="112"', tag)


def render(path, root):
    """Return the text of path with the current chrome (path is not written)."""
    path, root = Path(path), Path(root)
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    prefix = "../" * rel.count("/")
    html = path.read_text(encoding="utf-8")
    if not HEADER_RE.search(html) or not FOOTER_RE.search(html):
        raise ValueError(f"{path}: <header> or <footer> not found")
    html = HEADER_RE.sub(lambda m: header(prefix, rel), html, count=1)

    def fix_footer(m):
        foot = LEGAL_RE.sub("", ZONE_RE.sub("", m.group(0)))
        nap = NAP_RE.search(foot)
        at = nap.end() if nap else foot.index(">") + 1
        return foot[:at] + footer_zone(prefix) + footer_legal(prefix) + foot[at:]

    html = FOOTER_RE.sub(fix_footer, html, count=1)
    html = _city_breadcrumb(html, rel)
    html = _consent_script(html, prefix)
    return LOGO_RE.sub(lambda m: _logo(m.group(0)), html)


def process(path, root=REPO_ROOT):
    """Rewrite the chrome of path. Return True if the file changed."""
    new = render(path, root)
    if new == Path(path).read_text(encoding="utf-8"):
        return False
    Path(path).write_text(new, encoding="utf-8")
    return True


def default_targets(root):
    root = Path(root)
    return sorted(
        p for p in root.rglob("*.html")
        if not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )


def main(argv):
    files = [Path(a) for a in argv] or default_targets(REPO_ROOT)
    changed, errors = 0, []
    for f in files:
        try:
            changed += process(f)
        except (OSError, ValueError) as e:
            errors.append(str(e))
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print(f"{changed} changed, {len(files) - changed - len(errors)} already ok, {len(errors)} errors")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
