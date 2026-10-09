# Architettura e stack

- **Sito**: pagine `.html` in radice, `blog/` per gli articoli, `styles/`, `fonts/`, `images/`.
- **Build**: `scripts/build_site.py` copia in `_site/` solo ciò che va online (esclude docs, test, strumenti).
- **Deploy**: GitHub Pages, workflow `.github/workflows/static.yml` su ogni merge in `main`.
- **Script Python** (`scripts/`): meta SEO e JSON-LD (`seo_head.py`), brand (`brand_head.py`), sitemap
  (`sitemap_lastmod.py`), controlli (`verify_jsonld.py`, `check_internal_links.py`, `check_page_similarity.py`).
- **Test**: pytest in `tests/` (script e regressione); end-to-end Playwright headless in `tests/e2e`.
- **CI**: `.github/workflows/ci.yml` (controlli + e2e) su ogni PR e su push in `main`; `main` è protetto.
- **Eccezione al flusso PR**: la pubblicazione settimanale del blog fa push diretto su `main`, solo file nuovi
  del blog più `resources.html` e `sitemap.xml`. Non toccare quei file a mano senza motivo.

Dettagli operativi e comandi: [README](../README.md); regole SEO: [SEO.md](SEO.md).
