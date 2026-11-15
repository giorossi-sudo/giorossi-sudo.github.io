# giorossi-sudo.tech

Sorgenti del sito statico personale **[giorossi-sudo.tech](https://giorossi-sudo.tech/)**, realizzato con **Hugo** applicando l'architettura modulare (partial, contenuti Markdown, dati strutturati in YAML, font self-hosted e deploy continuo a costo zero) descritta in `docs/`.

---

## 1. Requisiti e sviluppo locale

Il sito richiede esclusivamente il binario singolo di **Hugo** (versione usata e verificata: `v0.170.0`, edizione standard, nessuna dipendenza Node/npm e zero JavaScript client-side).

### Avviare il server di sviluppo con live-reload

```bash
hugo server -D
```

Il sito è visibile su **`http://localhost:1313/`** e si aggiorna in tempo reale a ogni modifica di template, contenuti Markdown o CSS.

### Generare la build di produzione e verificare i link

```bash
hugo --gc --minify --baseURL "https://giorossi-sudo.tech/" --printPathWarnings --panicOnWarning
python3 scripts/check-links.py
```

L'output statico completo viene scritto nella cartella `./public/` (ignorata da Git).

---

## 2. Come aggiungere contenuti

### Aggiungere un nuovo progetto in Home
Modifica il file `data/progetti.yaml` aggiungendo un elemento alla lista (con `id`, `title`, `description`, `tags`, `repo_url`, `links`, `image`, `image_alt`, `lazy`). Il numero progressivo (`01`, `02`, `03`...) e il totale vengono calcolati in automatico dal template `layouts/index.html`.

### Aggiungere un nuovo articolo
Puoi usare il comando Hugo:

```bash
hugo new content articoli/nome-articolo.md
```

oppure duplicare uno dei file `.md` esistenti in `content/articoli/`, compilando il front matter (`title`, `description`, `date`, `lastmod`, `url`, `categoria`, `tags`, `list_summary`, `hero_image`, `repo_url`, `related`).

---

## 3. Migrazione sul repository online e deploy gratuito (GitHub Pages)

Il sito è progettato per essere pubblicato gratuitamente su **GitHub Pages** tramite **GitHub Actions** (file `.github/workflows/hugo.yml`) sul repository `giorossi-sudo/giorossi-sudo.github.io`.

### Passo A — Creare un tag di backup del sito vecchio
Prima di sostituire i file del repository esistente (`~/giorossi-sudo.github.io`), crea e pubblica un tag Git (`v1-static-backup`) per conservare uno snapshot immutabile della versione precedente:

```bash
cd ~/giorossi-sudo.github.io
git status
git tag -a v1-static-backup -m "Backup del sito HTML/Tailwind prima della migrazione a Hugo"
git push origin v1-static-backup
```

### Passo B — Portare il nuovo sito nel repository e pubblicare
Una volta verificato il sito in locale, sostituisci il contenuto lavorativo del repository (preservando la cartella `.git` di `~/giorossi-sudo.github.io`) con i file di questa cartella:

```bash
# 1. Rimuovi i file tracciati della vecchia versione (mantenendo .git/)
cd ~/giorossi-sudo.github.io
git rm -rf .
rm -rf node_modules

# 2. Copia i file del nuovo progetto Hugo (escludendo .git/, public/, resources/ e docs/ di sito-nuovo)
rsync -av --exclude='.git' --exclude='public' --exclude='resources' --exclude='docs' ~/Scaricati/sito-nuovo/ ~/giorossi-sudo.github.io/

# 3. Ripristina il file CNAME alla radice dal tag di backup
git show v1-static-backup:CNAME > CNAME && git add CNAME

# 4. Controlla lo stato, fai commit e push su main
git add -A
git status
git commit -m "feat: migrazione del sito a Hugo con workflow GitHub Actions e font self-hosted"
git push origin main
```

### Passo C — Passare a "GitHub Actions" nelle impostazioni di GitHub Pages
1. Apri il repository su GitHub: `https://github.com/giorossi-sudo/giorossi-sudo.github.io/settings/pages`
2. Nella sezione **Build and deployment** → **Source**, cambia l'impostazione da *Deploy from a branch* a **GitHub Actions**.
3. Apri la scheda **Actions** del repository (`https://github.com/giorossi-sudo/giorossi-sudo.github.io/actions`): il workflow **Deploy Hugo site to Pages** partirà in automatico a ogni push su `main` (puoi anche avviarlo manualmente con *Run workflow*). Se il primo run dopo il push dovesse fallire perché il cambio sorgente a **GitHub Actions** è stato salvato dopo il push, esegui **Actions → Re-run all jobs** sul run fallito.

### Passo D — Controllo del dominio personalizzato e HTTPS
1. Nella stessa pagina **Settings → Pages**:
   - Verifica esplicitamente che nel campo **Custom domain** sia salvato `giorossi-sudo.tech`. **Importante:** quando si pubblica tramite **GitHub Actions** (e non da un branch), il file `static/CNAME` dentro l'artefatto **non basta** a configurare o mantenere il dominio su GitHub Pages: il dominio personalizzato deve essere impostato nella UI di **Settings → Pages → Custom domain** (noi manteniamo anche `static/CNAME` per compatibilità in caso di rollback al deploy da branch).
   - Verifica che la casella **Enforce HTTPS** sia spuntata.
2. A deploy completato, controlla da terminale che il dominio risponda in HTTPS con stato `200`:

```bash
curl -ILs https://giorossi-sudo.tech/ | head -n 20
```

---

## 4. Procedura di Rollback (ripristino immediato)

Se dopo la pubblicazione riscontri qualsiasi problema e vuoi tornare immediatamente al sito precedente:

1. **Ripristino del codice dal tag di backup `v1-static-backup`:**
   ```bash
   cd ~/giorossi-sudo.github.io
   git checkout main
   git reset --hard v1-static-backup
   git push --force-with-lease origin main
   ```
2. **Ripristino della sorgente GitHub Pages:**
   - Vai in **Settings → Pages → Build and deployment → Source** e reimposta **Deploy from a branch** → branch `main` → cartella `/ (root)`.
   - In meno di un minuto GitHub Pages tornerà a servire i file HTML statici originali.

---

## 5. Licenze dei font self-hosted

I font in `static/fonts/` (*Bricolage Grotesque*, *Instrument Sans* e *DM Mono*, formato `.woff2` subset latino) sono distribuiti con licenza **SIL Open Font License 1.1**. I testi integrali delle licenze sono inclusi nella cartella `static/fonts/OFL-*.txt`.
