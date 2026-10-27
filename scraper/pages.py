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

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "g"
SITE = "https://guitle.com"
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


def _render(product, kind, store_names):
    k = KINDS[kind]
    esc = lambda v: html.escape(str(v or ""), quote=True)
    name, brand, slug = product["name"], product.get("brand") or "", product["slug"]
    stores = sorted({store_names.get(i["s"], i["s"]) for i in product["items"]})
    n = len(stores)
    desc = (f"Precio de la {name}: compáralo en {n} {'tienda' if n == 1 else 'tiendas'} "
            f"({', '.join(stores[:4])}{'…' if n > 4 else ''}) y mira su histórico para saber si es buen momento para comprar.")
    img = f"/img/p/{product['th']}" if product.get("th") else None
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "brand": {"@type": "Brand", "name": brand} if brand else None, "category": k["label"],
          "image": SITE + img if img else None, "gtin13": product.get("ean"), "url": f"{SITE}/g/{slug}.html"}
    ld = {key: v for key, v in ld.items() if v}
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2a78d6">
<title>{esc(name)}: precio e histórico · guitle</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/g/{slug}.html">
<meta property="og:title" content="{esc(name)}: precio e histórico">
<meta property="og:description" content="{esc(desc)}">
{f'<meta property="og:image" content="{SITE}{img}">' if img else ''}
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="stylesheet" href="/fonts/inter.css">
<link rel="stylesheet" href="/catalogo.css">
<link rel="stylesheet" href="/producto.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script src="/vendor/chart.umd.min.js"></script>
</head>
<body data-id="{esc(product['id'])}" data-kind="{kind}" data-src="/{k['src']}" data-history="/{k['history']}"{f' data-sku="{esc(product["sku"])}"' if product.get('sku') else ''}>
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
      <div id="price" class="big">&nbsp;</div>
      <div id="where" class="muted">Comparamos su precio en {n} {'tienda' if n == 1 else 'tiendas'}: {esc(', '.join(stores))}.</div>
      <div id="verdict" class="verdict hidden"></div>
      {f'<div class="muted small">EAN {esc(product["ean"])}</div>' if product.get('ean') else ''}
    </div>
  </article>
  <section><h3>Tiendas</h3><div class="table-wrap"><table id="stores"></table></div></section>
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
        text = _render(p, kind, store_names)
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
