---
title: "Fedora Hyprland Dotfiles"
description: "Configurazione di Hyprland per Fedora Linux: convivenza con GNOME, calibrazione per display OLED ASUS Zenbook 14 e guida all'installazione rapida."
date: 2026-11-07T10:00:00+01:00
lastmod: 2026-11-10T10:00:00+01:00
url: "/articoli/fedora-hyprland.html"
categoria: "Guida e approfondimento"
eyebrow: "Guida e approfondimento"
date_display: "7 novembre 2026"
lastmod_prefix: "Aggiornato a"
lastmod_display: "novembre 2026"
tags:
  - "Hyprland"
  - "Fedora"
  - "Waybar"
subtitle: "Un ambiente a finestre affiancate per Fedora Linux, progettato per convivere stabilmente con GNOME e calibrato per schermi moderni ad alta definizione."
list_summary: 'Un ambiente a finestre affiancate per Fedora Linux basato su Hyprland 0.57+ (Lua) e doppia barra Waybar, progettato per convivere stabilmente con GNOME senza alterare <code>/etc/environment</code> e calibrato per il display OLED 2.8K dell''ASUS Zenbook 14.'
hero_image: "images/hyprland-desktop.webp"
hero_alt: "Desktop Hyprland su Fedora con barre Waybar in alto e in basso"
repo_url: "https://github.com/giorossi-sudo/fedora-hyprland-dotfiles"
repo_label: "Apri il repository fedora-hyprland-dotfiles su GitHub"
repo_text: "Tutti i file di configurazione, lo script di installazione automatizzato e i dettagli completi sono pubblicati e liberamente consultabili su GitHub."
repo_credits: 'Configurazione originale e crediti a <a href="https://github.com/RiccardoPP/dotfiles" target="_blank" rel="noopener noreferrer">Riccardo Palombo (RiccardoPP/dotfiles)</a>.'
related:
  - url: "/articoli/xfce-dotfiles.html"
    cat: "Arch Linux & XFCE4"
    title: "XFCE Dotfiles per PC datati"
    desc: "Configurazione XFCE4 su Arch Linux con correzioni per monitor VGA e icone Papirus-Dark."
  - url: "/articoli/ottimizzare-xfce-poca-ram.html"
    cat: "Guida tecnica"
    title: "Ottimizzare XFCE su un PC con poca RAM"
    desc: "Approfondimento su ZRAM, compositing disattivato, Thunar e accelerazione hardware VA-API."
---

## Cos'è e perché esiste

Hyprland è un gestore di finestre per Linux che organizza le applicazioni a griglia, affiancandole automaticamente sullo schermo senza sovrapporle. Si controlla prevalentemente con scorciatoie da tastiera, offrendo un flusso di lavoro rapido e privo di distrazioni visive.

Questo progetto nasce come adattamento per **Fedora Linux** (versioni 40, 41, 42 e 44) della configurazione di Riccardo Palombo, ideata in origine per Arch Linux su computer ThinkPad.

Questo adattamento permette di provare Hyprland senza rinunciare a GNOME: le due sessioni coesistono e si sceglie quale avviare dalla schermata di login.

## Cosa cambia rispetto alla configurazione originale

Il passaggio dall'ambiente di origine a Fedora ha richiesto modifiche precise per evitare conflitti e adattarsi al nuovo hardware:

### Convivenza pacifica con GNOME

Su Arch Linux alcune variabili globali venivano scritte in `/etc/environment`, ma su Fedora questo corrompe l'avvio della sessione GNOME tramite GDM. In questo progetto il file `/etc/environment` non viene toccato: le variabili necessarie vengono caricate unicamente nella sessione Hyprland con `hl.env`, lasciando GNOME del tutto inalterato.

### Adattamento all'ecosistema Fedora

Tutti i pacchetti di Arch e AUR sono stati convertiti per gli strumenti di Fedora. L'installazione sfrutta `dnf` e attiva un repository COPR per il menu delle applicazioni `tofi`. I binari Polkit in `/usr/libexec/` gestiscono l'autenticazione con un fallback compatibile con GNOME, MATE e KDE. Nella shell viene inoltre impiegato lo strumento moderno `eza` al posto del deprecato `exa`.

### Ottimizzazione per ASUS Zenbook 14 OLED

La grafica è calibrata per lo schermo OLED 2.8K (**2880×1800 a 90Hz**) con scala 1.6, garantendo elementi definiti e testi nitidi. Sul touchpad sono attivati scorrimento naturale, tocco per il clic e gesture a tre dita per cambiare workspace, eliminando le direttive specifiche del TrackPoint ThinkPad.

### Hyprland 0.57+ (Lua) e barre Waybar stabili

Con Hyprland 0.57 il compositor adotta il parser nativo in Lua: la configurazione risiede in `hyprland.lua`, mantenendo il file `hyprland.conf` come riferimento compatibile. Le due barre Waybar sono gestite con `systemd-run --user`, garantendo persistenza ed evitando barre duplicate ai reload.

## Come si usa

Mettere in funzione la configurazione è semplice, sia nell'installazione iniziale sia nell'utilizzo quotidiano.

### Installazione rapida

Non servono configurazioni manuali complesse. Basta clonare il repository sul proprio computer ed eseguire lo script di installazione:

<div class="code-block"><code>git clone https://github.com/giorossi-sudo/fedora-hyprland-dotfiles.git<br>
cd fedora-hyprland-dotfiles<br>
chmod +x install.sh<br>
./install.sh</code></div>

Lo script gestisce tutto in automatico: installa i pacchetti necessari con `dnf`, abilita COPR per `tofi`, installa i font JetBrains Mono e FontAwesome, posiziona le configurazioni in `~/.config/`, copia lo sfondo in `~/Pictures/` e aggiunge alias comodi nella shell.

### Cambio di sessione dal login

Dopo l'installazione è possibile passare liberamente da GNOME a Hyprland:

1. Effettua il **Logout** dalla sessione attiva.
2. Nella schermata di login GDM, seleziona il tuo utente.
3. Clicca sull'icona a ingranaggio **⚙** in basso a destra.
4. Scegli **Hyprland** oppure **GNOME**.
5. Inserisci la password e accedi.

Per chi collega un monitor esterno tradizionale a 1080p, basta impostare scala 1.0 e risoluzione preferred nel file `~/.config/hypr/hyprland.lua`.
