"""Tests for scripts/verify_jsonld.py: syntax, schema sanity, @id coherence."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("verify_jsonld", ROOT / "scripts" / "verify_jsonld.py")
verify_jsonld = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_jsonld)


def page(tmp_path, name, jsonld):
    path = tmp_path / name
    path.write_text(f'<head><script type="application/ld+json">{jsonld}</script></head>', encoding="utf-8")
    return str(path)


def test_valid_graph(tmp_path):
    p = page(tmp_path, "a.html", '{"@graph": [{"@type": "WebPage", "@id": "x", "name": "A"}]}')
    assert verify_jsonld.check(p, {}) is None


def test_raw_newline_in_string_is_invalid(tmp_path):
    p = page(tmp_path, "a.html", '{"@type": "WebPage", "name": "A\nB"}')
    assert "invalid JSON" in verify_jsonld.check(p, {})


def test_node_without_type(tmp_path):
    p = page(tmp_path, "a.html", '{"@graph": [{"name": "A"}]}')
    assert "@type" in verify_jsonld.check(p, {})


def test_breadcrumb_positions(tmp_path):
    p = page(tmp_path, "a.html", '{"@type": "BreadcrumbList", "itemListElement": ['
             '{"position": 1, "name": "Home", "item": "/"}, {"position": 3, "name": "B", "item": "/b"}]}')
    assert "positions" in verify_jsonld.check(p, {})


def test_same_id_with_different_data_across_pages(tmp_path):
    ids = {}
    a = page(tmp_path, "a.html", '{"@type": "Organization", "@id": "#biz", "name": "A"}')
    b = page(tmp_path, "b.html", '{"@type": "Organization", "@id": "#biz", "name": "B"}')
    c = page(tmp_path, "c.html", '{"@type": "WebPage", "about": {"@id": "#biz"}}')
    assert verify_jsonld.check(a, ids) is None
    assert verify_jsonld.check(c, ids) is None  # a bare reference is not data
    assert "#biz" in verify_jsonld.check(b, ids)


def test_whole_site_passes():
    assert verify_jsonld.main(["verify_jsonld.py"]) == 0
    expected = len(list(ROOT.glob("*.html"))) + len(list((ROOT / "blog").glob("*.html"))) + 1
    assert len(verify_jsonld.repo_pages()) == expected  # + crucidev/privacy
