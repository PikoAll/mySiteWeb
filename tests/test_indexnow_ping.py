"""Tests for scripts/indexnow_ping.py (no network: the sender is injected)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("indexnow_ping", ROOT / "scripts" / "indexnow_ping.py")
indexnow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexnow)


def test_key_file_in_site_root_holds_its_own_name():
    key = indexnow.find_key(ROOT)
    assert len(key) == 32
    assert (ROOT / f"{key}.txt").read_text(encoding="utf-8").strip() == key


def test_files_to_urls():
    urls = indexnow.files_to_urls([
        "index.html", "blog/2026-09-04-prova.html", "styles/style.css",
        "crucidev/privacy/index.html", "sitemap.xml", "blog/nuovo.html",
    ])
    assert urls == [
        "https://pikobit.it/",
        "https://pikobit.it/blog/2026-09-04-prova.html",
        "https://pikobit.it/crucidev/privacy/",
        "https://pikobit.it/blog/nuovo.html",
    ]


def test_noindex_pages_are_not_sent():
    assert indexnow.files_to_urls(["privacy.html"]) == []


def test_payload():
    body = indexnow.payload("abc", ["https://pikobit.it/"])
    assert body == {
        "host": "pikobit.it",
        "key": "abc",
        "keyLocation": "https://pikobit.it/abc.txt",
        "urlList": ["https://pikobit.it/"],
    }


def test_dry_run_sends_nothing(capsys):
    sent = []
    code = indexnow.main(["index.html"], sender=lambda body: sent.append(body) or 200)
    assert code == 0 and sent == []
    assert "https://pikobit.it/" in capsys.readouterr().out


def test_send(capsys):
    sent = []
    code = indexnow.main(["--invia", "index.html"], sender=lambda body: sent.append(body) or 202)
    assert code == 0
    assert json.loads(json.dumps(sent[0]))["urlList"] == ["https://pikobit.it/"]


def test_send_failure_exit_1():
    assert indexnow.main(["--invia", "index.html"], sender=lambda body: 403) == 1


def test_nothing_to_send():
    assert indexnow.main(["--invia", "styles/style.css"], sender=lambda body: 1 / 0) == 0


def test_dal_without_ref_exit_2(capsys):
    assert indexnow.main(["--dal"]) == 2
    assert "--dal" in capsys.readouterr().err


def test_dal_with_unknown_ref_exit_2(capsys):
    assert indexnow.main(["--dal", "non-esiste-questo-ref"]) == 2
    assert "non-esiste-questo-ref" in capsys.readouterr().err
