#!/usr/bin/env python3
"""Sostituisce il blocco Google Fonts (preconnect + css2?family=Poppins) con
un preload del woff2 di Poppins servito dal sito stesso.

Uso: python3 scripts/remove_google_fonts.py [--dry-run]

Il file styles/style.css contiene gia' le regole @font-face (pesi 400 e 600,
font-display: swap) che puntano a fonts/poppins/*.woff2, quindi qui basta
aggiungere il preload del peso 400 (quello usato per il body/testo, il piu'
determinante per il rendering iniziale) e togliere le richieste a
fonts.googleapis.com / fonts.gstatic.com.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Blocco da rimuovere: due preconnect + il link css2?family=Poppins (su una
# riga sola o spezzato su piu' righe, con o senza self-closing slash: le
# pagine del sito non sono tutte scritte allo stesso modo).
BLOCK_RE = re.compile(
    r'<link rel="preconnect" href="https://fonts\.googleapis\.com"[^>]*>\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\s*'
    r'<link\s+href="\s*https://fonts\.googleapis\.com/css2\?family=Poppins[^"]*"'
    r'\s*rel="stylesheet"\s*/?>',
)


def relative_prefix(html_path: Path) -> str:
    """Prefisso relativo da <file>.html verso la radice del sito."""
    depth = len(html_path.relative_to(ROOT).parent.parts)
    return "../" * depth


def build_replacement(indent: str, prefix: str) -> str:
    href = f"{prefix}fonts/poppins/poppins-latin-400-normal.woff2"
    return (
        f'{indent}<link\n'
        f'{indent}  rel="preload"\n'
        f'{indent}  href="{href}"\n'
        f'{indent}  as="font"\n'
        f'{indent}  type="font/woff2"\n'
        f'{indent}  crossorigin\n'
        f'{indent}/>'
    )


def process(html_path: Path, dry_run: bool) -> bool:
    text = html_path.read_text(encoding="utf-8")
    match = BLOCK_RE.search(text)
    if not match:
        return False

    # Indentazione presa dalla riga del primo preconnect trovato.
    line_start = text.rfind("\n", 0, match.start()) + 1
    indent = text[line_start:match.start()]

    prefix = relative_prefix(html_path)
    replacement = build_replacement(indent, prefix)

    new_text = text[:line_start] + replacement + text[match.end():]

    # Deve restare esattamente un preload di Poppins e zero riferimenti a
    # Google Fonts, altrimenti non si scrive nulla (fail-closed).
    if "fonts.googleapis.com" in new_text or "fonts.gstatic.com" in new_text:
        raise RuntimeError(f"{html_path}: riferimento a Google Fonts residuo dopo la sostituzione")
    if new_text.count('rel="preload"') != 1:
        raise RuntimeError(f"{html_path}: preload inatteso ({new_text.count('rel=\"preload\"')})")

    if not dry_run:
        html_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    html_files = sorted(ROOT.rglob("*.html"))
    changed = []
    skipped_no_match = []
    for f in html_files:
        if process(f, dry_run):
            changed.append(f)
    print(f"File modificati: {len(changed)}")
    for f in changed:
        print(f"  {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
