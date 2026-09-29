#!/usr/bin/env python3
"""Check that a restyling lost no sentence of the visible text in <main>.

The format may change (lists become cards, a paragraph is split in two), the
words may not: the words of every sentence of <main> in the old version must
still be in the new one, in the same order (whitespace and punctuation are
ignored). Only <main> is compared (header, menu
and footer change on purpose); <script>/<style> are ignored.

Usage:
    python3 scripts/compare_page_text.py OLD_DIR NEW_DIR [PAGE...]
      e.g. OLD_DIR = a `git archive main` export, NEW_DIR = the repo
    (no PAGE: every *.html of OLD_DIR)

Exit code: 0 nothing lost, 1 sentences lost (printed per page).
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


BLOCK = "\x00"  # block boundary; source newlines are only whitespace


class _MainText(HTMLParser):
    SKIP = {"script", "style", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0  # inside <main>
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth += 1
        elif tag in self.SKIP:
            self.skip += 1
        elif tag in ("p", "li", "h1", "h2", "h3", "h4", "div", "section", "br", "blockquote"):
            self.parts.append(BLOCK)

    def handle_endtag(self, tag):
        if tag == "main":
            self.depth -= 1
        elif tag in self.SKIP:
            self.skip -= 1
        elif tag in ("p", "li", "h1", "h2", "h3", "h4", "div", "section", "blockquote"):
            self.parts.append(BLOCK)

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.parts.append(data)


def main_text(html):
    parser = _MainText()
    parser.feed(html)
    return "".join(parser.parts)


def sentences(text):
    """Blocks split on . ! ? followed by a space, whitespace collapsed."""
    out = []
    for block in text.split(BLOCK):
        block = re.sub(r"\s+", " ", block).strip()
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+", block) if s.strip()]
    return out


def _words(s):
    """The words of s, punctuation dropped: a card title may lose the colon
    of the old "<strong>Title:</strong> text", never a word."""
    return " " + " ".join(re.findall(r"\w+", s)) + " "


def lost_sentences(old_html, new_html):
    new = _words(main_text(new_html).replace(BLOCK, " "))
    # A sentence with no word ("*" after "privacy.") has nothing to lose.
    return [s for s in sentences(main_text(old_html)) if _words(s).strip() and _words(s) not in new]


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    old_dir, new_dir = Path(argv[0]), Path(argv[1])
    pages = argv[2:] or sorted(str(p.relative_to(old_dir)) for p in old_dir.rglob("*.html"))
    lost_total = 0
    for page in pages:
        new_path = new_dir / page
        if not new_path.exists():
            print(f"{page}: MISSING in {new_dir}")
            lost_total += 1
            continue
        lost = lost_sentences(
            (old_dir / page).read_text(encoding="utf-8"), new_path.read_text(encoding="utf-8")
        )
        for s in lost:
            print(f"{page}: LOST {s!r}")
        lost_total += len(lost)
    print(f"{len(pages)} pages compared, {lost_total} sentences lost")
    return 1 if lost_total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
