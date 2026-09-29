# SEO di pikobit.it: cosa c'è e perché

Questo documento spiega, in parole semplici, cosa c'è nel sito per farsi
trovare su Google e perché è fatto così. Quasi tutto lo mettono gli script:
a mano si scrivono solo i testi.

**In breve**

- Ogni pagina ha **una sola parola chiave principale**, così le pagine non si
  rubano le posizioni a vicenda (tabella qui sotto).
- Title al massimo **60 caratteri** e finisce con **" | Pikobit"**; description
  al massimo **155 caratteri**.
- I **dati strutturati** (JSON-LD) descrivono un'unica attività, Pikobit, e
  un'unica persona, Giuseppe: identici su tutte le pagine.
- Le **date** (sitemap e articoli) cambiano solo quando cambia il testo vero.
- Prima di ogni pubblicazione: `python3 scripts/seo_head.py --verifica` deve
  dire 0 pagine non conformi.

---

## 1. Una pagina, una parola chiave

Se due pagine puntano alla stessa ricerca, Google ne sceglie una e l'altra
sparisce (si chiama *cannibalizzazione*). Per questo ogni pagina ha il suo
bersaglio:

| Pagina | Parola chiave principale | Dove sta la parola esatta |
|---|---|---|
| Home (`index.html`) | programmatore e web designer a Monopoli | title, testo |
| `programmatore-monopoli.html` | realizzazione / creazione siti web a Monopoli | title, h1 |
| `websites.html` | realizzazione e creazione siti web **in Puglia** | title, h1 |
| `custom-software.html` | sviluppo software e gestionali su misura **in Puglia** | title, h1 |
| `modern-apps.html` | sviluppatore app e applicazioni web **in Puglia** | title, h1 |
| `programmatore-<città>.html` (13 città, Turi compresa) | programmatore e web designer a *città* | title, h1 |

Regole che ne derivano:

- La pagina Monopoli **non** usa "programmatore" o "web designer" nell'h1:
  quelle parole, per Monopoli, sono della home.
- Le pagine servizio dicono "in Puglia", mai "a Monopoli e in Puglia", così
  non competono con la pagina Monopoli.
- Chi linka la pagina Monopoli usa il testo "Siti web a Monopoli"; chi vuole
  dire "programmatore a Monopoli" linka la home.
- La frase chiave esatta sta in **title, h1 e al massimo un h2**. Nel testo si
  scrive in italiano normale ("quando creo un sito", non "nella creazione siti
  web"): Google capisce i sinonimi, i lettori odiano le frasi forzate.
- Le pagine città hanno testo diverso per davvero:
  `python3 scripts/check_page_similarity.py` deve restare basso (oggi il
  peggiore è 9,1%, il limite è 40%).

## 2. Cosa c'è nell'`<head>` di ogni pagina

| Cosa | A cosa serve | Regola |
|---|---|---|
| `<title>` | il titolo blu nei risultati di Google | ≤ 60 caratteri, finisce con " \| Pikobit" (blog: "- Blog Pikobit") |
| `meta description` | le due righe grigie sotto il titolo | ≤ 155 caratteri, parola chiave + città nei primi 120, "Preventivo gratuito" se ci sta |
| `meta robots` | dice a Google cosa può mostrare | `index, follow, max-image-preview:large, max-snippet:-1`; la privacy resta `noindex` |
| `link canonical` | l'indirizzo "ufficiale" della pagina | un URL pulito, senza spazi o a capo |
| Open Graph (`og:*`) | l'anteprima quando il link si condivide su WhatsApp, Facebook, LinkedIn | `og:description` = meta description, immagine 1200×630 del brand |
| Twitter (`twitter:*`) | la stessa anteprima per X | title e description uguali agli `og:` |
| favicon, manifest | l'icona nella scheda del browser e sul telefono | solo i file approvati del brand |

## 3. Dati strutturati (JSON-LD)

Sono un blocco di testo invisibile che descrive a Google **chi sei** in un
formato che capisce senza interpretare. Ogni pagina ne ha **uno solo**, con
dentro un elenco di "schede" (`@graph`):

- **`#business`**: l'attività Pikobit (`ProfessionalService`). Indirizzo solo
  come città (Monopoli, BA, 70043), coordinate del centro di Monopoli, orari,
  telefono, email, le 13 città servite, il catalogo servizi, il link alla
  scheda Google Maps e i profili (Google Maps, Instagram, YouTube).
- **`#giuseppe`**: la persona Giuseppe Alaimo, Software Engineer, con LinkedIn,
  Superprof e le tecnologie che usa (`knowsAbout`).
- Scheda della pagina: `WebPage`/`AboutPage`/`ContactPage`…
- **`Service`** nelle pagine servizio e città (per le città: "Realizzazione
  siti web, software e app a *città*", solo quella città).
- **`BreadcrumbList`**: il percorso Home › … › pagina, su tutte le pagine
  tranne la home.
- **`BlogPosting`** negli articoli, con `datePublished` e `dateModified` veri.

Le schede `#business` e `#giuseppe` sono **identiche byte per byte** su tutte
le pagine: Google le unisce per `@id`, e due versioni diverse della stessa
scheda sono una contraddizione. Per cambiarle si cambia **solo**
`scripts/seo_head.py` (`BUSINESS_NODE`, `PERSON_NODE`) e si rilancia lo script.

Esempio ridotto (una pagina città):

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "ProfessionalService", "@id": "https://pikobit.it/#business", "name": "Pikobit", "…": "…" },
    { "@type": "Person", "@id": "https://pikobit.it/#giuseppe", "name": "Giuseppe Alaimo", "…": "…" },
    { "@type": "WebPage", "@id": "https://pikobit.it/programmatore-bari.html",
      "about": { "@id": "https://pikobit.it/#business" },
      "breadcrumb": { "@id": "https://pikobit.it/programmatore-bari.html#breadcrumb" } },
    { "@type": "Service", "@id": "https://pikobit.it/programmatore-bari.html#service",
      "name": "Realizzazione siti web, software e app a Bari",
      "provider": { "@id": "https://pikobit.it/#business" },
      "areaServed": { "@type": "City", "name": "Bari", "addressCountry": "IT" } },
    { "@type": "BreadcrumbList", "@id": "https://pikobit.it/programmatore-bari.html#breadcrumb",
      "itemListElement": ["Home", "Dove lavoro", "Bari"] }
  ]
}
```

(Nell'esempio le briciole sono accorciate: nel sito ogni voce è un `ListItem`
con posizione, nome e URL.)

## 4. Sitemap, date e IndexNow

- **`sitemap.xml`** elenca tutte le pagine con il `lastmod`, la data
  dell'ultima modifica **del testo**. Cambiare menu, footer, `<head>` o una
  maiuscola ("PikoBit" → "Pikobit") **non** sposta la data; nemmeno il box
  "Ti serve un sito…" uguale in fondo a tutti gli articoli. Se le date si
  muovessero a ogni rilascio, Google smetterebbe di fidarsi.
- Gli articoli hanno `dateModified` = data dell'ultima modifica vera del testo;
  se il testo non è mai cambiato, è uguale a `datePublished`.
- **IndexNow** avvisa Bing e Yandex delle pagine cambiate (Google non lo usa).
  La chiave è il file `<chiave>.txt` in radice: è pubblica per costruzione.

## 5. Cosa non si fa (mai)

- **Niente testo nascosto**: niente testo dello stesso colore dello sfondo,
  fuori schermo, minuscolo o `display:none`. Google lo considera spam.
- **Niente recensioni o stelle nei dati strutturati del proprio sito**
  (`aggregateRating`, `review`): Google le ignora o penalizza. Le recensioni
  vere stanno su Google Maps.
- **Niente FAQ strutturate senza domande visibili**: `FAQPage` c'è solo su
  Monopoli, dove le domande si leggono nella pagina.
- **Niente promesse non confermate** da Giuseppe (tempi, prezzi, garanzie,
  servizi inclusi) e **niente fatti inventati** (clienti, numeri, lavori). I
  lavori citabili sono traslochimalusardi.it e Crucidev.
- **Niente parole chiave infilate** a forza nel testo.

## 6. Gli script e come lanciarli

Tutti da lanciare nella radice del repo. Sono idempotenti: rilanciati non
cambiano nulla se è già tutto a posto.

| Script | Cosa fa |
|---|---|
| `scripts/brand_head.py [FILE…]` | favicon, og:image e logo del brand nell'`<head>` |
| `scripts/seo_head.py [FILE…]` | JSON-LD, meta robots, og/twitter, canonical pulito, date degli articoli |
| `scripts/seo_head.py --verifica` | controlla le regole delle sezioni 2 e 3 (title, description, robots, og/twitter, canonical, JSON-LD, date, immagini esistenti): exit 1 se una pagina non è conforme. Le regole della sezione 5 (testo nascosto, promesse, fatti) le controlla una persona |
| `scripts/sitemap_lastmod.py` (`--check`) | aggiorna (o controlla) le date della sitemap |
| `scripts/verify_jsonld.py` | JSON-LD valido su tutte le pagine, stessa `@id` = stessi dati |
| `scripts/indexnow_ping.py FILE…` (`--invia`) | anteprima (o invio vero) a IndexNow |
| `scripts/check_page_similarity.py` | quanto si somigliano le pagine città |
| `scripts/check_internal_links.py` | nessun link interno rotto |

Giro completo prima di pubblicare:

```bash
python3 scripts/brand_head.py && python3 scripts/seo_head.py && python3 scripts/sitemap_lastmod.py
python3 scripts/seo_head.py --verifica && python3 scripts/verify_jsonld.py && python3 scripts/sitemap_lastmod.py --check
python3 -m pytest -q
```

Per la pipeline del venerdì i passi sono nel [README](../README.md).

### Cosa viene pubblicato e cosa no

GitHub Pages pubblica la cartella `_site/`, creata a ogni push dal workflow
con `scripts/build_site.py`. **Va online** tutto il sito: le pagine `.html`
(blog e `crucidev/privacy/` compresi), `styles/`, `fonts/`, `images/`, gli
script `.js` delle pagine, `robots.txt`, `sitemap.xml`, `site.webmanifest`,
favicon e il file chiave IndexNow. **Non va online**: `docs/` (anche questo
documento), `README.md`, `tests/`, `.github/`, gli script Python e `.mjs`,
`images/_archivio/`, i file `.backup`, cache e file nascosti.
Lo script copia tutto tranne un elenco di esclusioni: una pagina o
un'immagine nuova va online da sola, uno strumento nuovo va escluso a mano
in `scripts/build_site.py`.

Per provarlo in locale:

```bash
python3 scripts/build_site.py                          # crea _site/ (una _site/ vecchia viene spostata, non cancellata)
python3 scripts/check_internal_links.py --root _site   # 0 riferimenti rotti
python3 -m http.server 8100 --directory _site          # il sito come sarà online
```

## 7. Storico delle decisioni (29/09/2026)

- **Entità unica**: un solo `#business` e un solo `#giuseppe`, uguali ovunque;
  `sameAs` con Google Maps, Instagram, YouTube (attività) e LinkedIn,
  Superprof (persona). GitHub non c'è: nel sito non c'era un profilo da
  citare.
- **Date vere**: esclusi dal calcolo il box CTA degli articoli e le sole
  differenze di maiuscole; 50 articoli su 51 hanno `dateModified =
  datePublished`.
- **Cannibalizzazione Monopoli**: la home prende "programmatore a Monopoli",
  la pagina Monopoli "realizzazione siti web a Monopoli", le pagine servizio
  "in Puglia". Link e h1 riallineati di conseguenza.
- **Contenuti**: testi nuovi sulle 12 città, sulla home e sui servizi;
  nuova pagina Turi; h2 delle città diversi per ogni città.
- **Italiano prima delle parole chiave**: la frase esatta solo in title, h1 e
  un h2; circa 50 frasi forzate riscritte.
- **Promesse tolte** perché non confermate: dominio "intestato a te",
  collegamento alla scheda Google Business, formazione per aggiornare da
  solo, esportazione dei dati (anche "esportare in Excel"), le "copie di
  sicurezza regolari" aggiunte al gestionale. Il "backup" citato in
  websites.html (card "Sicurezza dei dati") c'era già su main e resta:
  SSL e backup li fa davvero l'hosting.
- **Pubblicazione**: online va solo il sito, costruito in `_site/` da
  `scripts/build_site.py`; docs, test e strumenti restano nel repo.
- **Meta**: title ≤ 60 con " | Pikobit", description ≤ 155, "Pikobit" scritto
  sempre così nei title, og:description = meta description. Le regole sono nel
  codice (`--verifica`), non solo qui.
- **Tecnologie**: nelle pagine servizio solo quelle confermate da Giuseppe
  (Java/Spring Boot, Python, C/C++, Flutter/Dart, Kotlin/Android Studio,
  Angular, React, HTML/CSS/JavaScript, WordPress su richiesta, PostgreSQL,
  MySQL, architettura pulita, design pattern, test automatici).
- **Google Maps**: link "Trovami su Google Maps" nel footer e in Contatti; il
  link "Lascia una recensione" è pronto in `contact.html` come commento, finché
  Giuseppe non fornisce l'indirizzo vero.
