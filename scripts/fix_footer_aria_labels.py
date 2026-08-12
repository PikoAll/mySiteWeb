import os
import re

# COMANDO: python3 scripts/fix_footer_aria_labels.py
# Fix Lighthouse "Navigazione agentica" > "Links must have discernible text":
# i 3 link icona social nel footer (YouTube, LinkedIn, Instagram) contengono
# solo un <svg aria-hidden="true">, quindi il link non ha nome accessibile.
# Aggiunge aria-label sull'<a> corrispondente.
#
# Nota: youtube.com/@pikobit01 compare anche altrove (JSON-LD "sameAs" e un
# link testuale "YouTube" in una lista contatti) - quei casi vanno IGNORATI,
# tocchiamo solo l'<a> immediatamente seguito da "<svg" (l'icona del footer).
# Idempotente: se l'aria-label e' gia' presente sul link, il file/link viene
# saltato.

ROOT_DIR = "."
BLOG_DIR = "blog"

# (href target url, aria-label, chiave di verifica idempotenza)
SOCIAL_LINKS = [
    (r"https://www\.youtube\.com/@pikobit01", "YouTube"),
    (r"https://www\.linkedin\.com/in/giuseppe-alaimo-aba40b226", "LinkedIn"),
    (r"https://www\.instagram\.com/pikobit_it/?", "Instagram"),
]


def build_pattern(url_re):
    # Cattura l'apertura del tag <a ... href="URL" ...> fino al primo '>'
    # che deve essere seguito immediatamente da '<svg' (icona del footer,
    # non i link testuali con lo stesso href presenti altrove nella pagina).
    return re.compile(
        r'(<a\s+href="\s*' + url_re + r'\s*"[\s\S]*?)>(?=<svg)',
        re.MULTILINE,
    )


def add_footer_aria_labels(content):
    changed = 0
    for url_re, label in SOCIAL_LINKS:
        pattern = build_pattern(url_re)

        def repl(m, label=label):
            nonlocal changed
            if f'aria-label="{label}"' in m.group(1):
                return m.group(0)
            changed += 1
            return f'{m.group(1)} aria-label="{label}">'

        content = pattern.sub(repl, content)
    return content, changed


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content, changed = add_footer_aria_labels(content)
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"OK   {path} ({changed} aria-label aggiunti)")
    else:
        print(f"skip {path} (nessuna modifica)")


def main():
    html_files = sorted(f for f in os.listdir(ROOT_DIR) if f.endswith(".html"))
    html_files += sorted(
        os.path.join(BLOG_DIR, f) for f in os.listdir(BLOG_DIR) if f.endswith(".html")
    )
    for path in html_files:
        process_file(path)
    print("Completato.")


if __name__ == "__main__":
    main()
