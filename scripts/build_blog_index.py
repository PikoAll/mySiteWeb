#!/usr/bin/env python3
"""Build blog/index.html: the archive of every article, newest first.

/blog/ used to answer 404 and the articles were only reachable from the
paged list of resources.html. The page reuses the header/footer and the
local CTA of the newest article, lists every blog/*.html (title and date
come from the article's JSON-LD BlogPosting) and goes through
scripts/seo_head.py, so title, description, canonical and JSON-LD follow
the same rules as every other page.

Usage:
    python3 scripts/build_blog_index.py            # rewrite blog/index.html
    python3 scripts/build_blog_index.py --check    # exit 1 if it is stale
Run it after adding an article (the weekly pipeline must do it too).
"""
import html as htmllib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
INDEX = BLOG / "index.html"
URL = "https://pikobit.it/blog/"
TITLE = "Archivio del blog: tutti gli articoli | Pikobit"
DESCRIPTION = "Tutti gli articoli del blog Pikobit: programmazione, AI, sicurezza e siti web per attività locali, dal più recente al più vecchio."

spec = importlib.util.spec_from_file_location("seo_head", ROOT / "scripts" / "seo_head.py")
seo_head = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_head)


def articles():
    """[(date, filename, headline)] newest first, index.html excluded."""
    out = []
    for path in BLOG.glob("*.html"):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8")
        head = text.partition("</head>")[0]
        for node in seo_head._nodes(seo_head._blocks(head)):
            if node.get("@type") == "BlogPosting":
                out.append((node["datePublished"], path.name, node["headline"]))
    return sorted(out, reverse=True)


def build():
    items = articles()
    newest = BLOG / items[0][1]
    base = newest.read_text(encoding="utf-8")
    head, sep, rest = base.partition("</head>")
    # a page of its own: no article metadata, no keywords, no BlogPosting
    head = re.sub(r'\n[ \t]*<meta\s+property="article:[a-z_]+"\s+content="[^"]*"\s*/>', "", head)
    head = re.sub(r'\n[ \t]*<meta\s+name="keywords"\s+content="[^"]*"\s*/>', "", head, flags=re.S)
    head = seo_head.TITLE_RE.sub(lambda m: m.group(1) + htmllib.escape(TITLE, quote=False) + m.group(3), head, count=1)
    head = seo_head._set_meta(head, "name", "description", DESCRIPTION, seo_head.VIEWPORT_RE)
    head = seo_head._set_meta(head, "property", "og:title", TITLE, seo_head.VIEWPORT_RE)
    head = seo_head.CANONICAL_RE.sub(lambda m: m.group(1) + URL + m.group(3), head)
    head = seo_head.OG_URL_RE.sub(lambda m: m.group(1) + URL + m.group(3), head)
    block = json.dumps({"@context": "https://schema.org", "@graph": [{"@type": "CollectionPage"}]}, indent=2)
    head = seo_head.BLOCK_RE.sub(lambda m: m.group(1) + '<script type="application/ld+json">\n' + block + "\n</script>", head, count=1)

    main_start = rest.index("<main>")
    main_end = rest.index("</main>")
    cta = rest[rest.index("<!-- pikobit-local-cta -->"):main_end].rstrip()
    rows = "\n".join(
        f'          <li><a href="{name}">{htmllib.escape(htmllib.unescape(title), quote=False)}</a> '
        f'<time datetime="{date}">{date}</time></li>'
        for date, name, title in items
    )
    main = f"""<main>
      <section class="intro">
        <div class="intro-container">
          <p class="tagline">Blog</p>
          <h1>Archivio del blog</h1>
          <p>Tutti gli articoli, dal più recente al più vecchio. Gli ultimi sono in evidenza nella pagina <a href="../resources.html">Risorse</a>.</p>
        </div>
      </section>

      <section class="why-pikobit">
        <h2>Tutti gli articoli ({len(items)})</h2>
        <ul class="blog-archive">
{rows}
        </ul>
      </section>
      {cta}
    """
    page = head + sep + rest[:main_start] + main + rest[main_end:]
    return seo_head.update_page(page, "blog/index.html")


def main(argv):
    new = build()
    if "--check" in argv:
        ok = INDEX.exists() and INDEX.read_text(encoding="utf-8") == new
        print("blog/index.html " + ("up to date" if ok else "STALE: run scripts/build_blog_index.py"))
        return 0 if ok else 1
    INDEX.write_text(new, encoding="utf-8")
    print(f"blog/index.html: {len(articles())} articles")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
