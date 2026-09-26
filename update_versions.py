import os
import re
#COMANDO PER AGGIORNARE LE VERSONI E python3 update_versions.py

# Directory dei file HTML
html_directory = "./"  # Cambia il percorso se necessario

# Nuova versione da aggiungere
new_version = "4.0.0.10"  # Aggiorna la versione qui

# Funzione per aggiornare CSS e JS
def update_version_in_html(file_path, new_version):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Aggiorna il riferimento a CSS e JS, a qualsiasi profondità
    # (./styles, ../styles, ../../scripts) e con o senza "defer"
    content = re.sub(
        r'((?:styles/style\.css|scripts/script\.js))(\?v=\d+\.\d+\.\d+\.\d+)?"',
        rf'\1?v={new_version}"',
        content
    )

    # Scrivi le modifiche nel file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Modifiche scritte su {file_path}")

# Scansiona tutti i file HTML, sottocartelle incluse (blog/, crucidev/)
for root, _dirs, files in os.walk(html_directory):
    if "/." in root:  # .git, .venv, ...
        continue
    for filename in files:
        if filename.endswith(".html"):
            file_path = os.path.join(root, filename)
            print(f"Aggiornamento versioni in: {file_path}")
            update_version_in_html(file_path, new_version)

print("Aggiornamento completato!")
