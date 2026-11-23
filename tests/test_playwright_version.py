"""La versione di @playwright/test negli e2e deve essere almeno 1.65."""
import json
import re
from pathlib import Path

PKG = Path(__file__).parent / "e2e" / "package.json"


def test_playwright_almeno_1_65():
    spec = json.loads(PKG.read_text())["devDependencies"]["@playwright/test"]
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", spec)
    assert m, spec
    assert (int(m.group(1)), int(m.group(2))) >= (1, 65), spec
