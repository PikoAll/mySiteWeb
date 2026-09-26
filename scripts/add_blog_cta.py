#!/usr/bin/env python3
"""Append the local-services CTA box at the end of every blog article.

The box links the article to programmatore-monopoli.html and to the three
service pages, so the developer-news articles stop being dead ends for a local
customer. It is inserted right before the LAST </main> of each article (the
JSON-LD in <head> is never touched) and is marked with MARKER: a file that
already carries the marker is left byte-for-byte unchanged, so the script is
idempotent and can be re-run after every new batch of articles.

Usage:
    python3 scripts/add_blog_cta.py              # all <repo>/blog/*.html
    python3 scripts/add_blog_cta.py FILE...      # only the given files
    python3 scripts/add_blog_cta.py --check ...  # exit 1 if a file lacks the box, write nothing

Exit code: 0 ok, 1 --check found missing boxes, 2 a file could not be processed.
"""
import sys
from pathlib import Path

MARKER = "<!-- pikobit-local-cta -->"

BOX = f"""{MARKER}
<section class="why-pikobit local-cta">
<h2>Ti serve un sito o un software su misura a Monopoli?</h2>
<p>
Sono Giuseppe, programmatore e web designer a Monopoli. Realizzo
<a href="../websites.html">siti web</a>,
<a href="../custom-software.html">gestionali su misura</a> e
<a href="../modern-apps.html">applicazioni</a> per attività e
professionisti di Monopoli e di tutta la zona tra Bari, Brindisi e
Taranto. Il preventivo è gratuito.
</p>
<p>
<a href="../programmatore-monopoli.html" class="cta-link"
>Scopri come lavoro e dove</a
>
</p>
</section>
"""

REPO_BLOG_DIR = Path(__file__).resolve().parent.parent / "blog"


def has_box(html):
    return MARKER in html


def process(path):
    """Insert the box in path. Return True if the file changed, False if it already had it."""
    path = Path(path)
    html = path.read_text(encoding="utf-8")
    if has_box(html):
        return False
    idx = html.rfind("</main>")
    if idx == -1:
        raise ValueError(f"{path}: no </main> found")
    path.write_text(html[:idx] + BOX + html[idx:], encoding="utf-8")
    return True


def main(argv):
    check = "--check" in argv
    files = [Path(a) for a in argv if a != "--check"] or sorted(REPO_BLOG_DIR.glob("*.html"))
    missing, changed, errors = [], [], []
    for f in files:
        try:
            if check:
                if not has_box(f.read_text(encoding="utf-8")):
                    missing.append(f)
            elif process(f):
                changed.append(f)
        except (OSError, ValueError) as e:
            errors.append(f"{f}: {e}")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if check:
        for f in missing:
            print(f"MISSING {f}")
        print(f"{len(files) - len(missing)}/{len(files)} articles have the CTA box")
        return 2 if errors else (1 if missing else 0)
    print(f"{len(changed)} changed, {len(files) - len(changed) - len(errors)} already ok, {len(errors)} errors")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
