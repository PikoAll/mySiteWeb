"""Tests for scripts/check_external_links.py (local server, no real network)."""
import importlib.util
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_external_links.py"
spec = importlib.util.spec_from_file_location("check_external_links", SCRIPT)
cel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cel)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/robots.txt":
            body, code = b"User-agent: *\nDisallow: /private\n", 200
        elif self.path == "/ok":
            body, code = b"ok", 200
        elif self.path == "/private":
            body, code = b"secret", 200
        else:
            body, code = b"nope", 404
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_HEAD = do_GET

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def make_site(root, base):
    (root / "blog").mkdir()
    (root / "index.html").write_text(
        f'<a href="{base}/ok">buono</a> <a href="{base}/gone">rotto</a>'
        f' <a href="{base}/private">vietato</a> <a href="about.html">interno</a>'
        ' <a href="mailto:a@b.c">m</a>'
    )
    (root / "blog" / "a.html").write_text(f'<a href="{base}/blog-only">x</a>')


def test_external_links_only_fixed_pages_and_http(tmp_path, server):
    make_site(tmp_path, server)
    links = cel.external_links(tmp_path)
    assert sorted(url for _, url in links) == sorted(
        [f"{server}/ok", f"{server}/gone", f"{server}/private"]
    )


def test_check_reports_status_and_respects_robots(tmp_path, server):
    make_site(tmp_path, server)
    results = {url: status for _, url, status in cel.check_all(cel.external_links(tmp_path), timeout=3)}
    assert results[f"{server}/ok"] == 200
    assert results[f"{server}/gone"] == 404
    assert results[f"{server}/private"] == "robots"


def test_unreachable_host_is_an_error_status(server):
    status = cel.check_url("http://127.0.0.1:1/x", timeout=2)
    assert isinstance(status, str) and status.startswith("errore")


def test_main_writes_report_and_exits_zero_even_with_broken(tmp_path, server):
    make_site(tmp_path, server)
    report = tmp_path / "rapporto.txt"
    code = cel.main(["--root", str(tmp_path), "--report", str(report), "--timeout", "3"])
    assert code == 0
    text = report.read_text()
    assert f"404 {server}/gone" in text
    assert "ROTTO" in text


def test_strict_exits_one_with_broken(tmp_path, server):
    make_site(tmp_path, server)
    assert cel.main(["--root", str(tmp_path), "--timeout", "3", "--strict"]) == 1


def test_real_page_lists_external_links_locally():
    links = cel.external_links(ROOT)
    assert links
    assert all(url.startswith(("http://", "https://")) for _, url in links)
    assert not any(page.parts[0] == "blog" for page, _ in links)
