#!/usr/bin/env python3
"""Measure how similar the city pages are, to keep them far from doorway pages.

For each page: take the visible text of <main> only (header, nav and footer are
shared by design and excluded; <script>/<style> ignored), lowercase it, split
into words, build word shingles of SHINGLE words, and compare every pair with
the Jaccard index. Prints every pair sorted by similarity and the worst one.

Usage:
    python3 scripts/check_page_similarity.py              # programmatore-*.html
    python3 scripts/check_page_similarity.py FILE...
    python3 scripts/check_page_similarity.py --max 0.40   # exit 1 above the threshold (default 0.40)
"""
import itertools
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SHINGLE = 4
REPO_ROOT = Path(__file__).resolve().parent.parent


class _MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth_main = 0
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth_main += 1
        elif tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.depth_main -= 1
        elif tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if self.depth_main > 0 and not self.skip:
            self.parts.append(data)


def main_text(html):
    p = _MainText()
    p.feed(html)
    return " ".join(p.parts)


def shingles(text, k=SHINGLE):
    words = re.findall(r"\w+", text.lower())
    return {tuple(words[i : i + k]) for i in range(max(len(words) - k + 1, 0))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def pairs(files):
    sets = {f: shingles(main_text(Path(f).read_text(encoding="utf-8"))) for f in files}
    out = [
        (jaccard(sets[a], sets[b]), Path(a).name, Path(b).name)
        for a, b in itertools.combinations(sorted(sets), 2)
    ]
    return sorted(out, reverse=True)


def main(argv):
    limit = 0.40
    if "--max" in argv:
        i = argv.index("--max")
        limit = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2 :]
    files = argv or sorted(str(p) for p in REPO_ROOT.glob("programmatore-*.html"))
    result = pairs(files)
    for sim, a, b in result:
        print(f"{sim:6.1%}  {a}  {b}")
    if not result:
        print("fewer than 2 pages")
        return 0
    worst = result[0]
    print(f"WORST {worst[0]:.1%} {worst[1]} <-> {worst[2]} ({len(files)} pages, "
          f"{SHINGLE}-word shingles, limit {limit:.0%})")
    return 1 if worst[0] > limit else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
