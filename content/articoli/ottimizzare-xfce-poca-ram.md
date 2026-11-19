---
title: "Ottimizzare XFCE su un PC con poca RAM"
description: "Guida pratica per ottimizzare XFCE4 su Arch Linux su un PC datato con poca RAM: ZRAM con swappiness a 180, compositing disattivato, Thunar e accelerazione VA-API."
date: 2026-11-10T10:00:00+01:00
lastmod: 2026-11-13T12:00:00+01:00
url: "/articoli/ottimizzare-xfce-poca-ram.html"
categoria: "Guida tecnica"
eyebrow: "Guida tecnica · Linux & Hardware Low-Spec"
date_display: "10 novembre 2026"
lastmod_prefix: "Aggiornato il"
lastmod_display: "13 novembre 2026"
lastmod_iso: "2026-11-13"
tags:
  - "XFCE4"
  - "ZRAM"
  - "Low-spec"
subtitle: 'Come ridurre al minimo il consumo di memoria e di CPU su un vecchio desktop: le modifiche fatte per <a href="/articoli/xfce-dotfiles.html">XFCE Dotfiles per PC datati</a>, dalla ZRAM ai servizi da disattivare.'
list_summary: 'Come abbassare i consumi di RAM e CPU su un vecchio desktop con AMD E1-2500: ZRAM con <code>vm.swappiness = 180</code>, <code>xfwm4</code> senza compositor, limiti alle anteprime di Thunar e accelerazione hardware VA-API.'
hero_image: "images/xfce-desktop.webp"
hero_alt: "Desktop XFCE4 su Arch Linux ottimizzato per hardware a basso consumo"
repo_url: "https://github.com/giorossi-sudo/xfce-dotfiles"
repo_label: "Apri il repository xfce-dotfiles su GitHub"
repo_text: 'Tutti i file di configurazione descritti in questo articolo (<code>xfwm4.xml</code>, <code>thunar.xml</code>, <code>99-zram.conf</code>, <code>gtk.css</code> e <code>install.sh</code>) sono disponibili nel repository GitHub del progetto.'
related:
  - url: "/articoli/xfce-dotfiles.html"
    cat: "Progetto correlato"
    title: "XFCE Dotfiles per PC datati"
    desc: "Panoramica completa della configurazione XFCE4 su Arch Linux, fix per monitor VGA e pacchetti consigliati."
  - url: "/articoli/fedora-hyprland.html"
    cat: "Wayland & Tiling WM"
    title: "Fedora Hyprland Dotfiles"
    desc: "Configurazione di Hyprland su Fedora Linux in coesistenza con GNOME, calibrata per display OLED 2.8K."
---

## Perché non basta installare un desktop leggero

Quando provi a rimettere in sesto un computer fisso di oltre dieci anni fa, di solito ti consigliano subito di installare una distro leggera con XFCE4. È vero che XFCE consuma molto meno di altri ambienti desktop, ma di base si porta dietro diverse impostazioni pensate per macchine recenti: sfondi vettoriali renderizzati al volo, compositing grafico attivo, demoni per il salvaschermo, anteprime generate senza limiti e nessuna accelerazione video forzata nel browser.

Con una CPU lenta e poca RAM DDR3, questi piccoli consumi si sommano in fretta. Bastano poche schede del browser aperte accanto a un documento di testo per vedere le finestre che scattano o il file manager che si blocca per qualche secondo.

Nel lavoro per il repository <a href="https://github.com/giorossi-sudo/xfce-dotfiles" target="_blank" rel="noopener noreferrer">xfce-dotfiles</a> sono partito dal tema XFCE di EndeavourOS su Arch Linux e ho tolto tutto quello che sprecava risorse, cercando comunque di tenere un desktop ordinato e comodo da usare tutti i giorni.

## Il contesto hardware reale

Il computer recuperato per questo progetto è un desktop compatto HP che all'inizio aveva solo 4 GB di RAM DDR3 e un disco meccanico tradizionale. Con poca spesa ho aggiunto un banco DDR3 per arrivare a 8 GB e montato un SSD SATA da 240 GB, ma il resto dell'hardware resta limitato:

- APU / Processore: AMD E1-2500 (architettura Jaguar a 2 core e 2 thread, frequenza fissa a 1,4 GHz).
- Memoria di sistema: 8 GB DDR3 affiancati da 3,6 GB di swap compresso in ZRAM.
- Grafica integrata: AMD Radeon HD 8240 (architettura Kabini GCN 1.1, gestita dal driver kernel `amdgpu` con stack Mesa e RADV).
- Uscita video: monitor 16:10 con risoluzione nativa `1680x1050` collegato tramite cavo analogico VGA.

Con due soli core a 1,4 GHz, ogni processo inutile in background toglie aria alle applicazioni che stai usando, e anche lo swap su disco basta a frenare il sistema. Qui sotto ci sono i sei interventi principali che ho applicato.

## 1. Gestione della memoria con ZRAM e swappiness a 180

Con 4 o 8 GB di RAM, basta aprire qualche sito pesante per saturare la memoria fisica. Mandare le pagine inattive sullo swap dell'SSD SATA rallenta tutto e consuma le celle NAND del disco senza motivo. Per evitarlo ho affiancato alla RAM un dispositivo ZRAM da 3,6 GB, cioè una parte della RAM stessa in cui i dati vengono compressi al volo.

### Perché impostare vm.swappiness = 180 e page-cluster = 0

Quando lo swap sta su disco conviene tenere basso `vm.swappiness` per ritardare la scrittura su disco. Con ZRAM vale l'opposto: comprimere e decomprimere blocchi in RAM è molto più rapido che passare dal bus SATA. Impostando `vm.swappiness = 180` in `/etc/sysctl.d/99-zram.conf`, insieme a `vm.page-cluster = 0` (che toglie il readahead inutile sullo swap in RAM) e ai parametri di `watermark`, il kernel sposta prima le pagine vecchie nella memoria compressa e lascia più RAM non compressa libera per la cache e le app attive:

<div class="code-block"><code># /etc/sysctl.d/99-zram.conf<br>
vm.swappiness = 180<br>
vm.watermark_boost_factor = 0<br>
vm.watermark_scale_factor = 125<br>
vm.page-cluster = 0</code></div>

Per rendere subito effettive le modifiche senza riavviare la macchina, lo script di installazione esegue `sudo sysctl -p /etc/sysctl.d/99-zram.conf`.

## 2. Disattivare il compositor di xfwm4 e gli sfondi SVG

Il gestore di finestre di XFCE (`xfwm4`) ha un suo compositor integrato per disegnare ombre, trasparenze dei pannelli e dissolvenze. Su una GPU integrata datata e una CPU da 1,4 GHz, tenerlo acceso fa andare a scatti il trascinamento delle finestre e consuma memoria video condivisa.

### Configurazione di xfwm4 senza compositing

Nel file `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml` ho disattivato il compositing (`use_compositing = false`) e le anteprime dell'Alt+Tab (`cycle_preview = false`), attivato `unredirect_overlays = true` e scelto il tema solido `Arc-Darker-solid`:

<div class="code-block"><code>&lt;property name="theme" type="string" value="Arc-Darker-solid"/&gt;<br>
&lt;property name="cycle_preview" type="bool" value="false"/&gt;<br>
&lt;property name="unredirect_overlays" type="bool" value="true"/&gt;<br>
&lt;property name="use_compositing" type="bool" value="false"/&gt;<br>
&lt;property name="margin_right" type="int" value="26"/&gt;</code></div>

La proprietà `margin_right` a `26` pixel serve invece per i vecchi monitor collegati tramite cavo analogico VGA: spesso il segnale subisce un leggero slittamento verso destra che taglia il pulsante di chiusura `[X]` delle finestre massimizzate. Con questo margine fisso, il bordo destro delle finestre si ferma sempre prima dell'area soggetta a overscan.

### Sfondo PNG pre-renderizzato al posto dell'SVG 4K

Anche lo sfondo del desktop gestito da `xfdesktop` può pesare all'avvio. Molte distribuzioni usano sfondi predefiniti in formato vettoriale SVG o in 4K (3840×2400), costringendo la libreria Cairo a rasterizzare e scalare l'immagine in memoria a ogni login o ridimensionamento. Nel repository ho messo un PNG statico già pronto alla risoluzione nativa esatta dello schermo (`1680x1050`, in `~/.local/share/backgrounds/xfce-x-1680x1050.png`), evitando lavoro inutile all'avvio.

## 3. Eliminare i processi in background non necessari

Con poca RAM conviene disattivare i demoni in memoria che non svolgono una funzione utile. In XFCE il primo da togliere è `xfce4-screensaver`: tenerlo attivo solo per mostrare uno schermo nero quando il PC è fermo non serve, perché a spegnere il monitor ci pensa già il protocollo DPMS tramite il gestore energetico.

Invece di disinstallare a forza pacchetti che potrebbero far parte del gruppo `xfce4-goodies`, la configurazione ne blocca l'avvio automatico creando un file di override locale in `~/.config/autostart/xfce4-screensaver.desktop`:

<div class="code-block"><code>[Desktop Entry]<br>
Type=Application<br>
Name=Screensaver<br>
Hidden=true</code></div>

## 4. Evitare i blocchi di Thunar sulle miniature

Il file manager Thunar è veloce e leggero, ma quando apri una cartella con video pesanti o archivi grandi il servizio che genera le miniature (`tumblerd`) avvia processi in background che saturano entrambi i core della CPU e fanno salire la RAM.

Nel file `~/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml` ho quindi impostato due limiti: generare le anteprime solo per i file sui dischi locali (ignorando le condivisioni di rete) e bloccare la creazione delle miniature per qualsiasi file sopra i 10 MB (`10485760` byte):

<div class="code-block"><code>&lt;channel name="thunar" version="1.0"&gt;<br>
  &lt;property name="misc-thumbnail-mode" type="string" value="THUNAR_THUMBNAIL_MODE_ONLY_LOCAL"/&gt;<br>
  &lt;property name="misc-thumbnail-max-file-size" type="uint" value="10485760"/&gt;<br>
&lt;/channel&gt;</code></div>

## 5. Spostare il carico grafico e video sulla GPU (VA-API e WebRender)

Sull'AMD E1-2500 la decodifica software dei video in Firefox porta subito la CPU al massimo utilizzo e fa scattare anche l'interfaccia del browser. La scheda integrata AMD Radeon HD 8240 (architettura GCN 1.1, supportata dal driver `amdgpu`) ha però la decodifica hardware, accessibile tramite VA-API e il driver Mesa `radeonsi`.

Mettendo le variabili d'ambiente in `~/.xprofile` (letto all'accesso da LightDM/X11), VA-API e Firefox passano alla GPU sia il rendering delle pagine (tramite WebRender) sia la decodifica video. Con `NO_AT_BRIDGE=1` si spegne anche il bridge di accessibilità `at-spi` per risparmiare altra RAM e traffico D-Bus:

<div class="code-block"><code># ~/.xprofile - Hardware acceleration environment for AMD GPU<br>
export LIBVA_DRIVER_NAME=radeonsi<br>
export MOZ_WEBRENDER=1<br>
export MOZ_ACCELERATED=1<br>
export NO_AT_BRIDGE=1</code></div>

## 6. Cura del pannello con CSS GTK3 e installazione automatica

Al posto di temi pesanti o barre esterne ho tenuto il pannello nativo `xfce4-panel`, togliendo `power-manager-plugin` (inutile su un PC fisso) e lasciando l'orologio in formato `%H:%M` senza secondi per evitare ridisegni continui. Ho poi abbinato le icone vettoriali Papirus-Dark, limitato lo scrollback a 10.000 righe in `xfce4-terminal` e aggiunto poche righe in `~/.config/gtk-3.0/gtk.css` per bloccare le trasformazioni delle icone (`-gtk-icon-transform: none`), uniformare le spaziature degli indicatori di stato e aggiungere il rientro di sicurezza per i monitor VGA.

Tutte queste modifiche sono raccolte nello script `install.sh` del repository, che adatta i percorsi alla cartella `$HOME` dell'utente corrente:

1. Copia le configurazioni di XFCE4, Thunar e GTK3 in `~/.config/` e gli sfondi nativi in `~/.local/share/backgrounds/`.
2. Aggiunge in `~/.xprofile` le variabili per l'accelerazione hardware e `NO_AT_BRIDGE=1` se non sono già presenti, senza sovrascrivere il resto del file.
3. Chiede conferma prima di applicare `/etc/sysctl.d/99-zram.conf` e poi ricarica subito il pannello e `xfwm4`.
