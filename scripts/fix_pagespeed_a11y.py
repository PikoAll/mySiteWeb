import os
import re

# COMANDO: python3 scripts/fix_pagespeed_a11y.py
# Fix mirati PageSpeed mobile (FCP/LCP) + Lighthouse "Accessibilita' per gli
# agenti" (albero di accessibilita' non ben formato) su tutte le pagine:
#   1) defer su scripts/script.js (non blocca piu' il parsing HTML)
#   2) preconnect a fonts.googleapis.com / fonts.gstatic.com prima del link
#      esistente al font Poppins
#   3) ruolo/stato ARIA sul menu hamburger (div usato come bottone) e sul
#      toggle dropdown "Servizi" (l'aggiornamento dinamico di aria-expanded
#      e' gestito in scripts/script.js, non da questo script)
# Idempotente: se un pattern e' gia' presente, il file viene saltato.

ROOT_DIR = "."
BLOG_DIR = "blog"

SCRIPT_TAG_RE = re.compile(r'<script src="([^"]*script\.js[^"]*)"></script>')

FONTS_LINK_RE = re.compile(
    r'^([ \t]*)(<link[^<]*?fonts\.googleapis\.com[^<]*?>)', re.MULTILINE
)

HAMBURGER_OLD = '<div class="hamburger" id="hamburger-menu">'
HAMBURGER_NEW = (
    '<div class="hamburger" id="hamburger-menu" role="button" tabindex="0" '
    'aria-label="Apri menu di navigazione" aria-expanded="false">'
)

DROPDOWN_OLD = '<a href="#" id="dropdown-toggle">'
DROPDOWN_NEW = '<a href="#" id="dropdown-toggle" aria-haspopup="true" aria-expanded="false">'


def add_defer(content):
    return SCRIPT_TAG_RE.sub(lambda m: f'<script defer src="{m.group(1)}"></script>', content)


def add_preconnect(content):
    # evita doppio inserimento se lo script viene rilanciato
    if 'rel="preconnect" href="https://fonts.googleapis.com"' in content:
        return content
    return FONTS_LINK_RE.sub(
        lambda m: (
            f'{m.group(1)}<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'{m.group(1)}<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'{m.group(1)}{m.group(2)}'
        ),
        content,
        count=1,
    )


def add_aria(content):
    content = content.replace(HAMBURGER_OLD, HAMBURGER_NEW)
    content = content.replace(DROPDOWN_OLD, DROPDOWN_NEW)
    return content


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = add_defer(content)
    new_content = add_preconnect(new_content)
    new_content = add_aria(new_content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"OK   {path}")
    else:
        print(f"skip {path} (nessuna modifica)")


def main():
    html_files = sorted(f for f in os.listdir(ROOT_DIR) if f.endswith(".html"))
    html_files += sorted(
        os.path.join(BLOG_DIR, f) for f in os.listdir(BLOG_DIR) if f.endswith(".html")
    )
    for path in html_files:
        process_file(path)
    print("Completato.")


if __name__ == "__main__":
    main()
