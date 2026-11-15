#!/usr/bin/env python3
"""
Verifica statica post-build di ./public/:
1. Assenza di feed RSS e pagine taxonomy (/tags/, /categories/).
2. Presenza di tutti gli URL del sito precedente.
3. Validazione di tutti i link interni, immagini, srcset, fogli di stile e ancore (#id).
4. Controllo SEO: canonical, og:url, JSON-LD e sitemap.xml con base https://giorossi-sudo.tech/.
5. Censimento completo dei link esterni.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BASE_URL = "https://giorossi-sudo.tech/"

EXPECTED_HTML = [
    "index.html",
    "chi-sono.html",
    "404.html",
    "articoli/index.html",
    "articoli/fedora-hyprland.html",
    "articoli/xfce-dotfiles.html",
    "articoli/ottimizzare-xfce-poca-ram.html",
]

FORBIDDEN_PATHS = [
    "index.xml",
    "articoli/index.xml",
    "tags",
    "categories",
]


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []       # (tag, attr, val)
        self.canonical = None
        self.og_url = None
        self.title = ""
        self._in_title = False
        self._in_ldjson = False
        self.ldjson_blocks = []
        self._cur_ld = []
        self.imgs_without_alt = []
        self.svgs_without_aria = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if "id" in ad and ad["id"]:
            self.ids.add(ad["id"])
        if tag == "title":
            self._in_title = True
        elif tag == "link":
            rel = ad.get("rel", "")
            href = ad.get("href", "")
            if rel == "canonical":
                self.canonical = href
            if href:
                self.links.append((tag, "href", href))
        elif tag == "meta":
            if ad.get("property") == "og:url":
                self.og_url = ad.get("content", "")
            if ad.get("property") == "og:image" or ad.get("name") == "twitter:image":
                c = ad.get("content", "")
                if c:
                    self.links.append((tag, "content", c))
        elif tag == "a":
            href = ad.get("href", "")
            self.links.append((tag, "href", href))
        elif tag == "img":
            src = ad.get("src", "")
            if src:
                self.links.append((tag, "src", src))
            srcset = ad.get("srcset", "")
            if srcset:
                for part in srcset.split(","):
                    u = part.strip().split()[0]
                    if u:
                        self.links.append((tag, "srcset", u))
            if not ad.get("alt"):
                self.imgs_without_alt.append(src)
        elif tag == "svg":
            if ad.get("aria-hidden") != "true" and not ad.get("aria-label"):
                self.svgs_without_aria.append(tag)
        elif tag == "script" and ad.get("type") == "application/ld+json":
            self._in_ldjson = True
            self._cur_ld = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_ldjson:
            self._in_ldjson = False
            self.ldjson_blocks.append("".join(self._cur_ld))

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ldjson:
            self._cur_ld.append(data)


def resolve_local_path(page_rel: Path, target_path: str) -> Path:
    if target_path.startswith("/"):
        cand = PUBLIC / target_path.lstrip("/")
    else:
        cand = (PUBLIC / page_rel).parent / target_path
    if cand.is_dir():
        cand = cand / "index.html"
    return cand.resolve()


def main():
    errors = []
    if not PUBLIC.is_dir():
        print(f"ERRORE: cartella {PUBLIC} non trovata.", file=sys.stderr)
        return 1

    # 0. Controllo assenza di github.io ( come baseURL del sito ) o localhost in qualsiasi file pubblicato
    for p in sorted(PUBLIC.rglob("*")):
        if p.is_file() and p.suffix in (".html", ".xml", ".txt", ".css"):
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if "localhost:" in txt or "127.0.0.1" in txt or "giorossi-sudo.github.io" in txt:
                errors.append(f"{p.relative_to(PUBLIC)}: contiene URL non di produzione (localhost o giorossi-sudo.github.io)")

    # 1. File proibiti (RSS / taxonomy)
    for fp in FORBIDDEN_PATHS:
        p = PUBLIC / fp
        if p.exists():
            errors.append(f"Trovato percorso disabilitato: {fp}")

    # 2. Pagine attese
    for exp in EXPECTED_HTML:
        if not (PUBLIC / exp).is_file():
            errors.append(f"Pagina mancante in public/: {exp}")

    # Analisi di tutte le pagine HTML generate
    html_files = sorted(PUBLIC.rglob("*.html"))
    inspectors = {}
    external_links = set()

    for hf in html_files:
        rel = hf.relative_to(PUBLIC)
        ins = PageInspector()
        ins.feed(hf.read_text(encoding="utf-8"))
        inspectors[rel] = ins

        # Accessibilità base: alt su img, aria-hidden su svg decorativi
        for s in ins.imgs_without_alt:
            errors.append(f"{rel}: <img> privo di attributo alt ({s})")
        if ins.svgs_without_aria:
            errors.append(f"{rel}: <svg> privo di aria-hidden='true'")

        # Canonical e og:url
        if not ins.canonical or not ins.canonical.startswith(BASE_URL):
            errors.append(f"{rel}: canonical non valido ({ins.canonical})")
        if not ins.og_url or not ins.og_url.startswith(BASE_URL):
            errors.append(f"{rel}: og:url non valido ({ins.og_url})")
        if ins.canonical != ins.og_url:
            errors.append(f"{rel}: canonical ({ins.canonical}) != og:url ({ins.og_url})")

        # JSON-LD
        if str(rel) != "404.html":
            if not ins.ldjson_blocks:
                errors.append(f"{rel}: blocco JSON-LD mancante")
            for raw in ins.ldjson_blocks:
                try:
                    parsed = json.loads(raw)
                except Exception as exc:
                    errors.append(f"{rel}: JSON-LD non valido: {exc}")
                    continue
                raw_dump = json.dumps(parsed)
                if BASE_URL not in raw_dump:
                    errors.append(f"{rel}: JSON-LD non contiene {BASE_URL}")

    # 3. Validazione link interni e ancore
    for rel, ins in inspectors.items():
        for tag, attr, val in ins.links:
            if not val:
                errors.append(f"{rel}: attributo vuoto {tag}[{attr}]")
                continue
            if val.startswith(("http://", "https://")):
                if val.startswith(BASE_URL):
                    # URL assoluto del sito stesso (es. og:image, canonical)
                    sub = "/" + val[len(BASE_URL):]
                    target_file = resolve_local_path(rel, sub)
                    if not target_file.is_file():
                        errors.append(f"{rel}: URL assoluto interno rotto {val} -> {target_file}")
                else:
                    external_links.add(val)
                continue
            if val.startswith(("mailto:", "tel:")):
                continue

            parsed = urlparse(val)
            path_part = unquote(parsed.path)
            frag = parsed.fragment

            if not path_part:
                target_file = (PUBLIC / rel).resolve()
            else:
                target_file = resolve_local_path(rel, path_part)

            if not target_file.is_file():
                errors.append(f"{rel}: link interno rotto '{val}' -> {target_file}")
                continue

            if frag:
                target_rel = target_file.relative_to(PUBLIC)
                target_ins = inspectors.get(target_rel)
                if target_ins and frag not in target_ins.ids:
                    errors.append(f"{rel}: ancora '#{frag}' non trovata in {target_rel}")

    # 4. Sitemap
    sitemap_path = PUBLIC / "sitemap.xml"
    if not sitemap_path.is_file():
        errors.append("sitemap.xml mancante")
    else:
        sm = sitemap_path.read_text(encoding="utf-8")
        locs = re.findall(r"<loc>([^<]+)</loc>", sm)
        if len(locs) != 6:
            errors.append(f"sitemap.xml contiene {len(locs)} URL invece di 6: {locs}")
        for loc in locs:
            if not loc.startswith(BASE_URL):
                errors.append(f"sitemap.xml loc senza {BASE_URL}: {loc}")
            if "404.html" in loc:
                errors.append("sitemap.xml non deve includere 404.html")

    if errors:
        print("FALLITO! Errori riscontrati:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(html_files)} pagine HTML verificate, 0 link interni rotti, SEO/JSON-LD/sitemap conformi.")
    print(f"Link esterni censiti ({len(external_links)}):")
    for ext in sorted(external_links):
        print(f"  - {ext}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
