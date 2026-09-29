#!/usr/bin/env python3
"""Structured data and SEO meta tags of every page's <head>. Idempotent.

One JSON-LD block per page, a @graph that always starts with the SAME two
nodes, byte for byte: the business (ProfessionalService, @id
https://pikobit.it/#business) and its founder (Person, @id
https://pikobit.it/#giuseppe). Google merges nodes by @id across pages: two
different versions of the same @id are a contradiction, so the entity lives
only here (BUSINESS_NODE, PERSON_NODE) and pages reference it by @id.

Page nodes already written (WebPage, AboutPage, BreadcrumbList, FAQPage,
BlogPosting...) are kept; the script only adds what is missing:
- blog: BlogPosting with dateModified (last CONTENT change, same logic as
  scripts/sitemap_lastmod.py), image, author/publisher by @id,
  mainEntityOfPage; breadcrumb Home > Blog > article; article:*_time meta;
- service pages: Service (name = <h1>, description = meta description);
- every page but the home: BreadcrumbList.
Meta: og:description = meta description; robots max-image-preview on indexable pages (a page already marked
noindex stays so), twitter:title/description equal to the og ones, canonical
and og:url without the whitespace the blog pipeline leaves in the href.
Nothing visible changes: title, description, h1, canonical URL stay the same.

crucidev/privacy/ is left out on purpose: it is the policy of an app, not a
page of the Pikobit site.

Usage:
    python3 scripts/seo_head.py                  # every page of the site
    python3 scripts/seo_head.py FILE...          # given pages only (new articles)
    python3 scripts/seo_head.py --verifica [FILE...]
Exit: 0 ok; 1 --verifica found non-conforming pages, or a page could not be
processed (message with the file name on stderr, the other pages still done).
In a shallow clone (the weekly pipeline clones with --depth 1) the git history
is not there: an existing dateModified is kept, a new article gets its
datePublished.
"""
import datetime
import html as htmllib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://pikobit.it/"
BUSINESS_ID = SITE + "#business"
PERSON_ID = SITE + "#giuseppe"
WEBSITE_ID = SITE + "#website"
OG_IMAGE = SITE + "images/brand/og-pikobit-1200x630.jpg"
LOGO = SITE + "images/brand/pikobit-logo-512.png"
MAPS = "https://www.google.com/maps?cid=16391512325002463359"
ROBOTS_CONTENT = "index, follow, max-image-preview:large, max-snippet:-1"
ROBOTS_TAG = f'<meta name="robots" content="{ROBOTS_CONTENT}" />'


def _load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_chrome = _load("site_chrome")
_lastmod = _load("sitemap_lastmod")

# Same list and order as the areaServed already on the home page.
CITY_NAMES = [
    "Monopoli", "Polignano a Mare", "Fasano", "Conversano", "Castellana Grotte",
    "Turi", "Casamassima", "Bari", "Brindisi", "Taranto", "Putignano", "Ostuni", "Lecce",
]
AREA_SERVED = [{"@type": "City", "name": c, "addressCountry": "IT"} for c in CITY_NAMES]

# Service names as written on the home page cards.
OFFERS = [
    ("Siti web personalizzati", "websites.html"),
    ("Applicazioni moderne", "modern-apps.html"),
    ("Software gestionali su misura", "custom-software.html"),
    ("Lezioni e tutorial", "lessons.html"),
    ("Bigliettini da Visita con QR Code", "creative-services.html"),
]
IMAGE_OBJECT = {"@type": "ImageObject", "url": LOGO, "width": 512, "height": 512}

BUSINESS_NODE = {
    "@type": "ProfessionalService",
    "@id": BUSINESS_ID,
    "name": "Pikobit",
    "url": SITE,
    "image": IMAGE_OBJECT,
    "logo": IMAGE_OBJECT,
    "description": "Programmatore e web designer a Monopoli: siti web, applicazioni e software gestionali su misura per aziende e professionisti.",
    "telephone": "+39-351-889-1903",
    "email": "piko.bit.00@gmail.com",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Monopoli",
        "addressRegion": "BA",
        "postalCode": "70043",
        "addressCountry": "IT",
    },
    # Centre of Monopoli, not a street address.
    "geo": {"@type": "GeoCoordinates", "latitude": 40.9500, "longitude": 17.3000},
    "hasMap": MAPS,
    "openingHours": "Mo-Fr 09:00-17:00",
    "sameAs": [
        MAPS,
        "https://www.instagram.com/pikobit_it/",
        "https://www.youtube.com/@pikobit01",
    ],
    "founder": {"@id": PERSON_ID},
    "employee": {"@id": PERSON_ID},
    "areaServed": AREA_SERVED,
    "knowsAbout": [name for name, _ in OFFERS],
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Servizi",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@id": f"{SITE}{page}#service"}}
            for name, page in OFFERS
        ],
    },
}

PERSON_NODE = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "Giuseppe Alaimo",
    "jobTitle": "Software Engineer",
    "description": "Software Engineer Senior specializzato in Java/Spring, sviluppa siti web, applicazioni e software su misura; crea anche tutorial e progetti di programmazione.",
    "url": SITE + "about.html",
    "image": IMAGE_OBJECT,
    "worksFor": {"@id": BUSINESS_ID},
    # Only the technologies Giuseppe confirmed (2026-09-29), as on the service pages.
    "knowsAbout": [
        "Java", "Spring Boot", "Python", "C", "C++", "Flutter", "Dart", "Kotlin",
        "Android Studio", "Angular", "React", "HTML", "CSS", "JavaScript", "WordPress",
        "PostgreSQL", "MySQL", "Clean Architecture", "Design pattern", "Test automatici",
    ],
    "sameAs": [
        "https://www.linkedin.com/in/giuseppe-alaimo-aba40b226",
        "https://www.superprof.it/laureato-informatica-lezioni-programmazione-web-per-creazione-sito-web-javascript-nodejs-html-css-python-flask.html",
    ],
}

WEBSITE_NODE = {
    "@type": "WebSite",
    "@id": WEBSITE_ID,
    "name": "Pikobit",
    "url": SITE,
    "description": "Sviluppo software su misura, siti web e applicazioni moderne per aziende e professionisti.",
    "inLanguage": "it",
    "publisher": {"@id": BUSINESS_ID},
}

ENTITY_TYPES = {"ProfessionalService", "LocalBusiness", "Organization", "WebSite", "Person"}
PAGE_TYPES = {"WebPage", "AboutPage", "ContactPage", "CollectionPage"}
SERVICE_PAGES = {page for _, page in _chrome.SERVICES}
CITY_PAGES = {page: label for label, page in _chrome.CITIES}
LABELS = {page: htmllib.unescape(label) for label, page, *_ in _chrome.SERVICES + _chrome.MENU}
LABELS["privacy.html"] = "Privacy"

BLOCK_RE = re.compile(r'([ \t]*)<script type="application/ld\+json">(.*?)</script>', re.S)
EXTRA_BLOCK_RE = re.compile(
    r'\n(?:[ \t]*\n)*(?:[ \t]*<!--(?:(?!-->).)*-->[ \t]*\n)*'
    r'[ \t]*<script type="application/ld\+json">.*?</script>', re.S
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _tag_re(attr, name):
    return re.compile(
        rf'<meta\s+{attr}="{re.escape(name)}"\s+content="([^"]*)"\s*/?>', re.S
    )


CANONICAL_RE = re.compile(r'(<link\s+rel="canonical"\s+href=")([^"]*)(")', re.S)
OG_URL_RE = re.compile(r'(<meta\s+property="og:url"\s+content=")([^"]*)(")', re.S)
VIEWPORT_RE = re.compile(r'^([ \t]*)<meta\s+name="viewport"[^>]*>', re.M)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
TITLE_RE = re.compile(r"(<title>)(.*?)(</title>)", re.S)
# The pipeline wraps long titles: "- Blog\nPikoBit" is the same suffix.
BLOG_SUFFIX_RE = re.compile(r"Blog(\s+)PikoBit(\s*)$")
TITLE_SUFFIX = " | Pikobit"
TITLE_MAX, DESCRIPTION_MAX = 60, 155
CITY_SERVICE_TYPE = "Realizzazione siti web e sviluppo software su misura"
RETIRED_RE = re.compile(r"images/(?:logo|banner|filigrana)\.webp")
ICON_LINK_RE = re.compile(r'<link\b[^>]*\brel="(?:icon|shortcut icon|apple-touch-icon|manifest)"[^>]*>', re.S)
HREF_RE = re.compile(r'\bhref="([^"]*)"')


class PageError(Exception):
    """A page this script cannot handle (no canonical, no BlogPosting...)."""


def _collapse(s):
    return " ".join(s.split())


def _text(s):
    return _collapse(htmllib.unescape(re.sub(r"<[^>]+>", " ", s)))


def _meta(head, attr, name):
    m = _tag_re(attr, name).search(head)
    return m.group(1) if m else None


def _line_indent(head, pos):
    start = head.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", head[start:]).group(0)


def _set_meta(head, attr, name, value, after):
    """Put <meta attr=name content=value /> in place of the existing one, or
    right after the first match of the `after` regex. No anchor: unchanged."""
    tag = f'<meta {attr}="{name}" content="{value}" />'
    rx = _tag_re(attr, name)
    if rx.search(head):
        return rx.sub(lambda m: tag, head, count=1)
    m = after.search(head)
    if not m:
        return head
    return head[: m.end()] + "\n" + _line_indent(head, m.start()) + tag + head[m.end():]


# --- dates -----------------------------------------------------------------

_SHALLOW = None


def _history_available():
    global _SHALLOW
    if _SHALLOW is None:
        res = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                             cwd=ROOT, capture_output=True, text=True)
        _SHALLOW = res.stdout.strip() != "false"
    return not _SHALLOW


def modified_date(rel, published, existing):
    """Date of the last content change of the article, never before it was published."""
    if not _history_available():
        return existing or published
    date, created = _lastmod.last_content_change(ROOT, rel, datetime.date.today().isoformat())
    # Text never changed since the article was committed: it was never modified.
    return published if created else max(date, published)


# --- JSON-LD ----------------------------------------------------------------

def _nodes(blocks):
    nodes = []
    for raw in blocks:
        data = json.loads(raw)
        items = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in items:
            node = dict(node)
            node.pop("@context", None)
            nodes.append(node)
    return nodes


def _is_entity(node):
    return node.get("@type") in ENTITY_TYPES or node.get("@id") in (BUSINESS_ID, PERSON_ID, WEBSITE_ID)


def _link_entities(node):
    for key in ("author", "creator"):
        if isinstance(node.get(key), dict):
            node[key] = {"@id": PERSON_ID}
    for key in ("provider", "publisher"):
        if isinstance(node.get(key), dict):
            node[key] = {"@id": BUSINESS_ID}
    main = node.get("mainEntity")
    if isinstance(main, dict) and main.get("@type") == "Person":
        node["mainEntity"] = {"@id": PERSON_ID}
    if node.get("@type") in PAGE_TYPES:
        # Not WebPage properties (an "Offer" with a text price is invalid too).
        node.pop("brand", None)
        node.pop("offers", None)


def _breadcrumb(url, trail):
    return {
        "@type": "BreadcrumbList",
        "@id": url + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": item}
            for i, (name, item) in enumerate(trail, 1)
        ],
    }


def build_graph(nodes, rel, url, head, body):
    kept = [n for n in nodes if not _is_entity(n)]
    for node in kept:
        _link_entities(node)
    types = [n.get("@type") for n in kept]

    if rel.startswith("blog/"):
        post = next((n for n in kept if n.get("@type") == "BlogPosting"), None)
        if post is None or "datePublished" not in post or "headline" not in post:
            raise PageError("no BlogPosting with headline and datePublished in the JSON-LD")
        post.setdefault("@id", url + "#article")
        post["mainEntityOfPage"] = {"@id": url}
        post["image"] = OG_IMAGE
        post["author"] = {"@id": PERSON_ID}
        post["publisher"] = {"@id": BUSINESS_ID}
        post["dateModified"] = modified_date(rel, post["datePublished"], post.get("dateModified"))
        post.setdefault("inLanguage", "it")

    description = _text(_meta(head, "name", "description") or "")
    if rel in SERVICE_PAGES or rel in CITY_PAGES:
        h1 = H1_RE.search(body)
        if h1 is None:
            raise PageError("no <h1> to name the Service")
        if "Service" not in types:
            kept.append({"@type": "Service", "@id": url + "#service", "url": url})
        svc = next(n for n in kept if n.get("@type") == "Service")
        # Name and description follow the page: a new h1 must not leave stale data.
        # A city page offers the whole service there, its h1 is about the person.
        if rel in CITY_PAGES:
            svc["name"] = f"Realizzazione siti web, software e app a {CITY_PAGES[rel]}"
            svc["serviceType"] = CITY_SERVICE_TYPE
        else:
            svc["name"] = _text(h1.group(1))
        svc["description"] = description
        svc.setdefault("@id", url + "#service")
        svc["provider"] = {"@id": BUSINESS_ID}
        svc["areaServed"] = (
            {"@type": "City", "name": CITY_PAGES[rel], "addressCountry": "IT"}
            if rel in CITY_PAGES else AREA_SERVED
        )

    if rel != "index.html" and "BreadcrumbList" not in types:
        if rel.startswith("blog/"):
            leaf = next(n for n in kept if n.get("@type") == "BlogPosting")["headline"]
            trail = [("Home", SITE), ("Blog", SITE + "resources.html"), (_collapse(leaf), url)]
        elif rel in CITY_PAGES:
            trail = [("Home", SITE), ("Dove lavoro", SITE + "dove-lavoro.html"), (CITY_PAGES[rel], url)]
        else:
            trail = [("Home", SITE), (LABELS[rel], url)]
        kept.append(_breadcrumb(url, trail))
        page = next((n for n in kept if n.get("@type") in PAGE_TYPES), None)
        if page is not None:
            page.setdefault("@id", url)
            page.setdefault("url", url)
            page["breadcrumb"] = {"@id": url + "#breadcrumb"}

    page = next((n for n in kept if n.get("@type") in PAGE_TYPES), None)
    title = TITLE_RE.search(head)
    if page is not None and title is not None:
        page["name"] = _text(title.group(2))
        if description:
            page["description"] = description

    entities = [BUSINESS_NODE, PERSON_NODE] + ([WEBSITE_NODE] if rel == "index.html" else [])
    return {"@context": "https://schema.org", "@graph": entities + kept}


def _brand_name(head, blog):
    """The brand is written "Pikobit" in titles (visible text stays as it is).
    Blog: only the " - Blog PikoBit" suffix, the article title is the author's."""
    if blog:
        return TITLE_RE.sub(lambda m: m.group(1) + BLOG_SUFFIX_RE.sub(r"Blog\1Pikobit\2", m.group(2)) + m.group(3), head, count=1)
    head = TITLE_RE.sub(lambda m: m.group(1) + m.group(2).replace("PikoBit", "Pikobit") + m.group(3), head, count=1)
    og = _tag_re("property", "og:title")
    return og.sub(lambda m: m.group(0).replace("PikoBit", "Pikobit"), head, count=1)


def _blocks(head):
    return [m.group(2) for m in BLOCK_RE.finditer(head)]


def _script(indent, graph):
    body = json.dumps(graph, indent=2, ensure_ascii=False)
    # A "</script>" in a value would close the block early: escape as JSON does.
    for char, esc in (("&", "\\u0026"), ("<", "\\u003c"), (">", "\\u003e")):
        body = body.replace(char, esc)
    body = "\n".join(indent + "  " + line for line in body.split("\n"))
    return f'{indent}<script type="application/ld+json">\n{body}\n{indent}</script>'


def _replace_jsonld(head, graph):
    first = BLOCK_RE.search(head)
    if first is None:
        indent = VIEWPORT_RE.search(head).group(1)
        block = f"\n{indent}<!-- Dati strutturati -->\n" + _script(indent, graph) + "\n"
        return head.rstrip() + "\n" + block
    before, after = head[: first.start()], head[first.end():]
    after = EXTRA_BLOCK_RE.sub("", after)
    return before + _script(first.group(1), graph) + after


# --- page ---------------------------------------------------------------------

def update_page(html, rel):
    head, sep, rest = html.partition("</head>")
    if not sep:
        raise PageError("no </head>")
    if not CANONICAL_RE.search(head):
        raise PageError('no <link rel="canonical">')
    if not VIEWPORT_RE.search(head):
        raise PageError('no <meta name="viewport"> (anchor for the new tags)')
    head = CANONICAL_RE.sub(lambda m: m.group(1) + m.group(2).strip() + m.group(3), head)
    head = OG_URL_RE.sub(lambda m: m.group(1) + m.group(2).strip() + m.group(3), head)
    url = CANONICAL_RE.search(head).group(2)

    robots = _meta(head, "name", "robots")
    if robots is None or "noindex" not in robots:
        head = _set_meta(head, "name", "robots", ROBOTS_CONTENT, VIEWPORT_RE)

    blog = rel.startswith("blog/")
    head = _brand_name(head, blog)
    head = _set_meta(head, "property", "og:type", "article" if blog else "website", VIEWPORT_RE)
    # The social preview says what the search result says.
    desc = _meta(head, "name", "description")
    if desc is not None and _meta(head, "property", "og:description") is not None:
        head = _set_meta(head, "property", "og:description", _collapse(desc), VIEWPORT_RE)
    for field in ("title", "description"):
        og = _meta(head, "property", f"og:{field}")
        if og is not None:
            anchor = _tag_re("name", "twitter:card") if _meta(head, "name", "twitter:card") else _tag_re("property", f"og:{field}")
            head = _set_meta(head, "name", f"twitter:{field}", _collapse(og), anchor)

    try:
        nodes = _nodes(_blocks(head))
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as e:
        raise PageError(f"invalid JSON-LD: {e}")
    graph = build_graph(nodes, rel, url, head, rest)
    head = _replace_jsonld(head, graph)

    if blog:
        post = next(n for n in graph["@graph"] if n.get("@type") == "BlogPosting")
        og_type = _tag_re("property", "og:type")
        head = _set_meta(head, "property", "article:published_time", post["datePublished"], og_type)
        head = _set_meta(head, "property", "article:modified_time", post["dateModified"],
                         _tag_re("property", "article:published_time"))
    return head + sep + rest


def verify_page(html, rel):
    problems = []
    head = html.partition("</head>")[0]
    if not re.search(r'<html[^>]*\blang="it"', html):
        problems.append('<html lang="it"> missing')
    blocks = _blocks(head)
    try:
        nodes = _nodes(blocks)
    except (json.JSONDecodeError, AttributeError) as e:
        return problems + [f"invalid JSON-LD: {e}"]
    if len(blocks) != 1:
        problems.append(f"{len(blocks)} JSON-LD blocks (expected 1)")
    if BUSINESS_NODE not in nodes:
        problems.append("ProfessionalService #business missing or different from BUSINESS_NODE")
    if PERSON_NODE not in nodes:
        problems.append("Person #giuseppe missing or different from PERSON_NODE")
    types = [n.get("@type") for n in nodes]
    if rel == "index.html" and WEBSITE_NODE not in nodes:
        problems.append("WebSite node missing on the home page")
    if rel != "index.html" and "BreadcrumbList" not in types:
        problems.append("BreadcrumbList missing")
    if (rel in SERVICE_PAGES or rel in CITY_PAGES) and not any(
        n.get("@type") == "Service" and n.get("provider") == {"@id": BUSINESS_ID} for n in nodes
    ):
        problems.append("Service with provider #business missing")
    problems += _asset_problems(html, head, rel)

    canonical = CANONICAL_RE.search(head)
    if canonical is None or canonical.group(2) != canonical.group(2).strip():
        problems.append("canonical missing or with whitespace in the href")
    og_url = OG_URL_RE.search(head)
    if og_url is not None and og_url.group(2) != og_url.group(2).strip():
        problems.append("og:url with whitespace in the content")

    robots = _meta(head, "name", "robots")
    if robots is None or ("noindex" not in robots and robots != ROBOTS_CONTENT):
        problems.append("robots meta missing or without max-image-preview:large")
    desc = _meta(head, "name", "description")
    og_desc = _meta(head, "property", "og:description")
    if desc is not None and og_desc is not None and og_desc != _collapse(desc):
        problems.append("og:description different from the meta description")
    for field in ("title", "description"):
        og = _meta(head, "property", f"og:{field}")
        if og is not None and _meta(head, "name", f"twitter:{field}") != _collapse(og):
            problems.append(f"twitter:{field} missing or different from og:{field}")

    blog = rel.startswith("blog/")
    title = TITLE_RE.search(head)
    title = title.group(2) if title else ""
    if (BLOG_SUFFIX_RE.search(title) if blog else "PikoBit" in title + (_meta(head, "property", "og:title") or "")):
        problems.append('brand written "PikoBit" in the title (use "Pikobit")')
    if not blog:
        text = _text(title)
        if not text.endswith(TITLE_SUFFIX):
            problems.append(f'title does not end with "{TITLE_SUFFIX}"')
        if len(text) > TITLE_MAX:
            problems.append(f"title longer than {TITLE_MAX} characters ({len(text)})")
        desc = _text(_meta(head, "name", "description") or "")
        if len(desc) > DESCRIPTION_MAX:
            problems.append(f"description longer than {DESCRIPTION_MAX} characters ({len(desc)})")
    if _meta(head, "property", "og:type") != ("article" if blog else "website"):
        problems.append("wrong og:type")
    if blog:
        post = next((n for n in nodes if n.get("@type") == "BlogPosting"), {})
        if not DATE_RE.match(str(post.get("dateModified", ""))):
            problems.append("BlogPosting without dateModified")
        expected = {
            "author": {"@id": PERSON_ID},
            "publisher": {"@id": BUSINESS_ID},
            "image": OG_IMAGE,
            "mainEntityOfPage": {"@id": canonical.group(2).strip() if canonical else None},
        }
        for key, value in expected.items():
            if post.get(key) != value:
                problems.append(f"BlogPosting {key} missing or wrong")
        if _meta(head, "property", "article:published_time") != post.get("datePublished"):
            problems.append("article:published_time missing or different from datePublished")
        if _meta(head, "property", "article:modified_time") != post.get("dateModified"):
            problems.append("article:modified_time missing or different from dateModified")
    return problems


def _local_file(ref, rel):
    """The repo file a URL of the page points to, None if it is external."""
    ref = ref.strip().split("?")[0].split("#")[0]
    if ref.startswith(SITE):
        return ROOT / ref[len(SITE):]
    if ref.startswith(("http://", "https://", "//", "data:")) or not ref:
        return None
    return ROOT / ref.lstrip("/") if ref.startswith("/") else (ROOT / rel).parent / ref


def _asset_problems(html, head, rel):
    problems = [f"references the retired image {m}" for m in sorted(set(RETIRED_RE.findall(html)))]
    refs = [HREF_RE.search(tag).group(1) for tag in ICON_LINK_RE.findall(head) if HREF_RE.search(tag)]
    refs += [v for v in (_meta(head, "property", "og:image"), _meta(head, "name", "twitter:image")) if v]
    for ref in refs:
        target = _local_file(ref, rel)
        if target is not None and not target.is_file():
            problems.append(f"{ref.strip()} does not exist")
    return problems


def pages():
    return sorted(
        [p for p in ROOT.glob("*.html")] + [p for p in (ROOT / "blog").glob("*.html")]
    )


def _rel(path):
    return str(Path(path).resolve().relative_to(ROOT.resolve()))


def _read(path):
    """(rel, html) of a page of the site; PageError if it is not one."""
    try:
        return _rel(path), Path(path).read_text(encoding="utf-8")
    except ValueError:
        raise PageError(f"not inside the site ({ROOT})")
    except OSError as e:
        raise PageError(f"cannot read: {e.strerror}")


def main(argv):
    check = "--verifica" in argv
    targets = [Path(a) for a in argv if a != "--verifica"] or pages()
    errors = 0
    if check:
        bad = set()
        for target in targets:
            try:
                rel, html = _read(target)
            except PageError as e:
                problems, rel = [str(e)], str(target)
            else:
                problems = verify_page(html, rel)
            for problem in problems:
                print(f"  - {rel}: {problem}")
                bad.add(rel)
        print(f"seo_head --verifica: {len(bad)}/{len(targets)} pages not conforming")
        return 1 if bad else 0
    changed = 0
    for page in targets:
        try:
            rel, html = _read(page)
            new = update_page(html, rel)
        except PageError as e:
            print(f"seo_head: {page}: {e}", file=sys.stderr)
            errors += 1
            continue
        if new != html:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"seo_head: {changed}/{len(targets)} pages updated, {errors} with errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
