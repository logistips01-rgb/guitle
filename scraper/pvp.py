"""PVP oficial de Fender en España (es.fender.com), para todo el catálogo de eléctricas.

La web de Fender da el precio de cada color con su referencia de fábrica (0140550518) pero sin EAN. Las tiendas del
catálogo que publican esa referencia junto al EAN (Musicopolix, Session: campo "ref" de offers.json) hacen de
puente: el PVP se guarda en el histórico del catálogo bajo el EAN de la guitarra, como tienda "fender_es", y la
página de la guitarra lo dibuja como "PVP oficial" (no cuenta para el mejor precio).

Solo responde desde los runners de GitHub; robots.txt respetado, 3-6 s entre peticiones, rotación por antigüedad.

Uso:
    python -m scraper.pvp --minutes 40 --out F    # CI: lee un lote y lo guarda en F
    python -m scraper.pvp --merge F               # CI: lo fusiona en data/catalog/pvp.json y en el histórico
"""
import argparse
import json
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


def scan(minutes):
    data = load(PVP, {"pages": {}, "prices": {}})
    fetcher = Fetcher()
    urls = sitemap_urls(fetcher, SITEMAP, lambda loc: "sitemap_products" in loc and "/en/" not in loc)
    urls = sorted({u for u in urls if "/products/" in u})
    pages = data["pages"]
    queue = [u for u in urls if u not in pages] + sorted((u for u in urls if u in pages), key=lambda u: pages[u]["checked"])
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
    return out


def merge(batch):
    data = load(PVP, {"pages": {}, "prices": {}})
    day = now_iso()[:10]
    for rec in batch["records"]:
        if rec["status"] in ("error", "robots_disallowed") and rec["url"] in data["pages"]:
            continue  # se conserva la última lectura buena
        data["pages"][rec["url"]] = {"checked": rec["checked"], "status": rec["status"]}
        for ref, price in rec["offers"].items():
            series = data["prices"].setdefault(ref, [])
            if series and series[-1][0] == day:
                series[-1][1] = price
            elif not series or series[-1][1] != price:
                series.append([day, price])
    alive = set(batch.get("urls") or data["pages"])
    data["pages"] = {u: p for u, p in data["pages"].items() if u in alive}
    write(PVP, data)
    link(data["prices"])


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
