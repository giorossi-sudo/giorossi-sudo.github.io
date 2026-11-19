---
title: "Fedora Hyprland Dotfiles"
description: "Configurazione di Hyprland per Fedora Linux: convivenza con GNOME, calibrazione per display OLED ASUS Zenbook 14 e guida all'installazione rapida."
date: 2026-11-07T10:00:00+01:00
lastmod: 2026-11-19T11:17:00+01:00
url: "/articoli/fedora-hyprland.html"
categoria: "Guida e approfondimento"
eyebrow: "Guida e approfondimento"
date_display: "7 novembre 2026"
lastmod_prefix: "Aggiornato il"
lastmod_display: "19 novembre 2026"
lastmod_iso: "2026-11-19"
tags:
  - "Hyprland"
  - "Fedora"
  - "Waybar"
subtitle: "Un ambiente a finestre affiancate per Fedora Linux che convive senza problemi con GNOME ed è regolato per schermi ad alta definizione."
list_summary: 'Configurazione per Fedora Linux con Hyprland 0.57+ (Lua) e doppia barra Waybar: convive con GNOME senza toccare <code>/etc/environment</code> ed è tarata per il display OLED 2.8K dell''ASUS Zenbook 14.'
hero_image: "images/hyprland-desktop.webp"
hero_alt: "Desktop Hyprland su Fedora con doppia barra Waybar, Firefox sul repository GitHub e terminali Foot affiancati"
repo_url: "https://github.com/giorossi-sudo/fedora-hyprland-dotfiles"
repo_label: "Apri il repository fedora-hyprland-dotfiles su GitHub"
repo_text: "Tutti i file di configurazione, lo script di installazione e le note complete sono su GitHub."
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

Hyprland è un gestore di finestre per Linux che dispone le applicazioni a griglia, affiancandole sullo schermo senza sovrapporle. Si usa quasi solo con scorciatoie da tastiera, così si lavora veloci e senza elementi inutili sullo schermo.

Questa configurazione adatta per Fedora Linux (versioni 40, 41, 42 e 44) i dotfiles di Riccardo Palombo, pensati in origine per Arch Linux su ThinkPad. L'idea è poter provare Hyprland senza togliere GNOME: le due sessioni restano entrambe disponibili e si sceglie quale avviare dalla schermata di login.

## Cosa cambia rispetto alla configurazione originale

Per portare il setup su Fedora e adattarlo al nuovo hardware ho dovuto cambiare diverse cose:

### Convivenza con GNOME

Su Arch Linux alcune variabili globali finivano in `/etc/environment`, ma su Fedora quella scelta rompe l'avvio di GNOME tramite GDM. Qui invece `/etc/environment` resta intatto: le variabili che servono vengono caricate solo dentro la sessione Hyprland tramite `hl.env`, così GNOME continua a partire senza problemi.

### Pacchetti e strumenti su Fedora

Ho convertito i pacchetti di Arch e AUR negli equivalenti per Fedora, usando `dnf` e attivando un repository COPR per il launcher `tofi`. I binari Polkit in `/usr/libexec/` gestiscono l'autenticazione con un fallback compatibile con GNOME, MATE e KDE. Nella shell uso `eza` al posto di `exa`, che ormai è deprecato.

### Ottimizzazione per ASUS Zenbook 14 OLED

Lo schermo è regolato sul pannello OLED 2.8K (2880×1800 a 90Hz) con fattore di scala 1.6, così testi e icone restano nitidi. Sul touchpad ho attivato scorrimento naturale, tocco per il clic e gesture a tre dita per cambiare workspace, rimuovendo le regole specifiche del TrackPoint ThinkPad.

### Hyprland 0.57+ (Lua) e barre Waybar stabili

Da Hyprland 0.57 il compositor usa il parser nativo in Lua: la configurazione sta in `hyprland.lua`, con `hyprland.conf` lasciato come riferimento compatibile. Le due barre Waybar vengono avviate tramite `systemd-run --user`, in modo che restino attive e non si duplichino quando ricarichi la configurazione.

## Come si usa

### Installazione rapida

Clona il repository sul tuo computer ed esegui lo script di installazione:

<div class="code-block"><code>git clone https://github.com/giorossi-sudo/fedora-hyprland-dotfiles.git<br>
cd fedora-hyprland-dotfiles<br>
chmod +x install.sh<br>
./install.sh</code></div>

Lo script fa tutto da solo: installa i pacchetti con `dnf`, abilita il COPR per `tofi`, installa i font JetBrains Mono e FontAwesome, copia le configurazioni in `~/.config/`, mette lo sfondo in `~/Pictures/` e aggiunge qualche alias comodo nella shell.

### Cambio di sessione dal login

Dopo l'installazione puoi passare da GNOME a Hyprland e viceversa:

1. Fai Logout dalla sessione attiva.
2. Nella schermata di login GDM, seleziona il tuo utente.
3. Clicca sull'icona a ingranaggio ⚙ in basso a destra.
4. Scegli Hyprland oppure GNOME.
5. Inserisci la password e accedi.

Se colleghi un monitor esterno tradizionale a 1080p, imposta scala 1.0 e risoluzione preferred nel file `~/.config/hypr/hyprland.lua`.
