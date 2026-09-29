#!/usr/bin/env python3
"""Put the approved Pikobit brand in every page's <head>. Idempotent.

Only <head> changes; title, description, canonical and every visible text stay
as they are.

- the old favicon (<link rel="icon" href=".../images/logo.webp" type="image/png">,
  a non-square WebP declared as PNG) becomes the favicon set built by
  scripts/build_brand_assets.py: favicon.ico, PNG 32/192, apple-touch-icon,
  web manifest and theme-color. Root-relative paths: same tags at any depth.
- og:image (the old banner.webp) becomes images/brand/og-pikobit-1200x630.jpg
  with width/height/alt, plus og:locale, og:site_name and the Twitter card.
- JSON-LD "image": ".../logo.webp" becomes the square 512px logo as an
  ImageObject, and the same object is added as "logo".

Usage:
    python3 scripts/brand_head.py            # every page of the site
    python3 scripts/brand_head.py FILE...    # given pages only
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://pikobit.it"
OG_IMAGE = f"{SITE}/images/brand/og-pikobit-1200x630.jpg"
LOGO = f"{SITE}/images/brand/pikobit-logo-512.png"

OLD_ICON_RE = re.compile(
    r'([ \t]*)<link rel="icon" href="[./]*images/logo\.webp" type="image/png"\s*/?>\n?'
)
OLD_OG_IMAGE_RE = re.compile(
    r'([ \t]*)<meta\s+property="og:image"\s+content="\s*[^"]*"\s*/?>'
)
OLD_JSONLD_IMAGE_RE = re.compile(
    r'([ \t]*)"image": "https://pikobit\.it/images/logo\.webp",'
)

FAVICON_TAGS = [
    '<link rel="icon" href="/favicon.ico" sizes="any" />',
    '<link rel="icon" type="image/png" sizes="32x32" href="/images/brand/favicon-32.png" />',
    '<link rel="icon" type="image/png" sizes="192x192" href="/images/brand/favicon-192.png" />',
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />',
    '<link rel="manifest" href="/site.webmanifest" />',
    '<meta name="theme-color" content="#0d0f12" />',
]
SOCIAL_TAGS = [
    f'<meta property="og:image" content="{OG_IMAGE}" />',
    '<meta property="og:image:width" content="1200" />',
    '<meta property="og:image:height" content="630" />',
    '<meta property="og:image:alt" content="Pikobit - programmatore e web designer a Monopoli" />',
    '<meta property="og:locale" content="it_IT" />',
    '<meta property="og:site_name" content="Pikobit" />',
    '<meta name="twitter:card" content="summary_large_image" />',
    f'<meta name="twitter:image" content="{OG_IMAGE}" />',
]
IMAGE_OBJECT = (
    '{"@type": "ImageObject", "url": "' + LOGO + '", "width": 512, "height": 512}'
)


def _block(indent, tags):
    return "\n".join(indent + tag for tag in tags)


def _head(head):
    # Favicon: the first old link becomes the new block, duplicates go away.
    seen = []

    def icon(m):
        seen.append(m)
        return _block(m.group(1), FAVICON_TAGS) + "\n" if len(seen) == 1 else ""

    head = OLD_ICON_RE.sub(icon, head)

    if "og:image:width" not in head:
        head = OLD_OG_IMAGE_RE.sub(lambda m: _block(m.group(1), SOCIAL_TAGS), head, count=1)

    head = OLD_JSONLD_IMAGE_RE.sub(
        lambda m: f'{m.group(1)}"image": {IMAGE_OBJECT},\n{m.group(1)}"logo": {IMAGE_OBJECT},',
        head,
    )
    return head


def update_head(html):
    head, sep, rest = html.partition("</head>")
    return _head(head) + sep + rest if sep else html


def pages():
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not {"node_modules", "tests", "_site"} & set(p.relative_to(ROOT).parts)
    )


def main(argv):
    targets = [Path(a) for a in argv] or pages()
    changed = 0
    for page in targets:
        html = page.read_text(encoding="utf-8")
        new = update_head(html)
        if new != html:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"brand_head: {changed}/{len(targets)} pages updated")


if __name__ == "__main__":
    main(sys.argv[1:])
