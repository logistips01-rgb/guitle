"""Comparador de Jordan (zapatillas y ropa) en tiendas Shopify que publican su catálogo en JSON.

Cada tienda expone /collections/<colección>/products.json (250 productos por página) con precio,
SKU y stock por talla. Los productos se emparejan entre tiendas por el código de estilo de Nike
(p. ej. DD1391-100), que va en el SKU, el título o la descripción.

Uso:
    python -m scraper.sneakers                 # consulta y guarda en data/sneakers_*.json
    python -m scraper.sneakers --dry-run       # solo informe
    python -m scraper.sneakers --records-out F / --merge F   # como scraper.run, para CI
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
HISTORY = DATA / "sneakers_history.json"
LATEST = DATA / "sneakers_latest.json"
MAX_PAGES = 20
STALE_DAYS = 7  # una oferta que no aparece en 7 días deja de mostrarse

STYLE_RE = re.compile(r"\b([A-Z]{2}\d{4}|\d{6})-(\d{3})\b")
TARGET_SIZES = ("43", "44")
US_TO_EU = {"9.5": "43", "10": "44"}  # tallaje de hombre Nike/Jordan
SHOE_TYPES = ("calzado", "sneaker", "footwear", "shoe", "zapatilla", "high top", "low top", "mid top")


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def style_code(product):
    texts = [v.get("sku") or "" for v in product.get("variants", [])]
    texts += [product.get("title") or "", " ".join(product.get("tags") or []), product.get("body_html") or ""]
    for text in texts:
        m = STYLE_RE.search(text.upper())
        if m:
            return f"{m.group(1)}-{m.group(2)}"
    return None


def size_eu(variant_title, system):
    m = re.search(r"\d{1,2}(?:[.,]5)?", variant_title or "")
    if not m:
        return None
    size = m.group(0).replace(",", ".")
    return US_TO_EU.get(size) if system == "us" else size


def category(product):
    kind = (product.get("product_type") or "").lower()
    if any(k in kind for k in SHOE_TYPES):
        return "zapatillas"
    sizes = [size_eu(v.get("title"), "eu") for v in product.get("variants", [])]
    numeric = [float(s) for s in sizes if s]
    return "zapatillas" if numeric and min(numeric) >= 30 else "ropa"


def parse_product(store, product):
    variants = product.get("variants", [])
    available = [v for v in variants if v.get("available")]
    pool = available or variants
    if not pool:
        return None
    price = min(float(v["price"]) for v in pool)
    compare = max((float(v.get("compare_at_price") or 0) for v in variants), default=0)
    sizes = {s: False for s in TARGET_SIZES}
    for v in available:
        eu = size_eu(v.get("title"), store["sizes"])
        if eu in sizes:
            sizes[eu] = True
    code = style_code(product)
    images = product.get("images") or []
    return {
        "key": code or f"{store['id']}:{product['handle']}",
        "code": code,
        "title": product.get("title"),
        "category": category(product),
        "image": images[0]["src"] if images else None,
        "url": f"{store['base']}/products/{product['handle']}",
        "price": price,
        "compare_at": compare if compare > price else None,
        "available": bool(available),
        "s43": sizes["43"],
        "s44": sizes["44"],
    }


def scrape_store(fetcher, store):
    """Devuelve (status, {key: oferta}). Nunca lanza: el job no se rompe por una tienda."""
    offers = {}
    try:
        for page in range(1, MAX_PAGES + 1):
            url = f"{store['base']}/collections/{store['collection']}/products.json?limit=250&page={page}"
            allowed, info = fetcher.allowed(url)
            if not allowed:
                return ("blocked_403" if "anti-bot" in info else "robots_disallowed"), offers
            resp = fetcher.get(url)
            if resp.status_code == 403:
                return "blocked_403", offers
            if resp.status_code != 200:
                return f"error_http_{resp.status_code}", offers
            products = resp.json().get("products", [])
            if not products:
                break
            for product in products:
                offer = parse_product(store, product)
                if offer and (offer["key"] not in offers or offer["price"] < offers[offer["key"]]["price"]):
                    offers[offer["key"]] = offer
        return "ok", offers
    except Exception as exc:  # noqa: BLE001 - registrar y seguir con la siguiente tienda
        return f"error: {type(exc).__name__}: {exc}"[:200], offers


def save(snapshot):
    """Fusiona una ejecución en el histórico (solo cambios) y regenera sneakers_latest.json."""
    DATA.mkdir(exist_ok=True)
    history = load(HISTORY, {})
    latest = load(LATEST, {"products": {}, "stores": {}})
    products = latest.get("products", {})
    date = snapshot["date"]
    for store_id, info in snapshot["stores"].items():
        latest.setdefault("stores", {})[store_id] = {"name": info["name"], "status": info["status"], "last_run": date,
                                                   "count": len(info["offers"])}
        for key, o in info["offers"].items():
            p = products.setdefault(key, {"key": key, "first_seen": date, "offers": {}})
            for field in ("code", "title", "category"):
                p[field] = p.get(field) or o[field]
            if o["image"] and not p.get("image"):
                p["image"] = o["image"]
            p["offers"][store_id] = {k: o[k] for k in ("price", "compare_at", "available", "s43", "s44", "url")}
            p["offers"][store_id]["last_seen"] = date
            if p.get("min_price") is None or o["price"] < p["min_price"]:
                p["min_price"], p["min_price_date"] = o["price"], date
            # Histórico compacto: solo se guarda cuando cambia precio o stock de tus tallas.
            point = [date, o["price"], o["s43"], o["s44"]]
            series = history.setdefault(key, {}).setdefault(store_id, [])
            if not series or series[-1][1:] != point[1:]:
                series.append(point)
    latest["updated"] = date
    latest["products"] = products
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    LATEST.write_text(json.dumps(latest, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", help="ids de tienda separados por coma")
    parser.add_argument("--records-out")
    parser.add_argument("--merge")
    args = parser.parse_args(argv)
    if args.merge:
        save(json.loads(Path(args.merge).read_text(encoding="utf-8")))
        return 0

    stores = load(ROOT / "sneakers_stores.json", [])
    only = set(args.only.split(",")) if args.only else None
    snapshot = {"date": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "stores": {}}
    fetcher = Fetcher()
    for store in stores:
        if only and store["id"] not in only:
            continue
        status, offers = scrape_store(fetcher, store)
        if store.get("currency") != "EUR":
            status, offers = "wrong_currency", {}
        snapshot["stores"][store["id"]] = {"name": store["name"], "status": status, "offers": offers}
        cheap = sum(1 for o in offers.values() if o["price"] <= 150)
        sized = sum(1 for o in offers.values() if o["s43"] or o["s44"])
        print(f"[{status}] {store['id']}: {len(offers)} productos, {cheap} ≤150 €, {sized} con talla 43/44", flush=True)

    if args.dry_run:
        return 0
    if args.records_out:
        Path(args.records_out).write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
        return 0
    save(snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
