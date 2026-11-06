"""Música grabada (vinilos, CD y casetes): tiendas de discos, el mismo disco por su código de barras (EAN) y una página
por disco con su precio en cada tienda. Objetivo: tráfico de búsqueda ("<disco> vinyl price").

De momento Reino Unido, con tiendas de discos en Shopify: el catálogo sale de /products.json (paginado) y el código
de barras de la ficha de cada producto (/products/<handle>.json), que se guarda para no volver a pedirlo. Siempre con
robots.txt y las pausas de siempre (scraper.fetch). Para España y el resto: los ficheros de producto de los programas
de afiliados (Awin), cuando los haya.

  python -m scraper.musica --pais uk --minutes 120   # lee (catálogos y códigos nuevos) y genera las páginas
  python -m scraper.musica --pais uk --build         # solo las páginas, con lo guardado
"""
import argparse
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "musica"

STORES = {
    "uk": {"recordstore": ("Recordstore", "https://www.recordstore.co.uk"),
           "assai": ("Assai Records", "https://www.assai.co.uk"),
           "sisterray": ("Sister Ray", "https://www.sisterray.co.uk"),
           "drift": ("Drift Records", "https://www.driftrecords.com"),
           "crash": ("Crash Records", "https://www.crashrecords.co.uk")},
    # Francia: tiendas afiliadas en Awin; el catálogo sale de su fichero de productos (read_awin), no de su web.
    "fr": {"cultura": ("Cultura", "https://www.cultura.com"), "fnac": ("Fnac", "https://www.fnac.com"),
           "zavvi": ("Zavvi", "https://fr.zavvi.com")},
}
STORES["it"] = {"radiation": ("Radiation Records", "https://shop.radiationrecords.net"),
                "umi": ("Universal Music Italia", "https://shop.universalmusic.it"),
                "ibs": ("IBS", "https://www.ibs.it"), "feltrinelli": ("laFeltrinelli", "https://www.lafeltrinelli.it"),
                "mondadori": ("Mondadori Store", "https://www.mondadoristore.it"),
                "laziale": ("Discoteca Laziale", "https://www.discotecalaziale.com")}
# España: tiendas de discos independientes (estudio: marketing/tiendas-discos-espana.md, rama de redes). Supersonic en
# Shopify (el código de barras va en la referencia); El Genio Equivocado y Alta Fidelidad en WooCommerce (WOO).
STORES["es"] = {"supersonic": ("Supersonic", "https://discossupersonicsantander.com"),
                "ege": ("El Genio Equivocado", "https://egebotiga.com"),
                "altafidelidad": ("Alta Fidelidad", "https://discosaltafidelidad.es")}
STORES["es"]["ega"] = ("Discos EGA", "https://discosega.es")
# Tiendas que publican en su mapa del sitio la dirección de cada disco con su código de barras al final
# (".../143-bunbury-palosanto-cd-0825646408641.html"): de cada ficha, precio y stock (JSON-LD), poco a poco (SITEMAP_MIN
# minutos al día), primero los discos que también tienen otras tiendas. Se guarda en consultas.json, como LOOKUP.
SITEMAP = {"es": {"ega": "https://discosega.es/1_es_0_sitemap.xml"}}
SITEMAP_MIN = 100
# Tiendas en WooCommerce: catálogo por su API pública de tienda (/wp-json/wc/store/v1/products), con el EAN en "sku".
WOO = {"es": {"ege", "altafidelidad"}}
# Tiendas en WooCommerce sin código de barras: sus discos se emparejan por artista, título y formato con los que sí lo
# tienen (de otras tiendas), solo cuando no hay duda de la edición (_name_key, build_data). No crean discos nuevos.
STORES["es"] |= {"revolver": ("Revolver Records", "https://revolverrecords.es"),
                 "borabora": ("Discos Bora Bora", "https://discosborabora.com"),
                 "maxvinilos": ("MaxVinilos", "https://maxvinilos.com"),
                 "bcore": ("BCore Disc", "https://bcstore.bcoredisc.com")}
WOO_NAME = {"es": {"revolver", "borabora", "maxvinilos", "bcore"}}
# Tiendas PrestaShop cuyo listado trae, de cada disco, la dirección con el código de barras al final y el precio:
# se lee el listado entero (páginas de ~100). Su nombre suele ser solo el título, así que solo se suman a discos que
# ya tienen otras tiendas (ONLY_MATCH), sin crear discos nuevos.
STORES["es"]["marilians"] = ("Marilians", "https://www.marilians.com")
LISTING = {"es": {"marilians": "https://www.marilians.com/2-inicio?page={n}"}}
ONLY_MATCH = {"marilians"}
# Tiendas que no dan su catálogo pero se consultan disco a disco por su código de barras (la dirección redirige a la
# ficha; precio, stock, foto y artista del JSON-LD). Probadas a mano; robots.txt las permite.
LOOKUP = {"it": {"ibs": "https://www.ibs.it/x/e/{ean}", "feltrinelli": "https://www.lafeltrinelli.it/x/e/{ean}",
                 "mondadori": "https://www.mondadoristore.it/x/p/{ean}", "laziale": "https://www.discotecalaziale.com/{ean}_x"}}
# Anunciantes de Awin de cada país: id de tienda → texto que lleva su nombre en Awin (en minúsculas).
AWIN = {"fr": {"cultura": "cultura", "fnac": "fnac", "zavvi": "zavvi"}}
# Formato por el título, el tipo o la variante; lo demás (camisetas, chapas, bolsas, tocadiscos…) no entra.
FORMATS = [("casete", r"\bcassette|\bcass\b|\btape\b|\bmc\b|\bcasete"), ("cd", r"\b[2-9]?cds?\b|compact disc"),
           ("vinilo", r"vinyl|vinilo|\b(?:7|10|12)\s?[″”]|\blp\b|\b2lp\b|\b3lp\b|\b12\"|\b7\"|\b10\"|\b12 inch|\b7 inch|\bep\b|\b33 ?tours|\b45 ?tours")]
NOT_MUSIC = re.compile(r"(?i)t-?shirt|\btee\b|hoodie|sweat|badge|tote|\bbag\b|slipmat|poster|turntable|record player|"
                       r"gift card|voucher|cleaning|sleeve[s]? pack|inner sleeves|outer sleeves|mug\b|\bhat\b|cap\b|book\b|"
                       r"\blivre\b|platine|tourne-?disque|partition|\bdvd\b|blu-?ray|carte cadeau|affiche|sac\b|"
                       r"\blibro\b|camiseta|sudadera|tocadiscos|tarjeta regalo|\bbolsa\b|\bp[óo]ster\b|\btaza\b")
CLEAN = re.compile(r"(?i)\s*[\(\[]?(?:\*?pre-?order\*?|due out[^\)\]]*|signed|indie exclusive|limited edition|"
                   r"vinyl lp|vinyl|\blp\b|\b2lp\b|\bcd\b|cassette|\btape\b)[\)\]]?\s*")


def _fmt(*texts):
    t = " ".join(x or "" for x in texts).lower()
    for f, rx in FORMATS:
        if re.search(rx, t):
            return f
    return None


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:90]


def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def read_awin(pais):
    """Países con tiendas afiliadas en Awin (Francia): su fichero de productos trae precio, stock, EAN y el enlace de
    afiliado de cada disco. Escribe tiendas.json y codigos.json con la misma forma que las tiendas Shopify, así que
    build_data y las páginas son las mismas. Necesita AWIN_FEED_KEY (la "Datafeed API key" de Awin, secreto de GitHub)."""
    import csv, gzip, io, os, requests
    key = os.environ.get("AWIN_FEED_KEY")
    if not key:
        print("[awin] falta AWIN_FEED_KEY: no se lee nada", flush=True)
        return
    folder = DATA / pais
    feeds = list(csv.DictReader(io.StringIO(requests.get(f"https://productdata.awin.com/datafeed/list/apikey/{key}",
                                                         timeout=120).text)))
    cols = ("aw_deep_link,product_name,merchant_name,search_price,currency,merchant_category,category_name,ean,"
            "product_GTIN,merchant_image_url,aw_image_url,in_stock,brand_name,aw_product_id")
    catalog, codes = {}, {}
    for sid, needle in AWIN[pais].items():
        mine = [f for f in feeds if needle in (f.get("Advertiser Name") or "").lower()
                and (f.get("Membership Status") or "").lower() in ("active", "joined")
                and (f.get("Primary Region") or "").upper() in ("FR", "") ]
        print(f"[awin] {sid}: {len(mine)} ficheros aprobados", flush=True)
        items = {}
        for f in mine:
            url = (f"https://productdata.awin.com/datafeed/download/apikey/{key}/language/any/fid/{f['Feed ID']}/columns/"
                   f"{cols}/format/csv/delimiter/%2C/compression/gzip/adultcontent/1/")
            try:
                raw = gzip.decompress(requests.get(url, timeout=600).content).decode("utf-8", "ignore")
            except Exception as exc:  # noqa: BLE001
                print(f"[awin] {sid} fichero {f['Feed ID']}: {exc}", flush=True)
                continue
            for row in csv.DictReader(io.StringIO(raw)):
                name = row.get("product_name") or ""
                fmt = _fmt(name, row.get("merchant_category"), row.get("category_name"))
                if not fmt or NOT_MUSIC.search(name):
                    continue
                ean = re.sub(r"\D", "", row.get("ean") or row.get("product_GTIN") or "").lstrip("0")
                try:
                    price = float(row.get("search_price") or 0)
                except ValueError:
                    continue
                if not price or not (11 <= len(ean) <= 13):
                    continue
                h = row.get("aw_product_id") or ean
                items[h] = {"t": name, "v": row.get("brand_name") or "", "ty": row.get("merchant_category") or "", "f": fmt,
                            "p": price, "st": (row.get("in_stock") or "1") not in ("0", "false", "no"),
                            "img": row.get("merchant_image_url") or row.get("aw_image_url"), "u": row.get("aw_deep_link")}
                codes.setdefault(sid, {})[h] = ean.zfill(13)
        if items:
            catalog[sid] = items
            print(f"[awin] {sid}: {len(items)} discos con EAN", flush=True)
    if catalog:
        _save(folder / "tiendas.json", catalog)
        _save(folder / "codigos.json", codes)


def read(pais, minutes):
    """Catálogo de cada tienda y códigos de barras que faltan, hasta agotar el tiempo."""
    if pais in AWIN:
        return read_awin(pais)
    from .fetch import Fetcher
    folder = DATA / pais
    catalog = _load(folder / "tiendas.json", {})   # {tienda: {handle: {t, v, ty, f, p, st, img}}}
    codes = _load(folder / "codigos.json", {})     # {tienda: {handle: ean o ""}}
    end = time.time() + minutes * 60
    fetcher = Fetcher(delay=(1.0, 2.0))
    fresh = (folder / "tiendas.json").exists() and time.time() - (folder / "tiendas.json").stat().st_mtime < 20 * 3600
    shops = {k: v for k, v in STORES[pais].items() if k not in LOOKUP.get(pais, {}) and k not in WOO.get(pais, ())
             and k not in WOO_NAME.get(pais, ()) and k not in SITEMAP.get(pais, {})
             and k not in LISTING.get(pais, {})}
    for sid, (name, base) in ([] if fresh else shops.items()):  # catálogos: una vez al día
        if time.time() > end:
            break
        items, page = {}, 1
        while time.time() < end and page <= 400:
            url = f"{base}/products.json?limit=250&page={page}"
            if not fetcher.allowed(url)[0]:
                break
            try:
                r = fetcher.get(url)
                prods = r.json().get("products", []) if r.status_code == 200 else []
            except Exception:  # noqa: BLE001
                break
            if not prods:
                break
            for p in prods:
                v = (p.get("variants") or [{}])[0]
                f = _fmt(p.get("title"), p.get("product_type"), " ".join(p.get("tags") or []), v.get("title"))
                if not f or NOT_MUSIC.search(p.get("title", "")):
                    continue
                try:
                    price = float(v.get("price"))
                except (TypeError, ValueError):
                    continue
                img = ((p.get("images") or [{}])[0]).get("src")
                # Tiendas cuya referencia es el código de barras (Universal Music Italia): sin pedir la ficha.
                sku = re.sub(r"\D", "", str(v.get("sku") or v.get("barcode") or "")).lstrip("0")
                if 11 <= len(sku) <= 13 and p["handle"] not in codes.get(sid, {}):
                    codes.setdefault(sid, {})[p["handle"]] = sku.zfill(13)
                items[p["handle"]] = {"t": p.get("title", ""), "v": p.get("vendor", ""), "ty": p.get("product_type", ""),
                                      "f": f, "p": price, "st": bool(v.get("available")), "img": img}
            page += 1
        if items:
            catalog[sid] = items
            print(f"[{sid}] {len(items)} discos", flush=True)
    for sid in ([] if fresh else sorted(WOO.get(pais, ())) + sorted(WOO_NAME.get(pais, ()))):
        if time.time() > end:
            break
        items = _read_woo(fetcher, STORES[pais][sid][1], end, codes.setdefault(sid, {}), need_ean=sid in WOO.get(pais, ()))
        if items:
            catalog[sid] = items
            print(f"[{sid}] {len(items)} discos", flush=True)
    for sid, tpl in ([] if fresh else sorted(LISTING.get(pais, {}).items())):
        items = _read_listing(fetcher, tpl, end, codes.setdefault(sid, {}))
        if items:
            catalog[sid] = items
            print(f"[{sid}] {len(items)} discos", flush=True)
    if not fresh:
        _save(folder / "tiendas.json", catalog)
    # Códigos de barras: de la ficha de cada disco, una vez
    # Una tienda por hilo, cada una con su Fetcher y sus pausas: avanzan a la vez sin apretar a ninguna.
    from concurrent.futures import ThreadPoolExecutor
    import threading
    lock, count = threading.Lock(), [0]

    # Con tiendas que se consultan por EAN (LOOKUP), los códigos solo se piden la mitad del tiempo: la otra mitad es
    # para consultar precios.
    codes_end = (time.time() + (end - time.time()) / 2) if pais in LOOKUP else end

    def store_codes(sid):
        f = Fetcher(delay=(1.0, 2.0))
        base = STORES[pais][sid][1]
        todo = [h for h in catalog.get(sid, {}) if h not in codes.get(sid, {})]
        for h in todo:
            if time.time() > codes_end:
                return
            url = f"{base}/products/{h}.json"
            if not f.allowed(url)[0]:
                return
            try:
                r = f.get(url)
                vs = r.json()["product"]["variants"] if r.status_code == 200 else []
                ean = re.sub(r"\D", "", str((vs[0] if vs else {}).get("barcode") or "")).lstrip("0")
            except Exception:  # noqa: BLE001
                continue
            with lock:
                codes.setdefault(sid, {})[h] = ean.zfill(13) if 11 <= len(ean) <= 13 else ""  # GTIN-14 con ceros: EAN
                count[0] += 1
                if count[0] % 500 == 0:
                    _save(folder / "codigos.json", codes)
    print(f"códigos por pedir: {sum(len([h for h in its if h not in codes.get(sid, {})]) for sid, its in catalog.items())}", flush=True)
    with ThreadPoolExecutor(len(catalog) or 1) as ex:
        list(ex.map(store_codes, [k for k in catalog if k in shops]))
    _save(folder / "codigos.json", codes)
    print(f"códigos nuevos: {count[0]}", flush=True)
    if pais in LOOKUP:
        _lookup(pais, end, catalog, codes)
    if pais in SITEMAP:
        _sitemap_stores(pais, end, catalog, codes)


def _nice(name):
    """"BUNBURY ENRIQUE - PALOSANTO (CD)" → "Bunbury Enrique - Palosanto": sin el formato y sin todo en mayúsculas."""
    name = re.sub(r"\s*[\(\[][^\)\]]*\b(?:cd|lp|vinilo|vinyl|casete|cassette|mc|ep|single)\b[^\)\]]*[\)\]]\s*$", "",
                  html.unescape(name or ""), flags=re.I).strip()
    name = re.sub(r"\s+-\s+(?:\d?cd|\d?lp|vinilo|vinyl|casete|cassette|mc|ep|single)\b[^-]*$", "", name, flags=re.I).strip()
    if name.isupper():
        name = re.sub(r"[^\W\d_]+(?:['´’][^\W\d_]+)?", lambda m: m.group(0)[:1].upper() + m.group(0)[1:], name.lower())
    return name


def _sitemap_stores(pais, end, catalog, codes):
    """Tiendas de SITEMAP: dirección y EAN de cada disco del mapa del sitio; precio y stock de la ficha (JSON-LD).
    Primero los nunca consultados que ya tienen otras tiendas, luego los nunca consultados y luego los más antiguos."""
    from datetime import date
    from .fetch import Fetcher
    folder = DATA / pais
    seen = _load(folder / "consultas.json", {})
    ours = {e for s, hs in codes.items() for e in hs.values() if e}
    today = date.today().isoformat()
    stop = min(end, time.time() + SITEMAP_MIN * 60)
    for sid, sm in SITEMAP[pais].items():
        f = Fetcher(delay=(1.0, 2.0))
        try:
            if not f.allowed(sm)[0]:
                continue
            urls = re.findall(r"<loc>(?:<!\[CDATA\[)?([^<\]]+?-(\d{12,13})\.html)", f.get(sm).text)
        except Exception as exc:  # noqa: BLE001
            print(f"[{sid}] sin mapa del sitio: {exc}", flush=True)
            continue
        url_of = {e.zfill(13): u for u, e in urls}
        done = seen.setdefault(sid, {})
        for e in [e for e in done if e not in url_of]:  # ya no está en la tienda
            del done[e]
        todo = sorted(url_of, key=lambda e: (e in done, e not in ours, done.get(e, [""])[0]))
        n = 0
        for e in todo:
            if time.time() > stop or done.get(e, [""])[0] == today:
                break
            u = url_of[e]
            if not f.allowed(u)[0]:
                break
            try:
                r = f.get(u)
                d = _ld_disc(r.text) if r.status_code == 200 else {}
            except Exception:  # noqa: BLE001
                continue
            done[e] = ([today, d["p"], d.get("st", True), u, _nice(d.get("t")), "", d.get("img") or "", _fmt(d.get("t")) or ""]
                       if d.get("p") else [today])
            n += 1
            if n % 500 == 0:
                _save(folder / "consultas.json", seen)
        print(f"[{sid}] {len(url_of)} discos en su mapa · {n} fichas leídas · {sum(1 for x in done.values() if len(x) > 1)} con precio", flush=True)
    _save(folder / "consultas.json", seen)


def _read_listing(fetcher, tpl, end, codes):
    """Listado de una tienda PrestaShop (LISTING), página a página: dirección con EAN, nombre, precio y si está agotado."""
    items, n = {}, 1
    while time.time() < end and n <= 300:
        url = tpl.format(n=n)
        if not fetcher.allowed(url)[0]:
            break
        try:
            r = fetcher.get(url)
            t = r.text if r.status_code == 200 else ""
        except Exception:  # noqa: BLE001
            break
        blocks = t.split('class="product-miniature')[1:]
        new = 0
        for b in blocks:
            m = re.search(r'href="(https?://[^"]+?-(\d{12,13})\.html)"', b)
            pr = re.search(r'itemprop="price"[^>]*>\s*([\d.]+,\d{2})', b)
            if not m or not pr:
                continue
            e = m.group(2).zfill(13)
            if e in items:
                continue
            name = re.search(r'product-title[^>]*><a[^>]*>([^<]+)</a>', b)
            img = re.search(r'<img[^>]+src="([^"]+)"', b)
            items[e] = {"t": html.unescape(name.group(1)).strip() if name else "", "v": "", "ty": "", "f": "",
                        "p": float(pr.group(1).replace(".", "").replace(",", ".")),
                        "st": not re.search(r"(?i)out[_-]of[_-]stock|agotado|sin stock", b), "img": img.group(1) if img else None,
                        "u": m.group(1)}
            codes[e] = e
            new += 1
        if not new:
            break
        n += 1
    return items


def _woo_name(name):
    """"Artista «Título» LP" (El Genio Equivocado) o "Artista | Título (Vinilo azul)" (Alta Fidelidad) → "Artista - Título"."""
    name = re.sub(r"\s+", " ", html.unescape(name)).strip()
    m = re.match(r"^(.+?)\s*«(.+?)»", name)
    if m:
        return f"{m.group(1).strip()} - {m.group(2).strip()}"
    m = re.match(r"^(.+?)\s+[\|–—]\s+(.+)$", name)
    if m:
        # Fuera "(Vinilo)" o "(CD)"; "(Vinilo azul)" se queda: es otra edición
        title = re.sub(r"\s*\(\s*(?:\d?\s?(?:vinilos?|cd|casete|lp)\s*)\)\s*$", "", m.group(2), flags=re.I)
        return f"{m.group(1).strip()} - {title.strip()}"
    return name


def _read_woo(fetcher, base, end, codes, need_ean=True):
    """Catálogo de una tienda WooCommerce por su API pública de tienda (la misma que usa su web): 100 productos por
    página. El EAN va en la referencia (sku): se guarda en codes sin pedir nada más."""
    items, page = {}, 1
    while time.time() < end and page <= 400:
        url = f"{base}/wp-json/wc/store/v1/products?per_page=100&page={page}"
        if not fetcher.allowed(url)[0]:
            break
        try:
            r = fetcher.get(url)
            prods = r.json() if r.status_code == 200 else []
        except Exception:  # noqa: BLE001
            break
        if not isinstance(prods, list) or not prods:
            break
        for p in prods:
            cats = " ".join([c.get("name", "") for c in p.get("categories") or []]
                            + [t.get("name", "") for a in p.get("attributes") or [] for t in a.get("terms") or []])
            raw = html.unescape(p.get("name") or "")
            f = _fmt(raw, cats)
            if not f or NOT_MUSIC.search(raw):
                continue
            pr = p.get("prices") or {}
            try:
                price = int(pr["price"]) / 10 ** int(pr.get("currency_minor_unit", 2))
            except (KeyError, TypeError, ValueError):
                continue
            ean = re.sub(r"\D", "", str(p.get("sku") or "")).lstrip("0")
            if not price or (need_ean and not (11 <= len(ean) <= 13)):
                continue
            h = str(p["id"])
            if need_ean:
                codes[h] = ean.zfill(13)
            items[h] = {"t": _woo_name(raw), "v": "", "ty": cats, "f": f, "p": price, "st": bool(p.get("is_in_stock")),
                        "img": ((p.get("images") or [{}])[0]).get("src"), "u": p.get("permalink")}
        page += 1
    return items


def _ld_disc(html_text):
    """Precio, stock, nombre, artista y foto del JSON-LD de una ficha (Product o MusicAlbum, también dentro de @graph)."""
    out = {}
    for m in re.finditer(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', html_text, re.S):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        nodes = d if isinstance(d, list) else d.get("@graph", [d]) if isinstance(d, dict) else []
        for x in nodes:
            if not isinstance(x, dict) or x.get("@type") not in ("Product", "MusicAlbum"):
                continue
            o = x.get("offers") or {}
            o = o[0] if isinstance(o, list) and o else o
            if not out.get("p") and isinstance(o, dict) and o.get("price"):
                try:
                    out["p"] = float(str(o["price"]).replace(",", "."))
                except ValueError:
                    pass
                out["st"] = "InStock" in str(o.get("availability", "InStock"))
            out.setdefault("t", x.get("name"))
            img = x.get("image")
            out.setdefault("img", img[0] if isinstance(img, list) and img else img)
            a = x.get("byArtist")
            if isinstance(a, dict) and a.get("name"):
                out["v"] = a["name"]
    return out


def _lookup(pais, end, catalog, codes):
    """Tiendas sin catálogo (LOOKUP): cada disco de los catálogos con código se busca por su EAN en cada una, primero
    los nunca consultados y luego los más antiguos. Lo encontrado (y lo no encontrado, para no repetir) se guarda en
    consultas.json (en git): {tienda: {ean: [fecha, precio, stock, url, nombre, artista, foto] o [fecha]}}."""
    from concurrent.futures import ThreadPoolExecutor
    from datetime import date
    from .fetch import Fetcher
    folder = DATA / pais
    seen = _load(folder / "consultas.json", {})
    fmt_of = {codes[s][h]: it["f"] for s, its in catalog.items() for h, it in its.items() if codes.get(s, {}).get(h)}
    eans = sorted(fmt_of, key=lambda e: (fmt_of[e] != "vinilo", e))  # los vinilos primero
    today = date.today().isoformat()

    def one_store(sid):
        f = Fetcher(delay=(1.0, 2.0))
        done = seen.setdefault(sid, {})
        todo = sorted(eans, key=lambda e: done.get(e, [""])[0])  # nunca consultados ("") y luego los más antiguos
        n = 0
        for e in todo:
            if time.time() > end or done.get(e, [""])[0] == today:
                break
            url = LOOKUP[pais][sid].format(ean=e)
            if not f.allowed(url)[0]:
                return
            try:
                r = f.get(url)
                d = _ld_disc(r.text) if r.status_code == 200 else {}
            except Exception:  # noqa: BLE001
                continue
            done[e] = ([today, d["p"], d.get("st", True), r.url, d.get("t") or "", d.get("v") or "", d.get("img") or ""]
                       if d.get("p") else [today])
            n += 1
        print(f"[{sid}] {n} discos consultados", flush=True)

    with ThreadPoolExecutor(len(LOOKUP[pais])) as ex:
        list(ex.map(one_store, LOOKUP[pais]))
    _save(folder / "consultas.json", seen)


_ED_WORDS = (r"colou?r|clear|transparent|marble|splatter|indie|limitad|limited|firmad|signed|deluxe|picture|especial|"
             r"aniversario|anniversary|\bbox\b|\bred\b|\bblue\b|\bgreen\b|\byellow\b|\bwhite\b|\bpink\b|\bpurple\b|"
             r"\borange\b|\bgold|azul|\brojo|verde|amarill|blanco|\brosa\b|naranja|morado|dorado|\b[2-9] ?(?:lp|cd)")
_NOISE = re.compile(r"(?i)\b(?:lp|2lp|3lp|cd|2cd|vinilo|vinyl|casete|cassette|mc|ep|ed|edici[oó]n|edition|reedici[oó]n|"
                    r"reissue|remaster(?:ed|izado)?|the|el|la|los|las)\b")


def _name_key(name):
    """Clave para emparejar sin código de barras: (artista, título) normalizados y si es una edición especial."""
    t = unicodedata.normalize("NFKD", html.unescape(name)).encode("ascii", "ignore").decode().lower()
    special = bool(re.search(_ED_WORDS, t))
    if " - " not in t:
        return None, special
    a, ti = t.split(" - ", 1)
    ti = re.sub(r"[\(\[].*?[\)\]]", " ", ti)
    ti = re.split(r"\b(?:lp|cd|vinilo|vinyl|ed\.?|edicion|edition)\b", ti)[0]  # lo que va tras el formato: edición
    norm = lambda x: " ".join(_NOISE.sub(" ", re.sub(r"[^a-z0-9]+", " ", x)).split())
    a, ti = norm(a), norm(ti)
    return ((a, ti) if a and ti else None), special


def _match_names(pais, catalog, by):
    """Discos de tiendas sin código (WOO_NAME) con el disco con código de mismo artista, título y formato. Solo si hay
    un único candidato con el mismo tipo de edición (normal o especial): si hay duda, no se empareja."""
    index = {}
    for ean, d in by.items():
        for n in d["names"]:
            k, sp = _name_key(n)
            if k:
                index.setdefault((k, d["fmt"], sp), set()).add(ean)
    matched = {}
    for sid in WOO_NAME[pais]:
        for h, it in catalog.get(sid, {}).items():
            k, sp = _name_key(it["t"])
            cands = index.get((k, it["f"], sp)) if k else None
            if cands and len(cands) == 1:
                ean = next(iter(cands))
                if all(i["s"] != sid for i in by[ean]["items"]):
                    by[ean]["items"].append({"s": sid, "p": it["p"], "u": it.get("u"), "st": it["st"]})
                    matched[sid] = matched.get(sid, 0) + 1
    print("emparejados por nombre: " + ", ".join(f"{s} {n}" for s, n in sorted(matched.items())), flush=True)


def build_data(pais):
    """Discos agrupados por código de barras: [{ean, name, fmt, img, items: [{s, p, u, st}]}]."""
    folder = DATA / pais
    catalog, codes = _load(folder / "tiendas.json", {}), _load(folder / "codigos.json", {})
    if pais in LOOKUP:  # lo encontrado en las tiendas que se consultan por EAN, como si fuera su catálogo
        fmt_of = {codes[s][h]: it["f"] for s, its in catalog.items() for h, it in its.items() if codes.get(s, {}).get(h)}
        for sid, found in _load(folder / "consultas.json", {}).items():
            for e, row in found.items():
                if len(row) >= 7 and e in fmt_of:
                    catalog.setdefault(sid, {})[e] = {"t": row[4], "v": row[5], "ty": "", "f": fmt_of[e], "p": row[1],
                                                      "st": row[2], "img": row[6], "u": row[3]}
                    codes.setdefault(sid, {})[e] = e
    if pais in SITEMAP:  # tiendas leídas por su mapa del sitio: todos sus discos con formato (también los que solo tienen ellas)
        found = _load(folder / "consultas.json", {})
        for sid in SITEMAP[pais]:
            for e, row in found.get(sid, {}).items():
                if len(row) >= 8 and row[7]:
                    catalog.setdefault(sid, {})[e] = {"t": row[4], "v": "", "ty": "", "f": row[7], "p": row[1], "st": row[2],
                                                      "img": row[6], "u": row[3]}
                    codes.setdefault(sid, {})[e] = e
    by = {}
    for sid, its in catalog.items():
        base = STORES[pais][sid][1]
        for h, it in its.items():
            ean = codes.get(sid, {}).get(h)
            if not ean:
                continue
            ean = ean.zfill(13)
            d = by.setdefault(ean, {"ean": ean, "names": [], "fmt": it["f"], "img": None, "items": []})
            artist = {"recordstore": it["v"], "sisterray": it["ty"], "cultura": it["v"], "fnac": it["v"],
                      "zavvi": it["v"], "ibs": it["v"], "feltrinelli": it["v"]}.get(sid, "")
            title = it["t"]
            if artist and " - " not in title and not title.lower().startswith(artist.lower()):
                title = f"{artist} - {re.sub(r':\s*(?:CD|Vinyl LP|Cassette)\s*$', '', title)}"
            d["names"].append(title)
            d["fmt"] = d["fmt"] or it["f"]  # las de ONLY_MATCH no saben el formato: el de las demás
            d["img"] = d["img"] or it.get("img")
            d["items"].append({"s": sid, "p": it["p"], "u": it.get("u") or f"{base}/products/{h}", "st": it["st"]})
    # Tiendas que solo se suman a discos de otras (ONLY_MATCH): fuera los que solo tienen ellas
    by = {e: d for e, d in by.items() if any(i["s"] not in ONLY_MATCH for i in d["items"])}
    for d in by.values():  # el formato y el nombre, de las otras tiendas
        own = [n for n, i in zip(d["names"], d["items"]) if i["s"] not in ONLY_MATCH]
        d["names"] = own or d["names"]
    if pais in WOO_NAME:
        _match_names(pais, catalog, by)
    out = []
    for d in by.values():
        # El nombre más limpio: con "Artista - Título" y sin coletillas de formato o reserva
        names = sorted(d.pop("names"), key=lambda n: (" - " not in n, len(n)))
        name = re.sub(r"\s{2,}", " ", CLEAN.sub(" ", names[0])).strip(" -–:*")
        items = {}
        for i in sorted(d["items"], key=lambda i: (not i["st"], i["p"])):
            items.setdefault(i["s"], i)  # una oferta por tienda
        d["items"] = sorted(items.values(), key=lambda i: (not i["st"], i["p"]))
        d["name"] = name
        d["slug"] = f"{slug(name)}-{TXT.get(pais, {}).get("sfx", {'vinilo': 'vinyl', 'cd': 'cd', 'casete': 'cassette'})[d['fmt']]}-{d['ean']}"
        out.append(d)
    out.sort(key=lambda d: (-len(d["items"]), d["name"]))
    # En git solo los que se comparan (dos o más tiendas): son los que tienen página. El catálogo de cada tienda
    # (tiendas.json) no se guarda en git: se vuelve a leer cada día.
    # En git (discos.json) solo los que se comparan: lo leen la portada y las lecturas de guitarras. Las páginas se
    # hacen de todos (también los de una sola tienda: llevan el botón de Amazon), en la lectura de discos.
    _save(folder / "discos.json", [d for d in out if len(d["items"]) >= 2])
    return out


# --- Páginas ---------------------------------------------------------------------------------------------------
TXT = {"uk": {"dir": "records", "one": "record", "home": "Records", "promo": "New: compare vinyl, CD & cassette prices", "tile": "Vinyl, CDs & cassettes", "fmts": {"vinilo": ("Vinyl", "vinyl"), "cd": ("CDs", "cds"),
                                                                                 "casete": ("Cassettes", "cassettes")},
              "fmt1": {"vinilo": "vinyl", "cd": "CD", "casete": "cassette"},
              "title": "{n} {f}: price comparison", "desc": "Compare the price of {n} on {f} in {k} UK record shops: today's price, stock and the cheapest shop.",
              "h_index": "Records: compare vinyl, CD and cassette prices", "d_index": "Compare the price of vinyl records, CDs and cassettes in UK record shops, every day.",
              "in_stock": "In stock", "out": "Out of stock", "shops": "shops", "buy": "Go to shop", "cheapest": "Cheapest today",
              "more": "Most compared", "note": "Prices include VAT; delivery may vary by shop.",
              "amazon": "https://www.amazon.co.uk/s?k={ean}&tag=guitle08-21", "amazon_btn": "Search this record on Amazon",
              "amazon_txt": "Prefer to buy on Amazon?",
              "desc1": "{n} on {f}: today's price at {s} and where else to buy it, including Amazon.", "where1": "at {s}",
              "search_ph": "Search records: artist or album…", "search_res": "{n} records found", "search_none": "No records found",
              "f_artist": "Artist or band", "f_format": "Format", "f_all": "All formats", "f_sort": "Sort",
              "s_price": "Cheapest first", "s_shops": "Most compared", "s_az": "A–Z",
              "artist_t": "{a}: vinyl, CD and cassette prices", "artist_d": "Compare the price of {n} {a} records on vinyl, CD and cassette in UK record shops.",
              "artist_all": "All their records",
              "deals": "Vinyl & CD deals", "deals_file": "deals", "save": "save {m} vs the dearest shop",
              "deals_desc": "The records with the biggest price difference between UK shops today (in stock only).",
              "guitars": "Guitar deals today", "guitars_more": "All guitar deals",
              "guide_file": "where-to-buy-vinyl-uk", "guide": "Where to buy vinyl cheapest in the UK",
              "guide_desc": "How to find the cheapest price for a vinyl record, CD or cassette in the UK: compare record shops, watch editions and delivery, with today's biggest savings.",
              "guide_body": """<section class="hub-sec guia" style="max-width:780px;line-height:1.65">
<h2>The same record can cost very different prices</h2>
<p>UK record shops price the same pressing differently, and the gap is often <strong>£5 to £20</strong> on new vinyl. Before buying, compare the exact same edition (same barcode) across shops: guitle does that every day for {shops} UK record shops and shows the cheapest one with stock.</p>
<h2>Check the edition</h2>
<ul>
<li><strong>Standard black vinyl</strong> is usually the cheapest pressing.</li>
<li><strong>Coloured, indie-exclusive or signed editions</strong> cost more and sell out fast: compare like with like.</li>
<li><strong>Reissues and remasters</strong> have their own barcode: a 2023 reissue is a different record from the original pressing.</li>
</ul>
<h2>Don't forget delivery</h2>
<p>Most UK record shops offer free delivery above a minimum order (often around £40 to £60). If you're buying one record, a slightly higher price with free delivery can work out cheaper.</p>
<h2>Pre-orders</h2>
<p>New releases are often cheapest on pre-order, and prices tend to rise once the first pressing sells out.</p>
</section>""",
              "faqs": [("Where is the cheapest place to buy vinyl in the UK?", "It depends on the record: the same pressing can be several pounds cheaper in one shop than another. Compare the exact edition (by barcode) across UK record shops before buying."),
                       ("Why is the same vinyl record different prices in different shops?", "Each shop sets its own price and runs its own offers, and stock levels change daily, so the cheapest shop for a record changes over time."),
                       ("Are coloured vinyl editions worth the extra cost?", "They're collectable and often limited, but the music is the same: if you just want to listen, the standard black pressing is usually cheaper.")]}}


TXT["fr"] = {
    "dir": "disques", "one": "disque", "home": "Disques", "promo": "Nouveau : comparez les prix des vinyles, CD et cassettes",
    "tile": "Vinyles, CD et cassettes",
    "fmts": {"vinilo": ("Vinyles", "vinyles"), "cd": ("CD", "cd"), "casete": ("Cassettes", "cassettes")},
    "fmt1": {"vinilo": "vinyle", "cd": "CD", "casete": "cassette"},
    "title": "{n} en {f} : comparateur de prix",
    "desc": "Comparez le prix de {n} en {f} chez {k} disquaires en ligne en France : prix du jour, stock et magasin le moins cher.",
    "desc1": "{n} en {f} : prix du jour chez {s} et où l'acheter ailleurs, Amazon compris.", "where1": "chez {s}",
    "h_index": "Disques : comparez les prix des vinyles, CD et cassettes",
    "d_index": "Comparez chaque jour le prix des vinyles, CD et cassettes chez les disquaires en ligne en France.",
    "in_stock": "En stock", "out": "Épuisé", "shops": "magasins", "buy": "Voir en magasin", "cheapest": "Le moins cher aujourd'hui",
    "more": "Les plus comparés", "note": "Prix TTC ; les frais de port peuvent varier selon le magasin.",
    "amazon": "https://www.amazon.fr/s?k={ean}&tag=guitle00-21", "amazon_btn": "Chercher ce disque sur Amazon",
    "amazon_txt": "Vous préférez Amazon ?",
    "search_ph": "Rechercher : artiste ou album…", "search_res": "{n} disques trouvés", "search_none": "Aucun disque trouvé",
    "f_artist": "Artiste ou groupe", "f_format": "Format", "f_all": "Tous les formats", "f_sort": "Trier",
    "s_price": "Moins cher d'abord", "s_shops": "Les plus comparés", "s_az": "A–Z",
    "artist_t": "{a} : prix des vinyles, CD et cassettes",
    "artist_d": "Comparez le prix de {n} disques de {a} en vinyle, CD et cassette chez les disquaires en ligne en France.",
    "artist_all": "Tous ses disques",
    "deals": "Bons plans vinyles et CD", "deals_file": "bons-plans", "save": "{m} de moins qu'au plus cher",
    "deals_desc": "Les disques avec le plus grand écart de prix entre magasins aujourd'hui (en stock uniquement).",
    "guitars": "Les bons plans guitares du jour", "guitars_more": "Tous les bons plans guitares",
}


TXT["it"] = {
    "dir": "dischi", "one": "disco", "home": "Dischi", "promo": "Novità: confronta i prezzi di vinili, CD e cassette",
    "tile": "Vinili, CD e cassette",
    "fmts": {"vinilo": ("Vinili", "vinili"), "cd": ("CD", "cd"), "casete": ("Cassette", "cassette")},
    "fmt1": {"vinilo": "vinile", "cd": "CD", "casete": "cassetta"},
    "title": "{n} in {f}: confronto prezzi",
    "desc": "Confronta il prezzo di {n} in {f} in {k} negozi di dischi online in Italia: prezzo di oggi, disponibilità e il negozio più economico.",
    "desc1": "{n} in {f}: il prezzo di oggi da {s} e dove comprarlo, anche su Amazon.", "where1": "da {s}",
    "h_index": "Dischi: confronta i prezzi di vinili, CD e cassette",
    "d_index": "Confronta ogni giorno il prezzo di vinili, CD e cassette nei negozi di dischi online in Italia.",
    "in_stock": "Disponibile", "out": "Esaurito", "shops": "negozi", "buy": "Vai al negozio", "cheapest": "Il più economico oggi",
    "more": "I più confrontati", "note": "Prezzi IVA inclusa; le spese di spedizione possono variare.",
    "amazon": "https://www.amazon.it/s?k={ean}&tag=guitle0e-21", "amazon_btn": "Cerca questo disco su Amazon", "amazon_txt": "Preferisci Amazon?",
    "search_ph": "Cerca: artista o album…", "search_res": "{n} dischi trovati", "search_none": "Nessun disco trovato",
    "f_artist": "Artista o gruppo", "f_format": "Formato", "f_all": "Tutti i formati", "f_sort": "Ordina",
    "s_price": "Prima i più economici", "s_shops": "I più confrontati", "s_az": "A–Z",
    "artist_t": "{a}: prezzi di vinili, CD e cassette",
    "artist_d": "Confronta il prezzo di {n} dischi di {a} in vinile, CD e cassetta nei negozi di dischi online in Italia.",
    "artist_all": "Tutti i suoi dischi",
    "deals": "Offerte vinili e CD", "deals_file": "offerte", "save": "{m} in meno del più caro",
    "deals_desc": "I dischi con la maggiore differenza di prezzo tra negozi oggi (solo disponibili).",
    "guitars": "Le offerte chitarre di oggi", "guitars_more": "Tutte le offerte chitarre",
}



TXT["es"] = {
    "dir": "discos", "one": "disco", "home": "Discos", "promo": "Nuevo: compara precios de vinilos, CD y casetes",
    "tile": "Vinilos, CD y casetes", "shops_n": 3, "sfx": {"vinilo": "vinilo", "cd": "cd", "casete": "casete"},
    "fmts": {"vinilo": ("Vinilos", "vinilos"), "cd": ("CD", "cd"), "casete": ("Casetes", "casetes")},
    "fmt1": {"vinilo": "vinilo", "cd": "CD", "casete": "casete"},
    "title": "{n} en {f}: comparador de precios",
    "desc": "Compara el precio de {n} en {f} en {k} tiendas de discos de España: precio de hoy, stock y la tienda más barata.",
    "desc1": "{n} en {f}: precio de hoy en {s} y dónde más comprarlo, también en Amazon.", "where1": "en {s}",
    "h_index": "Discos: compara precios de vinilos, CD y casetes",
    "d_index": "Compara cada día el precio de vinilos, CD y casetes en tiendas de discos de España.",
    "in_stock": "Disponible", "out": "Agotado", "shops": "tiendas", "buy": "Ver en la tienda", "cheapest": "El más barato hoy",
    "more": "Los más comparados", "note": "Precios con IVA; los gastos de envío dependen de cada tienda.",
    "amazon": "https://www.amazon.es/s?k={ean}&tag=guitle-21", "amazon_btn": "Buscar este disco en Amazon",
    "amazon_txt": "¿Prefieres comprarlo en Amazon?",
    "search_ph": "Busca un disco: artista o álbum…", "search_res": "{n} discos encontrados", "search_none": "No hay discos con esa búsqueda",
    "f_artist": "Artista o grupo", "f_format": "Formato", "f_all": "Todos los formatos", "f_sort": "Ordenar",
    "s_price": "Más baratos primero", "s_shops": "Más comparados", "s_az": "A–Z",
    "artist_t": "{a}: precios de vinilos, CD y casetes",
    "artist_d": "Compara el precio de {n} discos de {a} en vinilo, CD y casete en tiendas de discos de España.",
    "artist_all": "Todos sus discos",
    "deals": "Chollos de vinilos y CD", "deals_file": "chollos", "save": "{m} menos que en la más cara",
    "deals_desc": "Los discos con más diferencia de precio entre tiendas hoy (solo con stock).",
    "guitars": "Chollos de guitarras de hoy", "guitars_more": "Todos los chollos de guitarras",
    "guide_file": "donde-comprar-vinilos-baratos", "guide": "Dónde comprar vinilos más baratos en España",
    "guide_desc": "Cómo encontrar el precio más bajo de un vinilo, CD o casete en España: compara tiendas de discos, fíjate en la edición y en el envío, con los mayores ahorros de hoy.",
    "guide_body": """<section class="hub-sec guia" style="max-width:780px;line-height:1.65">
<h2>El mismo disco puede costar muy distinto</h2>
<p>Cada tienda de discos pone su precio a la misma edición, y en vinilo nuevo la diferencia suele ser de <strong>3 a 15 €</strong>. Antes de comprar, compara exactamente la misma edición (el mismo código de barras) en varias tiendas: guitle lo hace cada día con {shops} tiendas de discos de España, además de Amazon, y te enseña la más barata con stock.</p>
<h2>Fíjate en la edición</h2>
<ul>
<li><strong>El vinilo negro normal</strong> suele ser la edición más barata.</li>
<li><strong>Los vinilos de color, ediciones limitadas o firmadas</strong> cuestan más y se agotan antes: compara siempre la misma edición.</li>
<li><strong>Las reediciones y remasterizaciones</strong> tienen su propio código de barras: una reedición de 2024 es un disco distinto del original.</li>
</ul>
<h2>No te olvides del envío</h2>
<p>Muchas tiendas de discos tienen envío gratis a partir de un importe mínimo. Si compras un solo disco, un precio algo más alto con envío gratis puede salir más barato.</p>
<h2>Preventas</h2>
<p>Las novedades suelen estar más baratas en preventa, y el precio tiende a subir cuando se agota la primera tirada.</p>
<h2>Compra en tiendas de discos</h2>
<p>Las tiendas independientes (Supersonic en Santander, El Genio Equivocado en Barcelona, Alta Fidelidad en Oviedo…) a menudo tienen mejor precio que las grandes superficies, y comprarles ayuda a que sigan abiertas.</p>
</section>""",
    "faqs": [("¿Dónde es más barato comprar vinilos en España?", "Depende del disco: la misma edición puede costar varios euros menos en una tienda que en otra. Compara la edición exacta (por su código de barras) en varias tiendas de discos antes de comprar."),
             ("¿Por qué el mismo vinilo tiene precios distintos en cada tienda?", "Cada tienda pone su precio y sus ofertas, y el stock cambia cada día, así que la tienda más barata de un disco va cambiando."),
             ("¿Merece la pena pagar más por un vinilo de color?", "Son coleccionables y a menudo limitados, pero la música es la misma: si solo quieres escucharlo, el vinilo negro normal suele ser más barato.")],
}

def _pre(pais):
    """Ruta de la web del país: España está en la raíz (guitle.com/discos/), los demás en su carpeta (/uk/records/)."""
    return "" if pais == "es" else f"/{pais}"


def _img(u, w):
    """Foto a un tamaño: las de Shopify se piden ya reducidas (?width=); las demás tal cual."""
    if not u:
        return ""
    if "cdn.shopify.com" in u or "/cdn/shop/" in u:
        return f'{u}{"&" if "?" in u else "?"}width={w}'
    return u


def _e(v):
    return html.escape(str(v or ""), quote=True)


def write_pages(pais, discs=None):
    """Página de cada disco con código (en una o más tiendas), listados por formato y el índice. Devuelve sus URL.
    Las páginas van en cajas (scraper/cajas.py, <país>/_r/): .github/r2.sh carpeta sube solo las cajas que cambian."""
    from . import intl, pages
    if pais not in TXT:
        return []
    discs = discs if discs is not None else _load(DATA / pais / "discos.json", [])
    if not discs:
        return []
    T, t = TXT[pais], intl.strings(pais)
    names = {sid: n for sid, (n, _) in STORES[pais].items()}
    out = (ROOT if pais == "es" else ROOT / pais) / T["dir"]
    css = ('<link rel="stylesheet" href="/catalogo.css">\n<style>.disc{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:24px;'
           'margin-top:16px}.disc img{width:100%;border-radius:12px;background:#fff}.offers{width:100%;border-collapse:collapse}'
           '.offers td{padding:10px 6px;border-bottom:1px solid var(--border)}.offers .p{font-weight:700;text-align:right;'
           'font-variant-numeric:tabular-nums}.offers .st{color:var(--text-muted);font-size:.85rem}@media(max-width:640px)'
           '{.disc{grid-template-columns:1fr}}.dl{display:grid;gap:8px}.dl a{display:flex;justify-content:space-between;gap:12px;'
           'padding:10px 12px;border:1px solid var(--border);border-radius:10px;color:var(--text-primary);text-decoration:none}'
           '.dl a:hover{border-color:var(--accent)}.dl small{color:var(--text-muted)}</style>\n')
    top = f'  <div class="topbar"><div class="row">{intl._logo(pais, t)}<a class="navlink" href="{_pre(pais)}/{T["dir"]}/">{_e(T["home"])}</a></div></div>\n'

    def page(url, title, desc, body, ld=None):
        extra = css + (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' if ld else "")
        return (intl._head(pais, f"{title} · guitle", desc, url, extra) + "</head>\n<body>\n<main>\n" + top
                + f'  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{_e(title)}</h2>\n{body}\n  '
                + intl._foot(pais, t) + '\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n')

    urls, keep = [], set()
    multi = [d for d in discs if len(d["items"]) >= 2]
    # Chollos de guitarras del día en cada disco (y discos en las fichas de guitarras): un público lleva al otro
    guitar_box = ""
    try:
        cats = intl.catalogs(pais)
        gs = [p for k in ("electrica", "acustica", "clasica") for p in cats.get(k, {}).get("products", [])
              if p.get("slug") and p.get("th") and len({i["s"] for i in p["items"]}) >= 2]
        gap_g = lambda p: (max(i["p"] for i in p["items"]) - p["items"][0]["p"]) / max(i["p"] for i in p["items"])
        gs = sorted((p for p in gs if 0.05 <= gap_g(p) <= 0.4), key=gap_g, reverse=True)[:4]
        gnames = {k: v for d in cats.values() for k, v in d["stores"].items()}
        if gs:
            from .guias_intl import _tile
            guitar_box = (f'  <section><h3>{_e(T["guitars"])} <a class="navlink" href="{_pre(pais)}/">{_e(T["guitars_more"])} →</a></h3>'
                          f'<div class="grid">' + "".join(_tile(pais, p, gnames, intl, t) for p in gs) + "</div></section>")
    except Exception:  # noqa: BLE001 - sin catálogo de guitarras, sin recuadro
        pass
    acount = {}
    for d in discs:
        if " - " in d["name"]:
            a = d["name"].split(" - ", 1)[0].strip()
            acount[a] = acount.get(a, 0) + 1
    for d in discs:  # todos: también los de una sola tienda (precio + botón de Amazon)
        f1 = T["fmt1"][d["fmt"]]
        url = f"{_pre(pais)}/{T['dir']}/{d['slug']}.html"
        path = out / f"{d['slug']}.html"
        a = d["name"].split(" - ", 1)[0].strip() if " - " in d["name"] else ""
        alink = (f' · <a href="{_pre(pais)}/{T["dir"]}/artist/{slug(a)}.html">{_e(T["artist_all"])} ({_e(a)})</a>'
                 if a and acount.get(a, 0) >= 2 and slug(a) else "")
        pages._write(path, _disc_page(pais, d, f1, url, names, T, t, guitar_box, alink))
        urls.append(url)
        keep.add(path)
    # Listados por formato e índice
    links = []
    for fk, (label, fname) in T["fmts"].items():
        ds = [d for d in multi if d["fmt"] == fk][:240]
        if not ds:
            continue
        items = "".join(_disc_tile(pais, d, T, names) for d in ds)
        url = f"{_pre(pais)}/{T['dir']}/{fname}.html"
        path = out / f"{fname}.html"
        pages._write(path, page(url, label, T["d_index"], f'  <div class="grid">{items}</div>'))
        urls.append(url)
        keep.add(path)
        links.append(f'<a class="chip" href="{url}">{_e(label)} <span class="muted">({len([d for d in multi if d["fmt"] == fk])})</span></a>')
    # Mayores diferencias entre tiendas (solo ofertas con stock): para la portada, Instagram y quien busca chollos
    def gap(d):
        live = [i["p"] for i in d["items"] if i["st"]]
        return (max(live) - min(live)) if len(live) >= 2 else 0
    deals = sorted((d for d in multi if gap(d) >= 2), key=gap, reverse=True)[:100]
    if deals:
        rows = "".join(_disc_tile(pais, d, T, names).replace('<div class="img">', f'<span class="badge">{_e(T["save"].format(m=intl.money(gap(d), pais)))}</span><div class="img">', 1)
                       for d in deals)
        url = f"{_pre(pais)}/{T['dir']}/{T['deals_file']}.html"
        path = out / f"{T['deals_file']}.html"
        pages._write(path, page(url, T["deals"], T["deals_desc"], f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["deals_desc"])}</p>\n  <div class="grid">{rows}</div>'))
        urls.append(url)
        keep.add(path)
        links.insert(0, f'<a class="chip" href="{url}">{_e(T["deals"])}</a>')
    best = "".join(_disc_tile(pais, d, T, names) for d in multi[:48])
    # Artistas: "Artista - Título" (lo de antes del guion); una página por artista con dos o más discos
    def artist(d):
        return d["name"].split(" - ", 1)[0].strip() if " - " in d["name"] else ""
    by_artist = {}
    for d in discs:
        if artist(d):
            by_artist.setdefault(artist(d), []).append(d)
    adir = out / "artist"
    akeep = set()
    for name_a, ds in by_artist.items():
        if len(ds) < 2:
            continue
        aslug = slug(name_a)
        if not aslug:
            continue
        url = f"{_pre(pais)}/{T['dir']}/artist/{aslug}.html"
        path = adir / f"{aslug}.html"
        tiles = "".join(_disc_tile(pais, d, T, names) for d in sorted(ds, key=lambda d: d["name"]))
        pages._write(path, page(url, T["artist_t"].format(a=name_a), T["artist_d"].format(a=name_a, n=len(ds)),
                                f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["artist_d"].format(a=name_a, n=len(ds)))}</p>\n'
                                f'  <div class="grid">{tiles}</div>'))
        urls.append(url)
        akeep.add(path)
    for f in adir.glob("*.html") if adir.exists() else []:
        if f not in akeep:
            f.unlink()
    artists_pages = {a for a, ds in by_artist.items() if len(ds) >= 2 and slug(a)}
    # Buscador con filtros: índice ligero [nombre, página, formato, precio, tiendas, foto, artista] y todo en el navegador
    idx = [[d["name"], d["slug"], T["fmt1"][d["fmt"]], min(i["p"] for i in d["items"]), len(d["items"]), d.get("img") or "", artist(d)]
           for d in multi]
    (out / "search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    top_artists = sorted(by_artist, key=lambda a: -len(by_artist[a]))[:400]
    datalist = "".join(f'<option value="{_e(a)}">' for a in sorted(top_artists, key=str.lower))
    fmts = "".join(f'<option value="{_e(T["fmt1"][k])}">{_e(v[0])}</option>' for k, v in T["fmts"].items())
    field = ('padding:10px 14px;border-radius:999px;border:1px solid var(--border);font:inherit;'
             'background:var(--surface-1);color:var(--text-primary)')
    search = (f'  <form class="search" role="search" onsubmit="return false" style="margin:14px 0 4px;display:flex;flex-wrap:wrap;gap:8px">'
              f'<input id="q" type="search" placeholder="{_e(T["search_ph"])}" autocomplete="off" aria-label="{_e(T["search_ph"])}" '
              f'style="flex:2 1 260px;{field}">'
              f'<input id="fa" list="artists" placeholder="{_e(T["f_artist"])}" aria-label="{_e(T["f_artist"])}" style="flex:1 1 180px;{field}">'
              f'<datalist id="artists">{datalist}</datalist>'
              f'<select id="ff" aria-label="{_e(T["f_format"])}" style="{field}"><option value="">{_e(T["f_all"])}</option>{fmts}</select>'
              f'<select id="fs" aria-label="{_e(T["f_sort"])}" style="{field}"><option value="p">{_e(T["s_price"])}</option>'
              f'<option value="n">{_e(T["s_shops"])}</option><option value="a">{_e(T["s_az"])}</option></select></form>\n'
              '  <section class="hub-sec" id="results" hidden><h2 id="rh"></h2><div class="grid" id="rg"></div></section>\n'
              + r"""  <script>(()=>{let idx=null;const $=i=>document.getElementById(i),q=$('q'),fa=$('fa'),ff=$('ff'),fs=$('fs'),sec=$('results'),g=$('rg'),h=$('rh');
const n=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();const e=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const money=v=>new Intl.NumberFormat(document.documentElement.lang,{style:'currency',currency:'__CUR__',minimumFractionDigits:v%1?2:0}).format(v);
const im=u=>/cdn\.shopify\.com|\/cdn\/shop\//.test(u)?u+(u.includes('?')?'&':'?')+'width=300':u;const AP=__AP__;
async function run(){const t=n(q.value.trim()),a=n(fa.value.trim()),f=ff.value;if(t.length<2&&!a&&!f){sec.hidden=true;return}
if(!idx)idx=await (await fetch('search.json')).json();const w=t.length>=2?t.split(/\s+/):[];
let r=idx.filter(d=>{const x=' '+n(d[0]).replace(/[^a-z0-9]+/g,' ');return w.every(k=>x.includes(' '+k))&&(!a||(' '+n(d[6]).replace(/[^a-z0-9]+/g,' ')).includes(' '+a.replace(/[^a-z0-9]+/g,' ').trim()))&&(!f||d[2]===f)});
const s=fs.value;r.sort((x,y)=>s==='n'?y[4]-x[4]||x[3]-y[3]:s==='a'?x[0].localeCompare(y[0]):x[3]-y[3]);const tot=r.length;r=r.slice(0,120);
const ap=fa.value.trim()&&AP[fa.value.trim()];h.innerHTML=(tot?'__RES__'.replace('{n}',tot):'__NONE__')+(ap?` · <a href="artist/${ap}.html">__ALL__ →</a>`:'');
g.innerHTML=r.map(d=>`<a class="tile" href="${e(d[1])}.html"><div class="img">${d[5]?`<img loading="lazy" src="${e(im(d[5]))}" alt="">`:''}</div><div class="body"><span class="brand">${e(d[2])}</span><span class="name">${e(d[0])}</span><span class="price"><strong>${money(d[3])}</strong></span><span class="foot"><span>${e(d[6])}</span><span class="stores-n">${d[4]}</span></span></div></a>`).join('');sec.hidden=false}
let tm;const go=()=>{clearTimeout(tm);tm=setTimeout(run,200)};[q,fa].forEach(x=>x.addEventListener('input',go));[ff,fs].forEach(x=>x.addEventListener('change',run));})();</script>
""".replace("__CUR__", intl.SITES[pais]["cur"] if pais in intl.SITES else "EUR").replace("__AP__", json.dumps({a: slug(a) for a in artists_pages}, ensure_ascii=False))
                 .replace("__RES__", _e(T["search_res"])).replace("__NONE__", _e(T["search_none"])).replace("__ALL__", _e(T["artist_all"])))
    body = (f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["d_index"])}</p>\n' + search + f'  <div class="links">{"".join(links)}</div>\n'
            f'  <section class="hub-sec"><h2>{_e(T["more"])}</h2><div class="grid">{best}</div></section>')
    path = out / "index.html"
    pages._write(path, page(f"{_pre(pais)}/{T['dir']}/", T["h_index"], T["d_index"], body))
    urls.insert(0, f"{_pre(pais)}/{T['dir']}/")
    keep.add(path)
    # Guía "dónde comprar vinilo más barato"
    if "guide_file" in T:
        gd = deals[:12] if deals else multi[:12]
        rows = "".join(f'<a href="{_pre(pais)}/{T["dir"]}/{d["slug"]}.html"><span>{_e(d["name"])} · {T["fmt1"][d["fmt"]]}</span><small>'
                       f'{_e(T["save"].format(m=intl.money(gap(d), pais)))}</small></a>' for d in gd if gap(d))
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in T["faqs"]]}
        faq = "".join(f"<details><summary>{_e(q)}</summary><p>{_e(a)}</p></details>" for q, a in T["faqs"])
        body = (f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["guide_desc"])}</p>\n'
                + T["guide_body"].format(shops=T.get("shops_n", len(STORES[pais]) - 1))
                + (f'\n  <section class="hub-sec"><h2>{_e(T["deals"])}</h2><div class="dl">{rows}</div></section>' if rows else "")
                + f'\n  <section class="hub-sec" style="max-width:780px"><h2>FAQ</h2>{faq}</section>\n' + guitar_box)
        url = f"{_pre(pais)}/{T['dir']}/{T['guide_file']}.html"
        path = out / f"{T['guide_file']}.html"
        pages._write(path, page(url, T["guide"], T["guide_desc"], body, ld))
        urls.insert(1, url)
        keep.add(path)
    # Mapa propio de discos para Google (uk/records/sitemap.xml, en robots.txt)
    sm = "".join(f"  <url><loc>https://guitle.com{u}</loc></url>\n" for u in urls)
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n', encoding="utf-8")
    for f in out.glob("*.html"):
        if f not in keep:
            f.unlink()
    print(f"música {pais}: {len(discs)} discos con código (todos con página), {len(multi)} en dos o más tiendas", flush=True)
    return urls


def _disc_tile(pais, d, T, names):
    from . import intl
    best = sorted(d["items"], key=lambda i: (not i["st"], i["p"]))[0]
    img = f'<img loading="lazy" src="{_e(_img(d["img"], 300))}" alt="">' if d.get("img") else ""
    return (f'<a class="tile" href="{_pre(pais)}/{T["dir"]}/{_e(d["slug"])}.html"><div class="img">{img}</div><div class="body">'
            f'<span class="brand">{_e(T["fmt1"][d["fmt"]])}</span><span class="name">{_e(d["name"])}</span>'
            f'<span class="price"><strong>{intl.money(best["p"], pais)}</strong></span><span class="foot">'
            f'<span>{_e(names.get(best["s"], best["s"]))}</span><span class="stores-n">{len(d["items"])}</span></span></div></a>')


def _disc_page(pais, d, f1, url, names, T, t, guitar_box, alink=""):
    """Página de un disco con las mismas piezas que la ficha de una guitarra (intl._product): cabecera, migas, foto y
    precio, tabla de tiendas con su botón y Amazon debajo. Sin gráfica de precios (aún no hay historial de discos)."""
    from . import intl, pages
    items = sorted(d["items"], key=lambda i: (not i["st"], i["p"]))  # la mejor: la más barata con stock
    best = items[0]
    colors = {st: pages.PALETTE[n % len(pages.PALETTE)] for n, st in enumerate(sorted({i["s"] for i in items}))}
    n, prices = len(items), [i["p"] for i in items]
    title = T["title"].format(n=d["name"], f=f1)
    desc = T["desc"].format(n=d["name"], f=f1, k=n) if n > 1 else T.get("desc1", T["desc"]).format(
        n=d["name"], f=f1, k=n, s=names.get(best["s"], best["s"]))
    where = (t["whereMany"].format(s=names.get(best["s"], best["s"]), n=n) if n > 1
             else T.get("where1", "at {s}").format(s=names.get(best["s"], best["s"]))) + (
        t["whereDiff"].format(d=intl.money(round(max(prices) - min(prices)), pais)) if max(prices) - min(prices) >= 1 else "")
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f"{d['name']} ({f1})", "gtin13": d["ean"],
          "image": d.get("img"), "url": f"https://guitle.com{url}",
          "offers": {"@type": "AggregateOffer", "priceCurrency": (intl.SITES[pais]["cur"] if pais in intl.SITES else "EUR"), "lowPrice": min(prices),
                     "highPrice": max(prices), "offerCount": n}}
    if not T.get("amazon"):
        amazon = ""
    elif len(d["items"]) == 1:  # una sola tienda: Amazon como segunda opción bien visible (botón)
        amazon = (f'\n    <p style="margin:14px 0 0">{_e(T["amazon_txt"])} <a class="btn-amz" href="{_e(T["amazon"].format(ean=d["ean"]))}" '
                  f'target="_blank" rel="sponsored noopener" style="display:inline-block;margin-left:8px;padding:8px 16px;'
                  f'border-radius:999px;border:1.5px solid var(--accent);color:var(--accent);font-weight:600;text-decoration:none">'
                  f'{_e(T["amazon_btn"])} →</a></p>')
    else:
        amazon = (f'\n    <p class="muted small amazon">{_e(T["amazon_txt"])} <a href="{_e(T["amazon"].format(ean=d["ean"]))}" '
                  f'target="_blank" rel="sponsored noopener">{_e(T["amazon_btn"])}</a></p>')
    img = f'<div class="pimg"><img src="{_e(_img(d["img"], 600))}" alt="{_e(d["name"])}"></div>' if d.get("img") else ""
    head = intl._head(pais, f"{title} · guitle", desc, url,
                      f'<meta property="og:title" content="{_e(title)}">\n<meta property="og:description" content="{_e(desc)}">\n'
                      + (f'<meta property="og:image" content="{_e(d["img"])}">\n' if d.get("img") else "")
                      + '<link rel="stylesheet" href="/catalogo.css">\n<link rel="stylesheet" href="/producto.css">\n'
                      '<style>@media(max-width:420px){#stores td{padding-left:3px;padding-right:3px}#stores .tag{font-size:.72rem;padding:1px 4px}}</style>\n'
                      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>')
    return f"""{head}
<body>
<main>
  <div class="topbar">
    <div class="row">
      {intl._logo(pais, t)}
      <a class="navlink" href="{_pre(pais)}/{T['dir']}/">{_e(T['home'])}</a>
    </div>
  </div>
  <nav class="crumbs"><a href="{_pre(pais)}/">{_e(t['home'])}</a> › <a href="{_pre(pais)}/{T['dir']}/">{_e(T['home'])}</a> › <a href="{_pre(pais)}/{T['dir']}/{T['fmts'][d['fmt']][1]}.html">{_e(T['fmts'][d['fmt']][0])}</a></nav>
  <article class="product">
    {img}
    <div class="pinfo">
      <div class="muted">{_e(f1.capitalize() if f1.islower() else f1)}{alink}</div>
      <h2 class="pname">{_e(d['name'])}</h2>
      <div id="price" class="big">{intl.money(best['p'], pais)}</div>
      <div id="where" class="muted">{_e(where)}</div>
      <div class="muted small">EAN {d['ean']} · {_e(T['note'])}</div>
    </div>
  </article>
  <section><h3>{_e(t['storesH3'])}</h3><div class="table-wrap"><table id="stores">{intl._rows({'items': items}, names, colors, pais, t)}</table></div>{amazon}</section>
{guitar_box}
  {intl._foot(pais, t)}
</main>
<script src="/c.js" defer></script>
</body>
</html>
"""


def home_deals(pais, n=4):
    """Los n discos con más diferencia entre tiendas (con stock), para la portada del país: [(disco, ahorro)]."""
    discs = _load(DATA / pais / "discos.json", [])
    out = []
    for d in discs:
        live = [i["p"] for i in d["items"] if i["st"]]
        if len(live) >= 2 and d.get("img") and max(live) - min(live) >= 2:
            out.append((d, max(live) - min(live), min(live)))
    return sorted(out, key=lambda x: -x[1])[:n]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pais", default="uk")
    ap.add_argument("--minutes", type=float, default=60)
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args(argv)
    if not a.build:
        read(a.pais, a.minutes)
    write_pages(a.pais, build_data(a.pais))
    return 0


if __name__ == "__main__":
    sys.exit(main())
