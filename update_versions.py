import os
import re
#COMANDO PER AGGIORNARE LE VERSONI E python3 update_versions.py

# Directory dei file HTML
html_directory = "./"  # Cambia il percorso se necessario

# Nuova versione da aggiungere
new_version = "4.0.0.5"  # Aggiorna la versione qui

# Funzione per aggiornare CSS e JS
def update_version_in_html(file_path, new_version):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        print(f"Contenuto originale di {file_path}:\n{content}\n{'-'*40}")

    # Aggiorna il riferimento al CSS
    content = re.sub(
        r'(<link rel="stylesheet" href="\.\/styles/style\.css)(\?v=\d+\.\d+\.\d+\.\d+)?"',
        rf'\1?v={new_version}"',
        content
    )

    # Aggiorna il riferimento al JS
    content = re.sub(
        r'(<script src="\/scripts/script\.js)(\?v=\d+\.\d+\.\d+\.\d+)?"',
        rf'\1?v={new_version}"',
        content
    )

    print(f"Contenuto aggiornato di {file_path}:\n{content}\n{'-'*40}")

    # Scrivi le modifiche nel file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Modifiche scritte su {file_path}")

# Scansiona tutti i file HTML nella directory
for filename in os.listdir(html_directory):
    if filename.endswith(".html"):
        file_path = os.path.join(html_directory, filename)
        print(f"Aggiornamento versioni in: {file_path}")
        update_version_in_html(file_path, new_version)

print("Aggiornamento completato!")
