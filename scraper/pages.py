"""Páginas propias de cada guitarra (g/<slug>.html) y sitemap.xml, para que Google las encuentre.

La página es estática en lo que no cambia a diario (nombre, marca, tipo, foto, tiendas); precios, veredicto e
histórico los pinta producto.js con los JSON del catálogo. Así no se reescriben miles de ficheros cada día:
un fichero solo se escribe si su contenido cambia.
"""
import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "g"
SITE = "https://guitle.com"
AMAZON_TAG = "guitle-21"  # Afiliados de Amazon (ID de tienda)
# Por categoría: título de la sección, página del catálogo y JSON (relativos a la raíz del sitio).
KINDS = {
    "electrica": {"label": "Guitarras eléctricas", "list": "catalogo.html",
                  "src": "data/catalog/products.json", "history": "data/catalog/history.json"},
    "acustica": {"label": "Guitarras acústicas", "list": "acusticas.html",
                 "src": "data/catalog/acusticas/acusticas.json", "history": "data/catalog/acusticas/history.json"},
    "clasica": {"label": "Guitarras clásicas", "list": "clasicas.html",
                "src": "data/catalog/acusticas/clasicas.json", "history": "data/catalog/acusticas/history.json"},
    "teclado": {"label": "Teclados y pianos", "list": "teclados.html",
                "src": "data/catalog/equipo/teclados.json", "history": "data/catalog/equipo/history.json"},
    "pedal": {"label": "Pedales de efectos", "list": "pedales.html",
              "src": "data/catalog/equipo/pedales.json", "history": "data/catalog/equipo/history.json"},
    "bajo": {"label": "Bajos", "list": "bajos.html",
             "src": "data/catalog/mas/bajos.json", "history": "data/catalog/mas/history.json"},
    "ampli": {"label": "Amplificadores", "list": "amplificadores.html",
              "src": "data/catalog/mas/amplis.json", "history": "data/catalog/mas/history.json"},
    "estuche": {"label": "Fundas y estuches", "list": "estuches.html",
                "src": "data/catalog/mas/estuches.json", "history": "data/catalog/mas/history.json"},
    "micro": {"label": "Micrófonos", "list": "micros.html",
              "src": "data/catalog/mas/micros.json", "history": "data/catalog/mas/history.json"},
    "varios": {"label": "Accesorios", "list": "varios.html",
               "src": "data/catalog/mas/varios.json", "history": "data/catalog/mas/history.json"},
}


def slug_for(product):
    """'Fender Player II Stratocaster RW Polar White' + EAN → 'fender-player-ii-stratocaster-rw-polar-white-885978109302'."""
    text = unicodedata.normalize("NFKD", product["name"]).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:80].rstrip("-")
    suffix = product.get("ean") or re.sub(r"[^a-z0-9]", "", str(product["id"]).lower())[-10:]
    return f"{text}-{suffix}"


PALETTE = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"]


def eur(v):
    """721.41 → '721,41 €'; 1299 → '1.299 €' (formato español)."""
    whole = int(round(v * 100)) // 100
    cents = int(round(v * 100)) % 100
    txt = f"{whole:,}".replace(",", ".")
    return f"{txt},{cents:02d} €" if cents else f"{txt} €"


MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def _day(iso):
    y, m, d = iso[:10].split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]}"


def _rows(product, store_names, colors):
    esc = lambda v: html.escape(str(v or ""), quote=True)
    best = product["items"][0]["p"]
    out = []
    for n, i in enumerate(product["items"]):
        store = esc(store_names.get(i["s"], i["s"]))
        go = f'href="{esc(i["u"])}" target="_blank" rel="sponsored noopener"' if i.get("u") else ""
        name = f'<a class="store-link" {go}>{store}</a>' if go else store
        if i.get("m"):  # precio añadido a mano a partir de una captura: se dice cuándo se comprobó
            name += f'<small class="manual">comprobado a mano el {_day(i["d"])}</small>'
        stock = '<span class="tag">en stock</span>' if i.get("st") is True else '<span class="tag warn">sin stock</span>' if i.get("st") is False else ""

        diff = "mejor precio" if n == 0 else "+" + eur(round(i["p"] - best, 2))
        button = f'<a class="go" {go}><span class="go-long">Ir a la tienda</span><span class="go-short">Ir</span></a>' if go else ""
        out.append(f'<tr class="{"best-row" if n == 0 else ""}"><td><span class="swatch" style="background:var({colors.get(i["s"], "--reference")})"></span>{name}</td>'
                   f'<td class="num"><strong>{eur(i["p"])}</strong></td><td class="num muted col-diff">{diff}</td><td>{stock}</td>'
                   f'<td class="num">{button}</td></tr>')
    return "\n".join(out)


def _render(product, kind, store_names, colors):
    k = KINDS[kind]
    esc = lambda v: html.escape(str(v or ""), quote=True)
    name, brand, slug = product["name"], product.get("brand") or "", product["slug"]
    stores = sorted({store_names.get(i["s"], i["s"]) for i in product["items"]})
    n = len(stores)
    prices = [i["p"] for i in product["items"]]
    best = product["items"][0]
    best_store = store_names.get(best["s"], best["s"])
    where = f"en {best_store}" + (f" · {n} tiendas" + (f", hasta {eur(round(max(prices) - min(prices)))} de diferencia"
                                                        if max(prices) - min(prices) >= 1 else "") if n > 1 else "")
    title = f"{name}: precio desde {eur(best['p'])} " + (f"en {n} tiendas" if n > 1 else f"en {best_store}")
    desc = (f"{name} desde {eur(best['p'])} en {best_store}. Compara su precio en {n} {'tienda' if n == 1 else 'tiendas'} "
            f"({', '.join(stores[:4])}{'…' if n > 4 else ''}) y mira su histórico para saber si es buen momento para comprar.")
    img = f"/img/p/{product['th']}" if product.get("th") else None
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "brand": {"@type": "Brand", "name": brand} if brand else None, "category": k["label"],
          "image": SITE + img if img else None, "gtin13": product.get("ean"), "url": f"{SITE}/g/{slug}.html",
          # Precio para los resultados de Google ("desde 721 € · 7 ofertas").
          "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": min(prices), "highPrice": max(prices),
                     "offerCount": len(product["items"])}}
    ld = {key: v for key, v in ld.items() if v}
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2a78d6">
<title>{esc(title)} · guitle</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/g/{slug}.html">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
{f'<meta property="og:image" content="{SITE}{img}">' if img else ''}
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="stylesheet" href="/fonts/inter.css">
<link rel="stylesheet" href="/catalogo.css">
<link rel="stylesheet" href="/producto.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script src="/vendor/chart.umd.min.js"></script>
</head>
<body data-ean="{esc(product.get('ean') or '')}" data-best="{best['p']}" data-history="/{k['history']}"{f' data-sku="{esc(product["sku"])}"' if product.get('sku') else ''}>
<script type="application/json" id="stores-data">{json.dumps({"names": {i["s"]: store_names.get(i["s"], i["s"]) for i in product["items"]}, "colors": colors} | ({"hk": product["hk"]} if product.get("hk") else {}), ensure_ascii=False)}</script>
<main>
  <div class="topbar">
    <div class="row">
      <h1 style="flex:1;margin:0"><a class="logo" href="/" aria-label="guitle, inicio"><img src="/icons/icon.svg" alt=""><span class="stack"><span class="word">gu<span class="i">ı</span>tle</span><span class="tag">guitarras al mejor precio</span></span></a></h1>
      <a class="navlink" href="/{k['list']}">{esc(k['label'])}</a>
    </div>
  </div>
  <nav class="crumbs"><a href="/">Inicio</a> › <a href="/{k['list']}">{esc(k['label'])}</a> › <a href="/marca/{plain_slug(brand)}.html">{esc(brand)}</a></nav>
  <article class="product">
    {f'<div class="pimg"><img src="{img}" alt="{esc(name)}"></div>' if img else ''}
    <div class="pinfo">
      <div class="muted">{esc(brand)}{' · ' + esc(product.get('type')) if product.get('type') and product.get('type') != 'Otras' else ''}{' · zurda' if product.get('lh') else ''}</div>
      <h2 class="pname">{esc(name)}</h2>
      <div id="price" class="big">{eur(best['p'])}</div>
      <div id="where" class="muted">{esc(where)}</div>
      <div id="verdict" class="verdict hidden"></div>
      {f'<div class="muted small">EAN {esc(product["ean"])}</div>' if product.get('ean') else ''}
    </div>
  </article>
  <section><h3>Tiendas</h3><div class="table-wrap"><table id="stores">{_rows(product, store_names, colors)}</table></div>
    {f'<p class="amazon-cta"><a class="go" href="https://www.amazon.es/s?k={quote_plus(name)}&amp;tag={AMAZON_TAG}" target="_blank" rel="sponsored noopener">Buscar en Amazon</a></p>' if kind == "varios" else f'<p class="muted small amazon">¿Prefieres comprar en Amazon? <a href="https://www.amazon.es/s?k={quote_plus(name)}&amp;tag={AMAZON_TAG}" target="_blank" rel="sponsored noopener">Buscar este modelo en Amazon</a></p>'}</section>
  <section><h3>Histórico de precios</h3>
    <div class="stats" id="stats"></div>
    <div class="chart-box"><canvas id="chart"></canvas></div>
    <p class="muted small" id="chart-note"></p>
  </section>
  <footer class="site-foot">
    <span>Algunos enlaces a tiendas son de afiliado: si compras, guitle puede recibir una comisión, sin coste para ti.</span>
    <span><a href="/legal.html#aviso">Aviso legal</a> · <a href="/legal.html#privacidad">Privacidad</a> · <a href="/legal.html#cookies">Cookies</a></span>
  </footer>
</main>
<script src="/producto.js"></script>
<script src="/c.js" defer></script>
</body>
</html>
"""


def write_pages(kind, products, store_names):
    """Escribe (o deja como están) las páginas de una categoría. Devuelve los slugs."""
    PAGES.mkdir(exist_ok=True)
    slugs, written = [], 0
    for p in products:
        page = PAGES / f"{p['slug']}.html"
        # Colores por guitarra (nunca pasa de 8 tiendas): distintos entre sí en la tabla y en la gráfica.
        colors = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sorted({i["s"] for i in p["items"]}))}
        text = _render(p, kind, store_names, colors)
        if not page.exists() or page.read_text(encoding="utf-8") != text:
            page.write_text(text, encoding="utf-8")
            written += 1
        slugs.append(p["slug"])
    (PAGES / f"_{kind}.txt").write_text("\n".join(sorted(slugs)) + "\n", encoding="utf-8")
    print(f"páginas {kind}: {len(slugs)} ({written} nuevas o cambiadas)", flush=True)
    write_sitemap()
    return slugs


def write_sitemap():
    """sitemap.xml con las páginas principales y las de todas las guitarras (listas g/_<categoría>.txt)."""
    urls = ["", "catalogo.html", "acusticas.html", "clasicas.html", "teclados.html", "pedales.html", "bajos.html",
            "amplificadores.html", "estuches.html", "micros.html", "varios.html", "chollos.html",
            "black-friday.html", "guitarras.html", "paises.html"]
    hubs = PAGES / "_hubs.txt"
    if hubs.exists():
        urls += hubs.read_text(encoding="utf-8").split()
    for lst in sorted(p for p in PAGES.glob("_*.txt") if p.name != "_hubs.txt"):
        urls += [f"g/{s}.html" for s in lst.read_text(encoding="utf-8").split()]
    body = "\n".join(f"  <url><loc>{SITE}/{u}</loc></url>" for u in urls)
    text = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    path = ROOT / "sitemap.xml"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


# --- Páginas por marca (marca/<marca>.html) y por tipo (tipo/<categoría>-<tipo>.html) ----------------------

TYPE_TITLES = {"ST": "tipo Stratocaster (ST)", "T": "tipo Telecaster (T)", "Single cut": "single cut (tipo Les Paul)",
               "Double cut": "double cut (tipo SG y PRS)", "Semihueca": "semihuecas y de caja",
               "Offset / Retro": "offset y retro (Jazzmaster, Jaguar, Mustang…)", "Moderna / Metal": "modernas y de metal",
               "Dreadnought": "dreadnought", "Auditorio / Concierto": "de auditorio y concierto", "Jumbo": "jumbo",
               "Parlor": "parlor", "12 cuerdas": "de 12 cuerdas", "Tamaño reducido": "de tamaño reducido",
               "Roundback": "roundback", "Clásica": "clásicas de concierto", "Flamenca": "flamencas",
               "Electroclásica": "electroclásicas",
               "Piano digital": "pianos digitales", "Piano de escenario": "pianos de escenario",
               "Teclado portátil": "teclados portátiles y de acompañamiento", "Sintetizador": "sintetizadores",
               "Controlador MIDI": "controladores MIDI", "Piano acústico": "pianos acústicos",
               "Overdrive y distorsión": "de overdrive, distorsión y fuzz", "Delay": "de delay", "Reverb": "de reverb",
               "Modulación": "de modulación (chorus, flanger, phaser, trémolo)", "Compresor": "compresores",
               "Wah y volumen": "de wah y volumen", "Looper": "loopers", "Afinador": "afinadores", "Multiefectos": "multiefectos",
               "Para bajo": "para bajo", "Octavador y pitch": "octavadores y de pitch", "Ecualizador": "ecualizadores",
               "Puerta de ruido": "puertas de ruido", "Sintetizador": "sintetizadores",
               "4 cuerdas": "de 4 cuerdas", "5 cuerdas": "de 5 cuerdas", "6 cuerdas o más": "de 6 cuerdas o más",
               "Acústico": "acústicos", "Fretless": "fretless (sin trastes)", "Escala corta": "de escala corta",
               "Para acústica": "para acústica", "Combo": "combo", "Cabezal": "de cabezal", "Pantalla": "de pantalla",
               "De auriculares y portátil": "de auriculares y portátiles", "Para clásica": "para clásica",
               "Para eléctrica": "para eléctrica", "Inalámbrico": "inalámbricos", "USB": "USB", "De cinta": "de cinta",
               "Para instrumento": "para instrumento y batería", "Condensador": "de condensador", "Dinámico": "dinámicos",
               "Cuerdas": "cuerdas de guitarra y bajo", "Púas": "púas", "Correas": "correas de guitarra y bajo",
               "Cables": "cables de instrumento", "Afinadores": "afinadores", "Cejillas": "cejillas",
               "Soportes": "soportes y colgadores de guitarra", "Pastillas": "pastillas (pickups)",
               "Recambios": "recambios (clavijas, puentes, golpeadores…)", "Mantenimiento": "limpieza y mantenimiento"}
NOUN = {"electrica": "Guitarras eléctricas", "acustica": "Guitarras acústicas", "clasica": "Guitarras clásicas",
        "teclado": "Teclados y pianos", "pedal": "Pedales", "bajo": "Bajos", "ampli": "Amplificadores",
        "estuche": "Fundas y estuches", "micro": "Micrófonos",
        "varios": "Accesorios"}
# Páginas por presupuesto (precio más bajo de hoy por debajo del límite) y guitarras que muestra cada una.
BUDGETS = {"electrica": (150, 300, 500, 1000, 2000), "acustica": (150, 300, 500, 1000), "clasica": (100, 200, 400),
           "teclado": (200, 500, 1000), "pedal": (50, 100, 200), "bajo": (200, 400, 800), "ampli": (100, 300, 600),
           "estuche": (50, 100), "micro": (50, 100, 200), "varios": (10, 25, 50)}
GUITAR_KINDS = {"electrica", "acustica", "clasica"}
BUDGET_TILES = 120
NOPHOTO = ('<svg class="nophoto" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3l-6.5 6.5"/><path d="M19.5 1.5l3 3-1.5 1.5-3-3z"/>'
           '<path d="M14.5 9.5c-1.6-1.6-3.9-1.3-5 .2-1 .4-2.6.1-4 1.5-2.1 2.1-1.7 5.4.6 7.7s5.6 2.7 7.7.6c1.4-1.4 1.1-3 1.5-4 '
           '1.5-1.1 1.8-3.4.2-5z"/><circle cx="9.6" cy="14.4" r="1.4"/></svg>')


def plain_slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def _tile(p, store_names):
    esc = lambda v: html.escape(str(v or ""), quote=True)
    best = p["items"][0]
    n = len({i["s"] for i in p["items"]})
    img = f'<img loading="lazy" src="/img/p/{esc(p["th"])}" alt="">' if p.get("th") else NOPHOTO
    sub = esc(p.get("type")) if p.get("type") and p.get("type") != "Otras" else ""
    return (f'<a class="tile" href="/g/{esc(p["slug"])}.html"><div class="img">{img}</div><div class="body">'
            f'<span class="brand">{esc(p.get("brand"))}{" · " + sub if sub else ""}</span><span class="name">{esc(p["name"])}</span>'
            f'<span class="price"><strong>{eur(best["p"])}</strong></span><span class="foot"><span>{esc(store_names.get(best["s"], best["s"]))}</span>'
            f'<span class="stores-n">{n} {"tienda" if n == 1 else "tiendas"}</span></span></div></a>')


def _hub(path, title, h1, intro, sections, store_names, canonical):
    esc = lambda v: html.escape(str(v or ""), quote=True)
    body = "".join(f'<section class="hub-sec">{f"<h2>{esc(h)}</h2>" if h else ""}<div class="grid">'
                   + "".join(_tile(p, store_names) for p in prods) + "</div></section>" for h, prods in sections)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2a78d6">
<title>{esc(title)} · guitle</title>
<meta name="description" content="{esc(intro)}">
<link rel="canonical" href="{SITE}/{canonical}">
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="stylesheet" href="/fonts/inter.css">
<link rel="stylesheet" href="/catalogo.css">
<style>.hub-sec {{ margin-top: 26px; }} .hub-sec h2 {{ font-size: 1.15rem; margin: 0 0 10px; }}
.hub-intro {{ color: var(--text-secondary); max-width: 780px; }} .links {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }}</style>
</head>
<body>
<main>
  <div class="topbar">
    <div class="row">
      <h1 style="flex:1;margin:0"><a class="logo" href="/" aria-label="guitle, inicio"><img src="/icons/icon.svg" alt=""><span class="stack"><span class="word">gu<span class="i">ı</span>tle</span><span class="tag">guitarras al mejor precio</span></span></a></h1>
      <a class="navlink" href="/marcas.html">Marcas</a>
    </div>
  </div>
  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{esc(h1)}</h2>
  <p class="hub-intro">{esc(intro)}</p>
  {body}
  <footer class="site-foot">
    <span>Algunos enlaces a tiendas son de afiliado: si compras, guitle puede recibir una comisión, sin coste para ti.</span>
    <span><a href="/legal.html#aviso">Aviso legal</a> · <a href="/legal.html#privacidad">Privacidad</a> · <a href="/legal.html#cookies">Cookies</a></span>
  </footer>
</main>
<script src="/c.js" defer></script>
</body>
</html>
"""


def _summary(prods, store_names):
    prices = [p["items"][0]["p"] for p in prods]
    cheapest = min(prods, key=lambda p: p["items"][0]["p"])
    multi = sum(len({i["s"] for i in p["items"]}) > 1 for p in prods)
    return (f"{len(prods)} modelos desde {eur(min(prices))} hasta {eur(max(prices))}. El más barato hoy: {cheapest['name']}, "
            f"a {eur(cheapest['items'][0]['p'])} en {store_names.get(cheapest['items'][0]['s'], cheapest['items'][0]['s'])}. "
            f"{multi} se pueden comparar en varias tiendas; en cada una verás su histórico de precios.")


def write_hubs():
    """Páginas de marca y de tipo con todas las guitarras (las tres categorías), e índice marcas.html."""
    catalogs = {}
    for kind, k in KINDS.items():
        try:
            data = json.loads((ROOT / k["src"]).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        catalogs[kind] = data
    names = {s: n for d in catalogs.values() for s, n in d["stores"].items()}
    order = lambda p: (-len({i["s"] for i in p["items"]}), p["items"][0]["p"])
    pages, written = [], 0
    by_brand = {}
    for kind, d in catalogs.items():
        for p in d["products"]:
            if p.get("brand") and p.get("slug"):
                by_brand.setdefault(p["brand"], {}).setdefault(kind, []).append(p)
    brands = []
    for brand, kinds in by_brand.items():
        allp = [p for ps in kinds.values() for p in ps]
        url = f"marca/{plain_slug(brand)}.html"
        sections = [(NOUN[k] if len(kinds) > 1 else None, sorted(ps, key=order)) for k, ps in kinds.items()]
        # Una marca solo de guitarras: "Guitarras Ibanez"; si vende también teclados o pedales, su nombre a secas.
        noun = f"Guitarras {brand}" if set(kinds) <= GUITAR_KINDS else brand
        written += _write(ROOT / url, _hub(url, f"{noun}: precios y comparativa", noun,
                                           _summary(allp, names), sections, names, url))
        pages.append(url)
        brands.append((brand, url, len(allp)))
    for kind, d in catalogs.items():
        types = {}
        for p in d["products"]:
            if p.get("type") and p["type"] != "Otras" and p.get("slug"):
                types.setdefault(p["type"], []).append(p)
        for t, ps in types.items():
            if len(ps) < 3:
                continue
            url = f"tipo/{kind}-{plain_slug(t)}.html"
            # "Pianos digitales" a secas (no "Teclados y pianos pianos digitales"); el resto, categoría + tipo.
            label = (TYPE_TITLES.get(t, t)[:1].upper() + TYPE_TITLES.get(t, t)[1:] if kind in ("teclado", "varios")
                     else f"{NOUN[kind]} {TYPE_TITLES.get(t, t)}")
            written += _write(ROOT / url, _hub(url, f"{label}: precios y comparativa", label, _summary(ps, names),
                                               [(None, sorted(ps, key=order))], names, url))
            pages.append(url)
    # Por presupuesto ("guitarra eléctrica por menos de 300 €"): las que hoy cuestan menos, las comparables primero.
    budget_links = []
    for kind, d in catalogs.items():
        prods = [p for p in d["products"] if p.get("slug") and p.get("items")]
        limits = BUDGETS.get(kind, ())
        links = []
        for limit in limits:
            ps = sorted((p for p in prods if p["items"][0]["p"] < limit), key=order)
            if len(ps) < 6:
                continue
            url = f"presupuesto/{kind}-menos-de-{limit}.html"
            links.append((f"Menos de {limit} €", url))
        for label, url in links:
            limit = int(url.rsplit("-", 1)[-1].split(".")[0])
            ps = sorted((p for p in prods if p["items"][0]["p"] < limit), key=order)
            noun = NOUN[kind]
            title = f"{noun} por menos de {limit} €: precios comparados"
            intro = (f"{noun} por menos de {limit} € en tiendas que venden en España, con el precio de cada tienda revisado "
                     f"cada día; primero las que puedes comparar en más tiendas. " + _summary(ps, names))
            chips = "".join(f'<a class="chip" href="/{u}">{html.escape(l)}</a>' for l, u in links if u != url)
            page = _hub(url, title, f"{noun} por menos de {limit} €", intro, [(None, ps[:BUDGET_TILES])], names, url)
            page = page.replace('<p class="hub-intro">', f'<div class="links">{chips}</div><p class="hub-intro">', 1)
            written += _write(ROOT / url, page)
            pages.append(url)
        budget_links += [(f"{NOUN[kind]}: {l.lower()}", u) for l, u in links]
    # Índice de marcas
    esc = lambda v: html.escape(str(v or ""), quote=True)
    links = "".join(f'<a class="chip" href="/{u}">{esc(b)} <span class="muted">({n})</span></a>'
                    for b, u, n in sorted(brands, key=lambda x: (-x[2], x[0])))
    index = _hub("marcas.html", "Marcas: precios por marca", "Marcas",
                 f"Compara precios de {len(brands)} marcas de guitarras, bajos, amplis, micrófonos, teclados y pedales en las tiendas de Europa.",
                 [], names, "marcas.html").replace('<p class="hub-intro">', f'<div class="links">{links}</div><p class="hub-intro">', 1)
    budgets = "".join(f'<a class="chip" href="/{u}">{esc(l)}</a>' for l, u in budget_links)
    index = index.replace("  <footer", f'  <section class="hub-sec"><h2>Por presupuesto</h2><div class="links">{budgets}</div></section>\n  <footer', 1)
    written += _write(ROOT / "marcas.html", index)
    # Marcas o tipos que ya no existen (p. ej. una marca renombrada) se borran.
    for folder in ("marca", "tipo", "presupuesto"):
        for f in (ROOT / folder).glob("*.html"):
            if f"{folder}/{f.name}" not in pages:
                f.unlink()
    (PAGES / "_hubs.txt").write_text("\n".join(["marcas.html"] + sorted(pages)) + "\n", encoding="utf-8")
    print(f"páginas de marca y tipo: {len(pages)} ({written} nuevas o cambiadas)", flush=True)
    write_sitemap()
