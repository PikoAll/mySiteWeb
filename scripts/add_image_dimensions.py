import os
import re

# COMANDO: python3 scripts/add_image_dimensions.py
# Aggiunge width/height nativi agli <img> del sito per riservare lo spazio
# (aspect-ratio) e ridurre il CLS. Il CSS continua a scalare le immagini
# (width:100% o width fisso in px), width/height HTML non forzano le
# dimensioni visive. Idempotente: se un tag ha gia' width, viene saltato.
#
# Per aggiungere una nuova immagine in futuro basta aggiungere una voce
# a IMAGES con la classe CSS usata nell'<img> e le dimensioni native.

ROOT_DIR = "."
BLOG_DIR = "blog"

IMAGES = {
    "banner": {"width": "1024", "height": "587"},
    "logo": {"width": "671", "height": "752"},
}

TAG_RE = re.compile(r'<img[^<>]*class="(banner|logo)"[^<>]*>')


def add_dimensions(content):
    def replace(match):
        tag = match.group(0)
        css_class = match.group(1)
        if "width=" in tag:
            return tag
        dims = IMAGES[css_class]
        attrs = f' width="{dims["width"]}" height="{dims["height"]}"'
        if tag.rstrip().endswith("/>"):
            insert_at = tag.rfind("/>")
            return tag[:insert_at].rstrip() + attrs + " " + tag[insert_at:]
        insert_at = tag.rfind(">")
        return tag[:insert_at].rstrip() + attrs + tag[insert_at:]

    return TAG_RE.sub(replace, content)


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = add_dimensions(content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"OK   {path}")
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
