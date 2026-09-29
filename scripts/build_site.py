#!/usr/bin/env python3
"""Build _site/: the public site only, what GitHub Pages publishes.

Everything is copied EXCEPT an explicit exclusion list: documentation and
strategy (docs/, *.md), tests, the workflow, the Python/Node tooling and its
caches, backups, the archived images and dotfiles. So a new page, image or
script of the site goes online by default; a new tool must be excluded here.

An existing _site/ is not deleted: it is moved to
~/.local/state/residui-tmp/ (cleaned after 3 days by pulisci-residui-tmp).
In CI the checkout is fresh and there is nothing to move.

Usage:
    python3 scripts/build_site.py            # -> <repo>/_site
    python3 scripts/build_site.py --out DIR
"""
import datetime
import fnmatch
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {"docs", "tests", ".github", ".git", "node_modules", "__pycache__",
                 ".pytest_cache", ".claude", "_site", "test-results", "playwright-report"}
EXCLUDED_PATHS = {"images/_archivio"}
EXCLUDED_FILES = ["*.md", "*.py", "*.pyc", "*.mjs", "*.backup*", "package.json",
                  "package-lock.json", "playwright.config.*", "pytest.ini", "conftest.py", ".*"]


def excluded(rel):
    parts = rel.parts
    if EXCLUDED_DIRS & set(parts[:-1]) or any(str(rel).startswith(p + "/") for p in EXCLUDED_PATHS):
        return True
    return any(fnmatch.fnmatch(parts[-1], pat) for pat in EXCLUDED_FILES)


def _move_away(out):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    dest = Path.home() / ".local/state/residui-tmp" / f"mysiteweb-site-{stamp}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(out), str(dest))
    return dest


def build(root, out):
    root, out = Path(root), Path(out)
    if out.exists():
        print(f"build_site: old {out} moved to {_move_away(out)}")
    count = 0
    for src in sorted(root.rglob("*")):
        rel = src.relative_to(root)
        if src.is_dir() or excluded(rel) or out in src.parents:
            continue
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        count += 1
    return count


def main(argv):
    out = Path(argv[1]) if argv[:1] == ["--out"] and len(argv) == 2 else ROOT / "_site"
    count = build(ROOT, out)
    print(f"build_site: {count} files in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
