---
title: "XFCE Dotfiles per PC datati"
description: "Configurazione XFCE4 su Arch Linux per un vecchio computer desktop: fix per monitor VGA, icone Papirus e ottimizzazioni per hardware a basso consumo."
date: 2026-11-07T09:00:00+01:00
lastmod: 2026-11-13T12:00:00+01:00
url: "/articoli/xfce-dotfiles.html"
categoria: "Guida e approfondimento"
eyebrow: "Guida e approfondimento"
date_display: "7 novembre 2026"
lastmod_prefix: "Aggiornato il"
lastmod_display: "13 novembre 2026"
lastmod_iso: "2026-11-13"
tags:
  - "XFCE4"
  - "Arch Linux"
  - "Dotfiles"
list_summary: "Configurazione di XFCE4 su Arch Linux per un desktop compatto HP collegato in VGA: corregge i margini tagliati dallo schermo analogico, usa le icone Papirus-Dark e si installa con uno script."
hero_image: "images/xfce-desktop.webp"
hero_alt: "Desktop XFCE4 su Arch Linux con pannello, icone Papirus scure, Firefox e Terminale"
repo_url: "https://github.com/giorossi-sudo/xfce-dotfiles"
repo_label: "Apri il repository xfce-dotfiles su GitHub"
repo_text: "Tutti i file di configurazione e lo script di installazione sono pubblicati su GitHub."
repo_credits: 'Licenza GPLv3. Creatore originale del tema: EndeavourOS Team (<a href="https://github.com/EndeavourOS-Community-Editions/endeavouros-xfce4-theming" target="_blank" rel="noopener noreferrer">https://github.com/EndeavourOS-Community-Editions/endeavouros-xfce4-theming</a>) e kerness (<a href="https://github.com/kerness" target="_blank" rel="noopener noreferrer">https://github.com/kerness</a>). Modifiche, fix VGA e ottimizzazioni per hardware low-power: giorossi-sudo (<a href="https://github.com/giorossi-sudo" target="_blank" rel="noopener noreferrer">https://github.com/giorossi-sudo</a>).'
related:
  - url: "/articoli/ottimizzare-xfce-poca-ram.html"
    cat: "Guida tecnica"
    title: "Ottimizzare XFCE su un PC con poca RAM"
    desc: "Analisi dettagliata delle configurazioni ZRAM, xfwm4 senza compositor, Thunar e VA-API."
  - url: "/articoli/fedora-hyprland.html"
    cat: "Wayland & Tiling WM"
    title: "Fedora Hyprland Dotfiles"
    desc: "Ambiente a finestre affiancate su Fedora Linux in coesistenza con GNOME per ASUS Zenbook 14 OLED."
---

## Cos'è e perché esiste

L'idea nasce dal voler recuperare un vecchio computer desktop che era praticamente inutilizzabile. Per pochi euro ho comprato un banco di RAM DDR3 da 8 GB, perché la macchina ne aveva solo 4 GB. Poi ho recuperato un SSD, ci ho installato Arch Linux e ho cercato una configurazione adatta da ottimizzare per questo computer.

XFCE4 è un ambiente desktop leggero per Linux. Questa configurazione è pensata per hardware a basso consumo e per monitor analogici collegati in VGA, ed è basata sul progetto originale del team di EndeavourOS.

## La macchina di riferimento

Questa configurazione è pensata per girare bene su processori a basso consumo e hardware datato. Il computer su cui l'ho provata ha queste caratteristiche:

- Processore: AMD E1-2500 APU (2 core, 2 thread a 1,4 GHz, architettura Jaguar)
- Memoria: 8 GB DDR3 più 3,6 GB di ZRAM compressa (`vm.swappiness = 180`, `vm.page-cluster = 0`)
- Scheda video: AMD Radeon HD 8240 (Kabini, GCN 1.1, driver amdgpu con supporto Mesa / RADV)
- Archiviazione: SSD SATA da 240 GB, con TRIM periodico abilitato
- Monitor: risoluzione nativa 1680x1050 (16:10), collegato alla porta analogica VGA

La ZRAM è una parte della memoria RAM usata come spazio di swap compresso.

## Cosa cambia

### Correzioni per lo schermo VGA

Sui monitor LCD collegati in analogico (VGA), un disallineamento del segnale può spostare l'immagine verso destra e tagliare il pulsante di chiusura delle finestre massimizzate. Per evitare il problema, `xfwm4` imposta un margine destro di 26 px così i pulsanti restano sempre visibili e cliccabili, mentre uno spaziatore a fine pannello (`#separator-15`) tiene il pulsante di spegnimento lontano dal bordo soggetto a overscan.

### Icone Papirus-Dark e tema solido

Al posto delle vecchie icone raster c'è Papirus-Dark (un tema vettoriale in SVG), abbinato al tema `Arc-Darker-solid` senza trasparenze. Sul pannello il pulsante di spegnimento sostituisce l'icona di disconnessione, e alcune regole CSS in `~/.config/gtk-3.0/gtk.css` disattivano il ridimensionamento delle icone (`-gtk-icon-transform: none`) e sistemano l'allineamento di orologio, volume e notifiche.

### Suite ufficio sul pannello

Sul pannello principale, accanto a Firefox, ci sono i lanciatori di LibreOffice Writer e LibreOffice Calc.

### Meno carico sul processore

- Sfondo PNG nativo a 1680x1050 (`xfce-x-1680x1050.png`) al posto dell'SVG da 3840x2400, così Cairo e `xfdesktop` non devono rasterizzare l'immagine a ogni avvio.
- Screensaver (`xfce4-screensaver`) disabilitato all'avvio con un override in `~/.config/autostart/xfce4-screensaver.desktop`: a spegnere lo schermo ci pensa già il risparmio energetico DPMS del monitor.
- Miniature in Thunar limitate ai file locali sotto i 10 MB, per evitare che cartelle pesanti mandino al massimo la CPU.
- Variabili in `~/.xprofile` (caricato direttamente da LightDM) per usare il driver `radeonsi` (VA-API) e WebRender, più `NO_AT_BRIDGE=1` per disattivare il bridge `at-spi` e risparmiare RAM e traffico D-Bus.
- Pannello, window manager e terminale più snelli: rimosso `power-manager-plugin` su desktop fisso, orologio senza secondi (`%H:%M`) per evitare ridisegni continui, compositing disattivato e `cycle_preview = false` in `xfwm4`, e scrollback limitato a 10.000 righe in `xfce4-terminal`.
- Parametri ZRAM in `/etc/sysctl.d/99-zram.conf` (`vm.swappiness = 180`, `vm.page-cluster = 0`, `vm.watermark_boost_factor = 0` e `vm.watermark_scale_factor = 125`) per sfruttare la compressione in RAM (tutti i dettagli nella guida [Ottimizzare XFCE su un PC con poca RAM](/articoli/ottimizzare-xfce-poca-ram.html)).

## Come si usa

Per installarla si clona il repository e si esegue lo script di installazione:

<div class="code-block"><code>git clone https://github.com/giorossi-sudo/xfce-dotfiles.git<br>
cd xfce-dotfiles<br>
./install.sh</code></div>

Pacchetti aggiuntivi consigliati per questa configurazione:

<div class="code-block"><code>sudo pacman -S --needed papirus-icon-theme libreoffice-still libreoffice-still-it ttf-liberation hunspell-it</code></div>
