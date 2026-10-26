"""Catálogo amplio de guitarras eléctricas.

Descubre las fichas en los sitemaps de las tiendas, lee cada día un lote (las nunca leídas y las más
antiguas, con un tope de tiempo por tienda) y agrupa los productos entre tiendas por EAN.

Ficheros en data/catalog/:
    offers.json    última lectura de cada ficha {url: {...}}
    history.json   cambios de precio {ean: {tienda: [[fecha, precio], ...]}}
    products.json  catálogo para la web, agrupado por EAN

Uso:
    python -m scraper.catalog [--minutes 50] [--limit N] [--only numemusic]
    python -m scraper.catalog --records-out F      # CI: lee y guarda el lote en F
    python -m scraper.catalog --merge F            # CI: fusiona el lote en data/catalog/
    python -m scraper.catalog --build              # regenera products.json
"""
import argparse
import gzip
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from . import jsonld
from .common import normalize_id
from .fetch import Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "catalog"
RECHECK_SKIPPED_DAYS = 60  # fichas que no son guitarra: no se vuelven a pedir en este tiempo
DROP_AFTER_DAYS = 30       # ofertas que desaparecen del sitemap y no se han leído en este tiempo

NOT_PRODUCT = re.compile(r"b-stock|bstock|outlet|usad[ao]|segunda-mano|gebraucht|pre-owned|demo|vorfuehr|gutschein", re.I)

# Session no dice en la URL qué es una guitarra: se preseleccionan marcas de guitarra eléctrica sin
# palabras de accesorio, y la ficha (breadcrumb "E-Gitarren") confirma.
SESSION_BRANDS = ("fender", "squier", "gibson", "epiphone", "ibanez", "prs", "gretsch", "esp", "ltd", "jackson",
                  "charvel", "schecter", "evh", "music-man", "sterling", "yamaha", "cort", "godin", "duesenberg",
                  "rickenbacker", "danelectro", "guild", "d-angelico", "heritage", "harmony", "solar", "strandberg",
                  "chapman", "reverend", "vintage", "framus", "warwick", "hagstrom", "eastman", "maybach")
SESSION_SKIP = re.compile(
    r"saite|string|gurt|strap|koffer|case|gig-?bag|tasche|bag|pickup|tonabnehmer|humbucker|schlagbrett|pickguard"
    r"|kit|staender|stand|amp|verstaerker|combo|head|topteil|cabinet|box|bass|akusti|acoustic|western|konzert"
    r"|klassik|ukulele|mandolin|banjo|pedal|effekt|kabel|cable|plektr|pick|hals|neck|body|korpus|mechanik|tuner"
    r"|stimm|bruecke|bridge|sattel|knopf|knob|schalter|switch|poti|buchse|tremolo|vibrato|shirt|hoodie|cap-|tasse"
    r"|buch|book|poster|sticker|halter|hanger|tuch|cloth|polish|pflege|clean|ersatz|schraube|feder|spring|saddle"
    r"|cover|kappe|dreadnought|parlor|jumbo|nylon|accessory|zubehoer|single-string|set-|-set|bundle|pack|b-ware"
    r"|snare|drum|mischpult|transistor|light|logo|festival|\d{3}-\d{3}", re.I)


def _pick_numemusic(url):
    return re.search(r"/\d+-guitarra-el[eé]?ctrica-", url) and not NOT_PRODUCT.search(url)


def _pick_session(url):
    slug = url.split("/products/")[-1].strip("/")
    return (slug.startswith(tuple(b + "-" for b in SESSION_BRANDS))
            and not SESSION_SKIP.search(slug) and not NOT_PRODUCT.search(slug))


SOURCES = {
    "numemusic": {"name": "Nume Music", "sitemap": "https://www.numemusic.com/media/sitemap/es_ES.xml",
                  "pick": _pick_numemusic, "guitar": lambda c: any(re.search(r"guitarras el[eé]ctricas", x, re.I) for x in c)},
    "session": {"name": "Session", "sitemap": "https://www.session.de/sitemap.xml",
                # "E-Gitarren & Zubehör" también agrupa accesorios: manda la última categoría.
                "pick": _pick_session,
                "guitar": lambda c: len(c) > 1 and c[-2].lower().startswith("e-gitarren")
                and re.search(r"gitarre", c[-1], re.I) and not re.search(r"zubeh|saite|koffer|tasche", c[-1], re.I),
                "sub": lambda u: "-product-" in u},
}

# Tipos comunes a partir del breadcrumb (Numemusic: "Modelos ST"; Session: "ST-Gitarren").
TYPES = [("ST", r"\bst\b|st-gitarren|strat"), ("T", r"modelos t\b|\bt-gitarren|tele"),
         ("Single cut", r"single.?cut"), ("Double cut", r"double.?cut"),
         ("Semihueca", r"hollow|semi|jazz|resonanz|archtop"),
         ("Moderna / Metal", r"heavy|metal|superstrat|moderne|[78] cuerdas|[78]-saiter"),
         ("Offset", r"offset|retro|jazzmaster|jaguar|mustang")]

# Marcas en mayúsculas o con variantes → nombre canónico.
BRANDS = {"squier by fender": "Squier", "squier": "Squier", "prs": "PRS", "esp": "ESP", "ltd": "LTD", "evh": "EVH",
          "esp ltd": "LTD", "ltd guitars": "LTD", "esp guitars": "ESP", "ernie ball music man": "Music Man", "music man": "Music Man", "d'angelico": "D'Angelico",
          "sterling by music man": "Sterling", "prs se": "PRS"}


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write(path, data, compact=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(data, ensure_ascii=False, indent=1)
    path.write_text(text + "\n", encoding="utf-8")


def canonical_brand(raw):
    raw = (raw or "").strip()
    if raw.lower() in BRANDS:
        return BRANDS[raw.lower()]
    return raw.title() if raw.isupper() and len(raw) > 3 else raw


def clean_name(name, brand_raw, brand):
    """'SQUIER BY FENDER Classic Vibe…' → 'Squier Classic Vibe…'."""
    name = re.sub(r"\s+", " ", name or "").strip()
    if brand_raw and name.lower().startswith(brand_raw.lower()):
        name = brand + name[len(brand_raw):]
    elif brand and not name.lower().startswith(brand.lower()):
        name = f"{brand} {name}"
    return name


def guitar_type(crumbs):
    leaf = crumbs[-1].lower() if crumbs else ""
    for label, pat in TYPES:
        if re.search(pat, leaf):
            return label
    return "Otras"


# --- Descubrimiento -------------------------------------------------------------------------------------

def sitemap_urls(fetcher, url, sub=None, depth=0):
    """URLs de un sitemap o índice de sitemaps (admite .gz). Respeta robots.txt."""
    allowed, _ = fetcher.allowed(url)
    if not allowed:
        return []
    resp = fetcher.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"sitemap {url}: HTTP {resp.status_code}")
    data = resp.content
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    text = data.decode("utf-8", "ignore")
    locs = [l.strip() for l in re.findall(r"<loc>\s*(.*?)\s*</loc>", text)]
    if "<sitemapindex" in text and depth < 2:
        out = []
        for loc in locs:
            if sub is None or sub(loc):
                out += sitemap_urls(fetcher, loc, None, depth + 1)
        return out
    return locs


# --- Lectura de fichas ----------------------------------------------------------------------------------

def _product_node(soup):
    crumbs, product = [], None
    for block in jsonld.load_blocks(soup):
        for node in jsonld._iter_nodes(block):
            types = jsonld._types(node)
            if "breadcrumblist" in types and not crumbs:
                for el in node.get("itemListElement") or []:
                    item = el.get("item") if isinstance(el, dict) else None
                    name = el.get("name") or (item.get("name") if isinstance(item, dict) else None)
                    if name:
                        crumbs.append(str(name))
            elif "product" in types and product is None:
                product = node
    return product, crumbs


def read_page(fetcher, store_id, url, now):
    src = SOURCES[store_id]
    rec = {"store": store_id, "url": url, "checked": now, "status": "error"}
    try:
        allowed, info = fetcher.allowed(url)
        if not allowed:
            rec["status"] = "robots_disallowed"
            return rec
        resp = fetcher.get(url)
        if resp.status_code in (404, 410):
            rec["status"] = "gone"
            return rec
        if resp.status_code != 200 or is_challenge(resp):
            rec.update(status="blocked_403" if resp.status_code == 403 or is_challenge(resp) else "error",
                       http_status=resp.status_code)
            return rec
        soup = BeautifulSoup(resp.text, "html.parser")
        product, crumbs = _product_node(soup)
        if not src["guitar"](crumbs):
            rec["status"] = "not_guitar"
            return rec
        offer = jsonld.extract(soup, [], store_id)
        if not product or not offer:
            rec["status"] = "no_price"
            return rec
        ean = next((normalize_id(product.get(k)) for k in ("gtin13", "gtin", "gtin12", "gtin14")
                    if product.get(k)), None)
        brand_raw = product.get("brand")
        brand_raw = brand_raw.get("name") if isinstance(brand_raw, dict) else brand_raw
        brand = canonical_brand(brand_raw)
        rec.update(status="ok" if offer["currency"] == "EUR" else "wrong_currency",
                   ean=ean.lstrip("0") if ean else None, brand=brand,
                   name=clean_name(product.get("name"), brand_raw, brand), type=guitar_type(crumbs),
                   price=offer["price"], currency=offer["currency"], in_stock=offer["in_stock"],
                   image=offer.get("image"))
    except requests.RequestException as exc:
        rec["note"] = type(exc).__name__
    except Exception as exc:  # noqa: BLE001 - una ficha rara no para el lote
        rec["note"] = f"{type(exc).__name__}: {exc}"[:200]
    return rec


def due_urls(store_id, urls, offers, now):
    """Orden de visita: nunca leídas, luego las más antiguas. Las que no son guitarra esperan 60 días."""
    skip_before = (datetime.fromisoformat(now) - timedelta(days=RECHECK_SKIPPED_DAYS)).isoformat()
    fresh, old = [], []
    for url in urls:
        o = offers.get(url)
        if o is None:
            fresh.append(url)
        elif o.get("status") in ("not_guitar", "gone") and o["checked"] > skip_before:
            continue
        else:
            old.append((o["checked"], url))
    return fresh + [u for _, u in sorted(old)]


def scan_store(store_id, offers, minutes, limit):
    src = SOURCES[store_id]
    fetcher = Fetcher()
    now = now_iso()
    out = {"store": store_id, "sitemap": None, "records": []}
    try:
        urls = sitemap_urls(fetcher, src["sitemap"], src.get("sub"))
        picked = sorted({u for u in urls if src["pick"](u)})
        out["sitemap"] = picked
        print(f"[{store_id}] sitemap: {len(urls)} URLs, {len(picked)} candidatas", flush=True)
    except Exception as exc:  # noqa: BLE001 - sin sitemap se revisan las ya conocidas
        print(f"[{store_id}] sitemap con error ({type(exc).__name__}); se usan las conocidas", flush=True)
        picked = sorted(u for u, o in offers.items() if o["store"] == store_id)
    queue = due_urls(store_id, picked, offers, now)
    deadline = time.monotonic() + minutes * 60
    for n, url in enumerate(queue[:limit] if limit else queue, 1):
        if time.monotonic() > deadline:
            break
        rec = read_page(fetcher, store_id, url, now_iso())
        out["records"].append(rec)
        if n % 50 == 0:
            ok = sum(r["status"] == "ok" for r in out["records"])
            print(f"[{store_id}] {n}/{len(queue)} leídas, {ok} guitarras", flush=True)
    stats = {}
    for r in out["records"]:
        stats[r["status"]] = stats.get(r["status"], 0) + 1
    print(f"[{store_id}] fin: {len(out['records'])} fichas {stats}; pendientes {max(0, len(queue) - len(out['records']))}", flush=True)
    return out


def scan(only=None, minutes=50, limit=None):
    offers = load(DIR / "offers.json", {})
    stores = [s for s in SOURCES if not only or s in only]
    with ThreadPoolExecutor(max_workers=len(stores)) as pool:
        return list(pool.map(lambda s: scan_store(s, offers, minutes, limit), stores))


# --- Fusión y catálogo para la web --------------------------------------------------------------------

def merge(batches):
    offers = load(DIR / "offers.json", {})
    history = load(DIR / "history.json", {})
    for batch in batches:
        for rec in batch["records"]:
            prev = offers.get(rec["url"], {})
            if rec["status"] in ("error", "blocked_403") and prev.get("status") == "ok":
                prev.update(checked=rec["checked"], last_error=rec["status"])  # se conserva el último precio bueno
                continue
            offers[rec["url"]] = rec
            if rec["status"] == "ok" and rec.get("ean") and rec.get("price") is not None:
                series = history.setdefault(rec["ean"], {}).setdefault(rec["store"], [])
                day = rec["checked"][:10]
                if series and series[-1][0] == day:
                    series[-1][1] = rec["price"]
                elif not series or series[-1][1] != rec["price"]:
                    series.append([day, rec["price"]])
        if batch.get("sitemap") is not None:
            # Lo que ya no está en el sitemap se olvida pasado un tiempo (producto retirado).
            alive = set(batch["sitemap"])
            cutoff = (datetime.now(timezone.utc) - timedelta(days=DROP_AFTER_DAYS)).isoformat()
            for url in [u for u, o in offers.items() if o["store"] == batch["store"] and u not in alive]:
                if offers[url]["checked"] < cutoff:
                    del offers[url]
    write(DIR / "offers.json", offers)
    write(DIR / "history.json", history)
    build(offers, history)


def _curated_offers():
    """Tiendas que ya seguimos en products.json/latest.json (Thomann, Egitana, eBay…), cruzadas por EAN."""
    products = load(ROOT / "products.json", [])
    latest = load(ROOT / "data" / "latest.json", {})
    stores = {s["id"]: s for s in load(ROOT / "stores.json", [])}
    by_sku = {p["sku"]: normalize_id(p["ean"]).lstrip("0") for p in products if p.get("ean")}
    out = {}
    for i in latest.get("items", []):
        ean = by_sku.get(i["sku"])
        store = stores.get(i["store"], {})
        if not ean or i.get("price") is None or i["store"] in SOURCES or store.get("reference"):
            continue
        out.setdefault(ean, []).append({"s": i["store"], "p": i["price"], "u": i.get("url"),
                                        "st": i.get("in_stock"), "d": (i.get("price_date") or "")[:10]})
    return out, {s: stores[s]["name"] for s in stores}, {v: k for k, v in by_sku.items()}


def build(offers=None, history=None):
    offers = offers if offers is not None else load(DIR / "offers.json", {})
    history = history if history is not None else load(DIR / "history.json", {})
    from .thumbs import existing, slenderness  # import aquí: thumbs importa este módulo
    curated, store_names, sku_by_ean = _curated_offers()
    groups = {}
    for o in offers.values():
        if o.get("status") != "ok" or o.get("price") is None:
            continue
        key = o.get("ean") or "url:" + o["url"]
        groups.setdefault(key, []).append(o)
    products = []
    for key, group in groups.items():
        # Nombre y foto preferidos: Numemusic (tienda española, nombres completos).
        group.sort(key=lambda o: (o["store"] != "numemusic", o["price"]))
        main = group[0]
        ean = main.get("ean")
        items = [{"s": o["store"], "p": o["price"], "u": o["url"], "st": o.get("in_stock"), "d": o["checked"][:10]}
                 for o in group]
        items += curated.get(ean, []) if ean else []
        items.sort(key=lambda i: i["p"])
        series = history.get(ean, {}) if ean else {}
        days = {d for s in series.values() for d, _ in s}
        low = min((p for s in series.values() for _, p in s), default=None) if len(days) > 1 else None
        prod = {"id": ean or main["url"], "ean": ean, "name": main["name"], "brand": main.get("brand"),
                "type": main.get("type"), "img": next((o["image"] for o in group if o.get("image")), None),
                "items": items, "low": low}
        # Miniatura: entre las fotos de todas las tiendas, la que muestra la guitarra entera (la más esbelta).
        thumbs = [t for t in (existing(o.get("image")) for o in group) if t]
        if thumbs:
            prod["th"] = max(thumbs, key=slenderness)
        if ean in sku_by_ean:
            prod["sku"] = sku_by_ean[ean]
        products.append(prod)
    products.sort(key=lambda p: (-len(p["items"]), p["name"]))
    names = {s: SOURCES[s]["name"] for s in SOURCES} | store_names
    used = {i["s"] for p in products for i in p["items"]}
    write(DIR / "products.json", {"updated": now_iso(), "stores": {s: names.get(s, s) for s in sorted(used)},
                                  "products": products})
    multi = sum(len({i["s"] for i in p["items"]}) > 1 for p in products)
    print(f"catálogo: {len(products)} guitarras, {multi} en más de una tienda", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="tiendas separadas por comas")
    parser.add_argument("--minutes", type=float, default=50, help="tope de tiempo por tienda")
    parser.add_argument("--limit", type=int, help="máximo de fichas por tienda")
    parser.add_argument("--records-out", help="guarda el lote en este fichero (CI)")
    parser.add_argument("--merge", help="fusiona en data/catalog/ un lote de --records-out")
    parser.add_argument("--build", action="store_true", help="solo regenera products.json")
    args = parser.parse_args(argv)
    if args.build:
        build()
        return 0
    if args.merge:
        merge(json.loads(Path(args.merge).read_text(encoding="utf-8")))
        return 0
    batches = scan(args.only.split(",") if args.only else None, args.minutes, args.limit)
    if args.records_out:
        Path(args.records_out).write_text(json.dumps(batches, ensure_ascii=False), encoding="utf-8")
    else:
        merge(batches)
    return 0


if __name__ == "__main__":
    sys.exit(main())
