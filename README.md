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

## Dati strutturati e meta SEO (anche per la pipeline del venerdì)

Cosa c'è nel sito per Google e perché (parole chiave per pagina, regole di title e description, dati strutturati, divieti, storico delle decisioni): [docs/SEO.md](docs/SEO.md).

Il JSON-LD e i meta SEO dell'`<head>` non si scrivono a mano: li mette [`scripts/seo_head.py`](scripts/seo_head.py), idempotente (rilanciato = zero differenze). Un'unica entità `ProfessionalService` (`https://pikobit.it/#business`) e un'unica `Person` (`#giuseppe`), identiche byte per byte su tutte le pagine; ogni articolo ha `BlogPosting` con `dateModified`, breadcrumb e `article:*_time`. `crucidev/privacy/` resta fuori (è la policy di un'app).

Dopo che l'agente ha scritto gli articoli nuovi, **prima del push**:

```bash
python3 scripts/brand_head.py blog/NUOVO-ARTICOLO.html # favicon, og:image, logo del brand nuovo
python3 scripts/seo_head.py blog/NUOVO-ARTICOLO.html   # uno o più file
python3 scripts/seo_head.py --verifica                 # exit 1 = pagina non conforme (anche immagini vecchie o mancanti), niente push
python3 scripts/verify_jsonld.py                       # JSON valido, stessa @id = stessi dati
```

Dopo il push (facoltativo, lo lancia Giuseppe): avvisare Bing/Yandex via IndexNow. Senza `--invia` mostra solo l'anteprima.

```bash
python3 scripts/indexnow_ping.py --invia blog/NUOVO-ARTICOLO.html
```

La chiave IndexNow è il file `<chiave>.txt` in radice: è pubblica per costruzione, non è un segreto. Google non usa IndexNow: per Google vale il `lastmod` della sitemap.

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
