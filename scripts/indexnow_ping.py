#!/usr/bin/env python3
"""Tell the IndexNow search engines (Bing, Yandex, Seznam...) which pages changed.

IndexNow is free and needs no account: the site proves it owns the key by
serving <key>.txt from its root (the file holding its own name). Google does
not use IndexNow; for Google the sitemap lastmod stays the signal.

Only HTML pages are sent, never a page marked noindex. A page that no longer
exists is sent too: that is how the engine learns it is gone.

Usage:
    python3 scripts/indexnow_ping.py FILE...            # preview, sends nothing
    python3 scripts/indexnow_ping.py --dal REF          # pages changed since git REF
    python3 scripts/indexnow_ping.py --invia FILE...    # real POST to api.indexnow.org
Files are paths relative to the repo root (blog/2026-10-02-x.html).
Exit: 0 sent / previewed / nothing to send, 1 the engine refused the request,
2 wrong usage (--dal without a ref or with an unknown one).
"""
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "pikobit.it"
SITE = f"https://{HOST}/"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE_RE = re.compile(r"^[0-9a-f]{32}\.txt$")
NOINDEX_RE = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.S)


def find_key(root=ROOT):
    for path in sorted(root.iterdir()):
        if KEY_FILE_RE.match(path.name) and path.read_text(encoding="utf-8").strip() == path.stem:
            return path.stem
    raise SystemExit("indexnow_ping: no <key>.txt in the site root")


def files_to_urls(files, root=ROOT):
    urls = []
    for rel in files:
        if not rel.endswith(".html"):
            continue
        page = root / rel
        if page.exists() and NOINDEX_RE.search(page.read_text(encoding="utf-8")):
            continue
        path = rel[: -len("index.html")] if rel.endswith("index.html") else rel
        urls.append(SITE + path)
    return urls


def payload(key, urls):
    return {"host": HOST, "key": key, "keyLocation": f"{SITE}{key}.txt", "urlList": urls}


def post(body):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status
    except urllib.error.HTTPError as e:
        return e.code


def changed_since(ref):
    """Files changed from git REF to HEAD, None if REF is unknown."""
    res = subprocess.run(["git", "diff", "--name-only", ref, "HEAD"],
                         cwd=ROOT, capture_output=True, text=True)
    return res.stdout.split() if res.returncode == 0 else None


def main(argv, sender=post):
    send = "--invia" in argv
    args = [a for a in argv if a != "--invia"]
    if args[:1] == ["--dal"]:
        if len(args) != 2:
            print("indexnow_ping: --dal wants one git ref, e.g. --dal HEAD~1", file=sys.stderr)
            return 2
        ref, args = args[1], changed_since(args[1])
        if args is None:
            print(f"indexnow_ping: unknown git ref {ref!r} (shallow clone? try the file names)", file=sys.stderr)
            return 2
    urls = files_to_urls(args)
    if not urls:
        print("indexnow_ping: no page to send")
        return 0
    body = payload(find_key(), urls)
    if not send:
        print("indexnow_ping: preview (add --invia to send)")
        print(json.dumps(body, indent=2))
        return 0
    status = sender(body)
    print(f"indexnow_ping: {len(urls)} URL, HTTP {status}")
    # 200 OK, 202 accepted (key still being validated): both fine.
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
