"""Tests for scripts/check_internal_links.py."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_internal_links.py"
spec = importlib.util.spec_from_file_location("check_internal_links", SCRIPT)
cil = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cil)


def make_site(root):
    (root / "blog").mkdir()
    (root / "sub").mkdir()
    (root / "sub" / "index.html").write_text("<p>ok</p>")
    (root / "a.png").write_bytes(b"")
    (root / "index.html").write_text(
        '<a href="blog/x.html#top">x</a> <img src="a.png?v=1"> <a href="sub/">s</a>'
        ' <a href="https://example.com/missing.html">ext</a> <a href="mailto:a@b.c">m</a>'
        ' <a href="tel:+39">t</a> <a href="#frag">f</a>'
    )
    (root / "blog" / "x.html").write_text('<a href="../index.html">home</a>')


def test_valid_site_has_no_broken_links(tmp_path):
    make_site(tmp_path)
    assert cil.broken_links(tmp_path) == []


def test_reports_missing_target(tmp_path):
    make_site(tmp_path)
    (tmp_path / "blog" / "x.html").write_text('<a href="../nope.html">x</a>')
    broken = cil.broken_links(tmp_path)
    assert [(src.name, href) for src, href in broken] == [("x.html", "../nope.html")]


def test_sitemap_locs_must_exist(tmp_path):
    make_site(tmp_path)
    (tmp_path / "sitemap.xml").write_text(
        "<urlset><url><loc>https://pikobit.it/</loc></url>"
        "<url><loc>https://pikobit.it/sub/</loc></url>"
        "<url><loc>https://pikobit.it/gone.html</loc></url></urlset>"
    )
    assert cil.missing_sitemap_targets(tmp_path, "https://pikobit.it/") == ["https://pikobit.it/gone.html"]


# --- assets referenced outside the HTML (css url(), manifest, fx scenes) ----

def test_css_url_must_exist(tmp_path):
    (tmp_path / "styles").mkdir()
    (tmp_path / "fonts").mkdir()
    (tmp_path / "fonts" / "a.woff2").write_bytes(b"")
    (tmp_path / "styles" / "s.css").write_text(
        '@font-face{src:url("../fonts/a.woff2")} .x{background:url(../img/no.svg)} .y{background:url(data:x)}')
    assert [str(t) for _, t in cil.broken_assets(tmp_path)] == ["../img/no.svg"]


def test_manifest_icons_must_exist(tmp_path):
    (tmp_path / "i.png").write_bytes(b"")
    (tmp_path / "site.webmanifest").write_text('{"icons": [{"src": "/i.png"}, {"src": "/gone.png"}]}')
    assert [t for _, t in cil.broken_assets(tmp_path)] == ["/gone.png"]


def test_fx_scene_needs_its_script_core_and_css(tmp_path):
    (tmp_path / "scripts" / "fx").mkdir(parents=True)
    (tmp_path / "styles").mkdir()
    (tmp_path / "scripts" / "fx" / "core.js").write_text("")
    (tmp_path / "scripts" / "fx" / "web.js").write_text("")
    (tmp_path / "index.html").write_text('<div data-fx="web"></div><div data-fx="qr"></div>')
    assert sorted(t for _, t in cil.broken_assets(tmp_path)) == ["scripts/fx/qr.js", "styles/fx.css"]


def test_root_argument(tmp_path, capsys):
    make_site(tmp_path)
    assert cil.main(["--root", str(tmp_path)]) == 0
    (tmp_path / "blog" / "x.html").write_text('<a href="../nope.html">x</a>')
    assert cil.main(["--root", str(tmp_path)]) == 1
