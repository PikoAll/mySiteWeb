# Pikobit — Sito statico su GitHub Pages

Sito web statico (HTML, CSS, JavaScript vanilla): nessun build tool, nessun backend, nessun server da gestire. Pubblicato su **GitHub Pages** con dominio custom **[pikobit.it](https://pikobit.it)**.

---

## Come aggiornare il sito

1. Modifica i file HTML/CSS/JS in locale.
2. Testa in locale prima di pubblicare:
   ```bash
   python3 -m http.server 8000
   ```
   Apri [http://localhost:8000](http://localhost:8000) e controlla le pagine modificate.
3. Committa e pusha su `main`:
   ```bash
   git add .
   git commit -m "descrizione della modifica"
   git push
   ```
4. Il push su `main` fa partire **in automatico** il workflow GitHub Actions definito in [`.github/workflows/static.yml`](.github/workflows/static.yml), che pubblica il sito su https://pikobit.it/. Ci mette circa **1 minuto**: nessuna azione manuale, nessun SSH, nessun server da riavviare.
5. Per verificare lo stato del deploy: tab **Actions** del repo su GitHub.

Non serve altro: non c'è una VPS da raggiungere via SSH, non ci sono permessi di file da sistemare, non c'è Nginx da ricaricare.

---

## Dominio e DNS

Il dominio `pikobit.it` è registrato/gestito su OVH, con il DNS configurato per puntare a GitHub Pages:

- 4 record **A** sulla root (`pikobit.it`) verso gli IP di GitHub Pages:
  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`
- 1 record **CNAME** per `www` verso `pikoall.github.io`

HTTPS è gestito automaticamente da GitHub Pages (certificato Let's Encrypt, rinnovo automatico) — non c'è certbot da configurare o rinnovare manualmente.

---

## Storia

In precedenza il sito girava su una VPS OVH con Nginx e certificati gestiti via certbot, con deploy manuale (SSH, `git pull`, `chown`/`chmod`, reload di Nginx a ogni modifica). Il sito è stato migrato a GitHub Pages per eliminare la gestione del server e automatizzare il deploy. I file della vecchia configurazione sulla VPS sono stati rinominati in `.backup` e non sono più serviti.
