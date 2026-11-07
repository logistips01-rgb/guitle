"""Página "Chollos de hoy" (guitle.com/hoy/ y /<país>/hoy/): enlace de la bio de Instagram. La página es fija; las
guitarras del día las lee hoy.js de data/hoy/<país>.json, que guarda la sesión de redes cada día."""
import json

from . import pages

TXT = {
    "es": ("Chollos de hoy", "Las guitarras que hemos publicado hoy en Instagram, con su mejor precio.", "Publicados el {d}.",
           "Hoy aún no hay chollos publicados.", "Ver el catálogo"),
    "en": ("Today's deals", "The guitars we posted on Instagram today, at their best price.", "Posted on {d}.",
           "No deals posted yet today.", "Browse the catalogue"),
    "fr": ("Les bons plans du jour", "Les guitares publiées aujourd'hui sur Instagram, au meilleur prix.", "Publiés le {d}.",
           "Pas encore de bons plans aujourd'hui.", "Voir le catalogue"),
    "it": ("Le offerte di oggi", "Le chitarre che abbiamo pubblicato oggi su Instagram, al miglior prezzo.", "Pubblicate il {d}.",
           "Oggi non ci sono ancora offerte.", "Vai al catalogo"),
    "de": ("Die Angebote von heute", "Die Gitarren, die wir heute auf Instagram gezeigt haben, zum besten Preis.",
           "Veröffentlicht am {d}.", "Heute noch keine Angebote.", "Zum Katalog"),
    "pt": ("Promoções de hoje", "As guitarras que publicámos hoje no Instagram, ao melhor preço.", "Publicadas a {d}.",
           "Ainda não há promoções hoje.", "Ver o catálogo"),
    "br": ("Ofertas de hoje", "As guitarras que postamos hoje no Instagram, pelo melhor preço.", "Postadas em {d}.",
           "Ainda não há ofertas hoje.", "Ver o catálogo"),
    "nl": ("Aanbiedingen van vandaag", "De gitaren die we vandaag op Instagram hebben gezet, voor de beste prijs.",
           "Geplaatst op {d}.", "Vandaag nog geen aanbiedingen.", "Naar de catalogus"),
}


def _box(pais, lang):
    title, desc, date, empty, catalog = TXT.get(lang, TXT["en"])
    t = json.dumps({"date": date, "empty": empty, "catalog": catalog}, ensure_ascii=False).replace("'", "&#39;")
    return title, desc, (f'<section class="hub-sec"><div id="hoy" data-pais="{pais}" data-t=\'{t}\'>'
                         f'<p class="hub-intro">…</p></div></section>\n<script src="/hoy.js" defer></script>')


def write_spain():
    title, desc, body = _box("es", "es")
    page = pages._hub("hoy/", f"{title} · guitle", title, desc, [], {}, "hoy/")
    page = page.replace("  <footer", f"{body}\n  <footer", 1)
    pages._write(pages.ROOT / "hoy" / "index.html", page)


def write_country(code, intl):
    """La página del país; devuelve su URL."""
    s, t = intl.SITES[code], intl.strings(code)
    title, desc, body = _box(code, s["t"])
    url = f"/{code}/hoy/"
    html = (intl._head(code, f"{title} · guitle", desc, url, '<link rel="stylesheet" href="/catalogo.css">\n<style>.hub-sec{margin-top:18px}</style>')
            + "</head>\n<body>\n<main>\n"
            f'  <div class="topbar"><div class="row">{intl._logo(code, t)}<a class="navlink" href="/{code}/">{intl.esc(t["home"])}</a></div></div>\n'
            f'  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{intl.esc(title)}</h2>\n'
            f'  <p class="hub-intro" style="color:var(--text-secondary)">{intl.esc(desc)}</p>\n  {body}\n'
            f'  {intl._foot(code, t)}\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n')
    pages._write(pages.ROOT / code / "hoy" / "index.html", html)
    return url


def fix_fotos():
    """Las fotos de data/hoy/<país>.json (las elige la sesión de redes al publicar) marcadas como cortadas o de espaldas
    en la revisión de fotos (data/fotos-revisadas.json: 1 espalda, 2 cortada) se cambian por la miniatura actual de su
    ficha en el catálogo. Solo usa la biblioteca estándar: lo lanza r2.yml antes de subir la web."""
    import glob
    root = pages.ROOT
    try:
        bad = {k for k, v in json.loads((root / "data" / "fotos-revisadas.json").read_text()).items() if v}
    except (FileNotFoundError, json.JSONDecodeError):
        return 0
    files = sorted(glob.glob(str(root / "data" / "hoy" / "*.json")))
    hoy = {f: json.loads(open(f, encoding="utf-8").read()) for f in files}
    need = {i.get("slug") for d in hoy.values() for i in d.get("items", []) if i.get("img") in bad}
    if not need:
        return 0
    th = {}
    for cat in glob.glob(str(root / "data" / "catalog" / "**" / "*.json"), recursive=True):
        try:
            for prod in json.loads(open(cat, encoding="utf-8").read()).get("products", []):
                if prod.get("slug") in need and prod.get("th") and prod["th"] not in bad:
                    th.setdefault(prod["slug"], prod["th"])
        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            continue
    n = 0
    for f, d in hoy.items():
        changed = False
        for i in d.get("items", []):
            if i.get("img") in bad and th.get(i.get("slug")):
                i["img"] = th[i["slug"]]
                changed = True
                n += 1
        if changed:
            open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False))
    print(f"hoy: {n} fotos cortadas o de espaldas cambiadas por la de su ficha")
    return n


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["--fotos"]:
        fix_fotos()
    else:
        write_spain()
