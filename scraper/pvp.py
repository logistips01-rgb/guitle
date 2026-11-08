"""PVP oficial de las marcas en España: Fender (es.fender.com), Gibson y Epiphone (gibson.com/es-eu) y Jackson
(es.jacksonguitars.com).

La web de Fender da el precio de cada color con su referencia de fábrica (0140550518) pero sin EAN. Las tiendas del
catálogo que publican esa referencia junto al EAN (Musicopolix, Session: campo "ref" de offers.json) hacen de
puente: el PVP se guarda en el histórico del catálogo bajo el EAN de la guitarra, como tienda "fender_es", y la
página de la guitarra lo dibuja como "PVP oficial" (no cuenta para el mejor precio).

Gibson y Jackson son tiendas Shopify: su /products/<ficha>.js da cada color con su código de barras (el EAN de las
tiendas) y su precio en euros, así que se enlazan directamente por EAN, como tiendas "gibson_eu" y "jackson_es".

Fender solo responde desde los runners de GitHub; robots.txt respetado, 3-6 s entre peticiones, rotación por antigüedad.

Uso:
    python -m scraper.pvp --minutes 40 --out F    # CI: lee un lote y lo guarda en F
    python -m scraper.pvp --merge F               # CI: lo fusiona en data/catalog/pvp.json y en el histórico
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from . import jsonld
from .catalog import load, sitemap_urls, write
from .common import normalize_id
from .fetch import Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog"
PVP = CATALOG / "pvp.json"
SITEMAP = "https://es.fender.com/sitemap.xml"
STORE = "fender_es"
# Webs de marca en Shopify: tienda en el histórico → sitemap, prefijo de mercado (precios en euros) y minutos por noche.
SHOPIFY = {"gibson_eu": ("https://www.gibson.com/sitemap.xml", "/es-eu", 15),
           "jackson_es": ("https://es.jacksonguitars.com/sitemap.xml", "", 8)}
ACCESSORY = re.compile(r"cable|footswitch|wrench|strap|string|pick|case|bag|stand|hanger|pedal|amp|cabinet|speaker"
                       r"|cover|shirt|hoodie|tee|hat|mug|poster|polish|cloth|tuner|knob|pickguard|bridge|saddle|nut|screw"
                       r"|neck|body|pickup|capo|slide|gift|card|wallet|keychain|bass", re.I)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read(fetcher, url):
    """{"status", "offers": {referencia: precio}} de una ficha de es.fender.com."""
    rec = {"url": url, "checked": now_iso(), "status": "error", "offers": {}}
    if not fetcher.allowed(url)[0]:
        rec["status"] = "robots_disallowed"
        return rec
    resp = fetcher.get(url)
    if resp.status_code in (404, 410):
        rec["status"] = "gone"
        return rec
    if resp.status_code != 200 or is_challenge(resp):
        rec["http_status"] = resp.status_code
        return rec
    for block in jsonld.load_blocks(BeautifulSoup(resp.text, "html.parser")):
        for node in jsonld._iter_nodes(block):
            if "product" not in jsonld._types(node):
                continue
            offers = node.get("offers")
            for o in offers if isinstance(offers, list) else [offers] if offers else []:
                ref = normalize_id(o.get("sku"))
                if ref and o.get("price") and (o.get("priceCurrency") or "EUR") == "EUR":
                    rec["offers"][ref] = float(o["price"])
    rec["status"] = "ok" if rec["offers"] else "no_price"
    return rec


def read_shopify(fetcher, url, market):
    """{"status", "offers": {EAN: precio}} de una ficha Shopify (/products/<ficha>.js, precios en céntimos)."""
    rec = {"url": url, "checked": now_iso(), "status": "error", "offers": {}}
    host, path = url.split("/products/", 1)
    js = f"{host}{market}/products/{path.split('?')[0]}.js"
    if not fetcher.allowed(js)[0]:
        rec["status"] = "robots_disallowed"
        return rec
    resp = fetcher.get(js)
    if resp.status_code in (404, 410):
        rec["status"] = "gone"
        return rec
    if resp.status_code != 200 or is_challenge(resp):
        rec["http_status"] = resp.status_code
        return rec
    try:
        variants = resp.json().get("variants") or []
    except ValueError:
        return rec
    for v in variants:
        ean = normalize_id(v.get("barcode")).lstrip("0")
        if ean.isdigit() and len(ean) >= 11 and v.get("price"):
            rec["offers"][ean] = round(v["price"] / 100, 2)
    rec["status"] = "ok" if rec["offers"] else "no_price"
    return rec


def scan_shopify(data, store, sitemap, market, minutes):
    """Lote de una web Shopify: primero las fichas sin leer, luego las más antiguas."""
    fetcher = Fetcher()
    pages = data.get("shopify", {}).get(store, {}).get("pages", {})
    try:
        urls = sorted({u for u in sitemap_urls(fetcher, sitemap, lambda loc: "sitemap_products" in loc) if "/products/" in u})
    except RuntimeError as exc:
        print(f"[pvp] {store}: {exc}", flush=True)
        return {"urls": [], "records": []}
    queue = sorted(urls, key=lambda u: (bool(ACCESSORY.search(u.rsplit("/", 1)[-1])), u in pages,
                                        pages.get(u, {}).get("checked", "")))
    out, deadline = {"urls": urls, "records": []}, time.monotonic() + minutes * 60
    for url in queue:
        if time.monotonic() > deadline:
            break
        rec = read_shopify(fetcher, url, market)
        out["records"].append(rec)
        if rec.get("http_status") in (403, 429):
            print(f"[pvp] {store}: HTTP {rec['http_status']}, se sigue mañana", flush=True)
            break
    stats = {}
    for r in out["records"]:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
    print(f"[pvp] {store}: {len(urls)} productos, {len(out['records'])} fichas {stats}", flush=True)
    return out


def scan(minutes):
    data = load(PVP, {"pages": {}, "prices": {}})
    fetcher = Fetcher()
    urls = sitemap_urls(fetcher, SITEMAP, lambda loc: "sitemap_products" in loc and "/en/" not in loc)
    urls = sorted({u for u in urls if "/products/" in u})
    pages = data["pages"]
    # Primero las guitarras: los accesorios (cables, pedales, cuerdas…) no los cruza el catálogo de guitarras.
    queue = sorted(urls, key=lambda u: (bool(ACCESSORY.search(u.rsplit("/", 1)[-1])), u in pages,
                                        pages.get(u, {}).get("checked", "")))
    print(f"[pvp] {len(urls)} productos en el sitemap, {sum(u not in pages for u in urls)} sin leer", flush=True)
    out, deadline = {"urls": urls, "records": []}, time.monotonic() + minutes * 60
    for url in queue:
        if time.monotonic() > deadline:
            break
        rec = read(fetcher, url)
        out["records"].append(rec)
        if rec.get("http_status") == 429:
            print("[pvp] 429: se sigue mañana", flush=True)
            break
    stats = {}
    for r in out["records"]:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
    print(f"[pvp] {len(out['records'])} fichas {stats}", flush=True)
    out["shopify"] = {store: scan_shopify(data, store, *conf) for store, conf in SHOPIFY.items()}
    return out


def _add(series, day, price):
    if series and series[-1][0] == day:
        series[-1][1] = price
    elif not series or series[-1][1] != price:
        series.append([day, price])


def merge(batch):
    data = load(PVP, {"pages": {}, "prices": {}})
    day = now_iso()[:10]
    for rec in batch["records"]:
        if rec["status"] in ("error", "robots_disallowed") and rec["url"] in data["pages"]:
            continue  # se conserva la última lectura buena
        data["pages"][rec["url"]] = {"checked": rec["checked"], "status": rec["status"]}
        for ref, price in rec["offers"].items():
            _add(data["prices"].setdefault(ref, []), day, price)
    alive = set(batch.get("urls") or data["pages"])
    data["pages"] = {u: p for u, p in data["pages"].items() if u in alive}
    for store, part in (batch.get("shopify") or {}).items():
        mine = data.setdefault("shopify", {}).setdefault(store, {"pages": {}, "prices": {}})
        for rec in part["records"]:
            if rec["status"] in ("error", "robots_disallowed") and rec["url"] in mine["pages"]:
                continue
            mine["pages"][rec["url"]] = {"checked": rec["checked"], "status": rec["status"]}
            for ean, price in rec["offers"].items():
                _add(mine["prices"].setdefault(ean, []), day, price)
        if part["urls"]:
            alive = set(part["urls"])
            mine["pages"] = {u: p for u, p in mine["pages"].items() if u in alive}
    write(PVP, data)
    link(data["prices"])
    link_ean(data.get("shopify", {}))


def link(prices):
    """Copia el PVP de cada referencia al histórico del catálogo, bajo el EAN de las guitarras con esa referencia."""
    offers = load(CATALOG / "offers.json", {})
    history = load(CATALOG / "history.json", {})
    eans = {}
    for o in offers.values():
        if o.get("ref") and o.get("ean"):
            eans.setdefault(o["ref"], set()).add(o["ean"])
    linked = 0
    for ref, series in prices.items():
        for ean in eans.get(ref, ()):
            history.setdefault(ean, {})[STORE] = series
            linked += 1
    write(CATALOG / "history.json", history)
    print(f"[pvp] {len(prices)} referencias con PVP, {linked} guitarras del catálogo enlazadas", flush=True)


def link_ean(shopify):
    """PVP de las webs Shopify al histórico de cada catálogo (eléctricas y acústicas), por EAN."""
    for folder in (CATALOG, CATALOG / "acusticas"):
        offers = load(folder / "offers.json", {})
        history = load(folder / "history.json", {})
        eans = {}
        for o in offers.values():
            if o.get("ean"):
                eans.setdefault(o["ean"].lstrip("0"), set()).add(o["ean"])
        linked = 0
        for store, part in shopify.items():
            for ean, series in part["prices"].items():
                for key in eans.get(ean, ()):
                    history.setdefault(key, {})[store] = series
                    linked += 1
        write(folder / "history.json", history)
        print(f"[pvp] {folder.name}: {linked} guitarras enlazadas con Gibson/Jackson", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=40)
    parser.add_argument("--out", help="guarda el lote en este fichero (CI)")
    parser.add_argument("--merge", help="fusiona un lote de --out")
    args = parser.parse_args(argv)
    if args.merge:
        merge(json.loads(Path(args.merge).read_text(encoding="utf-8")))
        return 0
    batch = scan(args.minutes)
    if args.out:
        Path(args.out).write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
    else:
        merge(batch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
