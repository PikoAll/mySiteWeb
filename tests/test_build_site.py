"""Tests for scripts/build_site.py: only the public site goes online."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)
spec = importlib.util.spec_from_file_location("cil", ROOT / "scripts" / "check_internal_links.py")
cil = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cil)


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("build") / "_site"
    build_site.build(ROOT, out)
    return out


def files(root):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def test_nothing_private_goes_online(site):
    for f in files(site):
        parts = Path(f).parts
        assert not {"docs", "tests", ".github", "__pycache__", "node_modules", "_site"} & set(parts), f
        assert not f.startswith("images/_archivio/"), f
        assert not parts[-1].startswith("."), f
        assert Path(f).suffix not in {".py", ".pyc", ".mjs", ".md"}, f
        assert ".backup" not in f, f
        assert parts[-1] not in {"package.json", "package-lock.json"}, f


def test_the_whole_public_site_is_there(site):
    got = files(site)
    pages = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*.html")
             if not {"tests", "node_modules", "_site", ".git"} & set(p.relative_to(ROOT).parts)}
    assert pages <= got
    assert "crucidev/privacy/index.html" in got
    for f in ["robots.txt", "sitemap.xml", "site.webmanifest", "favicon.ico", "apple-touch-icon.png",
              "styles/style.css", "styles/fx.css", "scripts/script.js", "scripts/consent.js",
              "scripts/fx/core.js", "scripts/fx/puglia.js", "images/icons.svg",
              "fonts/poppins/poppins-latin-400-normal.woff2"]:
        assert f in got, f


def test_indexnow_key_is_published(site):
    keys = [f for f in files(site) if len(f) == 36 and f.endswith(".txt")]
    assert len(keys) == 1
    assert (site / keys[0]).read_text().strip() == keys[0][:-4]


def test_no_broken_reference_in_the_built_site(site):
    assert cil.broken_links(site) == []
    assert cil.broken_assets(site) == []
    assert cil.missing_sitemap_targets(site) == []


def test_retired_images_are_not_used_by_any_page():
    for page in ROOT.rglob("*.html"):
        if "tests" in page.parts or "node_modules" in page.parts or "_site" in page.parts:
            continue
        assert "_archivio" not in page.read_text(encoding="utf-8"), page


def test_old_build_is_moved_away_not_deleted(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    out = tmp_path / "_site"
    out.mkdir()
    (out / "stale.html").write_text("old")
    build_site.build(ROOT, out)
    assert not (out / "stale.html").exists()
    kept = list((tmp_path / "home" / ".local/state/residui-tmp").rglob("stale.html"))
    assert len(kept) == 1


def test_cli(tmp_path):
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out", str(tmp_path / "o")],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert (tmp_path / "o" / "index.html").is_file()
