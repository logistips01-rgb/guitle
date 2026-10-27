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


def _rows(product, store_names, colors):
    esc = lambda v: html.escape(str(v or ""), quote=True)
    best = product["items"][0]["p"]
    out = []
    for n, i in enumerate(product["items"]):
        store = esc(store_names.get(i["s"], i["s"]))
        go = f'href="{esc(i["u"])}" target="_blank" rel="sponsored noopener"' if i.get("u") else ""
        name = f'<a class="store-link" {go}>{store}</a>' if go else store
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
<script type="application/json" id="stores-data">{json.dumps({"names": {i["s"]: store_names.get(i["s"], i["s"]) for i in product["items"]}, "colors": colors}, ensure_ascii=False)}</script>
<main>
  <div class="topbar">
    <div class="row">
      <h1 style="flex:1;margin:0"><a class="logo" href="/" aria-label="guitle, inicio"><img src="/icons/icon.svg" alt=""><span class="stack"><span class="word">gu<span class="i">ı</span>tle</span><span class="tag">guitarras al mejor precio</span></span></a></h1>
      <a class="navlink" href="/{k['list']}">{esc(k['label'])}</a>
    </div>
  </div>
  <nav class="crumbs"><a href="/">Inicio</a> › <a href="/{k['list']}">{esc(k['label'])}</a> › <a href="/{k['list']}?brand={esc(brand)}">{esc(brand)}</a></nav>
  <article class="product">
    <div class="pimg">{f'<img src="{img}" alt="{esc(name)}">' if img else ''}</div>
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
    <p class="muted small amazon">¿Prefieres comprar en Amazon? <a href="https://www.amazon.es/s?k={quote_plus(name)}&amp;tag={AMAZON_TAG}" target="_blank" rel="sponsored noopener">Buscar este modelo en Amazon</a></p></section>
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
    urls = ["", "catalogo.html", "acusticas.html", "clasicas.html", "guitarras.html"]
    for lst in sorted(PAGES.glob("_*.txt")):
        urls += [f"g/{s}.html" for s in lst.read_text(encoding="utf-8").split()]
    body = "\n".join(f"  <url><loc>{SITE}/{u}</loc></url>" for u in urls)
    text = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    path = ROOT / "sitemap.xml"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
