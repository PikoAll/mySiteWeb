"""Tests for scripts/check_page_weight.py: per-page weight budget."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cpw", ROOT / "scripts" / "check_page_weight.py")
cpw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpw)

PAGE = ('<html><head><link rel="stylesheet" href="s.css"></head><body>'
        '<img src="img/a.png"><script src="/j.js"></script>'
        '<img src="https://example.com/x.png"></body></html>')


def make_site(root):
    root.mkdir(parents=True, exist_ok=True)
    (root / "img").mkdir(exist_ok=True)
    (root / "index.html").write_text(PAGE)
    (root / "s.css").write_text("@font-face{src:url(f.woff2)}")
    (root / "f.woff2").write_bytes(b"f" * 100)
    (root / "img" / "a.png").write_bytes(b"a" * 1000)
    (root / "j.js").write_bytes(b"j" * 200)
    return len(PAGE) + len("@font-face{src:url(f.woff2)}") + 100 + 1000 + 200


def test_weight_sums_local_resources_only(tmp_path):
    expected = make_site(tmp_path)
    assert cpw.page_weight(tmp_path, tmp_path / "index.html") == expected


def test_page_under_budget_passes(tmp_path):
    expected = make_site(tmp_path)
    assert cpw.over_budget(tmp_path, expected) == []


def test_page_over_budget_is_reported(tmp_path):
    expected = make_site(tmp_path)
    over = cpw.over_budget(tmp_path, expected - 1)
    assert [(p.name, w) for p, w in over] == [("index.html", expected)]


def test_cli_exit_codes(tmp_path):
    expected = make_site(tmp_path / "site")
    budget = tmp_path / "b.json"
    script = str(ROOT / "scripts" / "check_page_weight.py")
    budget.write_text(json.dumps({"max_page_bytes": expected}))
    ok = subprocess.run([sys.executable, script, "--root", str(tmp_path / "site"), "--budget", str(budget)],
                        capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout
    budget.write_text(json.dumps({"max_page_bytes": expected - 1}))
    ko = subprocess.run([sys.executable, script, "--root", str(tmp_path / "site"), "--budget", str(budget)],
                        capture_output=True, text=True)
    assert ko.returncode == 1
    assert "index.html" in ko.stdout


def test_built_site_is_within_budget(tmp_path):
    out = tmp_path / "_site"
    build = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out", str(out)],
                           capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_page_weight.py"), "--root", str(out)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout


def test_new_tools_are_not_published(tmp_path):
    out = tmp_path / "_site"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out", str(out)],
                   capture_output=True, text=True, check=True)
    assert not (out / "scripts" / "check_page_weight.py").exists()
    assert not (out / "scripts" / "page_weight_budget.json").exists()
