"""Tests for scripts/sitemap_lastmod.py: lastmod = last commit that changed the CONTENT."""
import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "sitemap_lastmod.py"
spec = importlib.util.spec_from_file_location("sitemap_lastmod", SCRIPT)
sitemap_lastmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sitemap_lastmod)

TODAY = "2026-09-29"


def page(title, text, version="1"):
    return (
        f'<html><head><title>{title}</title>'
        f'<link rel="stylesheet" href="style.css?v={version}" /></head>'
        f"<body><header>menu</header><main><p>{text}</p></main></body></html>"
    )


def git(repo, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{date}T12:00:00"
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)


def commit(repo, files, date):
    for name, content in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", date, date=date)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    commit(tmp_path, {"a.html": page("A", "uno"), "index.html": page("Home", "ciao")}, "2024-12-29")
    commit(tmp_path, {"a.html": page("A", "uno due")}, "2026-09-10")
    # Head-only / cache-busting change: must NOT move lastmod.
    commit(tmp_path, {"a.html": page("A", "uno due", version="2")}, "2026-09-26")
    return tmp_path


def test_loc_to_path():
    assert sitemap_lastmod.loc_to_path("https://pikobit.it/") == "index.html"
    assert sitemap_lastmod.loc_to_path("https://pikobit.it/a.html") == "a.html"
    assert sitemap_lastmod.loc_to_path("https://pikobit.it/crucidev/privacy/") == "crucidev/privacy/index.html"


def test_head_only_commit_does_not_move_lastmod(repo):
    assert sitemap_lastmod.last_content_date(repo, "a.html", TODAY) == "2026-09-10"


def test_file_never_changed_keeps_its_first_commit(repo):
    assert sitemap_lastmod.last_content_date(repo, "index.html", TODAY) == "2024-12-29"


def test_markup_only_change_is_not_content(repo):
    wrapped = page("A", "uno due", version="2").replace("<p>uno due</p>", "<div><p>uno</p> <p>due</p></div>")
    commit(repo, {"a.html": wrapped}, "2026-09-28")
    assert sitemap_lastmod.last_content_date(repo, "a.html", TODAY) == "2026-09-10"


def test_title_change_counts_as_content(repo):
    commit(repo, {"a.html": page("A nuovo", "uno due", version="2")}, "2026-09-27")
    assert sitemap_lastmod.last_content_date(repo, "a.html", TODAY) == "2026-09-27"


def test_uncommitted_content_change_is_today(repo):
    (repo / "a.html").write_text(page("A", "uno due tre"), encoding="utf-8")
    assert sitemap_lastmod.last_content_date(repo, "a.html", TODAY) == TODAY


def test_uncommitted_head_only_change_keeps_date(repo):
    (repo / "a.html").write_text(page("A", "uno due", version="3"), encoding="utf-8")
    assert sitemap_lastmod.last_content_date(repo, "a.html", TODAY) == "2026-09-10"


def test_untracked_file_is_today(repo):
    (repo / "nuovo.html").write_text(page("N", "x"), encoding="utf-8")
    assert sitemap_lastmod.last_content_date(repo, "nuovo.html", TODAY) == TODAY


def test_update_sitemap_only_touches_lastmod():
    xml = (
        "<urlset>\n    <url>\n        <loc>https://pikobit.it/a.html</loc>\n"
        "        <lastmod>2024-12-29</lastmod>\n        <priority>0.8</priority>\n    </url>\n"
        "     <url>\n        <loc>https://pikobit.it/b.html</loc>\n"
        "        <lastmod>2025-01-01</lastmod>\n    </url>\n</urlset>\n"
    )
    out = sitemap_lastmod.update_sitemap(xml, {"https://pikobit.it/a.html": "2026-09-10"})
    assert out == xml.replace("2024-12-29", "2026-09-10")


def test_refuses_shallow_clone(repo, tmp_path_factory):
    shallow = tmp_path_factory.mktemp("shallow") / "clone"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)], check=True)
    (shallow / "sitemap.xml").write_text("<urlset></urlset>", encoding="utf-8")
    assert sitemap_lastmod.main(["--repo", str(shallow)]) == 2


CTA = ('<!-- pikobit-local-cta -->\n<section class="why-pikobit local-cta">\n'
       '<h2>Ti serve un sito?</h2><p>Sono Giuseppe.</p></section>')


def test_standard_cta_block_is_not_content(tmp_path):
    git(tmp_path, "init", "-q")
    commit(tmp_path, {"b.html": page("B", "articolo")}, "2026-07-28")
    commit(tmp_path, {"b.html": page("B", "articolo").replace("</main>", CTA + "</main>")}, "2026-09-26")
    assert sitemap_lastmod.last_content_date(tmp_path, "b.html", TODAY) == "2026-07-28"


def test_last_content_change_tells_when_text_never_changed(repo):
    assert sitemap_lastmod.last_content_change(repo, "index.html", TODAY) == ("2024-12-29", True)
    assert sitemap_lastmod.last_content_change(repo, "a.html", TODAY) == ("2026-09-10", False)


def test_case_only_change_is_not_content():
    # "PikoBit" -> "Pikobit" in a title is a spelling fix, not new content.
    assert sitemap_lastmod.signature(page("Blog PikoBit", "x")) == sitemap_lastmod.signature(page("Blog Pikobit", "x"))
