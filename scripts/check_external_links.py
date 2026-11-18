#!/usr/bin/env python3
"""List the external links of the fixed pages and report their HTTP status.

Fixed pages = every *.html of the repo except blog/ (weekly articles), tests/,
.git, node_modules and _site. Each distinct http(s) URL is checked once with a
short timeout (HEAD, then GET if the server refuses HEAD). The robots.txt of
the target host is respected: a URL it disallows is not fetched and is shown as
"robots". Not run by the checks on every change nor by the CI: only on request.

Usage:
    python3 scripts/check_external_links.py                    # print the report
    python3 scripts/check_external_links.py --report out.txt   # also write it
    python3 scripts/check_external_links.py --strict           # exit 1 if broken
Options: --root DIR, --timeout SECONDS (default 5).
Exit: 0 always (broken links only appear in the report), unless --strict.
"""
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "tests", "node_modules", "_site", "blog"}
USER_AGENT = "pikobit-link-check"
DEFAULT_TIMEOUT = 5


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value and value.strip().startswith(("http://", "https://")):
                    self.links.append(value.strip())


def external_links(root):
    """Sorted (page relative to root, url) of external links on the fixed pages."""
    root = Path(root)
    found = []
    for page in sorted(root.rglob("*.html")):
        rel = page.relative_to(root)
        if SKIP_DIRS.intersection(rel.parts):
            continue
        parser = _LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        found += [(rel, url) for url in dict.fromkeys(parser.links)]
    return found


_robots_cache = {}


def _allowed(url, timeout):
    parts = urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots_cache:
        parser = RobotFileParser()
        try:
            req = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                parser.parse(resp.read().decode("utf-8", "replace").splitlines())
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                parser.disallow_all = True
            else:
                parser.allow_all = True
        except Exception:
            parser.allow_all = True
        _robots_cache[origin] = parser
    return _robots_cache[origin].can_fetch(USER_AGENT, url)


def _request(url, method, timeout):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as err:
        return err.code


def check_url(url, timeout=DEFAULT_TIMEOUT):
    """HTTP status (int), "robots" if disallowed, or "errore: ..." on failure."""
    try:
        if not _allowed(url, timeout):
            return "robots"
        status = _request(url, "HEAD", timeout)
        if status in (403, 405, 501):
            status = _request(url, "GET", timeout)
        return status
    except Exception as err:
        return f"errore: {type(err).__name__}"


def check_all(links, timeout=DEFAULT_TIMEOUT):
    """(page, url, status) for each link; each distinct URL is fetched once."""
    cache = {}
    results = []
    for page, url in links:
        if url not in cache:
            cache[url] = check_url(url, timeout)
        results.append((page, url, cache[url]))
    return results


def is_broken(status):
    return isinstance(status, str) and status != "robots" or isinstance(status, int) and status >= 400


def format_report(results):
    lines = [f"{'ROTTO' if is_broken(s) else 'ok':5} {s} {url}  ({page})" for page, url, s in results]
    broken = sum(is_broken(s) for _, _, s in results)
    lines.append(f"{len(results)} link esterni controllati, {broken} rotti")
    return "\n".join(lines) + "\n"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    opts = {"--root": str(REPO_ROOT), "--report": None, "--timeout": str(DEFAULT_TIMEOUT)}
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    while args:
        if len(args) < 2 or args[0] not in opts:
            print(__doc__)
            return 2
        opts[args[0]] = args[1]
        args = args[2:]
    results = check_all(external_links(opts["--root"]), float(opts["--timeout"]))
    report = format_report(results)
    print(report, end="")
    if opts["--report"]:
        Path(opts["--report"]).write_text(report, encoding="utf-8")
    return 1 if strict and any(is_broken(s) for _, _, s in results) else 0


if __name__ == "__main__":
    sys.exit(main())
