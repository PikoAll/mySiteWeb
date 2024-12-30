# Guida Completa: Configurazione Dominio OVH, VPS e Pubblicazione Sito Web con SEO e Ottimizzazioni

Questa guida raccoglie tutte le fasi eseguite per configurare un dominio acquistato su OVH, collegarlo a una VPS, configurare Nginx, pubblicare un sito web statico (HTML, CSS, JavaScript) e ottimizzarlo per SEO e performance. Include tutti i passaggi, errori riscontrati e soluzioni, fornendo un flusso completo dall'inizio alla fine.

---

## **1. Acquisto e Configurazione del Dominio OVH**

### Acquisto del Dominio
1. Vai su [OVH](https://www.ovhcloud.com/).
2. Cerca e seleziona il dominio desiderato.
3. Completa l'acquisto e verifica che il dominio sia visibile nella tua area cliente OVH.

### Configurazione del DNS
1. Accedi all'area cliente OVH.
2. Vai su **Domini** > **Zona DNS**.
3. Configura i seguenti record:
   - **A Record**: Punta all'indirizzo IP della tua VPS (es: `123.456.789.0`).
   - **CNAME Record** (opzionale): Per configurare sottodomini (es: `www`).
4. Salva e attendi la propagazione (di solito entro 24-48 ore).

---

## **2. Configurazione della VPS**

### Accesso e Installazione
1. Accedi alla tua VPS tramite SSH:
   ```bash
   ssh utente@IP_della_tua_VPS
   ```
2. Aggiorna i pacchetti:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. Installa Nginx:
   ```bash
   sudo apt install nginx -y
   ```
4. Avvia e abilita il servizio:
   ```bash
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

### Configurazione di Nginx
1. Modifica il file predefinito di Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```
2. Configura il server per il tuo dominio:
   ```nginx
   server {
       listen 80;
       server_name tuodominio.it www.tuodominio.it;

       root /var/www/tuodominio;
       index index.html;

       location / {
           try_files $uri $uri/ =404;
       }
   }
   ```
3. Crea la directory del sito:
   ```bash
   sudo mkdir -p /var/www/tuodominio
   ```
4. Imposta i permessi:
   ```bash
   sudo chown -R www-data:www-data /var/www/tuodominio
   sudo chmod -R 755 /var/www/tuodominio
   ```
5. Verifica la configurazione:
   ```bash
   sudo nginx -t
   ```
6. Ricarica Nginx:
   ```bash
   sudo systemctl reload nginx
   ```

---

## **3. Creazione del Sito Web**

### Struttura del Progetto
1. Vai nella directory del sito:
   ```bash
   cd /var/www/tuodominio
   ```
2. Crea i file principali:
   ```bash
   touch index.html style.css script.js
   ```
3. Contenuto base per `index.html`:
   ```html
   <!DOCTYPE html>
   <html lang="it">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <meta name="description" content="Descrizione del tuo sito">
       <title>Titolo del Sito</title>
       <link rel="stylesheet" href="style.css">
   </head>
   <body>
       <h1>Benvenuto!</h1>
       <script src="script.js"></script>
   </body>
   </html>
   ```

---

## **4. Ottimizzazioni SEO**

### Lista di Priorità
Durante il progetto, abbiamo definito una lista di priorità:
1. **Titoli e meta description**: Aggiunti e ottimizzati per ogni pagina.
2. **Header Tags**: Strutturazione logica con H1, H2, H3.
3. **URL leggibili**: Evitare parametri inutili.
4. **Testo alternativo per immagini**: Inserito in tutte le immagini.
5. **Compressione file e ottimizzazione immagini**: Completata.

### File Robots.txt
1. Crea il file:
   ```bash
   nano /var/www/tuodominio/robots.txt
   ```
2. Inserisci:
   ```txt
   User-agent: *
   Disallow:
   Sitemap: https://tuodominio.it/sitemap.xml
   ```

### File Sitemap.xml
1. Crea il file:
   ```bash
   nano /var/www/tuodominio/sitemap.xml
   ```
2. Contenuto:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
       <url>
           <loc>https://tuodominio.it/</loc>
           <lastmod>2024-12-30</lastmod>
           <priority>1.0</priority>
       </url>
   </urlset>
   ```

---

## **5. Configurazione Google Analytics**

### Integrazione
1. Crea un account su [Google Analytics](https://analytics.google.com/).
2. Genera una proprietà e copia il codice di monitoraggio.
3. Inserisci il codice in `index.html` prima del tag `</head>`:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXX-Y"></script>
   <script>
       window.dataLayer = window.dataLayer || [];
       function gtag(){dataLayer.push(arguments);}
       gtag('js', new Date());
       gtag('config', 'UA-XXXXX-Y');
   </script>
   ```
4. Verifica con **Google Tag Assistant**.

---

## **6. Ottimizzazioni delle Performance**

### Compressione GZIP
1. Modifica il file di configurazione globale di Nginx:
   ```bash
   sudo nano /etc/nginx/nginx.conf
   ```
2. Aggiungi:
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
   ```
3. Ricarica:
   ```bash
   sudo systemctl reload nginx
   ```

### Caching del Browser
1. Modifica `/etc/nginx/sites-available/default`:
   ```nginx
   location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg|eot)$ {
       expires 1y;
       add_header Cache-Control "public";
   }
   ```
2. Ricarica:
   ```bash
   sudo systemctl reload nginx
   ```

---

## **7. Errori Riscontrati e Soluzioni**

### Problemi con il DNS
- **Errore**: Il dominio non puntava correttamente alla VPS.
- **Soluzione**: Verificato e aggiornato l'A Record su OVH.

### Problemi con Google Analytics
- **Errore**: Il codice di monitoraggio non funzionava.
- **Soluzione**: Corretto il posizionamento del codice nel file `index.html`.

### Problemi di Cache
- **Errore**: Le modifiche non si riflettevano immediatamente.
- **Soluzione**: Pulizia della cache del browser e del server.

---

## **8. Test Finale**

1. **Compatibilità Mobile**: Testata con lo strumento di compatibilità Google.
2. **Performance**: Analizzata con PageSpeed Insights e ottimizzata.
4. **SEO**: Verificata con Lighthouse.

Con questa guida completa, sarai in grado di replicare tutto il lavoro eseguito, configurando autonomamente un dominio, una VPS, un sito web e implementando ottimizzazioni per SEO e performance.




Certamente, puoi continuare ad aggiungere ulteriori pagine al tuo progetto! Ogni volta che aggiungi un file HTML o una nuova pagina al tuo sito, ci sono alcuni passaggi da seguire per assicurarti che tutto funzioni correttamente e che la nuova pagina venga indicizzata da Google.

### **Passaggi da seguire quando aggiungi una nuova pagina HTML:**

#### **1. Creazione della nuova pagina**
1. **Crea il file HTML nella directory del tuo progetto**, ad esempio:
   ```bash
   nano /var/www/tuodominio/nuovapagina.html
   ```
2. Aggiungi contenuti ottimizzati per SEO nella pagina:
   - **Titolo unico** (`<title>`).
   - **Meta description** specifica.
   - **Header tags** (H1, H2, ecc.).
   - **Testo alternativo (alt)** per immagini.

   Esempio di struttura:
   ```html
   <!DOCTYPE html>
   <html lang="it">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <meta name="description" content="Descrizione unica della nuova pagina">
       <title>Nuova Pagina</title>
       <link rel="stylesheet" href="style.css">
   </head>
   <body>
       <h1>Benvenuto nella Nuova Pagina!</h1>
       <p>Contenuti della nuova pagina...</p>
   </body>
   </html>
   ```

#### **2. Aggiungi un link alla nuova pagina**
- Modifica il file `index.html` (o qualsiasi altra pagina esistente) per includere un link alla nuova pagina:
  ```html
  <a href="/nuovapagina.html">Vai alla Nuova Pagina</a>
  ```

#### **3. Verifica la nuova pagina**
1. Visita la nuova pagina nel browser, ad esempio:
   ```
   http://tuodominio.it/nuovapagina.html
   ```
2. Controlla che il layout e i contenuti siano corretti.

#### **4. Aggiorna la Sitemap**
- Apri il file `sitemap.xml`:
  ```bash
  nano /var/www/tuodominio/sitemap.xml
  ```
- Aggiungi un nuovo blocco per la pagina:
  ```xml
  <url>
      <loc>https://tuodominio.it/nuovapagina.html</loc>
      <lastmod>2024-12-30</lastmod>
      <priority>0.8</priority>
  </url>
  ```
- Salva e chiudi.

#### **5. Richiedi indicizzazione su Google**
1. Vai su **Google Search Console**.
2. Usa lo strumento **Controllo URL** per inserire l'URL della nuova pagina (es. `https://tuodominio.it/nuovapagina.html`).
3. Clicca su **Richiesta di indicizzazione**.

#### **6. Test di compatibilità e performance**
- Usa gli stessi strumenti utilizzati per la homepage:
  - **Google Mobile-Friendly Test** per la compatibilità mobile.
  - **Google PageSpeed Insights** per ottimizzazioni di performance.

---

### **Buone pratiche per aggiungere nuove pagine**
1. **Collegamenti interni**:
   - Assicurati che ogni nuova pagina sia linkata da altre pagine del sito.
   - Questo aiuta sia i visitatori che i crawler di Google a trovarle.

2. **Contenuti originali**:
   - Scrivi contenuti unici e rilevanti per ogni nuova pagina.
   - Evita duplicazioni con altre pagine.

3. **Aggiorna il file `robots.txt` se necessario**:
   - Se desideri escludere determinate pagine dall'indicizzazione, aggiungile nel file `robots.txt`.

4. **Backup regolari**:
   - Prima di apportare modifiche al sito, esegui un backup per evitare perdite di dati.

---

Se hai bisogno di supporto per un passaggio specifico, sono qui per aiutarti! 😊

