import re
import glob
from urllib.parse import unquote

pattern = re.compile(
    r'https://www\.google\.com/url\?q=([^\s"]+?)&(?:amp;)?source=gmail[^\s"]*'
)

files = [
    "blog/2026-07-28-mcp-specifica-stateless.html",
    "blog/2026-07-28-multa-lusha-vendita-dati-personali.html",
    "blog/2026-07-28-passkey-spiegate-semplice.html",
    "blog/2026-07-28-phishing-finto-portale-automobilista.html",
]

for path in files:
    with open(path, encoding="utf-8", newline="") as f:
        content = f.read()

    def repl(m):
        return unquote(m.group(1))

    new_content, n = pattern.subn(repl, content)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new_content)
    print(f"{path}: {n} link corretti")
