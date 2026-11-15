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
subtitle: 'Come recuperare un computer desktop datato riducendo al minimo il consumo di memoria e il carico sul processore: tutte le scelte tecniche adottate nel progetto <a href="/articoli/xfce-dotfiles.html">XFCE Dotfiles per PC datati</a>, dalla gestione della ZRAM alla disattivazione dei servizi ridondanti.'
list_summary: 'Come ridurre al minimo il consumo di memoria e i picchi sulla CPU su un vecchio desktop con processore AMD E1-2500: configurazione di ZRAM con <code>vm.swappiness = 180</code>, disattivazione del compositor di <code>xfwm4</code>, limiti alle miniature di Thunar e accelerazione hardware VA-API.'
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

Quando si prova a riportare in vita un computer fisso di oltre dieci anni fa, il primo consiglio che si incontra è quasi sempre quello di installare una distribuzione leggera accompagnata da **XFCE4**. Sebbene XFCE sia effettivamente molto più sobrio rispetto agli ambienti desktop più complessi, una configurazione standard include comunque una serie di automatismi pensati per macchine moderne: sfondi vettoriali renderizzati al volo, compositing grafico attivo, demoni per il salvaschermo, indicizzazione indiscriminata delle anteprime e assenza di accelerazione video esplicita nel browser.

Su un processore a basso consumo e con un quantitativo ridotto di memoria RAM DDR3, questi piccoli carichi si sommano rapidamente. Basta aprire qualche scheda del browser accanto a un documento di testo per notare rallentamenti nel ridisegno delle finestre o blocchi temporanei durante l'esplorazione delle cartelle.

Nel lavoro svolto per il repository <a href="https://github.com/giorossi-sudo/xfce-dotfiles" target="_blank" rel="noopener noreferrer">xfce-dotfiles</a>, l'obiettivo è stato partire dal tema XFCE di EndeavourOS su **Arch Linux** ed eliminare sistematicamente ogni spreco di risorse, mantenendo però un aspetto pulito, moderno e comodo per l'uso quotidiano.

## Il contesto hardware reale

Ogni ottimizzazione ha senso solo se rapportata ai colli di bottiglia reali della macchina. Il computer recuperato per questo progetto è un desktop compatto HP che in origine montava appena **4 GB di RAM DDR3** e un disco meccanico tradizionale. Con una spesa minima sono stati aggiunti un banco DDR3 per arrivare a 8 GB e un **SSD SATA da 240 GB**, ma il cuore del sistema resta fortemente limitato:

- **APU / Processore:** AMD E1-2500 (architettura Jaguar a 2 core e 2 thread, frequenza fissa a 1,4 GHz).
- **Memoria di sistema:** 8 GB DDR3 affiancati da 3,6 GB di swap compresso in **ZRAM**.
- **Grafica integrata:** AMD Radeon HD 8240 (architettura Kabini GCN 1.1, gestita dal driver kernel `amdgpu` con stack Mesa e RADV).
- **Uscita video:** monitor 16:10 con risoluzione nativa `1680x1050` collegato tramite cavo analogico **VGA**.

Con due soli core a 1,4 GHz, qualsiasi operazione superflua in background sottrae cicli preziosi alle applicazioni in primo piano, e qualsiasi accesso allo swap su disco rallenta l'intero sistema. Vediamo nel dettaglio i sei interventi principali applicati nella configurazione.

## 1. Gestione della memoria con ZRAM e swappiness a 180

Su macchine con 4 GB o 8 GB di RAM, l'esaurimento della memoria fisica durante la navigazione web moderna è un rischio concreto. Scrivere pagine di memoria inattive sullo swap dell'SSD SATA introduce latenze elevate e usura inutilmente le celle NAND del disco. La soluzione adottata consiste nell'affiancare alla RAM un dispositivo **ZRAM** da 3,6 GB: una porzione della RAM stessa in cui i dati vengono compressi al volo.

### Perché impostare vm.swappiness = 180 e page-cluster = 0

Sui sistemi con swap tradizionale su disco si tende ad abbassare il parametro `vm.swappiness` per ritardare il più possibile la scrittura su disco. Con ZRAM vale il principio opposto: comprimere e decomprimere blocchi direttamente in RAM è enormemente più rapido rispetto all'I/O su SATA. Impostando `vm.swappiness = 180` in `/etc/sysctl.d/99-zram.conf` insieme a `vm.page-cluster = 0` (che disabilita il readahead superfluo sullo swap in RAM) e ai parametri di `watermark`, il kernel sposta proattivamente le pagine meno recenti nella memoria compressa lasciando libera la RAM non compressa per la cache e le app attive:

<div class="code-block"><code># /etc/sysctl.d/99-zram.conf<br>
vm.swappiness = 180<br>
vm.watermark_boost_factor = 0<br>
vm.watermark_scale_factor = 125<br>
vm.page-cluster = 0</code></div>

Per rendere subito effettiva l'impostazione senza riavviare la macchina, lo script di installazione esegue `sudo sysctl -p /etc/sysctl.d/99-zram.conf`.

## 2. Disattivare il compositor di xfwm4 e gli sfondi SVG

Il gestore di finestre di XFCE (`xfwm4`) integra un proprio compositor per disegnare ombre, trasparenze dei pannelli e dissolvenze. Su una GPU integrata datata e una CPU da 1,4 GHz, mantenere attivo il compositing introduce latenza nel trascinamento delle finestre e consuma memoria video condivisa.

### Configurazione di xfwm4 senza compositing

Nel file `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml` il compositing è stato disattivato (`use_compositing = false`) insieme a `cycle_preview = false` (per evitare anteprime pesanti durante l'Alt+Tab), all'attivazione di `unredirect_overlays = true` e al tema solido `Arc-Darker-solid`:

<div class="code-block"><code>&lt;property name="theme" type="string" value="Arc-Darker-solid"/&gt;<br>
&lt;property name="cycle_preview" type="bool" value="false"/&gt;<br>
&lt;property name="unredirect_overlays" type="bool" value="true"/&gt;<br>
&lt;property name="use_compositing" type="bool" value="false"/&gt;<br>
&lt;property name="margin_right" type="int" value="26"/&gt;</code></div>

Nota anche la proprietà `margin_right` impostata a `26` pixel: sui vecchi monitor collegati tramite cavo analogico VGA capita spesso che il segnale subisca un leggero slittamento orizzontale, tagliando il pulsante di chiusura `[X]` delle finestre massimizzate. Con questo margine fisso, il bordo destro delle finestre si ferma sempre prima dell'area soggetta a overscan.

### Sfondo PNG pre-renderizzato al posto dell'SVG 4K

Un altro dettaglio spesso trascurato riguarda lo sfondo del desktop gestito da `xfdesktop`. Molte distribuzioni forniscono sfondi predefiniti in formato vettoriale SVG o ad altissima risoluzione (3840×2400). Ad ogni avvio della sessione o ridimensionamento, la libreria Cairo deve rasterizzare e scalare l'immagine in memoria. Nel repository lo sfondo SVG è stato sostituito con un file PNG statico pre-renderizzato alla risoluzione nativa esatta del pannello (`1680x1050`, salvato in `~/.local/share/backgrounds/xfce-x-1680x1050.png`), azzerando il tempo di calcolo all'avvio.

## 3. Eliminare i processi in background non necessari

Su un PC con poca RAM, ogni demone residente in memoria che non svolge una funzione essenziale va disabilitato. Il caso più evidente in XFCE è `xfce4-screensaver`: tenere un processo costantemente attivo solo per mostrare uno schermo nero quando il computer è inutilizzato è ridondante, perché la stessa funzione è già svolta a livello hardware dal protocollo **DPMS** del monitor tramite il gestore energetico.

Invece di disinstallare forzatamente pacchetti che potrebbero far parte del gruppo `xfce4-goodies`, la configurazione disabilita l'avvio automatico creando un file di override locale in `~/.config/autostart/xfce4-screensaver.desktop`:

<div class="code-block"><code>[Desktop Entry]<br>
Type=Application<br>
Name=Screensaver<br>
Hidden=true</code></div>

## 4. Evitare i blocchi di Thunar sulle miniature

Il file manager **Thunar** è uno dei punti di forza di XFCE per rapidità e leggerezza. Tuttavia, se si apre una cartella che contiene video pesanti o archivi di grandi dimensioni, il servizio di generazione delle miniature (`tumblerd`) avvia processi in background che saturano rapidamente entrambi i core della CPU e gonfiano il consumo di RAM.

Nel file `~/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml` sono state applicate due restrizioni fondamentali: generare le anteprime esclusivamente per i file presenti sui dischi locali (ignorando le condivisioni di rete) e bloccare la creazione delle miniature per qualsiasi file superiore a **10 MB** (`10485760` byte):

<div class="code-block"><code>&lt;channel name="thunar" version="1.0"&gt;<br>
  &lt;property name="misc-thumbnail-mode" type="string" value="THUNAR_THUMBNAIL_MODE_ONLY_LOCAL"/&gt;<br>
  &lt;property name="misc-thumbnail-max-file-size" type="uint" value="10485760"/&gt;<br>
&lt;/channel&gt;</code></div>

## 5. Spostare il carico grafico e video sulla GPU (VA-API e WebRender)

Su un processore AMD E1-2500 la decodifica software dei flussi video in Firefox porta immediatamente la CPU al massimo utilizzo, rendendo scattosa anche l'interfaccia del browser. La scheda integrata **AMD Radeon HD 8240** (architettura GCN 1.1 supportata dal driver `amdgpu`) dispone però di un blocco dedicato alla decodifica hardware accessibile tramite **VA-API** e il driver Mesa `radeonsi`.

Inserendo le variabili d'ambiente direttamente in `~/.xprofile` (letto all'accesso da LightDM/X11), il sistema istruisce sia la libreria VA-API sia Firefox ad affidare il rendering della pagina (tramite **WebRender**) e la decodifica dei flussi video alla GPU, disattivando al tempo stesso il bridge di accessibilità `at-spi` (`NO_AT_BRIDGE=1`) per risparmiare RAM e traffico D-Bus:

<div class="code-block"><code># ~/.xprofile - Hardware acceleration environment for AMD GPU<br>
export LIBVA_DRIVER_NAME=radeonsi<br>
export MOZ_WEBRENDER=1<br>
export MOZ_ACCELERATED=1<br>
export NO_AT_BRIDGE=1</code></div>

## 6. Cura del pannello con CSS GTK3 e installazione automatica

Ottimizzare un sistema per poca RAM non significa rinunciare all'ordine visivo. Al posto di temi pesanti o barre esterne aggiuntive, è stato mantenuto il pannello nativo `xfce4-panel` (senza `power-manager-plugin` su PC fisso e con orologio `%H:%M` senza secondi per evitare ridisegni continui) abbinato al set di icone vettoriali **Papirus-Dark**, allo scrollback limitato a 10.000 righe in `xfce4-terminal` e a poche righe mirate in `~/.config/gtk-3.0/gtk.css` che disattivano le trasformazioni superflue delle icone (`-gtk-icon-transform: none`), uniformano le spaziature degli indicatori di stato e aggiungono il rientro di sicurezza per i monitor VGA.

Tutte queste modifiche sono raccolte e automatizzate nello script `install.sh` del repository, che adatta automaticamente i percorsi alla cartella `$HOME` dell'utente corrente:

1. Copia le configurazioni di XFCE4, Thunar e GTK3 in `~/.config/` e gli sfondi nativi in `~/.local/share/backgrounds/`.
2. Aggiunge in modo non distruttivo le variabili di accelerazione hardware e `NO_AT_BRIDGE=1` in `~/.xprofile` se non sono già presenti.
3. Chiede conferma prima di applicare `/etc/sysctl.d/99-zram.conf` e ricarica all'istante il pannello e `xfwm4`.
