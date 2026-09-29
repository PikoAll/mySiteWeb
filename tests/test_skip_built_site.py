"""No page-scanning script may touch _site/ (the built copy published by
scripts/build_site.py): editing it is useless, checking it doubles the pages."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def tree(tmp_path):
    for rel in ["index.html", "blog/a.html", "_site/index.html", "_site/blog/a.html"]:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("<html><head></head><body></body></html>")
    return tmp_path


def rels(paths, root):
    return sorted(str(Path(p).relative_to(root)) for p in paths)


@pytest.mark.parametrize("name, call", [
    ("check_internal_links", lambda m, root: m.pages(root)),
    ("site_chrome", lambda m, root: m.default_targets(root)),
    ("add_footer_nap", lambda m, root: m.default_targets(root)),
])
def test_rooted_scanners_skip_site(tree, name, call):
    assert rels(call(load(name), tree), tree) == ["blog/a.html", "index.html"]


@pytest.mark.parametrize("name", ["brand_head", "perf_hints", "remove_google_fonts"])
def test_root_constant_scanners_skip_site(tree, monkeypatch, name):
    mod = load(name)
    monkeypatch.setattr(mod, "ROOT", tree)
    assert rels(mod.pages(), tree) == ["blog/a.html", "index.html"]
