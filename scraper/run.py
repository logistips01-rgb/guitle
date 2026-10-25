"""Ejecución diaria: recorre stores.json, extrae precios y actualiza data/history.json y data/latest.json.

Uso:
    python -m scraper.run              # ejecuta y guarda
    python -m scraper.run --dry-run    # ejecuta y muestra informe sin tocar data/
    python -m scraper.run --only thomann,kirstein
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import css, ebay, jsonld, meta
from .fetch import Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EXTRACTORS = {"jsonld": jsonld.extract, "meta": meta.extract, "css": css.extract}
CHAIN = ["jsonld", "meta", "css"]
EXPECTED_CURRENCY = "EUR"


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def scrape_ebay(store, item, products, now):
    """Tiendas consultadas por la API oficial de eBay en lugar de su web."""
    rec = {"date": now, "store": store["id"], "sku": item["sku"], "url": item.get("url"),
           "price": None, "currency": None, "in_stock": None, "status": "error",
           "method": "ebay", "http_status": None, "note": None}
    try:
        status, data = ebay.search(store, products.get(item["sku"], {"name": item["sku"]}))
        rec["status"] = status
        if data:
            rec.update(price=data["price"], currency=data["currency"], url=data["url"] or rec["url"],
                       in_stock=True, note=data["title"])
            if data["image"]:
                rec["image"] = data["image"]
            if data["currency"] != EXPECTED_CURRENCY:
                rec["status"] = "wrong_currency"
    except requests.RequestException as exc:
        rec["http_status"] = getattr(exc.response, "status_code", None)
        rec["note"] = f"{type(exc).__name__}: {exc}"[:300]
    return rec


def scrape_item(fetcher, store, item, products, now):
    rec = {"date": now, "store": store["id"], "sku": item["sku"], "url": item["url"],
           "price": None, "currency": None, "in_stock": None, "status": "error",
           "method": None, "http_status": None, "note": None}
    url = item["url"]
    product = products.get(item["sku"], {})
    product_ids = [item["sku"], product.get("ean")]
    try:
        allowed, robots_info = fetcher.allowed(url)
        if not allowed:
            # Si robots.txt no es legible por un challenge anti-bot no hay reglas reales:
            # es un bloqueo, no una prohibición. Igualmente no pedimos la URL.
            status = "blocked_403" if "anti-bot" in robots_info else "robots_disallowed"
            rec.update(status=status, note=robots_info + "; URL no solicitada")
            return rec
        resp = fetcher.get(url)
        rec["http_status"] = resp.status_code
        if resp.status_code == 403:
            rec["status"] = "blocked_403"
            if is_challenge(resp):
                rec["note"] = "challenge anti-bot"
            return rec
        if resp.status_code != 200:
            rec["note"] = f"HTTP {resp.status_code}"
            return rec
        soup = BeautifulSoup(resp.content, "html.parser")
        # Primero el método declarado por la tienda, luego el resto de la cadena.
        order = [store.get("method")] + [m for m in CHAIN if m != store.get("method")]
        for method in [m for m in order if m in EXTRACTORS]:
            result = EXTRACTORS[method](soup, product_ids, store)
            if result:
                break
        else:
            rec["status"] = "no_price"
            rec["note"] = _block_hint(resp, soup)
            return rec
        currency = result["currency"] or store.get("currency_default")
        rec.update(price=result["price"], currency=currency, in_stock=result["in_stock"],
                   method=method, note=result["note"])
        image = result.get("image") or _og_image(soup, resp.url)
        if image:
            rec["image"] = image
        if result["identifiers"]:
            rec["identifiers"] = result["identifiers"]
            # La página declara un EAN distinto al del producto => URL mal asignada.
            # GTIN-12/13/14: se comparan sin ceros a la izquierda (0885978110698 == 885978110698).
            page_eans = {d.lstrip("0") for d in map(_digits, result["identifiers"]) if len(d) in (12, 13, 14)}
            if product.get("ean") and page_eans and product["ean"].lstrip("0") not in page_eans:
                rec["status"] = "sku_mismatch"
                rec["note"] = f"EAN página {sorted(page_eans)} != {product['ean']}"
                return rec
        if currency != EXPECTED_CURRENCY:
            rec["status"] = "wrong_currency"
            if currency is None:
                rec["note"] = "moneda no declarada"
        else:
            rec["status"] = "ok"
    except requests.RequestException as exc:
        rec["note"] = f"{type(exc).__name__}: {exc}"[:300]
    except Exception as exc:  # nunca romper el job por una tienda
        rec["note"] = f"{type(exc).__name__}: {exc}"[:300]
    return rec


def _og_image(soup, base_url):
    tag = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "og:image"})
    url = tag.get("content") if tag else None
    return urljoin(base_url, url) if url else None


def _digits(value):
    return "".join(c for c in str(value) if c.isdigit())


def _block_hint(resp, soup):
    """Pista cuando no hay precio: páginas de challenge (Cloudflare, captcha...) devuelven 200."""
    text = (soup.title.get_text(strip=True) if soup.title else "")[:120]
    body = resp.text[:20000].lower()
    for marker in ("captcha", "cf-challenge", "just a moment", "access denied", "datadome", "perimeterx"):
        if marker in body:
            return f"posible bloqueo ({marker}); title={text!r}"
    return f"title={text!r}"


def manual_records(history):
    """Precios apuntados a mano en data/manual.json (tiendas bloqueadas). Se ingieren una sola vez."""
    seen = {(r["date"], r["store"], r["sku"]) for r in history if r.get("method") == "manual"}
    out = []
    for m in load(DATA / "manual.json", []):
        date = str(m["date"])
        if (date, m["store"], m["sku"]) in seen:
            continue
        out.append({"date": date, "store": m["store"], "sku": m["sku"], "url": m.get("url"),
                    "price": float(m["price"]), "currency": "EUR", "in_stock": m.get("in_stock"),
                    "status": "ok", "method": "manual", "http_status": None, "note": m.get("note")})
    return out


def update_latest(history, products, stores):
    latest = {}
    for rec in sorted(history, key=lambda r: r["date"]):
        key = f"{rec['store']}|{rec['sku']}"
        entry = latest.setdefault(key, {"store": rec["store"], "sku": rec["sku"]})
        if rec.get("method") != "manual":
            entry.update(last_run=rec["date"], status=rec["status"], url=rec["url"])
        if rec["status"] == "ok":
            if rec.get("image"):
                entry["image"] = rec["image"]
            entry.update(price=rec["price"], currency=rec["currency"], in_stock=rec["in_stock"],
                         price_date=rec["date"], price_method=rec["method"])
            if entry.get("min_price") is None or rec["price"] < entry["min_price"]:
                entry.update(min_price=rec["price"], min_price_date=rec["date"])
    return {
        "updated": max((r["date"] for r in history), default=None),
        "products": with_live_pvp(products, latest, stores),
        "stores": [{k: s.get(k) for k in ("id", "name", "domain", "reference")} for s in stores],
        "items": sorted(latest.values(), key=lambda e: (e["sku"], e["store"])),
    }


def with_live_pvp(products, latest, stores):
    """PVP = último precio ok de la tienda de referencia (Fender); products.json queda como respaldo."""
    refs = {s["id"] for s in stores if s.get("reference")}
    out = []
    for p in products:
        p = {**p, "pvp_fallback": p.get("pvp"), "pvp_source": "products.json" if p.get("pvp") else None}
        for entry in latest.values():
            if entry["store"] in refs and entry["sku"] == p["sku"] and entry.get("price") is not None:
                p.update(pvp=entry["price"], pvp_source=entry["store"], pvp_date=entry["price_date"])
                break
        # Foto de una tienda (es la del acabado exacto); la web de la marca comparte foto entre colores.
        images = sorted((e["store"] in refs, e["store"], e["image"]) for e in latest.values()
                        if e["sku"] == p["sku"] and e.get("image"))
        if images:
            p["image"] = images[0][2]
        out.append(p)
    return out


def print_report(records):
    w = sys.stdout.write
    w(f"\n{'tienda':<13}{'sku':<24}{'status':<18}{'método':<8}{'precio':>10} {'mon':<4}{'stock':<7}{'http':<5} nota\n")
    w("-" * 120 + "\n")
    for r in records:
        price = f"{r['price']:.2f}" if r["price"] is not None else "-"
        stock = {True: "sí", False: "no", None: "?"}[r["in_stock"]]
        note = r.get("note") or ""
        if r.get("identifiers"):
            note = (note + " ids=" + ",".join(r["identifiers"])).strip()
        w(f"{r['store']:<13}{r['sku']:<24}{r['status']:<18}{r['method'] or '-':<8}{price:>10} "
          f"{r['currency'] or '-':<4}{stock:<7}{r['http_status'] or '-'!s:<5} {note}\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="no escribe data/")
    parser.add_argument("--only", help="ids de tienda separados por coma")
    args = parser.parse_args(argv)

    products = load(ROOT / "products.json", [])
    stores = load(ROOT / "stores.json", [])
    only = set(args.only.split(",")) if args.only else None
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    by_sku = {p["sku"]: p for p in products}
    fetcher = Fetcher()
    records = []
    for store in stores:
        if only and store["id"] not in only:
            continue
        for item in store.get("items", []):
            if store.get("method") == "ebay":
                if not ebay.has_credentials():  # sin claves no se registra nada (evita ruido en la página)
                    print(f"[skip] {store['id']}: faltan EBAY_CLIENT_ID / EBAY_CLIENT_SECRET", flush=True)
                    break
                rec = scrape_ebay(store, item, by_sku, now)
                records.append(rec)
                print(f"[{rec['status']}] {store['id']} {item['sku']} {rec['price']}", flush=True)
                continue
            if not item.get("url"):
                continue
            rec = scrape_item(fetcher, store, item, by_sku, now)
            records.append(rec)
            print(f"[{rec['status']}] {store['id']} {item['sku']} {rec['price']}", flush=True)

    print_report(records)
    if args.dry_run:
        return 0

    DATA.mkdir(exist_ok=True)
    history = load(DATA / "history.json", [])
    history += manual_records(history) + records
    (DATA / "history.json").write_text(json.dumps(history, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    latest = update_latest(history, products, stores)
    (DATA / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
