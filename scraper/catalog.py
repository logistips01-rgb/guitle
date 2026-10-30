"""Catálogo amplio de guitarras: eléctricas por un lado; acústicas y clásicas por otro.

Descubre las fichas en los sitemaps de las tiendas, lee cada día un lote (las nunca leídas y las más
antiguas, con un tope de tiempo por tienda) y agrupa los productos entre tiendas por EAN (o por nombre,
en tiendas sin EAN).

Cada catálogo (--cat) tiene su carpeta:
    electrica → data/catalog/            products.json
    acustica  → data/catalog/acusticas/  acusticas.json y clasicas.json (una sola lectura de las tiendas;
                                         la categoría de la tienda decide en qué página va cada guitarra)
con offers.json (última lectura de cada ficha) e history.json (cambios de precio).

Uso:
    python -m scraper.catalog [--cat acustica] [--minutes 50] [--limit N] [--only numemusic]
    python -m scraper.catalog --records-out F      # CI: lee y guarda el lote en F
    python -m scraper.catalog --merge F            # CI: fusiona el lote
    python -m scraper.catalog --build              # regenera los JSON de la web
"""
import argparse
import functools
import gzip
import html
import json
import re
import unicodedata
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests
from bs4 import BeautifulSoup

from . import affiliates, analytics, deals, jsonld, pages
from .common import normalize_currency, normalize_id, parse_availability, parse_price
from .fetch import DELAY, Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "catalog"
RECHECK_SKIPPED_DAYS = 60  # fichas que no son guitarra: no se vuelven a pedir en este tiempo
RECHECK_NO_PRICE_DAYS = 14  # fichas de guitarra sin precio (no disponibles): se miran cada dos semanas
DROP_AFTER_DAYS = 30       # ofertas que desaparecen del sitemap y no se han leído en este tiempo
MIN_PRICE = {"electrica": 60, "acustica": 40, "clasica": 35,  # por debajo no es una guitarra (ni infantil)
             "teclado": 40, "pedal": 20, "portuguesa": 150, "bajo": 80, "ampli": 30, "estuche": 12, "micro": 15, "varios": 3}
GUITAR_KINDS = {"electrica", "acustica", "clasica", "portuguesa"}
MIN_SLENDERNESS = 1.7      # alto/ancho mínimo de la miniatura de una guitarra entera (un primer plano ronda 1)

NOT_PRODUCT = re.compile(r"b-stock|bstock|b-ware|outlet|usad[ao]|segunda-mano|gebraucht|pre-owned|\bused\b|demo|vorfuehr|gutschein|stock[ -]b\b", re.I)

# Session no dice en la URL qué es una guitarra: se preseleccionan marcas de guitarra eléctrica sin
# palabras de accesorio, y la ficha (breadcrumb "E-Gitarren") confirma.
SESSION_BRANDS = ("fender", "squier", "gibson", "epiphone", "ibanez", "prs", "gretsch", "esp", "ltd", "jackson",
                  "charvel", "schecter", "evh", "music-man", "sterling", "yamaha", "cort", "godin", "duesenberg",
                  "rickenbacker", "danelectro", "guild", "d-angelico", "heritage", "harmony", "solar", "strandberg",
                  "chapman", "reverend", "vintage", "framus", "warwick", "hagstrom", "eastman", "maybach")
SESSION_SKIP = re.compile(
    r"saite|string|gurt|strap|koffer|case|gig-?bag|tasche|bag|pickup|tonabnehmer|humbucker|schlagbrett|pickguard"
    r"|kit|staender|stand(?!ard)|(?<![a-z])amp|verstaerker|combo|head(?!less)|topteil|cabinet|box|bass|akusti|acoustic|western|konzert"
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


EGITANA_BRANDS = ("fender", "squier", "gibson", "epiphone", "ibanez", "prs", "gretsch", "esp", "ltd", "jackson",
                  "charvel", "schecter", "evh", "music-man", "sterling", "cort", "godin", "duesenberg", "rickenbacker",
                  "danelectro", "guild", "harley", "vintage", "solar", "chapman", "reverend", "framus", "hagstrom",
                  "sire", "suhr", "mooer", "yamaha")
EGITANA_SKIP = re.compile(
    r"estojo|saco|correia|corda|captador|pickguard|escudo|kit|suporte|stand|amplificador|\bamp\b|combo|cabeca|coluna"
    r"|cabo|palheta|\bpua|capo|afinador|pedal|baixo|bass|acust|acoustic|classic|ukulele|cavaquinho|bandolim|banjo"
    r"|t-shirt|camisola|bone|caneca|livro|correa|funda|cuerda|pastilla|mastil|braco|corpo|tarraxa|ponte|cordal"
    r"|parafuso|mola|botao|potenciometro|interruptor|jack|limpeza|polish|oleo|tremolo|strings|case|gig|bag|strap"
    r"|pick|neck|body|tuner|bridge|knob|switch|cable|headphone|monitor|speaker|cover|capa|overdrive|boost|delay"
    r"|reverb|fuzz|chorus|tone|wah|looper|trbx|\bgsr|\bsr\d|\bbtb|\bsrx", re.I)


def _pick_egitana(url):
    slug = url.split("egitana.es/")[-1].split("/p/")[0]
    if not slug.startswith(tuple(b + "-" for b in EGITANA_BRANDS)) or EGITANA_SKIP.search(slug) or NOT_PRODUCT.search(slug):
        return False
    # Yamaha vende sobre todo pianos y audio: solo sus eléctricas.
    return not slug.startswith("yamaha-") or re.search(r"pacifica|revstar|\brs[ps]?\d|\bsg\d", slug)


def _parse_egitana(soup, text):
    """Egitana no publica JSON-LD de producto ni EAN: datos de su analítica (scraper.analytics) y breadcrumb.
    Sin bloque de analítica = producto no disponible (sin precio)."""
    crumbs = [a.get_text(strip=True) for a in soup.find_all(attrs={"itemprop": "itemListElement"})]
    crumbs = [c for c in crumbs if c] or analytics.crumbs(text)
    d = analytics.detail(text)
    if not d:
        return {"crumbs": crumbs}
    image = soup.find("meta", attrs={"property": "og:image"})
    # El formato ("guitarras formato ST") va al final: de ahí sale el tipo.
    return {"crumbs": crumbs + [d["category"]], "name": d["name"], "brand_raw": d["brand"], "price": d["price"],
            "currency": "EUR", "in_stock": None, "image": image.get("content") if image else None, "ean": None}


# Thomann no tiene sitemap en español ni EAN en la ficha: las fichas salen de sus listados por forma
# (?pg= lo permite su robots.txt) y se leen con microdatos de schema.org.
THOMANN = "https://www.thomann.es/"
THOMANN_ELECTRIC = ("giegst", "giegte", "gieglp", "giegsg", "gieges", "gieghe", "giegja", "giegba", "gieg7s",
                    "gieg8s", "gieg12", "giegmm", "gieglh", "giegsc", "giegsa")
THOMANN_MAX_PAGES = 40


def _discover_thomann(fetcher, codes, base=THOMANN):
    """Fichas de los listados de Thomann. Un código (giegst) es un listado de forma; un nombre de página
    (cat_allProducts_GF_guitarras_electricas.html) se usa tal cual. base: thomann.es, thomann.pt…"""
    urls = set()
    # La página "todas las eléctricas" (cat_allProducts_GF_guitares_electriques.html…) devuelve en algunos países el
    # catálogo general (software, baterías…): las eléctricas se leen por sus listados de forma, iguales en todos.
    codes = [c for code in codes for c in (THOMANN_ELECTRIC if re.search(r"electr|elettr|elektr|e-gitarren", code) else (code,))]
    for code in codes:
        for pg in range(1, THOMANN_MAX_PAGES + 1):
            page = code if code.endswith(".html") else f"cat_GK_{code}.html"
            url = f"{base}{page}?ls=100&pg={pg}"
            if not fetcher.allowed(url)[0]:
                break
            resp = fetcher.get(url)
            if resp.status_code == 429:
                raise RuntimeError("HTTP 429")
            if resp.status_code != 200:
                break
            found = {base + h.split("?")[0] for h in re.findall(r'class="product__content[^"]*"\s+href="([^"]+\.htm)[?"]', resp.text)}
            if not found - urls:
                break
            urls |= found
    return sorted(urls)


def _parse_thomann(soup, text):
    crumbs = [li.get_text(" ", strip=True) for li in soup.select('[itemtype="https://schema.org/BreadcrumbList"] [itemprop=itemListElement]')]
    crumbs = [c for c in crumbs if c]
    brand = soup.select_one('[itemprop=brand] [itemprop=name]')
    brand = brand.get("content") if brand else None
    if crumbs and brand and crumbs[-1].lower() == brand.lower():
        crumbs = crumbs[:-1]  # el último elemento es la marca, no la forma
    offer = soup.select_one('[itemprop=offers]')
    price = offer.select_one('[itemprop=price]') if offer else None
    h1 = soup.find("h1")
    if not price or not price.get("content") or not h1:
        return {"crumbs": crumbs}
    currency = offer.select_one('[itemprop=priceCurrency]')
    avail = offer.select_one('[itemprop=availability]')
    image = soup.find("meta", attrs={"property": "og:image"})
    return {"crumbs": crumbs, "name": h1.get_text(" ", strip=True), "brand_raw": brand, "price": float(price["content"]),
            "currency": currency.get("content") if currency else "EUR",
            "in_stock": ("instock" in avail.get("href", avail.get("content", "")).lower()) if avail else None,
            "image": image.get("content") if image else None, "ean": None}


# MAT Guitars (PrestaShop): la categoría va en la URL (/es/<categoría>/<id>-<nombre>-<EAN>.html) y la ficha trae
# JSON-LD con EAN pero sin breadcrumb: la categoría de la URL hace de breadcrumb.
MAT_ELECTRIC = {"guitarras-tipo-stratocaster", "guitarras-tipo-superstrat", "guitarras-double-cut", "guitarras-tipo-telecaster",
                "guitarras-jaguar-jazzmaster-mustang-offset", "guitarras-de-caja-o-semicaja", "guitarras-les-paul",
                "guitarras-modelos-signature", "guitarras-de-7-y-8-cuerdas", "guitarras-electricas-para-zurdos",
                "guitarras-single-cut", "guitarras-tipo-v-y-explorer", "guitarras-electricas-para-principiantes",
                "guitarras-de-rock", "guitarras-electricas", "guitarras-tipo-sg", "otras-guitarras-electricas",
                "guitarras-multiescala", "guitarras-escala-corta", "guitarras-electricas-baratas", "guitarras-de-jazz",
                "guitarras-heavy"}
_MAT_ACOUSTIC = re.compile(r"^(guitarras-(electro)?acusticas|guitarras-(clasicas|flamencas)|otras-guitarras-(electroacusticas|clasicas)"
                           r"|guitarras-(dreadnought|jumbo)$|guitarras-con-cuerdas-de-nylon)")


def _mat_vat(data, text):
    """MAT (PrestaShop) da el precio sin IVA a algunas visitas de fuera de la UE (el lector corre en EE. UU.): si el
    precio leído coincide con su "price_tax_exc", se le suma el IVA español (21 %)."""
    m = re.search(r"price_tax_exc&quot;:([0-9.]+)", text) or re.search(r'"price_tax_exc":([0-9.]+)', text)
    if m and data.get("price") and abs(float(m.group(1)) - data["price"]) < 0.02:
        data["price"] = round(float(m.group(1)) * 1.21, 2)
    return data


def _mat_category(url):
    parts = url.split("/")
    return parts[4] if len(parts) > 5 else ""


def _mat_crumbs(url):
    cat = _mat_category(url)
    return (["Guitarras eléctricas"] if cat in MAT_ELECTRIC else []) + [cat.replace("-", " ")]


# Pronorte publica el producto en microdatos de schema.org (con gtin13) y el breadcrumb en la página.
def _parse_microdata(soup, text):
    crumbs = [li.get_text(" ", strip=True) for li in soup.select("ul.breadcrumbs li")][1:]
    meta = {}
    for m in soup.find_all("meta", attrs={"itemprop": True}):
        if not m.find_parent(attrs={"itemtype": re.compile("BreadcrumbList")}):
            meta.setdefault(m["itemprop"], m.get("content"))
    if crumbs and meta.get("name") and crumbs[-1].strip().lower() == meta["name"].strip().lower():
        crumbs = crumbs[:-1]
    if not meta.get("price") or not meta.get("name"):
        return {"crumbs": crumbs}
    ean = normalize_id(meta.get("gtin13") or meta.get("gtin") or "")
    return {"crumbs": crumbs, "name": meta["name"], "brand_raw": meta.get("brand"), "price": float(meta["price"]),
            "currency": meta.get("priceCurrency") or "EUR", "in_stock": "instock" in (meta.get("availability") or "").lower(),
            "image": meta.get("image"), "ean": ean if len(ean) in (12, 13, 14) else None}


def _parse_drunkat(soup, text):
    """Drunkat (drunkat.es): microdatos de schema.org con gtin13 y breadcrumb; la moneda va en "pricecurrency"."""
    crumbs = [li.get_text(" ", strip=True) for li in soup.select('[itemtype$="BreadcrumbList"] [itemprop=itemListElement]')]
    product = soup.find(attrs={"itemtype": re.compile(r"schema\.org/Product$")})
    if not product:
        return {"crumbs": crumbs}
    name = product.find(attrs={"itemprop": "name"}, recursive=True)
    while name is not None and name.find_parent(attrs={"itemtype": re.compile("Brand$")}):
        name = name.find_next(attrs={"itemprop": "name"})
    name = name.get_text(" ", strip=True) if name else None
    if crumbs and name and crumbs[-1].lower().startswith(name.lower()):
        crumbs = crumbs[:-1]
    meta = lambda prop: (product.find(attrs={"itemprop": prop}) or {}).get("content") if product.find(attrs={"itemprop": prop}) else None
    brand = product.select_one('[itemprop=brand] [itemprop=name]')
    price, avail = meta("price"), product.find(attrs={"itemprop": "availability"})
    if not price or not name:
        return {"crumbs": crumbs}
    image = product.find("link", attrs={"itemprop": "image"}) or soup.find("meta", attrs={"property": "og:image"})
    ean = normalize_id(meta("gtin13") or "")
    brand = (brand.get("content") or "").strip() if brand else None
    if crumbs and brand and crumbs[-1].strip().lower() == brand.lower():
        crumbs = crumbs[:-1]  # el último nivel es la marca ("Guitarra eléctrica tipo Heavy" › "Ibanez")
    return {"crumbs": crumbs, "name": " ".join(name.split()), "brand_raw": brand, "price": float(price),
            "currency": (meta("pricecurrency") or meta("priceCurrency") or "EUR").upper(),
            "in_stock": "instock" in (avail.get("href", "") if avail else "").lower(),
            "image": image.get("href") or image.get("content") if image else None, "ean": ean if len(ean) in (12, 13, 14) else None}


_DRUNKAT_ELECTRIC = re.compile(r"-guitarra-electrica(-|$)")
_DRUNKAT_ACOUSTIC = re.compile(r"-guitarra-(electro)?(acustica|clasica|flamenca|espanola)(-|$)")
_DRUNKAT_SKIP = re.compile(r"para-guitarra|para-bajo|juego-de-cuerdas|-bajo-|kit-|pack-|-set-", re.I)


PRONORTE_SKIP = re.compile(SESSION_SKIP.pattern + r"|funda|estuche|correa|cuerda|pastilla|soporte|cable|ampli|bajo|ukelele"
                           r"|pedal|afinador|cejilla|pua|clavija|repuesto", re.I)


def _pick_pronorte(url, brands):
    slug = url.split("/p/")[-1]
    return "/p/" in url and slug.startswith(tuple(b + "-" for b in brands)) and not PRONORTE_SKIP.search(slug) \
        and not NOT_PRODUCT.search(slug)


def _only(kind, pred):
    return lambda crumbs: kind if pred(crumbs) else None


def _is_electric(crumbs):
    return any(x.strip().lower() == "guitarras eléctricas" for x in crumbs)


SOURCES = {
    "numemusic": {"name": "Nume Music", "sitemap": "https://www.numemusic.com/media/sitemap/es_ES.xml",
                  "pick": _pick_numemusic, "kind": _only("electrica", lambda c: any(re.search(r"guitarras el[eé]ctricas", x, re.I) for x in c))},
    "session": {"name": "Session", "sitemap": "https://www.session.de/sitemap.xml",
                # "E-Gitarren & Zubehör" también agrupa accesorios: manda la última categoría.
                "pick": _pick_session,
                "kind": _only("electrica", lambda c: len(c) > 1 and c[-2].lower().startswith("e-gitarren")
                and re.search(r"gitarre", c[-1], re.I) and not re.search(r"zubeh|saite|koffer|tasche", c[-1], re.I)),
                "sub": lambda u: "-product-" in u},
    # Egitana responde a veces con estado 500 pero con la ficha completa: vale si trae los datos.
    "musicopolix": {"name": "Musicopolix", "sitemap": "https://musicopolix.com/1_es_0_sitemap.xml",
                    "pick": lambda u: "/guitarras/electricas/" in u and re.search(r"/\d+-[^/]+\.html$", u)
                    and not NOT_PRODUCT.search(u),
                    "kind": _only("electrica", _is_electric)},
    "alfasoni": {"name": "Alfasoni", "sitemap": "https://alfasoni.com/1_index_sitemap.xml",
                 "pick": lambda u: "/guitarras-electricas-" in u and u.endswith(".html") and not NOT_PRODUCT.search(u),
                 "kind": _only("electrica", _is_electric)},
    "egitana": {"name": "Egitana", "sitemap": "https://www.egitana.es/sitemaps/es/products_sitemap.xml",
                "pick": _pick_egitana, "parse": _parse_egitana, "ok_status": (200, 500),
                "kind": _only("electrica", _is_electric)},
    # Ya nos frenó una vez (429): más despacio que las demás, y si vuelve a pasar se para hasta el día siguiente.
    "thomann": {"name": "Thomann", "discover": lambda f: _discover_thomann(f, THOMANN_ELECTRIC), "delay": (8.0, 14.0),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u),
                "parse": _parse_thomann, "kind": _only("electrica", _is_electric)},
    "mat": {"name": "MAT Guitars", "sitemap": "https://www.matguitars.com/1_es_0_sitemap.xml",
            "pick": lambda u: _mat_category(u) in MAT_ELECTRIC and not NOT_PRODUCT.search(u), "crumbs": _mat_crumbs,
            "fix": _mat_vat,
            "kind": _only("electrica", _is_electric)},
    "drunkat": {"name": "Drunkat", "sitemap": "https://drunkat.es/var/sitemap.xml", "parse": _parse_drunkat,
                "sub": lambda u: "sitemap-productos" in u,
                "pick": lambda u: bool(_DRUNKAT_ELECTRIC.search(u)) and not _DRUNKAT_SKIP.search(u) and not NOT_PRODUCT.search(u),
                "kind": _only("electrica", _is_electric)},
    "pronorte": {"name": "Pronorte", "sitemap": "https://www.pronorte.es/sitemap.xml", "parse": _parse_microdata,
                 # Yamaha vende también pianos, baterías y audio: solo sus eléctricas.
                 "pick": lambda u: _pick_pronorte(u, SESSION_BRANDS + ("sire", "harley-benton", "vintage", "aria"))
                 and (not u.split("/p/")[-1].startswith("yamaha-") or re.search(r"pacifica|revstar|-rs[ps]?\d|-sg\d", u)),
                 "kind": _only("electrica", _is_electric)},
}

# --- Acústicas y clásicas -------------------------------------------------------------------------
ACOUSTIC_BRANDS = ("taylor", "martin", "yamaha", "ortega", "lag", "cort", "takamine", "gibson", "epiphone", "fender",
                   "guild", "furch", "eastman", "alhambra", "cordoba", "ibanez", "seagull", "larrivee", "lakewood",
                   "hanika", "hoefner", "hofner", "washburn", "breedlove", "maton", "sigma", "cole-clark", "godin",
                   "norman", "art-lutherie", "simon-patrick", "la-patrie", "ramirez", "raimundo", "admira", "camps",
                   "alvarez", "ovation", "gretsch", "lowden", "collings", "santa-cruz", "boucher", "prodipe",
                   "valencia", "esteve", "manuel-rodriguez", "jose-torres", "rafael-martin", "paco-castillo",
                   "martinez", "salvador-cortez", "kremona", "tanglewood", "faith", "recording-king", "harmony",
                   "framus", "squier", "gewa", "pro-arte", "ashton", "fender-cd", "sire", "enya", "lava")
ACOUSTIC_SKIP = re.compile(
    r"saite|string|cuerda|corda|gurt|strap|correa|correia|koffer|case|estojo|estuche|gig-?bag|tasche|bag|funda|saco"
    r"|pickup|tonabnehmer|pastilla|captador|stand|staender|suporte|soporte|amp|verstaerker|amplificador|combo|bass"
    r"|baixo|bajo|ukulele|ukelele|mandolin|bandolim|banjo|cavaquinho|pedal|kabel|cable|cabo|plektr|pick|palheta|pua"
    r"|capo|cejilla|kapodaster|tuner|afinador|stimmger|mechanik|tarraxa|clavijero|bridge|ponte|steg|sattel|cover|capa"
    r"|shirt|hoodie|tasse|caneca|book|buch|livro|poster|halter|hanger|tuch|cloth|polish|pflege|clean|limpeza|humidif"
    r"|e-gitarre|electric|electrica|eletrica|single-string|bundle|pack|b-ware|ersatz|repuesto", re.I)
_ACOUSTIC_URL = re.compile(r"/\d+-guitarra-(electro)?(ac[uú]?stica|cl[aá]?sica|flamenca|espa[nñ]ola)-")


def _pick_acoustic_brand(slug):
    return (slug.startswith(tuple(b + "-" for b in ACOUSTIC_BRANDS)) and not ACOUSTIC_SKIP.search(slug)
            and not NOT_PRODUCT.search(slug))


def acoustic_kind(crumbs):
    """'clasica', 'acustica' o None según las categorías de la tienda (ES y DE)."""
    leaf = " / ".join(crumbs[-2:]).lower()
    if re.search(r"\bbajos? (ac|el)|\bbass|bässe|ukelele|ukulele|accesori|zubehör$|fundas?\b|cuerdas|saiten|estuches"
                 r"|koffer|taschen|pastillas|amplific|cejillas|correas|ständer|soportes|repuestos", leaf):
        return None
    text = " / ".join(crumbs).lower()
    if re.search(r"konzertgitarren|klassikgitarren|flamenco|guitarras? (el[eé]ctricas )?(cl[aá]sicas?|espa[nñ]olas?|flamencas?)"
                 r"|guitarra cl[aá]sica|electrocl[aá]sicas|flamencas|cuerdas? de nylon", text):
        return "clasica"
    if re.search(r"westerngitarren|guitarras? (el[eé]ctricas |electro)?ac[uú]sticas?|electroac[uú]sticas|\bac[uú]sticas\b"
                 r"|guitarras de viaje", text):
        return "acustica"
    return None


ACOUSTIC_SOURCES = {
    "numemusic": {**SOURCES["numemusic"], "pick": lambda u: bool(_ACOUSTIC_URL.search(u)) and not NOT_PRODUCT.search(u),
                  "kind": acoustic_kind},
    "session": {**SOURCES["session"], "pick": lambda u: _pick_acoustic_brand(u.split("/products/")[-1].strip("/")),
                "kind": acoustic_kind},
    "musicopolix": {**SOURCES["musicopolix"], "kind": acoustic_kind,
                    "pick": lambda u: re.search(r"/cat/guitarras/(acusticas|electroacusticas|guitarra-clasica-guitarra-espanola"
                                                r"|electroclasicas|guitarras-flamencas)/", u)
                    and re.search(r"/\d+-[^/]+\.html$", u) and not NOT_PRODUCT.search(u)},
    "alfasoni": {**SOURCES["alfasoni"], "kind": acoustic_kind,
                 "pick": lambda u: re.search(r"alfasoni\.com/guitarras-(acusticas|clasicas|flamencas|electroacusticas"
                                             r"|electroclasicas)", u) and u.endswith(".html") and not NOT_PRODUCT.search(u)},
    "egitana": {**SOURCES["egitana"], "kind": acoustic_kind,
                "pick": lambda u: _pick_acoustic_brand(u.split("egitana.es/")[-1].split("/p/")[0])},
    "mat": {**SOURCES["mat"], "kind": acoustic_kind,
            "pick": lambda u: bool(_MAT_ACOUSTIC.search(_mat_category(u))) and not NOT_PRODUCT.search(u)},
    "drunkat": {**SOURCES["drunkat"], "kind": acoustic_kind,
                "pick": lambda u: bool(_DRUNKAT_ACOUSTIC.search(u)) and not _DRUNKAT_SKIP.search(u) and not NOT_PRODUCT.search(u)},
    "pronorte": {**SOURCES["pronorte"], "kind": acoustic_kind,
                 "pick": lambda u: "/p/" in u and _pick_acoustic_brand(u.split("/p/")[-1])},
}

# --- Teclados y pedales (catálogo "equipo") ----------------------------------------------------------
# Cada tienda preselecciona por su categoría en la URL; la ficha (breadcrumb, URL y nombre) decide si es un teclado,
# un pedal o un accesorio (soportes, fundas, alimentadores, pedales de sustain o de bombo…), que no entra.
EQUIPO_SKIP = re.compile(
    r"soporte|suporte|\bstand\b|staender|funda|bolsa|\bcapa\b|tasche|\bbag\b|\bcase\b|estuche|estojo|koffer|maleta|flight"
    r"|banqueta|\bbanco\b|taburete|\bbench\b|cubierta|cubre|\bcover\b|alimentador|fuente de alim|adaptador|netzteil"
    r"|power ?supply|latiguillo|\bpatch\b|\bcables?\b|kabel|\bcabo\b|pedalboard|pedal ?board|bombo|bater[ií]a|\bdrums?\b"
    r"|percusi|auricular|headphone|platillo|ilumina|\bluz\b|\bled\b|\bdj\b|acorde[oó]n|lit[uú]rgic|sustain|sostenido"
    r"|para teclado|para piano|mantenimiento|repuesto|conmutador|footswitch|\bmaza\b|efectos sonoros|libro|\bbook\b"
    r"|amplificador|interfa[cz]e? midi|cables? midi|tuerca|bot[oó]n|\bkit de\b|tremolo ?arm|palanca|\bmount\b|montaje"
    r"|pickup|pastilla|\bgk-?\d|zubeh|ersatz|halterung", re.I)
_KEYBOARD = re.compile(r"piano|teclado|keyboard|sintetiz|synth|workstation|arranger|controlador midi|teclas|stage ?piano"
                       r"|tastatur|klavier", re.I)
_PEDAL = re.compile(r"pedal|efecto|effekt|multiefect|multi.?efect|overdrive|distors|distortion|fuzz|delay|\beco\b|echo"
                    r"|reverb|chorus|flanger|phaser|tr[eé]molo|vibrato|wah|looper|fraseo|compres|booster|\bboost\b"
                    r"|octav|preamp|afinador de pedal|bodentreter", re.I)


def equipo_text(crumbs, url, name):
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return " / ".join([*crumbs, re.sub(r"[-_]+", " ", slug), name or ""]).lower()


def equipo_kind(crumbs, url, name):
    """'teclado', 'pedal' o None (accesorio u otra cosa) según categoría, URL y nombre."""
    text = equipo_text(crumbs, url, name)
    if EQUIPO_SKIP.search(text) or NOT_PRODUCT.search(name or ""):
        return None
    # Una guitarra con previo (Fishman "preamp") no es un pedal: manda la categoría de la tienda.
    path = " / ".join(crumbs).lower()
    if re.search(r"guitarras? (cl[aá]sic|el[eé]ctric|ac[uú]stic|electroac)|bajos? el[eé]ctric|westerngitarren|e-gitarren"
                 r"|konzertgitarren", path) and not _PEDAL.search(path):
        return None
    if _PEDAL.search(text) and not re.search(r"piano digital|pianos? (electr|digital)|teclado|sintetizador con teclado", text):
        return "pedal"
    if _KEYBOARD.search(text):
        return "teclado"
    return None


KEYBOARD_TYPES = [("Controlador MIDI", r"controlador|teclado maestro|\bmidi\b|keystep|launchkey|nanokey|minilab|keylab"),
                  ("Piano acústico", r"piano ac[uú]stico|pianos ac[uú]sticos|piano vertical|piano de cola|silent"),
                  ("Piano de escenario", r"escenario|stage|nord (piano|electro|grand)"),
                  ("Sintetizador", r"sintetiz|synth|workstation|m[oó]dulo"),
                  ("Piano digital", r"piano digital|pianos (digitales|electr)|piano electr|celviano|clavinova|arius|\b88 teclas"),
                  ("Teclado portátil", r"teclado|arranger|acompa[nñ]amiento|port[aá]til|\bpsr|\bct-?s|\blk-?\d")]
PEDAL_TYPES = [("Para bajo", r"\bbajos?\b|\bbass\b|bass-?effekt"),
               ("Multiefectos", r"multi|pedalera|procesador|modelador|modeling"),
               ("Afinador", r"afinador|tuner"),
               ("Octavador y pitch", r"octav|pitch|whammy|\bpog\b|harmoni|shifter|\bdrop\b"),
               ("Ecualizador", r"ecualiz|equaliz|\beq\b|\bge-?7|graphic"),
               ("Puerta de ruido", r"noise|\bgate\b|ruido|suppressor|hum debugger|\bns-?2"),
               ("Sintetizador", r"synth|sintetiz|organ|piano machine|sitar"),
               ("Looper", r"loop|fraseo"),
               ("Wah y volumen", r"wah|volumen|volume|expresi"),
               ("Compresor", r"compres|kompressor"),
               ("Delay", r"delay|\beco\b|echo"),
               ("Reverb", r"reverb|\bhall\b"),
               ("Modulación", r"chorus|flanger|phaser|tr[eé]molo|vibrato|modula|rotary|uni.?vibe"),
               ("Overdrive y distorsión", r"overdrive|distors|distortion|fuzz|boost|drive|preamp|metal|crunch|verzerr|zerr")]


def _pick_equipo(pattern, skip=None):
    rx, sk = re.compile(pattern, re.I), re.compile(skip, re.I) if skip else None
    return lambda u: bool(rx.search(u)) and not (sk and sk.search(u)) and not NOT_PRODUCT.search(u)


_ALFASONI_EQUIPO = (r"alfasoni\.com/(pedales-de-(?!bombo|sustain)[a-z-]+|otros-pedales-de-(guitarra|bajo)|multiefectos-para-"
                    r"(guitarra-electrica|bajo)|pedales-para-guitarra-acustica|pedales-afinadores|armonizadores-y-modelado-en-pedal"
                    r"|procesadores-de-voz-en-pedal|sintetizadores-(con-teclado|en-modulo|de-guitarra-y-bajo)|pianos-de-escenario"
                    r"|teclados-portatiles|pianos-digitales-[a-z]+|teclados-de-acompanamiento|teclados-midi-de-\d+-teclas"
                    r"|workstations)/[^/]+\.html$")
_MAT_EQUIPO = {"overdrive", "fuzz", "distorsion", "delay", "reverb", "wah-wah", "otros-pedales-para-guitarra-electrica",
               "chorus", "compresor", "booster", "multiefectos", "sintetizador", "previos-para-bajo-pedales-para-bajo",
               "compresor-para-bajo", "overdrive-para-bajo", "octavador", "looper-loop-station", "fuzz-para-bajo",
               "octavador-para-bajo", "pedales-para-guitarra-acustica", "wah-wah-para-bajo", "chorus-para-bajo",
               "multiefectos-para-bajo", "distorsion-para-bajo", "pedales-para-guitarra-electrica", "procesadores-multiefectos",
               "sintetizador-para-bajo", "reverb-para-bajo", "efectos-de-voz-pedales"}
_PEDAL_WORDS = r"pedal|overdrive|distortion|distorsion|fuzz|delay|reverb|chorus|flanger|phaser|tremolo|wah|looper|compressor|booster|octave|drive|echo"

EQUIPO_SOURCES = {
    "numemusic": {**SOURCES["numemusic"], "kind_url": equipo_kind,
                  "pick": _pick_equipo(r"/\d+-(pedal-|pedalera-multi|piano-digital|teclado-|organo-stage|modulo-sintetizador"
                                       r"|m.dulo-sintetizador|procesador-de-efectos)",
                                       r"pedal-de-(sostenido|bombo)|para-teclado|pedalboard")},
    "musicopolix": {**SOURCES["musicopolix"], "kind_url": equipo_kind,
                    "pick": _pick_equipo(r"/cat/(teclados-musicales/(pianos-electronicos|teclados-electronicos|sintetizadores)"
                                         r"|produccion-musical/teclados-controladores|accesorios/accesorios-de-guitarra/"
                                         r"pedales-de-guitarra/(pedales|pedaleras)|accesorios/accesorios-de-bajo/pedales-bajo)/"
                                         r"(.+/)?\d+-[^/]+\.html$")},
    "alfasoni": {**SOURCES["alfasoni"], "kind_url": equipo_kind, "pick": _pick_equipo(_ALFASONI_EQUIPO)},
    "mat": {**SOURCES["mat"], "kind_url": equipo_kind,
            "pick": lambda u: _mat_category(u) in _MAT_EQUIPO and not NOT_PRODUCT.search(u)},
    "drunkat": {**SOURCES["drunkat"], "kind_url": equipo_kind,
                "pick": _pick_equipo(r"drunkat\.es/[^/]*(-pedal-|piano-digital|-teclado-|teclado-(midi|workstation|portatil)"
                                     r"|-sintetizador|pedalera-multiefect|multiefectos)",
                                     r"soporte|banqueta|latiguillo|pedalboard|funda|bolsa|alimentador|sustain")},
    "pronorte": {**SOURCES["pronorte"], "kind_url": equipo_kind,
                 "pick": _pick_equipo(rf"/p/[^/]*({_PEDAL_WORDS}|piano|synth|keyboard|nord-)", r"case|bag|board|cable|supply|stand")},
    "egitana": {**SOURCES["egitana"], "kind_url": equipo_kind,
                "pick": _pick_equipo(r"egitana\.es/[^/]*(pedal|overdrive|distor|fuzz|delay|reverb|chorus|flanger|phaser|wah"
                                     r"|looper|compress|multiefeito|multi-efeito|piano-digital|teclado|sintetizador|controlador-midi)",
                                     r"suporte|banco|capa|saco|estojo|sustain|fonte|cabo|pedalboard")},
    "session": {**SOURCES["session"], "kind_url": equipo_kind,
                "pick": _pick_equipo(rf"/products/[^/]*({_PEDAL_WORDS})",
                                     r"pedalboard|case|bag|power|supply|cable|kabel|patch|netzteil|steel|knob|switch")},
}

# --- Bajos, amplificadores y estuches (catálogo "mas", España) ------------------------------------------------------
# Mismas tiendas que el resto; la categoría sale de su breadcrumb, la URL y el nombre. Fuera los accesorios.
MAS_SKIP = re.compile(
    r"(?<![\d-])(?<!\d )(?:cuerdas?\b|\bstrings?\b|saiten|saiter)|encordad|correa|\bstrap|\bgurt|soporte|\bstand\b|st[aä]nder|cable|kabel|latiguillo"
    r"|\bp[uú]as?\b|plectr|afinador|\btuner|cejilla|\bcapo\b|clavij|mechanik|puente|\bbridge|cejuela|selleta|golpeador"
    r"|pickguard|potenci[oó]metro|\bjack\b|recambio|repuesto|ersatz|mantenimiento|limpieza|footswitch|fussschalter"
    r"|v[aá]lvulas?\b|\btubes?\b|r[oö]hre|pastillas?\b|\bpickups?\b|tonabnehmer|cubierta|\bcover\b|para (amplificador|ampli|combo|cabezal)"
    r"|pedalboard|pedal ?board|teclado|piano|bater[ií]a|\bdrums?\b|bombo|platillo|auriculares? (de|para) (estudio|dj)"
    r"|altavoz (activo|de pa)|monitor de estudio|mesa de mezclas|\bdj\b|ukelele|ukulele|contrabajo|kontrabass|violonchelo"
    r"|bass ?drum|subwoofer|\bsub\b|micr[oó]fono|libro|\bbook\b|m[eé]todo", re.I)
_CASE = re.compile(r"estuche|funda|gig ?bag|\bbag\b|flexi ?case|\bcase\b|softcase|hardcase|koffer|tasche|\bbolsa|estojo", re.I)
_AMP = re.compile(r"amplificador|\bampli\b|\bcombo|cabezal|pantalla|cabinet|\bamps?\b|verst[aä]rker|topteil|gitarrenbox"
                  r"|bassbox|\bthr\d|katana|spark|amplug|fly ?3|mini tower", re.I)
_BASS = re.compile(r"\bbajos?\b|\bbass\b|\bbasses\b|b[aä]sse\b|e-bass|\bbaixo|basso\b", re.I)
_GUITAR_CONTEXT = re.compile(r"guitarra|guitar|gitarre|\bbajo|\bbass|ac[uú]stic|el[eé]ctric|cl[aá]sic|guitare|chitarr", re.I)


# Efectos y libros "de bajo" que no son bajos (también limpia lo leído antes de afinar el filtro, al construir).
MAS_DROP = re.compile(r"\bpedal\b|pedales|efecto|overdrive|distors|delay|reverb|chorus|compress|compresor|fuzz"
                      r"|octav|\bwah\b|flanger|phaser|lehrbuch|verlag|\bbook\b|libro|m[eé]todo|limiter|enhancer|\bdriver\b|effekt|prozessor"
                      r"|processor|clarinet|posaune|tuba|mundst|winder|polish|artist ahead|rockstarter", re.I)


# Micrófonos (Numemusic quita las tildes de la URL: "micrfono"), sin sus accesorios ni previos o interfaces.
_MIC = re.compile(r"micr[oó]?fonos?|microphones?|mikrofon|\bmics?\b", re.I)
_MIC_ACC = re.compile(r"soporte|\bpie\b|\bstand|pinza|\bclip|anti-?pop|pop ?filter|paravientos|windscreen|espuma|ara[ñn]a"
                      r"|shock ?mount|suspensi|cable|adaptador|funda|estuche|bolsa|\bcase\b|maleta|repuesto|accesorio|previo"
                      r"|preamp|interfa|mezcla|mixer|grabador|recorder|brazo|\bboom\b|pantalla|absorbente|auriculares|kabel|st[aä]nder|halter"
                      r"|klemme|spinne|popschutz|windschutz|koffer|tasche|adapter|\bxlr\b.*\bxlr\b"
                      r"|cachimbo|canopla|c[aá]psula|arara|expositor|pedestal|globo|garra|haste|\bpara micr", re.I)


WITH_CASE = re.compile(r"\+ ?(g \+ )?(funda|estuche)|con (funda|estuche)|\bw/? ?case|incl", re.I)
MAX_PRICE = {"estuche": 800, "varios": 500}  # un "estuche" más caro es un instrumento con su estuche


# "Varios": accesorios de guitarra y bajo. El tipo sale de VARIOS_TYPES; aquí, solo si lo es.
_VARIOS = re.compile(r"(?<!-)(?<!\s\d )(?<!^\d )(?<!12 )(cuerdas?\b|\bstrings?\b|saiten)|juego de cuerdas|encordado|\b0?\d\d-\d{2,3}\b|\bp[uú]as?\b|plectr|\bpicks?\b"
                     r"|plektr|correa|\bstraps?\b|\bgurt\b|strap ?lock|cable|kabel|latiguillo|cejilla|\bcapo\b|kapodaster"
                     r"|afinador|\btuner\b|stimmger|soporte|\bstand\b|st[aä]nder|colgador|wall ?hanger|pastillas?\b|\bpickups?\b"
                     r"|tonabnehmer|humbucker|single ?coil|limpia|limpieza|polish|cleaner|aceite|\boil\b|winder|clavijas?\b"
                     r"|mec[aá]nicas?\b|tuning machines|mechaniken|golpeador|pickguard|cejuela|selleta|\bnut\b|\bsaddle|slide\b"
                     r"|bottleneck|potenci[oó]metro|\bknobs?\b|\bjack\b", re.I)
_GUITAR_ACC = re.compile(r"guitarr|guitar|gitarr|\bbajo|\bbass|\bbaixo|el[eé]ctric|ac[uú]stic|cl[aá]sic|instrument|\bjack\b"
                         r"|p[uú]a|plectr|\bpick|cejilla|\bcapo|kapodaster|pastilla|pickup|humbucker|single ?coil|tonabnehmer"
                         r"|dunlop|ernie ball|d'?addario|elixir|fender|gibson|ibanez|planet waves|savarez|la bella|rotosound|dr strings"
                         r"|gator|levy|righton|seymour|dimarzio|emg|kluson|gotoh|schaller|grover|snark|korg|tc electronic polytune"
                         r"|hercules|k ?& ?m|warwick|ortola|cleartone|martin|augustine|aquila|gewa|rockboard|evidence"
                         r"|\bp10\b|santo angelo|tagima|giannini|strinberg|michael|\bnig\b|\bsg\b|izzo|dolphin|rozini|onerr", re.I)
_NOT_GUITAR_ACC = re.compile(r"bater[ií]a|\bdrums?\b|\btom\b|hi-?hat|platillo|caja|snare|bombo|piano|teclado|keyboard|viol[ií]n"
                             r"|viola\b|cello|chelo|contrabajo|ukelele|ukulele|mandolin|banjo|bandurria|la[uú]d|arpa|saxo|\bsax\b|clarinete|sopro"
                             r"|cavaco|cavaquinho|bandolim|violoncelo|boquilha|trompeta"
                             r"|flauta|clarinete|tromb|micr[oó]?fono|microphone|mikrofon|\bmic\b|\bdj\b|altavo|speaker|\bxlr\b|midi"
                             r"|\busb\b|hdmi|dmx|iluminaci|foco|atril|partitura|tablet|m[oó]vil|smartphone|pedalboard|\bpedal\b"
                             r"|alimentador|fuente de alimentaci|power ?supply|v[aá]lvula|\btubes?\b|amplificador|cabezal|combo"
                             r"|libro|m[eé]todo|\bbook\b|\bcd\b|\bdvd\b|camiseta|t-?shirt|gorra|taza|llavero", re.I)


def varios_kind(crumbs, url="", name=""):
    """'varios' si es un accesorio de guitarra o bajo (cuerdas, púas, correas, cables, afinadores…), si no None."""
    text = equipo_text(crumbs, url, name)
    if not _VARIOS.search(name or "") or _NOT_GUITAR_ACC.search(name or "") or NOT_PRODUCT.search(name or ""):
        return None
    if re.search(r"\b(0?[4-9]|1[0-2]) (cuerdas|cordas|strings?)\b", name or "", re.I):  # "Ibanez 07 Cordas RG7421": guitarra
        return None
    return "varios" if _GUITAR_ACC.search(text) and not _NOT_GUITAR_ACC.search(" / ".join(crumbs or [])) else None


def mas_kind(crumbs, url="", name=""):
    """'bajo', 'ampli', 'estuche', 'micro', 'varios' o None, por la categoría, la URL y el nombre."""
    # Primero accesorio: "D'Addario EXL170 cuerdas bajo" son cuerdas, no un bajo.
    return varios_kind(crumbs, url, name) or _mas_kind(crumbs, url, name)


def _mas_kind(crumbs, url="", name=""):
    text = equipo_text(crumbs, url, name)
    if NOT_PRODUCT.search(name or "") or MAS_DROP.search(text) \
            and not _AMP.search(name or ""):
        return None
    if _MIC.search(text) and not _AMP.search(name or ""):
        return None if _MIC_ACC.search(text) else "micro"
    # Funda o estuche solo si lo dice el nombre o la última categoría: "Alhambra 3C + funda" o un bajo "w/ case" son
    # instrumentos con su funda.
    if (_CASE.search(name or "") or crumbs and _CASE.search(crumbs[-1]) or not name and _CASE.search(text)) \
            and not WITH_CASE.search(name or ""):
        other = re.search(r"teclado|piano|bater[ií]a|platillo|micr[oó]fono|pedal|\bdj\b|altavoz|ukelele|ukulele|viol[ií]n|saxo"
                          r"|trompeta|flauta|clarinete|acorde[oó]n|tambor|snare|\bmic\b|mezclador|controlador|cello|chelo|viola\b"
                          r"|contrabajo|herrajes|castañuelas|xil[oó]fono|hk audio|ld systems|\bjbl\b|subwoofer|\bsub\b|mackie|\bsrm\d|speaker|bafle", text)
        return "estuche" if not other and not _AMP.search(text) and not MAS_SKIP.search(name or "") else None
    if MAS_SKIP.search(text):
        return None
    if _AMP.search(text):
        if re.search(r"nitro amp|strike amp|yamaha emx|\bemx ?\d|bater[ií]a|\bdrums?\b|e-drum|para teclado|keyboard amp|teclado|monitor", text):
            return None
        return "ampli" if _GUITAR_CONTEXT.search(text) or re.search(
            r"marshall|orange|\bvox\b|blackstar|laney|peavey|mesa|engl|ampeg|markbass|hartke|roland|positive grid|line ?6"
            r"|kemper|aguilar|darkglass|\bebs\b|fishman|\baer\b|bugera|yamaha thr|boss|fender|victory|friedman|evh|randall", text) else None
    # Bajo por el nombre, la última categoría o la URL: "Guitarras y bajos" más arriba no basta (Numemusic).
    if _BASS.search(" / ".join([name or "", crumbs[-1] if crumbs else "", url])):
        # Marcas que solo hacen amplificadores de bajo ("Ampeg Rocket Bass RB-110")
        return "ampli" if re.search(r"ampeg|markbass|hartke|gallien|trace elliot|\beden\b|\bebs\b", text) else "bajo"
    return None


MAS_KINDS = {"bajo", "ampli", "estuche", "micro"}  # "varios" va aparte: sus filtros son otros
VARIOS_TYPES = [("Cuerdas", r"(?<!-)(?<!\s\d )(?<!^\d )(?<!12 )(cuerdas?\b|\bstrings?\b|saiten)|juego de cuerdas|encordado"
                            r"|\b0?\d\d-\d{2,3}\b"),
                ("Púas", r"\bp[uú]as?\b|plectr|\bpicks?\b|plektr"),
                ("Correas", r"correa|\bstraps?\b|\bgurt\b|strap ?lock"),
                ("Cables", r"cable|kabel|latiguillo"),
                ("Afinadores", r"afinador|\btuner\b|stimmger"),
                ("Cejillas", r"cejilla|\bcapo\b|kapodaster"),
                ("Soportes", r"soporte|\bstand\b|st[aä]nder|colgador|wall ?hanger"),
                ("Pastillas", r"pastillas?\b|\bpickups?\b|tonabnehmer|humbucker|single ?coil"),
                ("Recambios", r"clavijas?\b|mec[aá]nicas?\b|tuning machines|mechaniken|golpeador|pickguard|cejuela|selleta|\bnut\b"
                              r"|\bsaddle|potenci[oó]metro|\bknobs?\b|\bjack\b"),
                ("Mantenimiento", r"limpia|limpieza|polish|cleaner|aceite|\boil\b|winder|slide\b|bottleneck"),
                ("Otras", r"(?!x)x")]
MICRO_TYPES = [("Inalámbrico", r"inal[aá]mbric|wireless|\bfunk|sistema (de )?(mano|petaca|diadema)"), ("USB", r"\busb\b"),
               ("De cinta", r"\bcinta\b|ribbon|b[aä]ndchen"),
               ("Para instrumento", r"instrumento|instrument|bater[ií]a|bombo|\bdrums?\b|\bkick|para ampli|e ?906|sm ?57|e ?609"),
               ("Condensador", r"condensador|condenser|kondensator|\bc ?214|\bat ?[24]0\d\d|\bm ?3\b|\bnt ?1|\btlm|\bu ?87|\bc ?414"),
               ("Dinámico", r"din[aá]mic|dynamic|sm ?58|sm ?7|beta ?58|e ?8[234]5|e ?9[34]5|pga ?48|md ?421|re ?20"),
               ("Otras", r"(?!x)x")]
BASS_TYPES = [("6 cuerdas o más", r"\b[6-9] ?(cuerdas|cordas|strings?|saiter)\b|\b[6-9]-(string|saiter)"),
              ("5 cuerdas", r"\b5 ?(cuerdas|cordas|strings?|saiter)\b|\b5-(string|saiter)"),
              ("Acústico", r"ac[uú]stic|acoustic|akustik|electroac"), ("Fretless", r"fretless|sin trastes"),
              ("Escala corta", r"short ?scale|escala corta|mustang|mikro|\bjunior|\bmini\b|3/4"),
              ("4 cuerdas", r".")]
AMP_TYPES = [("Para bajo", r"\bbajos?\b|\bbaixos?\b|contrabaixo|\bbass\b|ampeg|markbass|hartke|aguilar|darkglass"),
             ("Para acústica", r"ac[uú]stic|acoustic|akustik|loudbox|\baer\b|viol[aã]o"),
             ("Combo", r"\bcombo|\bcubo\b"), ("Cabezal", r"cabezal|cabe[cç]ote|\bhead\b|topteil|\bcabeza\b"),
             ("Pantalla", r"pantalla|caixa|gabinete|cabinet|\bcab\b|\bbox\b|gitarrenbox"),
             ("De auriculares y portátil", r"auricular|headphone|amplug|port[aá]til|\bmini\b|bater[ií]a|\bfly\b"),
             ("Combo", r".")]
CASE_TYPES = [("Para bajo", r"\bbajos?\b|\bbaixos?\b|\bbass\b"),
              ("Para clásica", r"cl[aá]sic|classic|espa[nñ]ola|konzert|nylon|n[aá]ilon"),
              ("Para acústica", r"ac[uú]stic|acoustic|western|folk|dreadnought|jumbo"), ("Para eléctrica", r".")]

# Fundas y estuches, solo si la URL dice que son de guitarra o bajo (si no, entran los de batería, violín…).
_CASES_URL = r"(estuche|funda|gig-?bag|case|koffer|tasche|estojo)"
# Accesorios de guitarra y bajo (catálogo "varios": cuerdas, púas, correas, cables…).
_VARIOS_URL = (r"cuerdas|strings|saiten|\bpuas?\b|pua-|plectr|picks?-|correa|strap|cables?-de-(guitarra|instrumento|jack)"
               r"|cables?-(para-)?instrument|cable-jack|jack-jack|instrumentenkabel|cejilla|capo-|afinador|tuner|stimmger"
               r"|soportes?-(de|para)-guitarra|soporte-guitarra|gitarrenst|pastillas?-|pickups?-|tonabnehmer|limpi|polish|winder"
               r"|clavijer|mecanica|golpeador|pickguard")
_MAS_URL = (_VARIOS_URL + r"|bajo|bass|baixo|ampli|combo|cabezal|pantalla|cabinet|verstaerker|amp-|-amp\b|micr[oó]?fono|microphone|mikrofon"
            r"|" + _CASES_URL + r"[^/]*(guitar|bajo|bass|clasic|acustic|electric|gitarre)"
            r"|(guitar|bajo|bass|gitarre)[^/]*" + _CASES_URL)
_MAS_URL_SKIP = (r"valvula|tube|pedalboard|footswitch|individual|ukelele|ukulele|violin|arco|cello|mandolin|banjo"
                 r"|cables?-(para-)?(microf|altavo|audio|midi|usb|dmx|alimenta)|xlr|speakon|patch-de-bateria"
                 r"|handle|corner|insert|herraje|bateria|drum|teclado|piano|alimentador|metronomo"
                 r"|altavo[zc]|auricular|headphone|parche|sordina|monitor|linha|100v|zonas|mezclador|mixer|cover|clamp"
                 r"|pie-de|pinza|suspensor|supensor|brazo|bolsas?-para|estuches?-para-micro|reflexion|jirafa|anti-?pop|paravientos"
                 r"|arco-|contrabajo|xil|conmutador|pedal|cabassa|mazas")

MAS_SOURCES = {
    "numemusic": {**SOURCES["numemusic"], "kind_url": mas_kind,
                  "pick": _pick_equipo(r"/\d+-[^/]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
    "musicopolix": {**SOURCES["musicopolix"], "kind_url": mas_kind,
                    "pick": _pick_equipo(r"/cat/([^/]*(bajo|amplific|estuche|funda)[^/]*|produccion-musical/microfonos"
                                         r"|accesorios/accesorios-de-(guitarra|bajo)|pro-audio/cables-de-audio/cables-para-instrumentos)"
                                         r"/(.+/)?\d+-[^/]+\.html$",
                                         _MAS_URL_SKIP)},
    "alfasoni": {**SOURCES["alfasoni"], "kind_url": mas_kind,
                 "pick": _pick_equipo(r"alfasoni\.com/([^/]*(bajo|amplificador|combo|cabezal|pantalla|estuche|funda|microfono)[^/]*"
                                      r"|cuerdas-para-(guitarra|bajo)[^/]*|correas[^/]*|cables-de-guitarra|cables-para-patch-de-guitarra"
                                      r"|puas[^/]*|pastillas-para-(guitarra|bajo)[^/]*|cejillas|accesorios-para-correas[^/]*"
                                      r"|soportes-(de|para)-guitarra[^/]*|afinadores[^/]*)/[^/]+\.html$",
                                      _MAS_URL_SKIP)},
    "drunkat": {**SOURCES["drunkat"], "kind_url": mas_kind, "pick": _pick_equipo(r"drunkat\.es/[^/]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
    "pronorte": {**SOURCES["pronorte"], "kind_url": mas_kind, "pick": _pick_equipo(r"/p/[^/]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
    "egitana": {**SOURCES["egitana"], "kind_url": mas_kind, "pick": _pick_equipo(r"egitana\.es/[^/]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
    "session": {**SOURCES["session"], "kind_url": mas_kind, "pick": _pick_equipo(r"/products/[^/]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
    "mat": {**SOURCES["mat"], "kind_url": mas_kind, "pick": _pick_equipo(r"matguitars\.com/[^?]*(" + _MAS_URL + ")", _MAS_URL_SKIP)},
}


# --- Portugal (catálogo "pt"): las mismas guitarras con los precios que cada tienda pone para Portugal ----------
# (IVA del 23 % y precios propios: Thomann.pt no cobra lo mismo que Thomann.es). Solo tiendas con web portuguesa.
PT_SKIP = re.compile(r"baixo|\bbass\b|ukulele|cavaquinho|bandolim|banjo|amplifica|estojo|\bsaco|\bcapa\b|corda|acess[oó]r"
                     r"|pastilha|captador|pedal|efeito|correia|suporte|afinador|palheta|cabo|kit|pack|conjunto|set\b|partes"
                     r"|pe[cç]as|livro|m[eé]todo|sistema sem fios|wireless|microfone|piano|teclado|bateria", re.I)


# Lo que se cuela en categorías de guitarra (cuerdas sueltas, paños, métodos…): se mira el nombre.
PT_NAME_SKIP = re.compile(r"(?<!\d )\bcordas?\b|\bpano\b|resist[eê]ncia|piano|m[eé]todo|livro|^(?:estojo|saco|capa)\b"
                          r"|afinador|correia|palhetas?\b|suporte|\bcabo\b|ukulele|cavaquinho|\bbaixo\b|\bbass\b", re.I)


def pt_kind(crumbs):
    """'electrica', 'acustica', 'clasica', 'portuguesa' o None, por las categorías (en portugués) de la tienda."""
    text = " / ".join(crumbs).lower()
    # "Guitarras e baixos" arriba no la descarta; un "Baixos" al final, sí
    leaf = re.sub(r"guitarras e baixos", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"guitarr", text) or PT_SKIP.search(leaf):
        return None
    if re.search(r"guitarras? portuguesas?", text):
        return "portuguesa"
    if re.search(r"cl[aá]ssic|concerto|flamenc|nylon", text):
        return "clasica"
    if re.search(r"ac[uú]stic|eletroac|electroac|ocidenta|folk|western|viagem", text):
        return "acustica"
    if re.search(r"el[eé]c?trica", text):
        return "electrica"
    return None


def _parse_egitana_pt(soup, text):
    """Egitana.pt: analítica (categoría y precio) como en egitana.es y, además, microdatos con el EAN (gtin13)."""
    data = _parse_egitana(soup, text)
    micro = _parse_microdata(soup, text)
    # El nombre va en el h1 (no en un meta), así que el EAN se coge suelto.
    gtin = soup.find("meta", attrs={"itemprop": re.compile("^gtin1[34]$", re.I)})
    ean = normalize_id(gtin.get("content") if gtin else "").lstrip("0")
    if len(ean) >= 11:
        data["ean"] = ean
    if not data.get("price") and micro.get("price"):
        data.update({k: micro[k] for k in ("name", "brand_raw", "price", "currency", "in_stock", "image")})
        data["ean"] = micro.get("ean")
    if micro.get("in_stock") is not None:
        data["in_stock"] = micro["in_stock"]
    return data


def _parse_salao(soup, text):
    """Salão Musical (PrestaShop): precio de su analítica (view_item) y GTIN13 en un meta (en mayúsculas)."""
    h1 = soup.find("h1")
    # El itemprop=price de la página es el del primer producto relacionado; el de la ficha va en su analítica.
    price = re.search(r'"view_item",\s*\{[^}]*?"value":\s*([\d.]+)', text)
    gtin = soup.find("meta", attrs={"itemprop": re.compile("^gtin13$", re.I)})
    if not h1 or not price:
        return {"crumbs": []}
    brand = soup.find(attrs={"itemprop": "brand"})
    brand = brand.get("content") or brand.get_text(" ", strip=True) if brand else None
    image = soup.find("meta", attrs={"property": "og:image"})
    ean = normalize_id(gtin.get("content") if gtin else "").lstrip("0")
    return {"crumbs": [], "name": h1.get_text(" ", strip=True), "brand_raw": brand, "price": float(price.group(1)),
            "currency": "EUR", "in_stock": None,  # la disponibilidad de la página es también la de los relacionados
            "image": image.get("content") if image else None, "ean": ean if len(ean) >= 11 else None}


_SALAO_GUITARS = {"todas-as-guitarras-eletricas": "Guitarras elétricas", "guitarras-classicas": "Guitarras clássicas",
                  "guitarra-classica": "Guitarras clássicas", "guitarras-flamenco": "Guitarras clássicas flamenco",
                  "guitarras-eletroacusticas": "Guitarras eletroacústicas", "guitarras-acusticas": "Guitarras acústicas",
                  "guitarras-portuguesas": "Guitarras portuguesas", "guitarra-portuguesa": "Guitarras portuguesas"}


def _salao_category(url):
    parts = url.split("/")
    return parts[4] if len(parts) > 5 and parts[3] == "pt" else ""


THOMANN_PT = "https://www.thomann.pt/"
_PT_BRANDS = tuple(sorted(set(EGITANA_BRANDS) | set(ACOUSTIC_BRANDS) | {"apc", "artimusica", "alvaro", "dias", "porto"}))

PT_SOURCES = {
    "egitana": {"name": "Egitana", "sitemap": "https://www.egitana.pt/sitemaps/pt/sitemap.xml", "parse": _parse_egitana_pt,
                "ok_status": (200, 500), "kind": pt_kind,
                "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _PT_BRANDS)) or "guitarra" in s)(
                    u.split("egitana.pt/")[-1].split("/p/")[0].lstrip("/")) and not PT_SKIP.search(u.replace("-", " "))
                and not NOT_PRODUCT.search(u)},
    "thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind": pt_kind,
                "discover": lambda f: _discover_thomann(f, ("cat_allProducts_GF_guitarras_electricas.html",
                                                            "cat_allProducts_GF_guitarras_ocidentais.html",
                                                            "cat_allProducts_GF_guitarras_de_concerto.html"), THOMANN_PT),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)},
    "salaomusical": {"name": "Salão Musical", "sitemap": "https://www.salaomusical.com/1_index_sitemap.xml",
                     "parse": _parse_salao, "kind": pt_kind,
                     "crumbs": lambda u: [_SALAO_GUITARS.get(_salao_category(u), "")],
                     "pick": lambda u: _salao_category(u) in _SALAO_GUITARS and not NOT_PRODUCT.search(u)},
}


# --- Francia --------------------------------------------------------------------------------------------

FR_SKIP = re.compile(r"\bbasses?\b|\bbass\b|ukul[eé]l|mandolin|banjo|ampli|[eé]tuis?\b|housses?|cordes?\b|accessoir"
                     r"|micros?\b|pickup|m[eé]diators?|sangles?|stands?\b|supports?|accordeurs?|c[aâ]bles?|p[eé]dales?"
                     r"|effets?|pi[eè]ces?|m[eé]thodes?|livres?|claviers?|pianos?|batteries", re.I)
# Nombres que se cuelan en categorías de guitarra.
FR_NAME_SKIP = re.compile(r"(?<!\d )\bcordes?\b|\bjeux? de\b|m[eé]thode|\blivre|^(?:[eé]tui|housse|sangle)\b|accordeur"
                          r"|m[eé]diators?|\bstand\b|ukul[eé]l|\bbasse\b|\bbass\b", re.I)


def fr_kind(crumbs):
    """'electrica', 'acustica', 'clasica' o None, por las categorías (en francés) de la tienda."""
    text = " / ".join(crumbs).lower()
    # "Guitares & Basses" arriba no la descarta; un "Basses" al final, sí
    leaf = re.sub(r"guitares? (?:&|et) basses?", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"guitare", text) or FR_SKIP.search(leaf):
        return None
    if re.search(r"classique|nylon|flamenc", text):
        return "clasica"
    if re.search(r"folk|acoustique|western|voyage|parlou?r", text):
        return "acustica"
    if re.search(r"[eé]lectrique", text):
        return "electrica"
    return None


SHOPIFY_KIND = {}  # URL de la ficha → categoría, según la colección de la que sale (tiendas Shopify sin breadcrumb)


def _discover_shopify(fetcher, base, collections):
    """Fichas de unas colecciones de Shopify (products.json, 250 por página). collections: tupla de colecciones o
    {colección: categoría}; en ese caso la categoría de cada ficha queda en SHOPIFY_KIND."""
    urls = set()
    kinds = collections if isinstance(collections, dict) else {}
    for col in collections:
        for page in range(1, 41):
            url = f"{base}/collections/{col}/products.json?limit=250&page={page}"
            if not fetcher.allowed(url)[0]:
                break
            resp = fetcher.get(url)
            if resp.status_code == 429:
                raise RuntimeError("HTTP 429")
            products = resp.json().get("products", []) if resp.status_code == 200 else []
            if not products:
                break
            for p in products:
                url = f"{base}/products/{p['handle']}"
                urls.add(url)
                if col in kinds:
                    SHOPIFY_KIND.setdefault(url, kinds[col])
    return urls


def _woodbrass_fix(data, text):
    """Woodbrass repite al final la referencia completa ("1687GT Deep Noir 1687GT-5-G"): fuera."""
    words = (data.get("name") or "").split()
    if len(words) > 2 and re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)+", words[-1]) \
            and any(len(w) >= 3 and words[-1].startswith(w.split("-")[0]) for w in words[:-1]):
        data["name"] = " ".join(words[:-1])
    return data


def _michenaud_fix(data, text):
    """Michenaud: breadcrumb en microdatos y la forma ("Guitare électrique > Formes > Les Paul") aparte."""
    soup = BeautifulSoup(text, "html.parser")
    crumbs = [c.get_text(" ", strip=True) for c in soup.select('[itemprop=itemListElement] [itemprop=name]')]
    forms = re.findall(r'class="linkTouch">[^<>]*?&gt;\s*Formes\s*&gt;\s*([^<]+)<|class="linkTouch">[^<>]*?>\s*Formes\s*>\s*([^<]+)<', text)
    form = next((a or b for a, b in forms), "").strip()
    data["crumbs"] = [c for c in crumbs if c.lower() != "accueil"] + ([form] if form else [])
    return data


THOMANN_FR = "https://www.thomann.fr/"
_FR_BRANDS = _PT_BRANDS + ("gibson", "lag", "eastman", "furch", "maton", "guild", "gretsch", "godin", "seagull", "norman")

FR_SOURCES = {
    "woodbrass": {"name": "Woodbrass", "kind": fr_kind, "fix": _woodbrass_fix,
                  "discover": lambda f: _discover_shopify(f, "https://woodbrass.com",
                                                          ("guitares-electriques", "guitares-folk", "guitares-classiques")),
                  "pick": lambda u: not NOT_PRODUCT.search(u)},
    "starsmusic": {"name": "Stars Music", "sitemap": "https://www.stars-music.fr/sitemap_sm/sitemap_prod_fr.xml.gz",
                   "kind": fr_kind,
                   "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _FR_BRANDS)))(u.rsplit("/", 1)[-1])
                   and not FR_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)},
    "thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind": fr_kind,
                "discover": lambda f: _discover_thomann(f, ("cat_allProducts_GF_guitares_electriques.html",
                                                            "cat_allProducts_GF_guitares_folk.html",
                                                            "cat_allProducts_GF_guitares_classiques.html"), THOMANN_FR),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)},
    "michenaud": {"name": "Michenaud", "sitemap": "https://www.michenaud.com/exchange/google/sitemap-fiches-prod.php",
                  "kind": fr_kind, "fix": _michenaud_fix,
                  "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _FR_BRANDS)))(u.rsplit("/", 1)[-1])
                  and not FR_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)},
}


# --- Italia ---------------------------------------------------------------------------------------------

IT_SKIP = re.compile(r"\bbass[oi]\b|\bbass\b|ukulele|mandolin|banjo|amplificator|custodi|borse?\b|\bcorde?\b|accessori"
                     r"|pedal|effett|tracoll|support|accordator|plettr|cav[oi]\b|pickup|microfon|tastier|pian[oi]|batteri"
                     r"|ricambi|libr[oi]|metodo", re.I)
IT_NAME_SKIP = re.compile(r"(?<!\d )\bcorde?\b|\bmuta\b|metodo|\blibro|^(?:custodia|borsa|tracolla)\b|accordatore"
                          r"|plettr|\bsupporto\b|ukulele|\bbasso\b|\bbass\b", re.I)


def it_kind(crumbs):
    """'electrica', 'acustica', 'clasica' o None, por las categorías (en italiano) de la tienda."""
    text = " / ".join(crumbs).lower()
    # "Chitarre e bassi" arriba no la descarta; un "Bassi" al final, sí
    leaf = re.sub(r"chitarre e bassi", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"chitarr", text) or IT_SKIP.search(leaf):
        return None
    if re.search(r"classic|nylon|flamenc", text):
        return "clasica"
    if re.search(r"acustic|western|folk|elettroacustic|viaggio|parlou?r", text):
        return "acustica"
    if re.search(r"elettric", text):
        return "electrica"
    return None


# Marcas de dos palabras que Guitarshop.it no da aparte (el nombre empieza por la marca).
_TWO_WORD_BRANDS = ("music man", "ernie ball", "harley benton", "d'angelico", "gibson custom", "fender custom",
                    "paco castillo", "jose ferrer", "josé ferrer", "jose torres", "josé torres", "salvador cortez",
                    "manuel rodriguez", "baton rouge", "line 6", "martin & co.", "la mancha", "vicente carrillo")


def _guitarshop_fix(data, text):
    """Guitarshop.it (WooCommerce): sin marca aparte, va al principio del nombre ("Ibanez RGRT421 • Weathered black")."""
    name = re.sub(r"\s*•\s*", " ", data.get("name") or "").strip()
    # "Alysée A120-CE-N Chitarra elettroacustica": la descripción del final sobra.
    name = re.sub(r"(?<=\S)\s+(?:-\s+)?chitarr[ae]\b.*$", "", name, flags=re.I) if len(name.split()) > 2 else name
    data["name"] = name
    if name and not data.get("brand_raw"):
        low = name.lower()
        two = next((b for b in _TWO_WORD_BRANDS if low.startswith(b + " ")), None)
        data["brand_raw"] = name[:len(two)] if two else name.split()[0]
    data["crumbs"] = [c for c in data.get("crumbs", []) if c.lower() != "home"]
    return data


THOMANN_IT = "https://www.thomann.it/"

IT_SOURCES = {
    "thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind": it_kind,
                "discover": lambda f: _discover_thomann(f, ("cat_allProducts_GF_chitarre_elettriche.html",
                                                            "cat_allProducts_GF_chitarre_western.html",
                                                            "cat_allProducts_GF_chitarre_classiche.html"), THOMANN_IT),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)},
    "guitarshop": {"name": "Guitar Shop", "sitemap": "https://guitarshop.it/wp-sitemap.xml", "kind": it_kind,
                   "fix": _guitarshop_fix,
                   "pick": lambda u: "/prodotto/" in u and not IT_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)},
}


# --- Reino Unido ----------------------------------------------------------------------------------------

UK_SKIP = re.compile(r"\bbass(es)?\b|\bamps?\b|amplifier|pedals?\b|effects?\b|strings\b|cases?\b|\bbags?\b|gig ?bags?"
                     r"|straps?\b|stands?\b|cables?\b|accessor|pickups?\b|ukulele|mandolin|banjo|\bparts\b|tuners?\b|capos?\b"
                     r"|books?\b|keyboards?|pianos?\b|drums?\b|microphones?|wireless|spares", re.I)
UK_USED = re.compile(r"second ?hand|pre-?owned|ex-?demo|serial no|\bused\b|b-?stock", re.I)
UK_NAME_SKIP = re.compile(r"(?<!\d )(?<!\d-)\bstrings?\b|^(?:case|gig ?bag|strap|stand)\b|\bbass\b|ukulele|\btuner\b|\bcapo\b"
                          r"|\bbook\b|\bpickguard\b|\bneck\s*(?:$|for\b)", re.I)  # "… Maple Neck, Black" sí es guitarra


def uk_kind(crumbs, url="", name=""):
    """'electrica', 'acustica', 'clasica' o None, por las categorías (en inglés) de la tienda y el nombre.
    Andertons a veces solo dice "Fender Player II Modified Guitars & Basses": entonces decide el modelo del nombre."""
    text = " / ".join(crumbs).lower()
    leaf = re.sub(r"guitars? (?:&|and) bass(es)?", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"guitar", text) or UK_SKIP.search(leaf) or re.search(r"\bbass\b", (name or "").lower()):
        return None
    text += " / " + (name or "").lower()  # el nombre suele decirlo ("… Classical Guitar", "… Electro Acoustic")
    if UK_USED.search(text):
        return None
    if re.search(r"classical|nylon|flamenco|spanish", text):
        return "clasica"
    if re.search(r"acoustic|western|folk|dreadnought|parlou?r|travel", text):
        return "acustica"
    if re.search(r"electric|solid ?body|hollow|semi|st style|t style|single ?cut|double ?cut", text):
        return "electrica"
    return "electrica" if name and type_from_name(name, "", "electrica") != "Otras" else None


def _shop_kind(url, name):
    """Tiendas Shopify: la categoría de la colección; un bajo o una de segunda mano colados en la colección, fuera."""
    return None if re.search(r"\bbass\b", (name or "").lower()) or UK_USED.search(name or "") else SHOPIFY_KIND.get(url)


THOMANN_UK = "https://www.thomann.co.uk/"
_UK_BRANDS = tuple(sorted(set(_FR_BRANDS) | {"prs", "jackson", "charvel", "evh", "schecter", "ltd", "esp", "squier", "gretsch",
                                               "sterling", "music-man", "chapman", "vintage", "heritage", "sigma", "faith",
                                               "tanglewood", "washburn", "guild", "martin", "taylor", "takamine", "cort"}))

UK_SOURCES = {
    "guitarguitar": {"name": "guitarguitar", "sitemap": "https://www.guitarguitar.co.uk/sitemap-products.xml",
                     "kind_url": uk_kind,
                     "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _UK_BRANDS)))(u.rsplit("--", 1)[-1])
                     and not UK_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)},
    "thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind_url": uk_kind,
                "discover": lambda f: _discover_thomann(f, ("cat_allProducts_GF_electric_guitars.html",
                                                            "cat_allProducts_GF_acoustic_guitars.html",
                                                            "cat_allProducts_GF_classical_guitars.html"), THOMANN_UK),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)},
    "andertons": {"name": "Andertons", "sitemap": "https://www.andertons.co.uk/xmlsitemap.php",
                  "sub": lambda l: "products" in l, "kind_url": uk_kind,
                  "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _UK_BRANDS)))(u.rstrip("/").rsplit("/", 1)[-1])
                  and not UK_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)},
    "dawsons": {"name": "Dawsons", "kind_url": lambda c, u, n: _shop_kind(u, n),
                "discover": lambda f: _discover_shopify(f, "https://www.dawsons.co.uk", {
                    "electric-guitars": "electrica", "acoustic-guitars": "acustica", "acoustic-electric-guitars": "acustica",
                    "classical-guitars": "clasica"}),
                "pick": lambda u: not NOT_PRODUCT.search(u)},
    "bonners": {"name": "Bonners Music", "kind_url": lambda c, u, n: _shop_kind(u, n),
                "discover": lambda f: _discover_shopify(f, "https://www.bonnersmusic.co.uk", {
                    "electric-guitars": "electrica", "acoustic-guitars": "acustica", "electro-acoustic-guitars": "acustica",
                    "classical-guitars": "clasica"}),
                "pick": lambda u: not NOT_PRODUCT.search(u)},
}


# --- Alemania -------------------------------------------------------------------------------------------

DE_SKIP = re.compile(r"\bbass|bässe|basse\b|verstärker|\bamps?\b|effekt|pedal|saiten|koffer|taschen|gig-?bag|gurt|ständer"
                     r"|kabel|zubehör|tonabnehmer|ersatzteil|ukulele|mandolin|banjo|stimmger|plektr|kapodaster|bücher|noten"
                     r"|keyboard|piano|drum|schlagzeug|mikrofon|pflege", re.I)
DE_NAME_SKIP = re.compile(r"(?<!\d )\bsaiten(satz)?\b|^(?:koffer|gigbag|tasche|gurt)\b|\bbass\b|ukulele|stimmgerät"
                          r"|b-?ware|gebraucht", re.I)


def de_kind(crumbs):
    """'electrica', 'acustica', 'clasica' o None, por las categorías (en alemán) de la tienda."""
    text = " / ".join(crumbs).lower()
    # "Gitarren und Bässe" (Thomann) o "E-Gitarren & Zubehör" (Session) arriba no la descartan; al final, sí.
    leaf = re.sub(r"gitarren (?:und|&) bässe|e-gitarren & zubehör", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"gitarre", text) or DE_SKIP.search(leaf):
        return None
    if re.search(r"konzertgitarre|klassik|flamenco|nylon", text):
        return "clasica"
    if re.search(r"halbakustik|semi-?akustik|hollow|jazzgitarre", text):
        return "electrica"  # halbakustische E-Gitarren
    if re.search(r"westerngitarre|akustikgitarre|akustik|folk|reisegitarre", text):
        return "acustica"
    if re.search(r"e-gitarre", text):
        return "electrica"
    return None


# Musikhaus Korn no tiene breadcrumb: el tipo va al final de la URL ("…-westerngitarre/pd/232348").
_KORN_TYPES = {"e-gitarre": "E-Gitarren", "westerngitarre": "Westerngitarren", "konzertgitarre": "Konzertgitarren"}


def _korn_type(url):
    m = re.search(r"-(e-gitarre|westerngitarre|konzertgitarre)/pd/\d+$", url)
    return m.group(1) if m else ""


THOMANN_DE = "https://www.thomann.de/de/"

DE_SOURCES = {
    "thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind": de_kind,
                "discover": lambda f: _discover_thomann(f, ("cat_allProducts_GF_e-gitarren.html",
                                                            "cat_allProducts_GF_westerngitarren.html",
                                                            "cat_allProducts_GF_konzertgitarren.html"), THOMANN_DE),
                "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)},
    "session": {**SOURCES["session"], "kind": de_kind,
                "pick": lambda u: _pick_session(u) or _pick_acoustic_brand(u.split("/products/")[-1].strip("/"))},
    "korn": {"name": "Musikhaus Korn", "sitemap": "https://www.musikhaus-korn.de/content/sitemaps/sitemap-index.xml",
             "kind": de_kind, "crumbs": lambda u: [_KORN_TYPES.get(_korn_type(u), "")],
             "pick": lambda u: "/de/" in u and bool(_korn_type(u)) and not NOT_PRODUCT.search(u)},
    "hermann": {"name": "Musikhaus Hermann", "sitemap": "https://www.musikhaus-hermann.de/sitemap.xml", "kind": de_kind,
                # Las fichas acaban en su número ("…-vintage-sunburst-42894/"); lo demás son categorías.
                "pick": lambda u: bool(re.search(r"-\d{4,6}/$", u)) and not DE_SKIP.search(u.replace("-", " "))
                and not NOT_PRODUCT.search(u)},
}


# --- Brasil ---------------------------------------------------------------------------------------------
# En Brasil "guitarra" es la eléctrica; las acústicas y clásicas son "violão" (de aço o de nylon).

BR_SKIP = re.compile(r"encordoament|\bcordas?\b|\bcase\b|\bcapa\b|\bbag\b|bolsa|correia|\bcabo\b|captador|palheta|pedal"
                     r"|amplificador|\bcubo\b|\bbaixo\b|tarraxa|\bponte\b|\bkit\b|suporte|afinador|estante|\bstrap\b|ukulele"
                     r"|cavaquinho|bandolim|banjo|\bcapotraste|alavanca|escala|\bbraço\b|\bcorpo\b|knob|chave|tampa|método|livro"
                     r"|outlet|mostru[aá]rio|seminov|usad"
                     r"|gabinete|\bcaixa\b|cabe[cç]ote|\bcombo\b|hard ?case|soft ?case|transmissor|receptor|diapas|escudo|abridor|enfeite|\bmolas?\b|chaveiro|miniatura"
                     r"|quadro|camiseta|caneca|poster|adaptador|\btrava|bot[aã]o|protetor|\bpar\b|\bjogo\b|\bp/"
                     # Accesorios "para guitarra / de violão": adhesivos, jacks, puentes, apoyos…
                     r"|adesivo|\bjack\b|interface|apoio|cavalete|abafador|redutor|bra[cç]adeira|tattoo|encor|\benc\b|limpa"
                     r"|flanela|polidor|\bpino|rastilho|\bnut\b|traste|microfone|\bfonte\b|bateria|\bpra\b"
                     r"|\b(?:para|de|p/) ?(?:o |a |um |uma )?(?:guitarra|viol)", re.I)


# Lo que empieza por "Guitarra…" o "Violão…" es el instrumento aunque luego liste lo que trae ("…com afinador, cabo,
# correia e palheta"); los accesorios empiezan por el accesorio ("Encordoamento para violão", "Pedal para guitarra").
_BR_INSTR_FIRST = re.compile(r"^(?:guitarra|viol[aã]o|violao)\b", re.I)
_BR_ALWAYS_SKIP = re.compile(r"outlet|mostru[aá]rio|seminov|\busad[oa]|ukulele|cavaquinho|bandolim|banjo|\bkit\b|\bbaixo\b"
                             r"|contrabaixo|\bcd\b(?![- ]?\d)|\bdvd\b|livro|m[eé]todo|revista", re.I)  # "CD-140" es un modelo
# Al construir, sobre el nombre ya sin "Guitarra"/"Violão" delante: solo si empieza por un accesorio.
BR_NAME_SKIP = re.compile(r"^(?:encordoament|cordas?\b|capa\b|bag\b|case\b|correia|cabo\b|captador|palheta|pedal|amplificador"
                          r"|cubo\b|tarraxa|ponte\b|suporte|afinador|estante|kit\b|adesivo|interface|microfone|gabinete|caixa\b"
                          r"|transmissor|receptor|diapas|escudo|abridor)|"
                          + _BR_ALWAYS_SKIP.pattern, re.I)


def _br_instrument(*texts):
    """True si es una guitarra o un violão (y no un accesorio, un usado o un kit)."""
    texts = [unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower().strip() for t in texts]
    joined = " ".join(texts)
    if _BR_ALWAYS_SKIP.search(joined):
        return False
    if any(_BR_INSTR_FIRST.search(t) for t in texts if t):
        return True
    return not BR_SKIP.search(joined)


def br_kind(crumbs, url="", name=""):
    """'electrica', 'acustica', 'clasica' o None, por la URL y el nombre (las tiendas brasileñas apenas dan categorías)."""
    text = " ".join([url.rsplit("/", 1)[-1].replace("-", " "), name or "", " ".join(crumbs)]).lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    full = crumbs[-1] if crumbs else name  # _br_fix deja ahí el nombre completo ("Violão Clássico Yamaha…")
    if not _br_instrument(url.rstrip("/").rsplit("/", 1)[-1].replace("-", " "), full, name):
        return None
    if re.search(r"\bviol[aoõ]o|\bviolao", text):
        return "clasica" if re.search(r"nylon|classico|flamenco|\bcordas de n", text) else "acustica"
    if re.search(r"\bguitarra", text):
        return "electrica"
    return None


def _parse_ld_loose(soup, text, cur="BRL"):
    """JSON-LD de producto que no siempre es JSON válido (Multisom, Casa da Música): primero el lector normal y, si no
    saca precio, los campos sueltos con expresiones regulares. cur: la moneda si el bloque no la dice."""
    data = _parse_jsonld(soup, "loose")
    if data.get("price"):
        return data
    block = next((b for b in re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', text, re.S) if '"Product"' in b), "")
    get = lambda k: (re.search(rf'"{k}"\s*:\s*"?([^",}}\n]+)', block) or [None, None])[1]
    name, price = get("name"), get("price")
    if not name or not price:
        return {"crumbs": data.get("crumbs", [])}
    brand = re.search(r'"brand"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', block)
    image = soup.find("meta", attrs={"property": "og:image"})
    ean = normalize_id(get("gtin13") or get("gtin") or "")
    return {"crumbs": data.get("crumbs", []), "name": html.unescape(name.strip()), "brand_raw": brand.group(1) if brand else None,
            "price": float(price), "currency": (get("priceCurrency") or cur).strip(),
            "in_stock": "instock" in (get("availability") or "").lower(), "image": image.get("content") if image else None,
            "ean": ean if len(ean) in (12, 13, 14) else None}


def _br_fix(data, text):
    """Los nombres empiezan por el instrumento ("Guitarra Tagima TG-500", "Violão Elétrico Yamaha FX310"): fuera, la
    categoría ya lo dice (y así la marca va delante)."""
    name = html.unescape(data.get("name") or "")  # Conca, China Som, Audio POA: "Viol&#227;o"
    data["name"] = name
    name = re.sub(r"^(?:guitarra|viol[aã]o)(?:\s+(?:el[eé]tric[oa]|eletroac[uú]stic[oa]|ac[uú]stic[oa]|folk|cl[aá]ssic[oa]"
                  r"|de|a[cç]o|nylon|n[aá]ilon|semi-?ac[uú]stic[oa]|7 cordas|12 cordas|infantil))*\s+", "", name, flags=re.I)
    # El nombre completo se queda en las categorías: de ahí sale si es de nylon o de aço (br_kind).
    data["crumbs"] = list(data.get("crumbs") or []) + [data.get("name") or ""]
    data["name"] = name.strip() or data.get("name")
    return data


_BR_PICK = re.compile(r"guitarra|viol[aã]o|violao")


def _pick_br(url):
    slug = url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")
    return bool(_BR_PICK.search(slug)) and _br_instrument(slug) and not NOT_PRODUCT.search(url)


BR_SOURCES = {
    "multisom": {"name": "Multisom", "sitemap": "https://www.multisom.com.br/sitemap/index", "parse": _parse_ld_loose,
                 "fix": _br_fix, "kind_url": br_kind, "pick": lambda u: bool(re.search(r"-p\d+$", u)) and _pick_br(u)},
    "mundomax": {"name": "Mundomax", "sitemap": "https://www.mundomax.com.br/sitemap.xml", "fix": _br_fix, "kind_url": br_kind, "pick": _pick_br},
    "teclacenter": {"name": "Teclacenter", "sitemap": "https://www.teclacenter.com.br/google_sitemap_1.xml", "fix": _br_fix, "kind_url": br_kind,
                    "pick": _pick_br},
    "casadamusica": {"name": "Casa da Música", "sitemap": "https://www.casadamusica.com.br/sitemap.xml", "parse": _parse_ld_loose,
                     "fix": _br_fix, "kind_url": br_kind, "pick": _pick_br},
    "megasom": {"name": "Megasom", "sitemap": "https://www.megasom.com.br/sitemap.xml", "fix": _br_fix, "kind_url": br_kind, "pick": _pick_br},
    "cheirodemusica": {"name": "Cheiro de Música", "sitemap": "https://www.cheirodemusica.com.br/sitemap.xml", "fix": _br_fix,
                       "kind_url": br_kind, "pick": _pick_br},
    "musitech": {"name": "Musitech", "sitemap": "https://musitech.com.br/sitemap.xml", "fix": _br_fix, "kind_url": br_kind,
                 "pick": lambda u: "/loja/" in u and _pick_br(u)},
}


# --- Países con solo Thomann de momento (Irlanda, Austria, Países Bajos) ----------------------------------

def nl_kind(crumbs):
    """'electrica', 'acustica', 'clasica' o None, por las categorías (en neerlandés) de Thomann.nl."""
    text = " / ".join(crumbs).lower()
    leaf = re.sub(r"gitaren & basgitaren", "", " / ".join(crumbs[-2:]).lower())
    if not re.search(r"gitar", text) or re.search(r"basgitar|versterker|effect|snaren|koffer|tas\b|gigbag|accessoire|ukelele"
                                                   r"|statief|kabel|element|pickup|onderdel", leaf):
        return None
    if re.search(r"klassiek|concert|flamenco|nylon", text):
        return "clasica"
    if re.search(r"semi-?akoest|halfakoest|hollow", text):
        return "electrica"
    if re.search(r"akoest|western|folk|reisgitar", text):
        return "acustica"
    if re.search(r"e-gitar|elektrisch", text):
        return "electrica"
    return None


def _thomann_only(base, pages, kind):
    return {"thomann": {"name": "Thomann", "delay": (8.0, 14.0), "parse": _parse_thomann, "kind": kind,
                        "discover": lambda f: _discover_thomann(f, pages, base),
                        "pick": lambda u: not NOT_PRODUCT.search(u) and not re.search(r"b_stock|bstock", u)}}


IE_SOURCES = _thomann_only("https://www.thomann.ie/", ("cat_allProducts_GF_electric_guitars.html",
                                                       "cat_allProducts_GF_acoustic_guitars.html",
                                                       "cat_allProducts_GF_classical_guitars.html"), uk_kind)
AT_SOURCES = _thomann_only("https://www.thomann.at/", ("cat_allProducts_GF_e-gitarren.html",
                                                       "cat_allProducts_GF_westerngitarren.html",
                                                       "cat_allProducts_GF_konzertgitarren.html"), de_kind)
NL_SOURCES = _thomann_only("https://www.thomann.nl/", ("cat_allProducts_GF_elektrische_gitaren.html",
                                                       "cat_allProducts_GF_akoestische_gitaren.html",
                                                       "cat_allProducts_GF_klassieke_gitaren.html"), nl_kind)


# --- Woodbrass en cada país ------------------------------------------------------------------------------
# Una sola tienda Shopify con una web por país (woodbrass.es, .it, .de…): mismas colecciones (con su nombre en
# francés), pero cada país con su precio y su surtido (una ficha que no se vende allí da 404).

WOODBRASS_ALL = {"guitares-electriques": "electrica", "guitares-folk": "acustica", "guitares-classiques": "clasica"}


def _woodbrass(base, collections=WOODBRASS_ALL):
    return {"name": "Woodbrass", "kind_url": lambda c, u, n: _shop_kind(u, n), "fix": _woodbrass_fix,
            "discover": lambda f: _discover_shopify(f, base, collections), "pick": lambda u: not NOT_PRODUCT.search(u)}


SOURCES["woodbrass"] = _woodbrass("https://woodbrass.es", {"guitares-electriques": "electrica"})
ACOUSTIC_SOURCES["woodbrass"] = _woodbrass("https://woodbrass.es", {"guitares-folk": "acustica", "guitares-classiques": "clasica"})
IT_SOURCES["woodbrass"] = _woodbrass("https://woodbrass.it")
DE_SOURCES["woodbrass"] = _woodbrass("https://woodbrass.de")
AT_SOURCES["woodbrass"] = _woodbrass("https://woodbrass.at")
NL_SOURCES["woodbrass"] = _woodbrass("https://woodbrass.nl")

# Auvisa (auvisa.com, Shopify): su robots.txt no deja paginar colecciones, así que se tira del sitemap (fichas de marcas
# de guitarras) y la categoría sale del breadcrumb de cada ficha ("Guitarras / Guitarras eléctricas / …").
AUVISA_SKIP = re.compile(r"cuerda|funda|estuche|correa|\bpua|cejilla|afinador|soporte|pastilla|clavijero|amplif|pedal|cable"
                         r"|\bbajo|ukelele|ukulele|recambio|golpeador|puente|boton|potenciometro|mastil|cuerpo|jack|combo"
                         r"|cabezal|pantalla|efecto|correa|limpieza|herramienta|atril|banqueta|cejuela|selleta|traste", re.I)


def auvisa_kind(crumbs):
    text = " / ".join(crumbs).lower()
    if not text.startswith("guitarras") or AUVISA_SKIP.search(text):
        return None
    if re.search(r"espa[nñ]ola|cl[aá]sica|flamenc", text):
        return "clasica"
    if re.search(r"ac[uú]stica", text):
        return "acustica"
    if re.search(r"el[eé]ctrica", text):
        return "electrica"
    return None


def _pick_auvisa(url):
    slug = url.rsplit("/", 1)[-1]
    return ("/products/" in url and slug.startswith(tuple(b + "-" for b in _UK_BRANDS + ("aranjuez", "prudencio-saez", "suhr",
                                                                                          "tokai", "maybach", "jet", "mooer")))
            and not AUVISA_SKIP.search(slug.replace("-", " ")) and not NOT_PRODUCT.search(url))


SOURCES["auvisa"] = {"name": "Auvisa", "sitemap": "https://auvisa.com/sitemap.xml", "pick": _pick_auvisa,
                     "kind": _only("electrica", lambda c: auvisa_kind(c) == "electrica")}
ACOUSTIC_SOURCES["auvisa"] = {"name": "Auvisa", "sitemap": "https://auvisa.com/sitemap.xml", "pick": _pick_auvisa,
                              "kind": lambda c: auvisa_kind(c) if auvisa_kind(c) in ("acustica", "clasica") else None}

# --- España: tiendas de las listas oficiales de Alhambra, Yamaha, Fender/Jackson y Gibson (sin datos de categoría fiables):
# el tipo de guitarra sale del nombre y de la URL.
ES_SKIP = re.compile(r"funda|estuche|\bcase\b|gig ?bag|(?<!\d[ -])cuerdas?\b|juego de|correa|pedal|amplificador|\bampli\b|\bcombo\b|cable"
                     r"|soporte|afinador|\bp[uú]as?\b|cejilla|ukelele|ukulele|\bbajos?\b|\bbass\b|banjo|mandolin|bandurria|la[uú]d"
                     r"|m[eé]todo|libro|partitura|\bpack\b|\bkit\b|recambio|pastilla|clavij|golpeador|puente|cejuela|selleta"
                     r"|usad|segunda mano|ocasi[oó]n|outlet|b-?stock|reacondicionad|exposici[oó]n|tarjeta regalo|bolsa|mochila"
                     r"|limpia|humidific|capodaster|\bdvd\b|\bcd\b(?![- ]?\d)|camiseta|taza|llavero|miniatura|guitalele|requinto", re.I)
_ES_CLASICA = r"cl[aá]sica|flamenca|espa[nñ]ola|nylon|n[aá]ilon|cadete|alhambra|admira|raimundo|camps\b|prudencio|esteve|paco castillo|j\.? ?torres"
_ES_ACUSTICA = r"ac[uú]stica|electroac|folk|western|dreadnought|jumbo|parlor|auditorium|taylor|\bmartin\b|tanglewood|sigma"
_ES_ELECTRICA = (r"el[eé]ctrica|electric|stratocaster|telecaster|\bstrat\b|\btele\b|les paul|\bsg\b|jazzmaster|jaguar|mustang"
                 r"|semi ?hueca|hollow|ibanez|\besp\b|\bltd\b|jackson|charvel|schecter|\bprs\b|gretsch|squier|epiphone|gibson"
                 r"|fender|yamaha pacifica|pacifica|revstar|\bcort\b|harley benton|sterling|evh|music man|\bg&l\b|suhr|tokai")


_ES_MODELS = [(r"\bortega (r|rce|rst)\d|\btakamine g?c\d|\byamaha (c|cg|cx|ncx|ntx|cs|cgs|gc)\d|\bcort ac\d|\bibanez (ga|gcs)\d"
               r"|\bfender cn ?\d", "clasica"),
              (r"\btakamine\b|\byamaha (f|fs|fg|fgx|fsx|apx|cpx|ll|ls|lj|ac|aj|storia|jr|red label)\s?\d|\bcort (af|ad|earth|luce|mr|ga|sfx|cec)"
               r"|\bibanez (aw|aeg|ac|pf|aam|aem|pn|tcy|v)\d|\bfender (cd|cc|cb|fa|ct|cp)\s?\d|\bfender (malibu|newporter|redondo|monterey)"
               r"|\bepiphone (dr|aj|j ?45|hummingbird|masterbilt|songmaker)|\bgibson (j ?45|hummingbird|sj ?200|l ?00)|\bguild\b|\bsigma\b"
               r"|\btanglewood\b|\bmaton\b|\bcole clark\b|\blag\b", "acustica"),
              (r"\bibanez (grg|rg|az|s|sa|as|ar|jem|jiva|gio|grx|gsa|gax|rgd|rga|rgr|rgms|ad|tod|ps|azs|mar|jsm|pgm|fr|q)\s?\d"
               r"|\bepiphone (the dot|dot|casino|es ?\d|les paul|lp|sg|explorer|flying v|firebird|riviera|sheraton|coronet|wilshire)"
               r"|\bgibson (les paul|lp|sg|es ?\d|explorer|flying v|firebird|midtown)|\bcort (g|x|kx|cr|z|m|ex)\s?\d"
               r"|\b(jackson|charvel|schecter|esp|ltd|evh|gretsch|squier|harley benton|sterling|tokai|g l|music man|suhr)\b"
               r"|\byamaha (pacifica|revstar|rs|pac)\s?\d|\bdean (guitars )?(guitars )?(ml|mlx|v|z|zx|thoroughbred|icon|exile|xile|md"
               r"|custom zone|vendetta|evo|vx|cadillac|dimebag|dime|michael|kerry|razorback)\b|\bvintage (v\d+|revo|pro shop|electro)",
               "electrica")]


# Lo que se cuela con nombre de guitarra: recambios, otros instrumentos ("Taylor Collins" hace trompetas), libros y partituras.
_ES_NOT_GUITAR = re.compile(
    r"placa (de )?control|control plate|tusq|bridge pins?|string tree|truss ?rod|saddles?\b|tremolo arm|neck ?plate|tapa anti"
    r"|\bpouch\b|polish|outfit|\bgator\b|ortola|(?<!airflow )\bbag\b|\bamp\b|\bpins\b|repuesto|trompet|\btrompa\b|saxof"
    r"|clarinet|\bsax(o|of[oó]n)?\b|bater[ií]a|fagot"
    r"|\btuba\b|baquet|cord[oó]n|(?<!sunburst )viol[ií]n(?! ?(sun)?burst)|violonc|\bcello\b|flauta|oboe|tromb[oó]n|caj[oó]n"
    r"|l[aá]mina|xil[oó]fono|\bpiano\b"
    r"|\bop\.? ?\d|estudios\b|\bvol\.? ?\d|songbook|selections|tablatura|antolog|\bpiezas\b|canciones|repertorio"
    r"|para guitarra|for guitar|\bpvg\b|\bjuegos?\b|\bjueg\b|\bset\b(?! neck)|cintur[oó]n|\bcases\b|t ?shirt|\bmug\b|shot glass"
    r"|\bhat\b|\bcap\b|gorra|bandolera|banqueta|teclado|bombardino|(?<!\d[ -])\bstrings?\b|maximizador"
    r"|\b0\d{2} 0\d{2}\b|\b(9|1[0-3]) ([45]\d|6[0-2])\b", re.I)  # calibres de cuerdas: "010-052", "10-48"
# Marcas que no hacen guitarras (cuerdas, efectos, audio, software) delante del nombre.
_ES_NOT_GUITAR_BRAND = re.compile(r"^(\d+ )?(dunlop|zoom|boss|kidam|crane|vic firth|alesis|motu|native instruments|dpa|fishman|korg"
                                  r"|hamilton|divitone|blackstar|orange|yuer|melda|sugar bytes|blue cat|righton|d ?addario|elixir"
                                  r"|savarez|ernie ball(?! music man)|yellow parts|gator|ortola|ace|tc electronic|line ?6"
                                  r"|mooer(?! gtrs)|bbe|lr baggs|dimarzio|taylor collins)\b", re.I)
# Recambios con la pieza delante ("Fender Placa Control Telecaster", "Fender Perilla Selector Stratocaster", "Golpeador …").
_ES_PART_WORD = re.compile(r"placa|golpeador|pickguard|m[aá]stil|neck|cuerpo|body|perilla|knobs?|selector|switch|pastillas?"
                           r"|pickups?|humbuckers?|puente|bridge|cejuela|nut|clavijas?|clavijero|tuners?|palanca|muelles?"
                           r"|tornillos?|tuercas?|trastes?|potenci[oó]metros?|jack|botones|straplocks?|herrajes?|hardware|previo|preamp")
# "Con funda" o "with bag" acompañan a la guitarra: no la descartan.
_ES_WITH_CASE = re.compile(r"(\b(con|with|w|incl|incluye|com|c|y|and)\b[\s./]*|\+\s*)(su |gig )?(funda|estuche|gig ?bag|bag|case"
                           r"|softcase|hardcase|bolsa|capa)\b", re.I)


def _es_is_part(text):
    words = [w for w in re.sub(r"[^a-z0-9áéíóúñ ]", " ", text.lower()).split() if not w.isdigit()][:3]
    for w in words:
        if w in ("guitarra", "guitar", "guitarras"):
            return False
        if _ES_PART_WORD.fullmatch(w):
            return True
    return False


def es_not_guitar(url, name):
    """¿El nombre o la URL dicen que es un accesorio, un recambio, otro instrumento o un libro?"""
    slug = re.sub(r"[-_]+", " ", url.rstrip("/").rsplit("/", 1)[-1])
    for text in (html.unescape(html.unescape(name or "")), slug):
        text = _ES_WITH_CASE.sub(" ", text)
        if (ES_SKIP.search(text) or _ES_NOT_GUITAR.search(text) or _ES_NOT_GUITAR_BRAND.search(text.strip())
                or _es_is_part(text)):
            return True
    return False


def _es_explicit_kind(text):
    """El tipo cuando el nombre lo dice ("guitarra eléctrica", "acoustic-electric", "Cort guitarra cla…")."""
    if re.search(r"semi.?ac[uú]stic|semi.?hollow|semihueca", text):
        return "electrica"
    if re.search(r"cl[aá]?sica|flamenca|nylon|n[aá]ilon|\bcla\b|cadete|guitarra espa[nñ]ola|guitarra de concierto", text):
        return "clasica"
    if re.search(r"ac[uú]?stica|electroa?c[uú]?stica|acoustic|\bacus\b|dreadnought|parlou?r|jumbo(?! frets?| trastes)|resonat"
                 r"|resonador|auditorium|\bfolk\b|western", text):
        return "acustica"
    if re.search(r"el[eé]?ctrica|\belectric\b|\bel guitar\b|\bguitar elec\b|\belectr\b|\btipo (335|strato?|tele|les paul|lp|sg)\b",
                 text):
        return "electrica"
    return None


def es_guitar_kind(crumbs, url="", name=""):
    """'electrica', 'acustica', 'clasica' o None para las tiendas españolas sin categorías fiables."""
    text = " ".join([url.rstrip("/").rsplit("/", 1)[-1].replace("-", " "), name or "", " ".join(crumbs or [])]).lower()
    if es_not_guitar(url, name):
        return None
    # Si el nombre (o la URL) dice qué es, manda sobre la marca o el modelo.
    explicit = _es_explicit_kind(" ".join([url.rstrip("/").rsplit("/", 1)[-1].replace("-", " "), name or ""]).lower())
    if explicit:
        return explicit
    # Modelos que las tiendas anuncian sin decir qué son ("Takamine GN30", "Ibanez GRG170DX", "Yamaha FGX830C").
    model = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    for pat, kind in _ES_MODELS:
        if re.search(pat, model):
            return kind
    if not re.search(r"guitarra|guitar|" + _ES_CLASICA + "|" + _ES_ACUSTICA + "|" + _ES_ELECTRICA, text):
        return None
    if re.search(_ES_CLASICA, text) and not re.search(r"el[eé]ctrica|folk|western|acero", text):
        return "clasica"
    if re.search(_ES_ACUSTICA, text):
        return "acustica"
    if re.search(_ES_ELECTRICA, text) and re.search(r"guitarra|guitar|el[eé]ctrica|stratocaster|telecaster|les paul|\bsg\b"
                                                    r"|pacifica|revstar|jazzmaster|jaguar|mustang|\bstrat\b|\btele\b", text):
        return "electrica"
    return None


_ES_PICK = re.compile(r"guitarra|guitar|" + _ES_CLASICA + "|" + _ES_ACUSTICA + "|stratocaster|telecaster|les-paul|pacifica", re.I)


_ES_NOT_PRODUCT = re.compile(r"/(blogs?|collections|brand|marcas?|categor[a-z]*|category|autor[a-z-]*|tags?|etiqueta|pages)/|%5C|\+-\+"
                             r"|/\d+-[a-z]+$|djembe", re.I)


def _pick_es(u):
    slug = u.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")
    return bool(_ES_PICK.search(slug)) and not es_not_guitar(u, "") and not NOT_PRODUCT.search(u) and not _ES_NOT_PRODUCT.search(u)


def _pick_es_shopify(u):
    return "/products/" in u and _pick_es(u)


# Otros idiomas: las palabras clave al español y se clasifica con es_guitar_kind (que también reconoce modelos).
_TO_ES = {
    "pt": [(r"el[eé]tric[ao]", "eléctrica"), (r"cl[aá]ssic[ao]", "clásica"), (r"\bbaixos?\b", "bajo"), (r"\bcordas\b", "cuerdas"),
           (r"estojo|\bsaco\b|\bcapa\b", "funda"), (r"correia", "correa"), (r"palhetas?", "púa"), (r"\bcabos?\b", "cable"),
           (r"suporte", "soporte"), (r"usad[ao]", "usado"), (r"livro", "libro"), (r"cavaquinho", "ukelele")],
    "it": [(r"chitarr[ae]", "guitarra"), (r"elettric[ah]e?", "eléctrica"), (r"classic[ah]e?", "clásica"), (r"acustic[ah]e?", "acústica"),
           (r"\bbass[oi]\b", "bajo"), (r"\bcorde\b", "cuerdas"), (r"custodi[ae]", "estuche"), (r"\bborsa\b", "funda"),
           (r"tracolla", "correa"), (r"plettr[oi]", "púa"), (r"\bcav[oi]\b", "cable"), (r"accordatore", "afinador"),
           (r"support[oi]", "soporte"), (r"amplificator[ei]", "amplificador"), (r"usat[oa]", "usado"), (r"pedal[ei]", "pedal")],
    "fr": [(r"guitares?", "guitarra"), (r"[eé]lectriques?", "eléctrica"), (r"classiques?", "clásica"), (r"acoustiques?", "acústica"),
           (r"\bbasses?\b", "bajo"), (r"\bcordes\b", "cuerdas"), (r"housses?", "funda"), (r"[eé]tuis?", "estuche"),
           (r"sangles?", "correa"), (r"m[eé]diators?", "púa"), (r"c[aâ]bles?", "cable"), (r"accordeurs?", "afinador"),
           (r"occasion", "usado"), (r"m[eé]thode", "método"), (r"\blivres?\b", "libro"), (r"p[eé]dales?", "pedal")],
    # Primero las semiacústicas ("Halbakustik", "Semi-Akustik"): son eléctricas, no acústicas.
    "de": [(r"halb-?akusti\w*|semi-?akusti\w*|hollow-?body|jazzgitarren?", "guitarra eléctrica semi hueca"),
           (r"\be-?gitarren?|elektrogitarren?", "guitarra eléctrica"), (r"westerngitarren?", "guitarra acústica western"),
           (r"elektro-?akusti\w*", "electroacústica"), (r"akustikgitarren?", "guitarra acústica"),
           (r"konzertgitarren?|klassi(?:k|sche) ?gitarren?|klassikgitarren?", "guitarra clásica"), (r"flamenco", "flamenca"),
           (r"gitarren?", "guitarra"), (r"\bakusti\w*", "acústica"), (r"e-b[aä]sse?|\bb[aä]sse?\b", "bajo"), (r"saiten(satz)?", "cuerdas"), (r"koffer", "estuche"),
           (r"tasche|gigbag", "funda"), (r"\bgurt\b", "correa"), (r"plektr(um|en)", "púa"), (r"kabel", "cable"),
           (r"stimmger[aä]t", "afinador"), (r"st[aä]nder", "soporte"), (r"verst[aä]rker|\bcombo\b", "amplificador"),
           (r"gebraucht|b-ware", "usado"), (r"\bschule\b|\bbuch\b", "libro"), (r"effektger[aä]t|effekt", "pedal")],
    # En neerlandés "semi-akoestisch" suele ser una electroacústica; las semihuecas eléctricas son "hollow body".
    "nl": [(r"semi[- ]?akoestisch\w*", "electroacústica"), (r"half-?akoestisch\w*|hollow-?body", "guitarra eléctrica semi hueca"),
           (r"elektrische gita(a|re)n?", "guitarra eléctrica"), (r"elektro-?akoestisch\w*", "electroacústica"),
           (r"akoestische gita(a|re)n?|westerngita(a|re)n?", "guitarra acústica"),
           (r"klassieke gita(a|re)n?|concertgita(a|re)n?|spaanse gita(a|re)n?", "guitarra clásica"), (r"flamenco", "flamenca"),
           (r"\bakoestisch\w*", "acústica"), (r"\bklassiek\w*", "clásica"), (r"\belektrisch\w*", "eléctrica"), (r"basgita(a|re)n?|\bbas\b", "bajo"), (r"gita(a|re)n?", "guitarra"),
           (r"snaren", "cuerdas"), (r"koffer", "estuche"), (r"\bhoes\b|gigbag|\btas\b", "funda"), (r"\briem\b|gitaarband", "correa"),
           (r"plectrum", "púa"), (r"kabel", "cable"), (r"stemapparaat", "afinador"), (r"standaard", "soporte"),
           (r"versterker", "amplificador"), (r"tweedehands|occasion", "usado"), (r"effectpedaal|pedaal", "pedal")],
    "en": [(r"semi-?hollow|hollow-?body|archtop", "eléctrica semi hueca"), (r"electro-?acoustic", "electroacústica"),
           (r"electric", "eléctrica"), (r"acoustic", "acústica"), (r"classical", "clásica"), (r"flamenco", "flamenca"),
           (r"\bguitars?\b", "guitarra"),
           (r"\bstrings?\b", "cuerdas"), (r"gig ?bag|\bcase\b|\bbag\b", "funda"), (r"\bstrap\b", "correa"),
           (r"\bpicks?\b|plectrums?", "púa"), (r"\bcables?\b|\blead\b", "cable"), (r"\btuner\b", "afinador"),
           (r"\bstand\b", "soporte"), (r"amplifier|\bamp\b|\bcombo\b", "amplificador"), (r"pre-?owned|\bused\b|b-stock", "usado"),
           (r"\bbook\b", "libro")]}


# Vocabulario de equipo (bajos, amplis, pedales, teclados, micros, estuches y accesorios) → el español que entienden
# mas_kind, equipo_kind y sus tipos (BASS_TYPES, AMP_TYPES…). Va antes que _TO_ES y solo con _to_es(…, equipo=True): las
# guitarras de cada país se siguen clasificando igual. Primero se separan las palabras compuestas ("Bassverstärker" →
# "bass verstärker") y luego se traduce cada parte.
_TO_ES_EQUIPO = {
    # URLs sin diéresis ("gitarrenverstaerker", "fur"): solo en las palabras que importan ("blue" no es "blü")
    "de": [(r"verstaerker", "verstärker"), (r"staender", "ständer"), (r"kopfhoerer", "kopfhörer"), (r"\bfuer\b|\bfur\b", "für"),
           (r"baesse", "bässe"), (r"geraete?", "gerät"), (r"roehre", "röhre"), (r"fluegel", "flügel"), (r"zubehoer", "zubehör"),
           (r"buehne", "bühne"), (r"huelle", "hülle"), (r"fu(?:ß|ss)-?schalter|fu(?:ß|ss)-?taster", "footswitch"),
           (r"\b(\w{3,}?)(koffer|taschen?|gigbags?|st[aä]nder|stativ|halter(?:ung)?|kabel|gurte?|saiten|verst[aä]rker"
            r"|combo|topteil|pedale?|mikrofone?|netzteile?|box(?:en)?|effekte?|effektger[aä]te?|plektr(?:um|en|on))\b", r"\1 \2"),
           (r"zubeh[oö]r", "accesorios"),
           (r"\b(gitarren|bass|e-?bass)\s+box(?:en)?\b", r"\1 pantalla"),
           # "Röhrencombo": un ampli de válvulas, no una válvula suelta (MAS_SKIP)
           (r"vollr[oö]hren?-?|r[oö]hren?-?\s*(?=\w*[- ]?(?:combo|topteil|verst|amp|head|kopf))", "valvular "),
           (r"\bgurte\b", "correas"), (r"\bhauben?-?(?:case|cover|h[uü]lle)?", "cubierta "),
           (r"saitens[aä]tze?", "juego de cuerdas"), (r"\bmit\b", "con"), (r"\binkl\b\.?|\binklusive\b", "incl"), (r"\bfür\b|\bfuer\b", "para"),
           (r"\bcombos?\b", "cubo amplificador"),  # "combo" a secas lo haría "amplificador" (_TO_ES) y se perdería el tipo
           (r"bassgitarren?|elektrobass|e-?bässe|e-?baesse", "bajo"), (r"akustik-?b[aä]ss\w*", "bajo acústico"),
           (r"kontrab[aä]ss\w*", "contrabajo"), (r"\btopteil\b", "cabezal"),
           (r"kopfh[oö]rer", "auriculares"), (r"multi[- ]?effekt\w*", "multiefectos"),
           (r"effekt-?ger[aä]te?|effekt-?pedale?|boden-?effekte?|bodentreter|tretminen?", "pedal"),
           (r"verzerrer", "distorsión"), (r"stimmger[aä]te", "afinador"),
           (r"stage-?pianos?|bühnenpianos?", "piano de escenario"), (r"digital-?pianos?|\be-?pianos?", "piano digital"),
           (r"synthesizer", "sintetizador"), (r"master-?keyboards?|midi-?keyboards?|midi-?controller|keyboard-?controller",
                                              "controlador midi"),
           (r"\bklavier(e)?\b", "piano acústico"), (r"(?<!ovaler )(?<!ovale )\bflügel\b", "piano de cola"),
           (r"\bkeyboards?\b|tastatur", "teclado"),
           (r"mikrofone?", "micrófono"), (r"kondensator\w*", "condensador"), (r"dynamisch\w*", "dinámico"),
           (r"\bfunk\w*|drahtlos\w*", "inalámbrico"), (r"\btaschen\b", "funda"), (r"hard-?case|form-?koffer", "estuche"),
           (r"kapodaster", "cejilla"), (r"mechanik\w*", "clavijas"), (r"bottle ?neck", "bottleneck"), (r"klammer|klemme", "pinza"),
           (r"taschensender", "transmisor inalámbrico"), (r"tonabnehmer", "pastilla"), (r"schlagbrett", "golpeador"),
           (r"wandhalter\w*", "colgador"), (r"\bstativ\w*|\bhalter(?:ung)?\b", "soporte"), (r"\bpflege\w*|reinig\w*", "limpieza"),
           (r"netzteile?", "alimentador"),
           (r"schutzh[uü]lle|abdeckung|staubschutz", "cubierta"), (r"ersatz\w*", "repuesto"),
           (r"schlagzeug\w*|\bdrums?\b|e-?drums?", "batería"), (r"\bbecken\b", "platillo"),
           (r"lehrbuch|songbook|notenbuch|\bnoten\b", "libro"), (r"lautsprecher", "altavoz")],
    "nl": [(r"\b(\w{3,}?)(versterkers?|koffers?|tas|hoes|snaren|kabels?|statief|standaard|pedalen|pedaal|microfoons?)\b", r"\1 \2"),
           (r"\bmet\b", "con"), (r"\binclusief\b|\bincl\b\.?", "incl"), (r"\bvoor\b", "para"),
           (r"basgita(?:a|re)n?|elektrische bas\w*", "bajo"), (r"\bbas\b", "bajo"), (r"versterkers?", "amplificador"),
           (r"\btop\b|\bkop\b", "cabezal"), (r"speakerkast\w*|\bkast\b", "pantalla"), (r"multi-?effect\w*", "multiefectos"),
           (r"effect-?pedalen|effect-?pedaal|pedalen|pedaal", "pedal"), (r"stemapparaten?", "afinador"),
           (r"digitale piano'?s?", "piano digital"), (r"stage ?piano'?s?", "piano de escenario"), (r"synthesizers?", "sintetizador"),
           (r"midi[- ]?(keyboard|controller)s?|masterkeyboards?", "controlador midi"), (r"keyboards?", "teclado"),
           (r"microfoons?", "micrófono"), (r"draadloze?", "inalámbrico"), (r"condensator\w*", "condensador"),
           (r"dynamische?", "dinámico"), (r"koffers?", "estuche"), (r"\btas\b|\bhoes\b|gigbags?", "funda"), (r"snaren", "cuerdas"),
           (r"\bkabels?\b", "cable"), (r"statief|standaard", "soporte"), (r"koptelefoons?", "auriculares"),
           (r"drumstel\w*|\bdrums?\b", "batería"), (r"bekkens?", "platillo"), (r"capo'?s?", "cejilla"),
           (r"element(en)?\b", "pastilla"), (r"voedingen?|adapters?", "alimentador")],
    "fr": [(r"\bavec\b", "con"), (r"\bpour\b", "para"),
           (r"micros? (?:guitare|basse|manche|chevalet|humbucker|simple|double|piezo)\w*", "pastilla"),
           (r"microphones?|micros? (?:chant|instrument|statique|dynamique|cardio\w*|usb|sans fil|hf|serre-t[eê]te|cravate)", "micrófono"),
           (r"sans fil|\bhf\b", "inalámbrico"), (r"statique|[àa] condensateur", "condensador"), (r"dynamique", "dinámico"),
           (r"amplificateurs?|\bamplis?\b", "amplificador"), (r"t[eê]tes? d'ampli\w*|\bt[eê]tes?\b", "cabezal"),
           (r"baffles?|enceintes? (?:guitare|basse)", "pantalla"), (r"multi-?effets?", "multiefectos"),
           (r"p[eé]dales? d'effets?", "pedal"), (r"accordeurs?", "afinador"), (r"pianos? num[eé]riques?", "piano digital"),
           (r"synth[eé]tiseurs?", "sintetizador"), (r"(?:clavier|contr[oô]leur) (?:ma[iî]tre|midi)", "controlador midi"),
           (r"claviers?", "teclado"), (r"capodastres?", "cejilla"), (r"\bsupports?\b|\bstands?\b", "soporte"),
           (r"casques?", "auriculares"), (r"batteries?", "batería"), (r"cymbales?", "platillo"), (r"alimentations?", "alimentador"),
           (r"contrebasses?", "contrabajo")],
    "it": [(r"\bper\b", "para"), (r"amplificator[ei]|\bampli\b", "amplificador"), (r"testat[ae]", "cabezal"),
           (r"\bcass[ae]\b|cabinet", "pantalla"), (r"multi-?effett[oi]", "multiefectos"), (r"pedal[ei]|effett[oi] a pedale", "pedal"),
           (r"accordator[ei]", "afinador"), (r"microfon[oi]", "micrófono"), (r"senza fili|radiomicrofon\w*", "inalámbrico"),
           (r"a condensatore|condensatore", "condensador"), (r"dinamic[oi]", "dinámico"),
           (r"pianoforte digitale|pianoforti digitali|pian[oi] digital[ei]", "piano digital"), (r"stage piano", "piano de escenario"),
           (r"sintetizzator[ei]", "sintetizador"), (r"(?:tastiera|controller) midi|master keyboard", "controlador midi"),
           (r"tastier[ae]", "teclado"), (r"capotast[oi]", "cejilla"), (r"cuffi[ae]", "auriculares"), (r"batteri[ae]", "batería"),
           (r"piatt[oi]", "platillo"), (r"alimentator[ei]", "alimentador"), (r"contrabbass[oi]", "contrabajo")],
    "pt": [(r"\bcom\b", "con"), (r"contrabaixos?", "contrabajo"), (r"cabe[cç]a|cabe[cç]otes?", "cabezal"),
           (r"\bcolunas?\b|\bcaixas?\b", "pantalla"), (r"pedaleiras?|multi-?efeitos?", "multiefectos"), (r"pedais", "pedal"),
           (r"afinadores?", "afinador"), (r"microfones?", "micrófono"), (r"sem fios?", "inalámbrico"),
           (r"\bteclados?\b", "teclado"), (r"sintetizadores?", "sintetizador"), (r"capotrastes?", "cejilla"),
           (r"captador(es)?", "pastilla"), (r"auscultadores|fones? de ouvido", "auriculares"), (r"bateria", "batería"),
           (r"pratos?\b", "platillo"), (r"fontes? de alimenta\w*", "alimentador")],
    "en": [(r"\bwith\b|\bw/\s*", "con "), (r"sparkl\w*", "brillante"),  # "Sparkling Burgundy" no es un Spark
           (r"machine ?heads?|tuning machines?|\btuners\b", "clavijas"), (r"bottle ?neck", "bottleneck"), (r"\bfor\b", "para"), (r"\bbass guitars?\b", "bajo"), (r"\bbasses\b", "bajo"),
           (r"\b(?:amp(?:lifier)? )?heads?\b", "cabezal"), (r"speaker cab(?:inet)?s?|\bcabs?\b", "pantalla"),
           (r"multi-?effects?", "multiefectos"), (r"effects? pedals?|stomp ?box(?:es)?", "pedal"),
           (r"digital pianos?", "piano digital"), (r"midi (?:keyboard|controller)s?|master keyboards?", "controlador midi"),
           (r"microphones?|\bmics?\b", "micrófono"), (r"headphones?", "auriculares"), (r"drum ?kits?|\bdrums?\b", "batería"),
           (r"cymbals?", "platillo"), (r"power suppl(?:y|ies)", "alimentador"), (r"double bass|upright bass", "contrabajo"),
           (r"\beffects?\b", "efecto")]}


def _to_es(text, lang, equipo=False):
    """lang: "de", o varios idiomas en orden ("nl+en": tiendas neerlandesas con nombres en inglés). equipo: también el
    vocabulario de equipo (_TO_ES_EQUIPO), antes que el general."""
    text = (text or "").lower()
    for one in lang.split("+"):
        for pat, es in (_TO_ES_EQUIPO.get(one, []) if equipo else []) + _TO_ES.get(one, []):
            text = re.sub(pat, es, text)
    return text


def guitar_kind_for(lang, keep=("electrica", "acustica", "clasica")):
    """Clasificador por nombre y URL para tiendas sin categorías fiables, en el idioma de la tienda."""
    def kind(crumbs, url="", name=""):
        k = es_guitar_kind([_to_es(c, lang) for c in crumbs or []], _to_es(url.rstrip("/").rsplit("/", 1)[-1], lang),
                           _to_es(name, lang))
        return k if k in keep else None
    return kind


_GEN_NOT_PRODUCT = re.compile(r"/(blogs?|collections|brand|marcas?|marques?|marken?|merken?|categor[a-z]*|kategorie[n]?|category"
                              r"|autor[a-z-]*|tags?|etiqueta|pages|news|magazin[e]?)/", re.I)


def pick_for(lang, shopify=False):
    def pick(u):
        slug = _to_es(u.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").replace("_", " "), lang)
        return (not shopify or "/products/" in u) and bool(_ES_PICK.search(slug)) and not ES_SKIP.search(slug) \
            and not NOT_PRODUCT.search(u) and not _GEN_NOT_PRODUCT.search(u)
    return pick


# --- Francia: tiendas de las listas oficiales de Alhambra, Yamaha, Fender y Gibson (PrestaShop casi todas) ----------
# La categoría de PrestaShop suele ir en la URL ("/guitare-electro-nylon/41948-yamaha-ntx1-nt.html"): si la hay, manda
# ella; si no (o no dice qué guitarra es), el nombre, como en las tiendas españolas de esas listas.
_FR_CAT_GUITAR = re.compile(r"guitar|[eé]lectriques?|acoustiques?|folks?|classiques?|nylon|flamenc|jazz|western|solid ?body"
                            r"|dreadnought|jumbo|parlou?r|auditorium|demi caisse|hollow|semi|single ?cut|double ?cut|type (?:st|t)\b",
                            re.I)
# Accesorios que nombran la guitarra ("Capodastre pour guitare acoustique", "Étui guitare électrique").
FR_DEALER_SKIP = re.compile(
    FR_NAME_SKIP.pattern
    + r"|capodastre|\b(?:pour|de|p/) ?guitares?\b|^(?:ampli|pack|kit|support|stand|c[aâ]ble|courroie|p[eé]dale|micro|corde|jeu|set"
    r"|bretelle|repose|pupitre)\b|\bamplis?\b|amplificateurs?|si[eè]ges?\b|syst[eè]mes? hf|housses?|\b[eé]tuis?\b|\bvalise\b"
    r"|\bpack\b|ukul[eé]l|ukebass|guitalele|guitarlele|mandolin|banjo|basse|\bbass\b|occasion|reconditionn|d[eé]mo\b|\bexpo\b"
    r"|discontinu|carte cadeau|ch[eè]que cadeau|partition|songbook|recueil|apprenti|\bvol(?:ume)?\.? ?\d|\btome\b"
    r"|\bpi[eè]ces?\b|chevalet|sillet|frettes?\b|chevilles?|m[eé]caniques?\b|plaque de protection|pickguard|s[eé]lecteur|switch"
    r"|\bmicros?\b(?! ?(?:piezo|actif))|\bpiezo\b|potentiom|\bjack\b|ferrule|nettoy|entretien|\bclean|polish"
    r"|\bstraps?\b|\bstrings?\b|gig ?bag|soft ?case|hard ?case|\bcase\b|coffre|\brack\b|\bcapo\b|\btuners?\b|\bpicks?\b|\bcable\b"
    r"|\bpedal\b|\bamp\b|effects?\b|\bdelay\b|overdrive|distortion|\bfuzz\b|looper|\bcombo\b|\bbaffle|\bcab\b|\b[1-4]x1[02]\b"
    r"|\b\d+ ?watts?\b|blues junior|(?:deluxe|twin|princeton|super|vibro) ?(?:reverb|champ)|\bchamp\b|bassbreaker|katana"
    r"|\bthr ?\d|\bvt\d+x|\bac ?(?:4|10|15|30)\b(?! ?\d)|\bmustang (?:gt|lt|i|ii|iii|iv|v)\b"
    r"|phosphore|extra light|\btirant|slinky|nickel wound|\b(?:0?(?:8|9|10|11|12|13)) ?[-/ ] ?(?:38|42|46|47|49|50|52|53|54|56)\b"
    r"|batterie|caisse claire|cymbale|baguettes|balais|cajon|fagots|accord[eé]on|orgue|\bpiano|clavier|violon|clarinette|saxo"
    r"|fl[uû]te|harpe|\bdvd\b|t-shirt|tee-shirt|\bmug\b|porte-cl|casquette|planche|filtre|anti-pop|baguettes?|tamborim|hickory"
    r"|coup de pouce|nylon tip"
    r"|^(?:d'?addario|elixir|rotosound|savarez|thomastik|aquila|dunlop|gator|hercules|k&m|boss|mooer|nux|mxr|meinl|vic firth"
    r"|rohema|pearl|tama|zildjian|sabian|paiste|evans|remo|shure|sennheiser|marshall|orange|blackstar|laney|roland|korg"
    r"|line ?6|fred'?s part|righton|kyser|g7th|planet waves|musicnomad|dv mark|ashdown|mackie|la ?bella|augustine|joyo"
    r"|blacksmith|galli|cleartone|curt mangan|optima|hannabach|pyramid|ghs|dr strings|ernie ball \d)\b", re.I)
# Lo que lleva la guitarra ("… avec étui", "+ housse") no la hace un accesorio.
_FR_WITH = re.compile(r"\s*(?:\b(?:avec|et|with|w/|incl\.?|inclus)\b|\+|&)\s*(?:son |sa |un |une |the )?(?:[eé]tui|housse|valise|soft ?case"
                      r"|hard ?case|gig ?bag|case|bag)\b.*$|\b(?:[eé]tui|housse|valise) (?:inclus|offert|fourni)e?s?\b.*$", re.I)


def _fr_category(url):
    """La categoría de la URL de PrestaShop ("guitare-electrique-type-strat-"), o "" si no la lleva."""
    parts = [p for p in url.rstrip("/").split("/")[3:-1] if not re.fullmatch(r"[a-z]{2}|\d+|products?|produits?|store\d*", p)]
    return parts[-1].replace("-", " ").replace("_", " ").strip() if parts else ""


def _fr_not_guitar(text):
    """Accesorio, bajo, ampli…: por FR_DEALER_SKIP o por las palabras de categoría de FR_SKIP ("12 cordes" no cuenta)."""
    text = re.sub(r"\b\d{1,2}[ -]cordes\b|guitares? (?:&|et) basses?", "", _FR_WITH.sub("", text or ""), flags=re.I)
    return bool(FR_DEALER_SKIP.search(text) or FR_SKIP.search(text))


def _fr_slug(url):
    return re.sub(r"\.html?$", "", url.rstrip("/").rsplit("/", 1)[-1]).replace("-", " ").replace("_", " ")


_fr_by_name = guitar_kind_for("fr")


def fr_dealer_kind(crumbs, url="", name=""):
    """'electrica', 'acustica', 'clasica' o None para las tiendas francesas de las listas de marcas."""
    if _fr_not_guitar(html.unescape(name or "")) or _fr_not_guitar(_fr_slug(url)):
        return None
    cats = [c for c in list(crumbs or []) + [_fr_category(url)] if c and c.lower() not in ("accueil", "home")]
    # "Guitare acoustique 12 cordes", "Guitares & basses" arriba: no son accesorios ni bajos.
    leaf = re.sub(r"\b\d{1,2} cordes\b|guitares? (?:&|et) basses?|guitares?[ -]basses?", "", " / ".join(cats[-2:]).lower())
    if cats and (FR_SKIP.search(leaf) or _fr_not_guitar(_fr_category(url))):
        return None
    kind = fr_kind([re.sub(r"\b\d{1,2} cordes\b", "", c) for c in cats]) if cats else None
    if kind:
        return kind
    # Categoría sin "guitare" ("Électrique", "Folk", "Classique") en una tienda que solo la usa para guitarras.
    if cats and _FR_CAT_GUITAR.search(cats[-1]) and re.fullmatch(r"\s*(?:guitares?\s*)?(?:[eé]lectriques?|folk|acoustiques?"
                                                                  r"|classiques?|[eé]lectro[- ]?acoustiques?)\s*", cats[-1].lower()):
        return fr_kind(["guitare " + cats[-1]])
    # Por el nombre, sin lo que lleva ("+ housse offerte") ni las cuerdas que tiene ("6 cordes"), que lo harían un accesorio.
    clean = lambda t: re.sub(r"\b\d{1,2}[ -]cordes\b", "", _FR_WITH.sub("", t or ""), flags=re.I)
    return _fr_by_name([clean(c) for c in crumbs or []], clean(url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ")),
                       clean(name))


def pick_fr_dealer(u):
    """Fichas de guitarra: por la categoría de la URL o, si no la lleva, por el nombre de la ficha."""
    last = u.rstrip("/").rsplit("/", 1)[-1]
    # Las fichas de PrestaShop llevan su número ("/41948-yamaha-ntx1-nt.html") y las de Oxatis acaban en "-c2x…";
    # las de WooCommerce van bajo /produit/. Lo demás son categorías y marcas.
    if NOT_PRODUCT.search(u) or _GEN_NOT_PRODUCT.search(u) or re.search(r"-c(?!2x)\d+x\d+$", last) \
            or not ("/produit/" in u or re.search(r"\d", last)):
        return False
    slug = _FR_WITH.sub("", _fr_slug(u))
    if _fr_not_guitar(slug) or ES_SKIP.search(_to_es(slug, "fr")):
        return False
    cat = _fr_category(u)
    if cat and _FR_CAT_GUITAR.search(cat):
        return not _fr_not_guitar(cat)
    return pick_for("fr")(u)


def _gtin_ok(code):
    """¿Dígito de control de EAN/UPC correcto? (algunas tiendas ponen códigos internos en gtin13)."""
    digits = [int(d) for d in code or ""]
    if len(digits) not in (12, 13, 14):
        return False
    body = digits[:-1][::-1]
    return (10 - sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(body)) % 10) % 10 == digits[-1]


# Tiendas y distribuidores que algunas fichas ponen de marca (Shopify: el "vendor").
_FR_NOT_BRAND = re.compile(r"musi(?:c|que)|beuscher|gaffarel|camac|\bhtd\b|algam|auditorium ?4|guitar maniac|centrale|tamtam"
                           r"|diapason", re.I)


def _fr_dealer_fix(data, text):
    """Nombres que empiezan por el instrumento ("Guitare Classique Yamaha CG192S"): fuera; queda en las categorías. La marca
    separada con guion o coma ("PRS - Custom 24", "Fender, Player II, Stratocaster") y la tienda como marca ("Azema
    Musique"), también."""
    name = re.sub(r"\s+", " ", html.unescape(data.get("name") or "")).strip()
    if re.search(r"Ã[\x80-\xbf]", name):  # UTF-8 leído como Latin-1 (Music Privilege: "Ã©picÃ©a")
        try:
            name = name.encode("latin-1").decode("utf-8")
        except UnicodeError:
            pass
    brand = html.unescape(html.unescape(data.get("brand_raw") or "")).strip() or None  # Station Music: "&amp;amp;"
    if brand and _FR_NOT_BRAND.search(brand) and not name.lower().startswith(brand.lower()):
        brand = None  # la tienda o el distribuidor como marca ("Azema Musique", "Paul Beuscher", "Gaffarel")
    short = re.sub(r"^(?:guitares?|guitar)(?:\s+(?:[eé]lectriques?|[eé]lectro|acoustiques?|classiques?|folk|western|jazz|de|nylon"
                   r"|voyage|[eé]lectro-?acoustiques?|[eé]lectro-?classiques?|semi-?(?:hollow|acoustique)|hollow ?body|enfant|junior"
                   r"|gaucher|sbody|taille|\d/\d|1/2|3/4|7/8|4/4))*\s+", "", name, flags=re.I)
    if short != name and short:
        data["crumbs"] = list(data.get("crumbs") or []) + [name]
    name = short or name
    m = re.match(r"^([^,\-]{2,25}?)\s*(?: - |, )(.+)$", name)
    # Sin marca aparte, solo si lo de delante es una palabra ("Schecter Reaper 6 - Sky Burst" no es marca y modelo).
    if m and (m.group(1).lower().startswith(brand.lower().split()[0]) if brand else len(m.group(1).split()) == 1):
        brand = brand or m.group(1)
        name = m.group(1) + " " + m.group(2).replace(", ", " ")
    data["name"] = name
    data["brand_raw"] = brand or _brand_from_name(name)
    if data.get("ean") and not _gtin_ok(data["ean"]):
        data["ean"] = None
    return data


def _tamtam_fix(data, text):
    """TamTam: "Lâg - GLA T70A-BLS - Auditorium Black Satin": marca, referencia del distribuidor y modelo (a veces con la
    marca y "Guitare électrique" otra vez delante). Queda marca + modelo."""
    parts = re.sub(r"\s+", " ", html.unescape(data.get("name") or "")).split(" - ")
    if len(parts) >= 3:
        brand, model = parts[0].strip(), " - ".join(parts[2:]).strip()
        plain = unicodedata.normalize("NFKD", brand).encode("ascii", "ignore").decode()  # "Lâg" → "Lag"
        model = re.sub(rf"^(?:{re.escape(brand)}|{re.escape(plain)})\s+", "", model, flags=re.I)
        data["crumbs"] = list(data.get("crumbs") or []) + [model]
        data["name"], data["brand_raw"] = f"{brand} {model}", brand
    return _fr_dealer_fix(data, text)


_parse_ld_eur = functools.partial(_parse_ld_loose, cur="EUR")


def _parse_og_micro(soup, text):
    """Sin JSON-LD de producto (PrestaShop de Centrale Guitars, Guitar Maniac, Audio System; Shopify de TamTam): nombre en
    el h1, precio en las meta de Open Graph (product:price o og:price), breadcrumb y EAN (gtin13) en los microdatos. Los
    productos relacionados de abajo también llevan microdatos: solo cuenta el primero (el de la ficha)."""
    crumbs = [c.get_text(" ", strip=True) for c in soup.select('[itemtype*="BreadcrumbList"] [itemprop=itemListElement] [itemprop=name]')]
    crumbs = [c for c in crumbs if c and c.lower() != "accueil"][:-1]  # el último es la propia ficha
    h1 = soup.select_one("h1[itemprop=name]") or soup.find("h1")
    price = soup.find("meta", attrs={"property": re.compile(r"^(?:product|og):price:amount$")})
    value = re.sub(r"\s", "", price.get("content") or "") if price else ""
    value = value.replace(".", "").replace(",", ".") if re.search(r",\d{2}$", value) else value.replace(",", "")
    if not h1 or not re.fullmatch(r"\d+(?:\.\d+)?", value) or not float(value):
        return {"crumbs": crumbs}
    cur = soup.find("meta", attrs={"property": re.compile(r"^(?:product|og):price:currency$")})
    name = " ".join(h1.get_text(" ", strip=True).split())
    gtin = soup.find(attrs={"itemprop": re.compile(r"^gtin(13)?$")})
    ean = re.sub(r"\D", "", (gtin.get("content") or gtin.get_text(strip=True)) if gtin else "")
    avail = soup.find(attrs={"itemprop": "availability"})
    avail = (avail.get("href") or avail.get("content") or "") if avail else ""
    brand = soup.select_one('[itemprop=brand] [itemprop=name], meta[itemprop=brand]')
    brand = (brand.get("content") or brand.get_text(" ", strip=True)) if brand else None
    image = soup.find("meta", attrs={"property": "og:image"})
    return {"crumbs": crumbs, "name": name, "brand_raw": brand or _brand_from_name(name), "price": float(value),
            "currency": cur.get("content") if cur else "EUR", "in_stock": "instock" in avail.lower() if avail else None,
            "image": image.get("content") if image else None, "ean": ean if len(ean) in (12, 13, 14) else None}


_PS = lambda l: "_nl_" not in l and "_en_" not in l  # PrestaShop: solo el sitemap en francés
_WOO = lambda l: "product-sitemap" in l  # WooCommerce (Yoast): solo los de fichas
_pick_ps = lambda u: u.endswith(".html") and pick_fr_dealer(u)  # PrestaShop: las fichas acaban en .html (lo demás, categorías)
for _id, _name, _sm, _sub, _parse, _pick in [
        ("hurricanemusic", "Hurricane Music", "https://www.hurricanemusic.fr/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("azemamusique", "Azema Musique", "https://www.azemamusique.fr/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("maccamusic", "Macca Music", "https://www.maccamusic.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("music3000", "Music 3000", "https://www.music3000.fr/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("scottomusique", "Scotto Musique", "https://www.scottomusique.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("ubico", "Ubico Musique", "https://www.ubico-musique.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("abroadmusic", "AB Road Music", "https://www.ab-roadmusic.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("ferremusique", "Ferré Musique", "https://www.ferremusique.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("musicmatos", "Musique Matos", "https://www.musicmatos.com/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("auditorium4", "Auditorium 4", "https://www.auditorium4.fr/1_index_sitemap.xml", _PS, _parse_ld_eur, _pick_ps),
        ("nuostore", "Music City", "https://nuostore.com/sitemap_index.xml", _WOO, _parse_ld_eur, pick_fr_dealer),
        ("westmusic", "West Music", "https://westmusic.fr/sitemap_index.xml", _WOO, _parse_ld_eur, pick_fr_dealer),
        ("seveneant", "Sévénéant Musique", "https://www.seveneant.com/sitemap_index.xml", _WOO, _parse_ld_eur, pick_fr_dealer),
        ("stationmusic", "Station Music", "https://station-music.com/sitemap_index.xml", _WOO, _parse_ld_eur, pick_fr_dealer),
        ("halldemusique", "Hall de la Musique", "https://www.halldemusique.com/sitemap.xml", None, _parse_ld_eur, pick_fr_dealer),
        ("musicprivilege", "Music Privilege", "https://www.music-privilege.fr/assets/sitemap.xml", None, _parse_ld_eur, pick_fr_dealer),
        # Oxatis: las fichas acaban en "-c2x<número>" (Lordel marca las descatalogadas con "DISCONTINUE" en el nombre).
        ("lordelmusique", "Lordel Musique", "https://www.lordelmusique.com/Sitemap.asp?AccID=133964&LangID=0", None, _parse_ld_eur,
         lambda u: bool(re.search(r"-c2x\d+$", u)) and pick_fr_dealer(u)),
        ("xlmusic", "XL Music", "https://www.xlmusic.fr/Sitemap.asp?AccID=32135&LangID=0", None, _parse_ld_eur,
         lambda u: bool(re.search(r"-c2x\d+$", u)) and pick_fr_dealer(u)),
        # Sin la palabra "guitare" en la URL ("/store1/Takamine-P3DC-p241093603"): todas sus fichas, y decide el nombre.
        ("musicandco", "Music & Co", "https://www.musicandco.net/sitemap.xml", None, _parse_ld_eur,
         lambda u: bool(re.search(r"-p\d+$", u)) and not _fr_not_guitar(_fr_slug(u)) and not NOT_PRODUCT.search(u)),
        ("diapasonmusic", "Diapason", "https://diapasonmusic.com/sitemap.xml", None, _parse_ld_eur,
         lambda u: "/products/" in u and pick_fr_dealer(u)),
        # Sin JSON-LD de producto: Open Graph y microdatos.
        ("tamtam", "TamTam", "https://www.tamtamonline.com/sitemap.xml", None, _parse_og_micro,
         lambda u: "/products/" in u and pick_fr_dealer(u)),
        ("centraleguitars", "Centrale Guitars", "https://www.centraleguitars.com/1_index_sitemap.xml", _PS, _parse_og_micro, _pick_ps),
        ("guitarmaniac", "Guitar Maniac", "https://www.guitarmaniac.com/1_index_sitemap.xml", _PS, _parse_og_micro, _pick_ps),
        ("audiosystem", "Audio System", "https://audiosystem.fr/1_index_sitemap.xml", _PS, _parse_og_micro, _pick_ps)]:
    FR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "sub": _sub, "parse": _parse, "fix": _fr_dealer_fix,
                       "kind_url": fr_dealer_kind, "pick": _pick}
FR_SOURCES["tamtam"]["fix"] = _tamtam_fix

# Guitar Legend (París): un sitemap por idioma; solo las fichas en francés. Breadcrumb y EAN en el JSON-LD.
FR_SOURCES["guitarlegend"] = {
    "name": "Guitar Legend", "sitemap": "https://www.guitar-legend.com/sitemap.xml", "sub": lambda l: "/fr/products" in l,
    "parse": _parse_ld_eur, "fix": _fr_dealer_fix, "kind_url": fr_dealer_kind,
    "pick": lambda u: "/fr/" in u and bool(re.search(r"-\d+\.html$", u)) and not _fr_not_guitar(_fr_slug(u))
    and not NOT_PRODUCT.search(u)}
# Paul Beuscher (París, Shopify): su sitemap son 370.000 partituras; las guitarras, de la colección "guitares".
# En gtin13 mezcla EAN de verdad con códigos internos que hasta cuadran el dígito de control ("1570050132734"): sin EAN.
FR_SOURCES["paulbeuscher"] = {"name": "Paul Beuscher", "parse": _parse_ld_eur, "kind_url": fr_dealer_kind,
                              "fix": lambda d, t: {**_fr_dealer_fix(d, t), "ean": None},
                              "discover": lambda f: _discover_shopify(f, "https://paul-beuscher.com", ("guitares",)),
                              "pick": lambda u: not NOT_PRODUCT.search(u) and not _fr_not_guitar(_fr_slug(u))}


def _es_fix(data, text):
    """WooCommerce da a veces la marca como lista ("brand": [{"name": …}]); el lector suelto pone BRL si falta la moneda."""
    brand = data.get("brand_raw")
    if isinstance(brand, list):
        brand = brand[0] if brand else None
    if isinstance(brand, dict):
        brand = brand.get("name")
    name = html.unescape(html.unescape(data.get("name") or ""))  # "G&amp;amp;L" (Zingla)
    # "Guitarra clásica Admira Paloma" → "Admira Paloma": la marca delante, como en el resto de tiendas.
    name = re.sub(r"^guitarra( (el[eé]ctrica|electroac[uú]stica|ac[uú]stica|cl[aá]sica|flamenca|electrocl[aá]sica))?"
                  r"( electrificada| infantil| junior| de viaje)?\s+", "", name, flags=re.I)
    if name:
        data["name"] = name
        # Marca que no sale en el nombre ("Adam Hall" en una Admira de Fusté, "Descatalogados" en Abrines): la del nombre.
        if not brand or brand.lower() not in name.lower():
            brand = _brand_from_name(name)
    data["brand_raw"] = brand
    # Códigos internos en el campo del EAN (Abrines: 1000000…; códigos de tienda 2…): no son EAN.
    if data.get("ean") and re.match(r"(2|10000)", data["ean"]):
        data["ean"] = None
    if data.get("price") is not None and data.get("currency") in (None, "", "BRL"):
        data["currency"] = "EUR"
    return data


def _es_store(store_id, name, sitemap, pick, kind=es_guitar_kind, fix=None, **extra):
    """La tienda en los dos catálogos: eléctricas en uno; acústicas y clásicas en el otro."""
    base = {"name": name, "sitemap": sitemap, "parse": _parse_ld_loose, "pick": pick, **extra,
            "fix": (lambda d, t: _es_fix(fix(d, t), t)) if fix else _es_fix}
    SOURCES[store_id] = {**base, "kind_url": lambda c, u="", n="": "electrica" if kind(c, u, n) == "electrica" else None}
    ACOUSTIC_SOURCES[store_id] = {**base, "kind_url": lambda c, u="", n="": k if (k := kind(c, u, n)) in ("acustica", "clasica")
                                  else None}


def _es_by_category(cats, cat_of):
    """Tiendas con la categoría en la URL: la categoría dice el tipo ("?": se deduce del nombre) y el nombre solo descarta
    accesorios y recambios que la tienda haya metido ahí."""
    def kind(crumbs, url="", name=""):
        k = cats.get(cat_of(url))
        if not k or es_not_guitar(url, name):
            return None
        return es_guitar_kind(crumbs, url, name) if k == "?" else k
    return kind


def _pick_by_category(cats, cat_of):
    return lambda u: cat_of(u) in cats and not NOT_PRODUCT.search(u) and not es_not_guitar(u, "")


# Shopify publica también los sitemaps de sus otros idiomas (/pt-pt/, /en/): solo los de la tienda en español.
_SHOPIFY_ES_SITEMAP = lambda u: bool(re.match(r"https://[^/]+/sitemap_products_\d+\.xml", u))
_WOO_PRODUCTS = lambda u: "product-sitemap" in u

for _id, _name, _sm in [("musicsales", "Musicsales", "https://www.musicsales.es/1_index_sitemap.xml"),
                        ("musicalsanfrancisco", "Musical San Francisco", "https://www.musicalsanfrancisco.es/sitemap_index.xml"),
                        ("malaga8", "Madrid Musical Málaga 8", "https://www.malaga8.com/1_index_sitemap.xml"),
                        ("rockbox", "Rockbox", "https://www.rockbox.es/1_index_sitemap.xml"),
                        ("hazen", "Hazen", "https://www.hazen.es/sitemap.xml")]:
    _es_store(_id, _name, _sm, _pick_es)

_es_store("microfusa", "Microfusa", "https://www.microfusa.com/sitemap.xml", _pick_es_shopify, sub=_SHOPIFY_ES_SITEMAP)
# Neomúsica es sobre todo partituras y viento: solo las fichas que empiezan por "guitarra-<tipo>-".
_es_store("neomusica", "Neomúsica", "https://www.neomusica.es/sitemap.xml", sub=_SHOPIFY_ES_SITEMAP,
          pick=lambda u: bool(re.search(r"/products/guitarra-(electro)?(ac[uú]stica|cl[aá]sica|flamenca|el[eé]ctrica)-", u))
          and _pick_es(u))
# WooCommerce (Fusté, Zingla): solo los sitemaps de producto (fuera entradas del blog y categorías) y fichas /producto/.
for _id, _name, _sm in [("fuste", "Musical Fusté", "https://www.musicalfuste.com/sitemap_index.xml"),
                        ("zingla", "Zingla Música", "https://www.zinglamusica.com/sitemap_index.xml")]:
    _es_store(_id, _name, _sm, lambda u: "/producto/" in u and _pick_es(u), sub=_WOO_PRODUCTS)

# PrestaShop con la categoría en la URL (/<categoría>/<id>-<nombre>): la categoría manda. Se corrige el precio sin IVA si
# lo diera (como en MAT).
_first_dir = lambda u: u.split("/")[3] if u.count("/") == 4 and re.search(r"/\d+-[^/]+$", u) else ""
_ABRINES = {**{c: "electrica" for c in ("guitarras-electricas-stratocaster", "guitarras-electricas-telecaster",
                                        "guitarras-electricas-les-paul", "guitarras-electricas-sg", "guitarras-electricas-otras-formas",
                                        "guitarras-electricas-para-zurdos", "guitarras-electricas-para-ninos")},
            **{c: "clasica" for c in ("guitarras-clasicas", "guitarras-clasicas-electrificadas", "guitarras-flamencas",
                                      "guitarras-flamencas-electrificadas", "guitarras-espanolas-crossover",
                                      "guitarras-espanolas-para-zurdos", "guitarras-12", "guitarras-14", "guitarras-34",
                                      "guitarras-78", "guitarras-de-luthier", "guitarras-silent")},
            **{c: "acustica" for c in ("guitarras-acusticas", "guitarras-electroacusticas", "guitarras-acusticas-12-cuerdas",
                                       "guitarras-acusticas-zurdos", "guitarras-acusticas-34", "guitarras-acusticas-de-luthier")}}
_es_store("abrines", "Abrines Música", "https://www.abrinesmusica.com/1_index_sitemap.xml",
          _pick_by_category(_ABRINES, _first_dir), _es_by_category(_ABRINES, _first_dir), fix=_mat_vat)
_PARTITURA = {**{c: "electrica" for c in ("superstrato", "strato", "double-cut", "single-cut", "tele", "semicaja", "semijazz",
                                          "otras-formas", "heavy", "7-8-cuerdas-electricas", "jazzmaster-mustang", "signature",
                                          "zurdas", "jazz", "mini", "baritona")},
              **{c: "acustica" for c in ("electroacusticas", "acustica", "acusticas-zurdas", "guitarras-12-cuerdas", "traveller",
                                         "guitarras")},
              **{c: "clasica" for c in ("clasica", "electrificada", "flamenca", "cadete", "clasica-zurda-flamenca-zurda")}}
_es_store("partitura", "Partitura", "https://www.partituraonline.com/1_index_sitemap.xml",
          _pick_by_category(_PARTITURA, _first_dir), _es_by_category(_PARTITURA, _first_dir), fix=_mat_vat)
# Trino Music (Drupal): /catalogo/guitarras/<categoría>/<nombre>. Su robots.txt pide 10 s entre peticiones.
_TRINO = {**{c: "clasica" for c in ("clasica", "clasica-electrificada", "flamenca", "clasica-espanola", "otros-tamanos")},
          **{c: "acustica" for c in ("dreadnought", "otras-acusticas", "concierto", "jumbo", "auditorium", "12-cuerdas", "parlor",
                                     "jumbo-auditorio", "mini")},
          "electrica": "electrica", "para-zurdos": "?"}
_trino_cat = lambda u: u.split("/")[5] if u.count("/") == 6 and "/catalogo/guitarras/" in u else ""
_es_store("trinomusic", "Trino Musical", "https://www.trinomusic.com/sitemap.xml", _pick_by_category(_TRINO, _trino_cat),
          _es_by_category(_TRINO, _trino_cat), delay=(10.0, 13.0))


# Alteisa (alteisa.com, Zamora; PrestaShop): tienda general de música, sonido e iluminación con venta a particulares.
# Su sitemap (~55.000 URLs) se filtra fuerte: fichas (/<id>-<nombre>.html, con o sin categoría delante) cuya categoría o
# cuyo nombre digan guitarra; el breadcrumb y el nombre deciden el tipo.
_ALTEISA_CAT = re.compile(r"alteisa\.com/(guitarras?-(el[eé]ctricas?|ac[uú]sticas?|electroac[uú]sticas?|cl[aá]sicas?|espa[nñ]olas?"
                          r"|flamencas?|electrocl[aá]sicas?)[a-z0-9-]*)/\d+-[^/]+\.html$")


def _pick_alteisa(u):
    if not re.search(r"/\d+-[^/]+\.html$", u) or NOT_PRODUCT.search(u) or es_not_guitar(u, ""):
        return False
    return bool(_ALTEISA_CAT.search(u)) or _pick_es(u)


_es_store("alteisa", "Alteisa", "https://alteisa.com/module/lgsitemaps/sitemap?name=sitemap_1", _pick_alteisa, fix=_mat_vat)


# --- Portugal e Italia: tiendas de los directorios de distribuidores (sitemap + JSON-LD) --------------------------
# Accesorios con nombre en el idioma de la tienda (o en inglés: Gewa en FAF Música) que el clasificador por nombre no
# reconoce: capos, atriles, clavijeros, golpeadores… Lo que diga el nombre manda sobre la categoría.
_DEALER_SKIP = {
    "pt": re.compile(r"transpositor|\bestante|\bpauta|\bapoio|dedeira|tarraxa|\bponte\b|pastilha|captador|\bal[cç]a\b|\bmala\b"
                     r"|limpeza|polimento|abafador|\bpe[cç]as?\b|\bkit\b|\bpack\b|conjunto|\bcordas?\b|encordoament|palheta"
                     r"|correia|afinador|suporte|estojo|\bsaco\b|\bcapa\b|\bbaixo\b|cavaquinho|bandolim|ukulele|guitalele"
                     r"|amplificador|\bpedal|efeito|\bcabo\b|microfone|m[eé]todo|livro|usad[oa]|recondicionad|seminov"
                     r"|cart[aã]o (de )?oferta|vale de oferta|\bpara guitarra|\bcurso\b|[aá]lbum|partitura|songbook|\bcd\b(?![- ]?\d)"
                     r"|\bdvd\b|bateria|baqueta|banco|cadeira|acess[oó]rio|\bjack\b|[oó]rg[aã]o|\bdrag[aã]o\b|a[cç]o inox"
                     r"|rastilho|pestana|trastes?\b|camiseta|caneca", re.I),
    "it": re.compile(r"capotasto|leggio|meccanic|\bponte\b|battipenna|\bpick-?ups?\b|tracoll|cinghi|custodi|astucci|\bborsa"
                     r"|\bcord[ae]\b|mut[ae] di|plettr|accordator|\bsupport[oi]\b|reggichitarr|amplificator|\bpedal|effett"
                     r"|\bcav[oi]\b|microfon|metodo|\blibr[oi]\b|usat[oa]|\bbass[oi]\b|ukulele|mandolin|banjo|ricambi|\bkit\b"
                     r"|\bpack\b|tastier|pian[oi]|pianoforte|ex ?demo|esposizione|ricondizionat|buono regalo|gift card"
                     r"|\bper chitarr|\bcorso\b|lezion|dizionario|\baccordi\b|spartit|songbook|antologia|\bstudi\b|batteri"
                     r"|bacchett|mallet|glockenspiel|xilofon|rullante|\bpiatt[oi]\b|panca|sgabell|accessori|didattica"
                     r"|edizioni|\bsingola\b|\bjack\b|alimentator|wireless|trasmettitor|synth|sellett|traversin|tappo"
                     r"|ponticell|tastini|maglietta|felpa|cappell[oi]|tazza|portachiavi|organo|\bmuta\b|\bset (?:chitarra|di corde)"
                     r"|\bper (?:violin|pianofort|flaut|sax|clarinett|tromb|viol|archi|canto)|potenziometr|\bmolle\b|teoria"
                     r"|\bbasi della\b|gadget|\bleva\b|poggiapiede", re.I)}
# Lo que el nombre dice que trae ("… com saco", "… con custodia", "… w/ case") no lo convierte en accesorio.
_DEALER_WITH = re.compile(r"\s(?:com|c/|con|w/|with|incl\.?|inclus[oa]|includ\w*|\+|&)\s.*$", re.I)
# "12 corde", "7 cordas", "6-string": es la guitarra, no las cuerdas.
_DEALER_STRINGS = re.compile(r"\b\d{1,2}[ -]?(?:cord[ae]s?|strings?)\b", re.I)
_EN_SKIP = re.compile(r"\bstrings?\b|\bpicks?\b|\bcapo\b|\bstraps?\b|gig ?bag|\bcase\b|\bstand\b|\btuners?\b|\bpickups?\b"
                      r"|\bbass\b|armrest|clamp|polish|cleaner|\bnut\b|saddle|bridge pins?|machine heads?|pickguard|\bknobs?\b"
                      r"|humidifier|\bslide\b|\bhanger\b|wall ?mount|\bcable\b|\bbook\b|\bbag\b|\bfor (?:\w+ )?guitars?\b"
                      r"|play.?along|\bvol(?:ume)?\.? ?(?:\d+|[ivx]+)\b|excerpts|drums?\b|sticks\b|mallets?\b|soundhole|phosphor"
                      r"|80/20|light bronze|silked|nickel wound|round ?wound|flat ?wound|(?:normal|high|hard|low) tension"
                      r"|wireless|synth|processor|humidity|power supply|truss ?rod|\bcover\b|fret ?wire|t-?shirt|hoodie|\bmug\b|poster|keychain"
                      r"|ball ?end|tie ?end|extra light|custom light|medium light|electric nickel|\bthemes\b|control plates?"
                      r"|tuning machines?|\bhat\b|beanie|switch tips?|potentiometer|\bsolos?\b|recorded versions?|feedback"
                      r"|monitoring|\bmat\b|springs?\b|taylorsense|\blicks\b|tremolo arm|trem arm|whammy|footrest"
                      # Calibres de cuerdas ("11-52", "010 - 046") y referencias de cuerdas Martin (MSP3100, MA540, M160…)
                      r"|\b0?(?:0[89]|1[0-4])\s?[-–]\s?0?(?:[3-7]\d|80)\b|\bmartin (?:msp|ma|mm|mfx?|m)\s?\d{2,4}"
                      # Marcas que solo hacen accesorios
                      r"|dimarzio|\bgator\b|righton|vic firth|d.?addario|elixir|seymour duncan|rotosound|dunlop|planet waves|carl martin"
                      # Editoriales de libros y partituras
                      r"|hal leonard|carisch|\bcurci\b|music sales|ricordi|volont[eé]|eschig|berklee|mel bay|\balfred\b|wise publ", re.I)
# Categorías que engloban guitarras con otras cosas: no descartan.
_DEALER_BOTH = re.compile(r"(?i)instrumentos( musicais)?( de)? cordas?|strumenti a corda|chitarre[ -]e[ -]bassi|chitarre bassi"
                          r"|guitarras? e baixos?|guitarra e baixo")
# El nombre lo dice claramente ("Chitarra classica", "Guitarra Eletroacústica"): manda sobre los modelos que reconoce
# es_guitar_kind ("Lag OC70 Chitarra Classica" no es acústica por ser Lag).
_DEALER_SAYS = [("clasica", re.compile(r"cl[aá]ssic(?:[ao]|he|al)\b|flamenc|\bnylon\b|\bconcerto\b", re.I)),
                ("acustica", re.compile(r"ac[uú]stic|folk\b|western|dreadnought", re.I)),
                ("electrica", re.compile(r"el[eé]c?tric[ao]\b|elettric[ah]e?\b|\belectric\b", re.I))]
# Modelos que las tiendas italianas y portuguesas anuncian sin decir qué son (Eko, Sire, Rocio…).
_DEALER_MODELS = [("clasica", re.compile(r"\beko(?: guitars)? (?:cs|vibra|studio|conservatorio)\b|\brocio\b", re.I)),
                  ("acustica", re.compile(r"\beko(?: guitars)? (?:ranger|nxt|tri|one|mia|marco polo|ego|dmv|ndr|laurel)\b", re.I)),
                  ("electrica", re.compile(r"\beko(?: guitars)? (?:s|ls|st|tl|vt|dv|vr|fire|aire|camaro|tero|cv|m)\b ?-?\d*"
                                           r"|\bsire(?: guitars)? (?:s|l|t|h|j|v)\d", re.I))]
_DEALER_SEMI = re.compile(r"semi-? ?(?:ac[uú]stic|hollow)|hollow ?body|semi-?ac[uú]stic", re.I)


def dealer_kind(lang):
    """'electrica', 'acustica', 'clasica' (o 'portuguesa', en Portugal) para las tiendas de los directorios: primero la
    categoría de la tienda (breadcrumb) si la hay y lo dice; si no, el nombre y la URL (guitar_kind_for)."""
    by_name = guitar_kind_for(lang)
    by_crumbs = {"pt": pt_kind, "it": it_kind}[lang]
    skip = lambda t: bool(_DEALER_SKIP[lang].search(t) or _EN_SKIP.search(t) or ES_SKIP.search(_to_es(t, lang)))

    def kind(crumbs, url="", name=""):
        name = _DEALER_STRINGS.sub(" ", name or "")
        core = _DEALER_WITH.sub("", name)
        slug = _DEALER_WITH.sub("", _DEALER_STRINGS.sub(" ", url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")))
        # La ruta de la URL suele llevar la categoría ("/chitarre/corde/…", "/negozio/chitarre/chitarre-acustiche/…").
        segs = [unquote(x).replace("-", " ").replace("_", " ") for x in urlsplit(url.rstrip("/")).path.split("/")[1:]
                if x and not re.fullmatch(r"[\d,]+", x)][:-1]  # sin la ficha (ni su número, si acaba en él)
        if skip(core) or (not name and skip(slug)) or _DEALER_SKIP[lang].search(_DEALER_BOTH.sub("", " / ".join(segs))):
            return None
        crumbs = [_DEALER_STRINGS.sub(" ", c) for c in crumbs or []
                  if c and c.strip().lower() not in ("início", "inicio", "home", "homepage")]
        text = " ".join(crumbs + [core, slug]).lower()
        if lang == "pt" and re.search(r"guitarras? portuguesas?|guitarras? (?:de )?fado", text):
            return "portuguesa"
        if _DEALER_SEMI.search(text) and not re.search(r"cl[aá]ssic|nylon", text):
            return "electrica"  # semiacústicas y hollow body: eléctricas
        if crumbs:
            k = by_crumbs(crumbs)
            if k in ("electrica", "acustica", "clasica"):
                return k
            if _DEALER_SKIP[lang].search(_DEALER_WITH.sub("", _DEALER_BOTH.sub("", crumbs[-1]))):
                return None  # la tienda lo tiene en accesorios, bajos…
        if segs and (k := by_crumbs(segs)) in ("electrica", "acustica", "clasica"):
            return k
        if re.search(r"guitar|chitarr", core.lower()):
            for k, pat in _DEALER_SAYS:
                if pat.search(core):
                    return k
        for k, pat in _DEALER_MODELS:
            if pat.search(core) or (not core and pat.search(slug)):
                return k
        return by_name(crumbs, "/" + slug.replace(" ", "-"), core)
    return kind


_DEALER_GENERIC = re.compile(r"^(?:(?:chitarr[ae]|guitarras?|guitars?|electric|acoustic|classical|el[eé]trica|eletroac[uú]stica"
                             r"|ac[uú]stica|cl[aá]ssica|elettric[ah]|acustic[ah]|classic[ah]|semiacustica|elettrificata|la|il"
                             r"|\d/\d)\s+)+", re.I)


def _dealer_fix(store_name):
    """Nombre sin " | Tienda" ni " - Tienda - Ciudad" al final; marca sin entidades HTML, ni la tienda ("Clan della Musica"),
    ni la jerarquía de Shopify ("Fender, Fender > Squier" → "Squier"), ni "Chitarra" (de "Chitarra elettrica Airline …").
    Los libros (EAN que es un ISBN: 978…, 979…) quedan como libros."""
    norm = lambda t: re.sub(r"[^a-z]", "", t.lower())

    def fix(data, text):
        parts = re.split(r"\s+[-|–]\s+", html.unescape(data.get("name") or "").strip())
        cut = next((i for i in range(1, len(parts)) if norm(store_name) in norm(parts[i])), len(parts))
        data["name"] = " - ".join(parts[:cut]).strip() or None
        brand = html.unescape(str(data.get("brand_raw") or "")).split(",")[-1].split(">")[-1].strip()
        if not brand or norm(brand) == norm(store_name) or _DEALER_GENERIC.fullmatch(brand + " "):
            brand = _brand_from_name(_DEALER_GENERIC.sub("", data["name"])) if data["name"] else None
        data["brand_raw"] = brand
        if brand and _EN_SKIP.search(brand):  # marca de accesorios (Vic Firth, D'Addario…), aunque el nombre no la lleve
            data["crumbs"] = ["accessori acessório"]
            return data
        bare = _DEALER_GENERIC.sub("", data["name"] or "").strip()
        if bare and bare != data["name"] and len(bare.split()) >= 2:
            data["crumbs"] = list(data.get("crumbs") or []) + [data["name"]]  # de ahí sale el tipo
            data["name"] = bare
        if str(data.get("ean") or "").startswith(("978", "979")):
            data["crumbs"] = ["libro livro"]
        return data
    return fix


def _parse_ld_eur(soup, text):
    """_parse_ld_loose para tiendas en euros: sin priceCurrency en el JSON-LD roto, el precio es en euros (no reales)."""
    data = _parse_ld_loose(soup, text)
    if data.get("price") and data.get("currency") == "BRL":
        data["currency"] = "EUR"
    return data


def _dealer(name, sitemap, lang, path=None, sub=None, parse=_parse_ld_eur, shopify=False, cat_path=None, **extra):
    """Fuente de una tienda de los directorios. path: la URL de una ficha tiene que contenerlo (regex). cat_path: tiendas
    cuya URL lleva la categoría ("/chitarre-elettriche/…"): se cogen todas las fichas de esa categoría aunque el nombre
    no diga "chitarra"."""
    if shopify and not path:
        path = r"^https?://[^/]+/products/"  # sin las copias en otros idiomas (/en/products/…)

    def pick(u):
        if (path and not re.search(path, u)) or (shopify and "/products/" not in u) or NOT_PRODUCT.search(u) \
                or _GEN_NOT_PRODUCT.search(u):
            return False
        slug = _DEALER_WITH.sub("", re.sub(r"\.html?$", "", u.rstrip("/").rsplit("/", 1)[-1]).replace("-", " ").replace("_", " "))
        if _DEALER_SKIP[lang].search(slug) or _EN_SKIP.search(slug) or ES_SKIP.search(_to_es(slug, lang)):
            return False
        return bool(cat_path and re.search(cat_path, u)) or bool(_ES_PICK.search(_to_es(slug, lang)))
    src = {"name": name, "sitemap": sitemap, "parse": parse, "fix": _dealer_fix(name), "kind_url": dealer_kind(lang),
           "pick": pick, **extra}
    if sub:
        src["sub"] = (lambda l: re.search(sub, l) is not None) if isinstance(sub, str) else sub
    return src


# Probadas a mano (unas 12 fichas por tienda): precio en euros y, casi siempre, la categoría en el breadcrumb o en la URL.
_DEALERS_PT = {
    "guitarcustom": _dealer("Guitar Custom", "https://guitarcustom.pt/wp-sitemap.xml", "pt", path="/produto/", sub="posts-product"),
    "discosom": _dealer("Discosom", "https://discosom.pt/sitemap_index.xml", "pt", path="/produto/", sub="product-sitemap"),
    "tonsemelodias": _dealer("Tons e Melodias", "https://www.tonsemelodias.com/wp-sitemap.xml", "pt", path="/produto/",
                             sub="posts-product"),
    "adagio": _dealer("Adagio", "https://adagio.pt/sitemap_index.xml", "pt", path="/loja/", sub="product-sitemap"),
    "russomusica": _dealer("Russo Música", "https://russomusica.com/wp-sitemap.xml", "pt", path="/loja/", sub="posts-product"),
}
_DEALERS_IT = {
    "musicis": _dealer("Musicis", "https://www.musicis.it/sitemap.xml", "it"),
    "cavalli": _dealer("Cavalli Musica", "https://www.cavallimusica.com/media/sitemap.xml", "it"),
    "zecchini": _dealer("Zecchini Musica", "https://www.zecchinimusica.it/sitemap.xml", "it", sub="nuovo"),
    "biasin": _dealer("Biasin", "https://biasin.com/sitemap.xml", "it"),
    "yourmusiconline": _dealer("Your Music Online", "https://yourmusiconline.it/sitemap.xml", "it", sub="sitemap_products",
                               shopify=True),
    "clandellamusica": _dealer("Clan della Musica", "https://www.clandellamusica.it/sitemap.xml", "it",
                               sub=r"\.it/sitemap_products", shopify=True),
    "disanto": _dealer("Di Santo Musica", "https://www.disantomusica.it/sitemap.xml", "it", sub="sitemap_products", shopify=True),
    "ceccherini": _dealer("Ceccherini Music", "https://ceccherinimusic.com/sitemap.xml", "it", sub="sitemap_products",
                          shopify=True),
    "globalnetshop": _dealer("Global Net Shop", "https://www.globalnetshop.it/sitemap.xml", "it", sub="sitemap_products",
                             shopify=True),
    "barone": _dealer("Barone Musica", "https://www.baronemusica.com/sitemap_index.xml", "it", path="/prodotto/",
                      sub="product-sitemap"),
    "lenzotti": _dealer("Lenzotti", "https://shop.lenzotti.it/sitemap_index.xml", "it", path="/negozio/", sub="product-sitemap",
                        cat_path=r"/negozio/chitarre/chitarre-(elettriche|acustiche|classiche)[^/]*/"),
    "emusicstore": _dealer("E-Musicstore", "https://www.e-musicstore.it/sitemap_index.xml", "it", path="/shop/",
                           sub="product-sitemap", cat_path=r"/shop/chitarre/chitarre-(elettriche|acustiche|classiche)[^/]*/"),
    "cappellani": _dealer("Cappellani Musica", "https://cappellanimusica.it/sitemap_index.xml", "it", path="/prodotto/",
                          sub="product-sitemap"),
    "cittadellamusica": _dealer("Cittadella della Musica", "https://cittadellamusica.store/media/mapping/sitemap/sitemap.xml",
                                "it", path=r"-mh\d+\.html$"),
    "smpalma": _dealer("SM Palma", "https://www.smpalma.it/sitemap_product_product_product.xml", "it"),
    "suonostore": _dealer("Suono Store", "https://shop.suonostore.com/sitemap_index.xml", "it", path="/p/", sub="product-sitemap"),
    "centrodellamusica": _dealer("Centro della Musica", "https://www.centrodellamusica.net/sitemap.xml", "it",
                                 sub="sitemap_products", shopify=True),
    "fireflyaudio": _dealer("Firefly Audio", "https://www.fireflyaudio.it/wp-sitemap.xml", "it", sub="posts-product",
                            path=r"/shop/[^?]*chitarr"),
    "direzionemusica": _dealer("Direzione Musica", "https://www.direzionemusica.it/sitemap.xml", "it"),
    "redhouse": _dealer("Red House", "https://redhouse.it/1_index_sitemap.xml", "it"),
    "stralu": _dealer("Stralù", "https://www.stralu.it/wp-sitemap.xml", "it", sub="posts-product"),
    "checcacci": _dealer("Checcacci", "https://www.checcacci.it/wp-sitemap.xml", "it", sub="posts-product"),
    "semstrumenti": _dealer("S&M Strumenti", "https://semstrumenti.it/sitemap.xml", "it", path="/catalogo-completo/",
                            cat_path=r"/catalogo-completo/chitarre-(elettriche|acustiche|classiche)"),
}
PT_SOURCES.update(_DEALERS_PT)
IT_SOURCES.update(_DEALERS_IT)


# Musifex (musifex.pt, Odoo): sin datos estructurados ni EAN. Las fichas salen de los listados de cada categoría de
# guitarras (de ahí la categoría) y el precio, del bloque de precio de la ficha.
MUSIFEX = "https://musifex.pt"
_MUSIFEX_CATS = {"guitarra-e-baixo-guitarras-guitarras-eletricas-190": "electrica",
                 "guitarra-e-baixo-guitarras-guitarras-acusticas-192": "acustica",
                 "guitarra-e-baixo-guitarras-guitarras-classicas-191": "clasica"}


def _discover_musifex(fetcher):
    urls = set()
    for cat, kind in _MUSIFEX_CATS.items():
        for page in range(1, 60):
            url = f"{MUSIFEX}/shop/category/{cat}" + (f"/page/{page}" if page > 1 else "")
            if not fetcher.allowed(url)[0]:
                break
            resp = fetcher.get(url)
            found = {MUSIFEX + h.split("?")[0] for h in re.findall(r'itemprop="name"[^>]*href="(/shop/[^"]+)"', resp.text)}
            if resp.status_code != 200 or not found - urls:
                break
            for u in found:
                SHOPIFY_KIND.setdefault(u, kind)
            urls |= found
    return urls


def _brand_from_name(name):
    low = (name or "").lower()
    two = next((b for b in _TWO_WORD_BRANDS if low.startswith(b + " ")), None)
    return name[:len(two)] if two else (name.split()[0] if name else None)


def _parse_odoo(soup, text):
    h1 = soup.find("h1")
    price = soup.select_one("#product_details .product_price .oe_currency_value") or soup.select_one(".product_price .oe_currency_value")
    if not h1 or not price:
        return {"crumbs": []}
    name = h1.get_text(" ", strip=True)
    image = soup.find("meta", attrs={"property": "og:image"})
    value = float(price.get_text().replace(".", "").replace(",", "."))
    return {"crumbs": [], "name": name, "brand_raw": _brand_from_name(name), "price": value, "currency": "EUR",
            "in_stock": None, "image": image.get("content") if image else None, "ean": None}


PT_SOURCES["musifex"] = {"name": "Musifex", "discover": _discover_musifex, "parse": _parse_odoo,
                         "kind_url": lambda c, u, n: _shop_kind(u, n), "pick": lambda u: not NOT_PRODUCT.search(u)}


# Music Maker (musicmaker.ie, Dublín): sin datos estructurados ni EAN; nombre, breadcrumb y precio de la propia página.
def _parse_musicmaker(soup, text):
    h1 = soup.find("h1")
    price = soup.select_one(".mm-price__now")
    if not h1 or not price:
        return {"crumbs": []}
    crumbs = []
    for a in soup.select('[aria-label=Breadcrumb] a, [aria-label=breadcrumb] a, .breadcrumb a'):
        c = a.get_text(" ", strip=True)
        if c and c.lower() != "home" and (not crumbs or crumbs[-1] != c):
            crumbs.append(c)
    name = h1.get_text(" ", strip=True)
    img = soup.select_one("#mm-gallery-img, img[itemprop=image]")
    stock = re.search(r"(?i)\b(out of stock|in stock)\b", text)
    return {"crumbs": crumbs, "name": name, "brand_raw": _brand_from_name(name),
            "price": float(re.sub(r"[^\d.]", "", price.get_text())), "currency": "EUR",
            "in_stock": stock.group(1).lower() == "in stock" if stock else None,
            "image": img.get("src") if img else None, "ean": None}


# --- Brasil: equipo (catálogo "brmas"): bajos, amplis, pedales, teclados, micros, estuches y accesorios ----------------
# Se traduce el texto al vocabulario de los clasificadores de España (mas_kind, equipo_kind y sus tipos) y se usan tal cual.
_PT_ES = [(r"contrabaixos?|baixos?(?= el[eé]trico| ativo| passivo| \d| de \d|\b)", "bajo"), (r"\bcordas\b", "cuerdas"),
          (r"encordoamentos?", "juego de cuerdas"), (r"palhetas?", "púas"), (r"correias?", "correa"), (r"\bcabos?\b", "cable"),
          (r"capotraste|braçadeira", "cejilla"), (r"suportes?|estantes?", "soporte"), (r"captador(es)?", "pastilla"),
          (r"tarraxas?", "clavijas"), (r"cabe[cç]otes?", "cabezal"), (r"\bcaixas?\b|gabinetes?", "pantalla"),
          (r"\bcubos?\b", "combo"), (r"microfones?", "micrófono"), (r"sem fio", "inalámbrico"), (r"pedaleiras?", "pedalera"),
          (r"\bcases?\b|\bbags?\b|\bcapas?\b|estojos?|semi ?case|hard ?case|soft ?case", "funda"), (r"viol[aã]o", "guitarra acústica"),
          (r"bateria", "batería"), (r"fones? de ouvido", "auriculares"), (r"\bteclados?\b", "teclado")]


def _pt_es(text):
    text = (text or "").lower()
    for pat, es in _PT_ES:
        text = re.sub(pat, es, text)
    return text


def br_mas_kind(crumbs, url="", name=""):
    """'bajo', 'ampli', 'pedal', 'teclado', 'micro', 'estuche', 'varios' o None, para las tiendas brasileñas."""
    crumbs, url, name = [_pt_es(c) for c in crumbs or []], _pt_es(url.rsplit("/", 1)[-1].replace("-", " ")), _pt_es(name)
    if re.search(r"\bkit\b|usad|seminov|outlet|mostru", name):
        return None
    return mas_kind(crumbs, url, name) or equipo_kind(crumbs, url, name)


def _br_mas_fix(data, text):
    """Como en las guitarras, y además el nombre traducido al final de las categorías: de ahí salen los tipos."""
    data = _br_fix(data, text)
    data["crumbs"] = list(data.get("crumbs") or []) + [_pt_es(data["crumbs"][-1] if data.get("crumbs") else data.get("name"))]
    return data


_BR_MAS_URL = re.compile(r"baixo|contrabaixo|amplificador|\bcubo|cabecote|cabeçote|caixa|pedal|pedaleira|teclado|piano|sintetiz"
                         r"|controlador|microfone|\bcase\b|\bbag\b|\bcapa\b|estojo|encordoamento|\bcordas?\b|palheta|correia"
                         r"|\bcabo\b|afinador|capotraste|suporte|captador|tarraxa|fone|interface|booster|overdrive|distortion|delay"
                         r"|reverb|fuzz|chorus|looper|multiefeito", re.I)


def _pick_br_mas(u):
    u = u.rstrip("/")
    slug = (u[:-2] if u.endswith("/p") else u).rsplit("/", 1)[-1].replace("-", " ")
    return bool(_BR_MAS_URL.search(slug)) and not NOT_PRODUCT.search(u) \
        and not re.search(r"(?i)\bkit\b|usad|seminov|outlet|mostru|bateria eletr|ac[uú]stica (bateria|tambor)", slug)


# Fender Brasil (fender.com.br, la lleva Pride Music, importador y distribuidor oficial, São Paulo): vende directamente y a veces más barato que las
# tiendas. Sus fichas no traen EAN, pero sí la referencia de Fender ("#026-6020-560"), que en otras tiendas va con EAN.
FENDER_BR = "https://www.fender.com.br"
_FENDER_BR_CATS = ("guitarras", "guitarras/stratocaster", "guitarras/telecaster", "guitarras/squier", "guitarras/lancamentos",
                   "acusticos", "acusticos/dreadnought", "acusticos/newporter", "acusticos/telecaster", "acusticos/lancamentos")
_REF_EAN = None


def _ref_ean():
    """Referencia de fabricante (0266020560) → EAN, de lo ya leído en todos los catálogos."""
    global _REF_EAN
    if _REF_EAN is None:
        _REF_EAN = {}
        for f in sorted(DIR.glob("**/offers.json")):
            for u, v in load(f, {}).items():
                if not v.get("ean"):
                    continue
                if v.get("ref"):
                    _REF_EAN.setdefault(re.sub(r"\D", "", str(v["ref"])), v["ean"])
                for c in re.findall(r"(?<!\d)(0\d{9}|\d{3}-\d{4}-\d{3})(?!\d)", f"{v.get('name') or ''} {u}"):
                    _REF_EAN.setdefault(c.replace("-", ""), v["ean"])
    return _REF_EAN


def _discover_fender_br(fetcher):
    # Su sitemap es viejo y sus enlaces dan fichas vacías: solo los listados de cada categoría.
    urls = set()
    for cat in _FENDER_BR_CATS:
        page = f"{FENDER_BR}/{cat}"
        if not fetcher.allowed(page)[0]:
            continue
        resp = fetcher.get(page)
        if resp.status_code == 200:
            urls |= set(re.findall(r'href="(https://www\.fender\.com\.br/produto/[^"#?]+)"', resp.text))
    # La misma ficha puede salir con y sin categoría en la URL: una por número de producto.
    return sorted({re.search(r"/produto/(\d+)", u).group(1): u for u in sorted(urls)}.values())


def _parse_fender_br(soup, text):
    plain = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    title = re.search(r"((?:GUITARRA|VIOL[ÃA]O|BAIXO|CONTRABAIXO)(?:(?!R\$|SKU:).){5,160}?)\s+SKU:", plain, re.I)
    price = re.search(r"SKU:\s*\d+\s*R\$\s*([\d.]+,\d{2})", plain)
    if not title or not price or price.group(1) == "0,00":  # sin precio: producto descatalogado
        return {"crumbs": []}
    name = re.sub(r"\s*[®™]", "", title.group(1)).strip()
    ref = re.search(r"Modelo:\s*#?\s*(\d{3}-?\d{4}-?\d{3})", plain)
    ref = ref.group(1).replace("-", "") if ref else None
    name = re.sub(r"\s*\d{3}-\d{4}-\d{3}\s*-?\s*", " ", name).strip()
    name = " ".join(w.capitalize() if w.isupper() and len(w) > 3 else w for w in name.split())
    img = soup.select_one('img[src*="/imgs/produtos/"]')
    return {"crumbs": [title.group(1)], "name": name, "brand_raw": "Squier" if re.search(r"squier", name, re.I) else "Fender",
            "price": float(price.group(1).replace(".", "").replace(",", ".")), "currency": "BRL",
            "in_stock": True if "ADICIONAR AO CARRINHO" in plain.upper() else (False if re.search(r"(?i)indispon|esgotad", plain) else None),
            "image": img.get("src") if img else None, "ean": _ref_ean().get(ref) if ref else None, "ref": ref}


# Tiendas de la lista oficial de distribuidores de Yamaha Brasil (br.yamaha.com/pt/dealers) que venden guitarras online
# y publican sitemap con precio en la ficha.
for _id, _name, _sm in [("tangomusic", "Tango Music", "https://www.tangomusic.com.br/sitemap.xml"),
                        ("ajoiamusical", "A Joia Musical", "https://www.ajoiamusical.com.br/sitemap.xml"),
                        ("carneiromusic", "Carneiro Music", "https://www.carneiromusic.com.br/sitemap.xml"),
                        ("destroyer", "Destroyer", "https://www.destroyer.com.br/sitemap.xml"),
                        ("musicalcentersom", "Musical Center Som", "https://www.musicalcentersom.com.br/sitemap.xml"),
                        ("palaciodosom", "Palácio do Som",
                         "https://dcdn-us.mitiendanube.com/stores/008/045/752/themes/common/sitemap.xml.gz")]:
    BR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "parse": _parse_ld_loose, "fix": _br_fix, "kind_url": br_kind,
                       "pick": _pick_br}
# De los distribuidores de Gibson/Epiphone (Royal Music, que tiene tienda propia) e Ibanez (Musical Express).
for _id, _name, _sm in [("royalmusic", "Royal Music", "https://store.royalmusic.com.br/sitemap.xml"),
                        ("musicacenter", "Música Center", "https://www.musicacenter.com.br/sitemap.xml"),
                        ("concamusic", "Conca Music", "https://www.concamusic.com.br/sitemap/index"),
                        ("lojapontomusical", "Ponto Musical",
                         "https://dcdn-us.mitiendanube.com/stores/001/130/862/themes/common/sitemap.xml.gz"),
                        ("duettomusical", "Duetto Musical", "https://duettomusical.com.br/sitemap.xml"),
                        ("eimusica", "Eimusica", "https://acdn-us.mitiendanube.com/stores/004/379/567/themes/common/sitemap.xml.gz"),
                        ("luggi", "Luggi", "https://www.luggi.com.br/sitemap.xml"),
                        ("estacaomusicalbh", "Estação Musical",
                         "https://dcdn-us.mitiendanube.com/stores/006/021/944/themes/common/sitemap.xml.gz"),
                        ("tamborim", "Tamborim de Ouro", "https://tamborimonline.com.br/sitemap.xml"),
                        ("rivermusic", "River Music", "https://dcdn-us.mitiendanube.com/stores/007/991/644/themes/common/sitemap.xml.gz")]:
    BR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "parse": _parse_ld_loose, "fix": _br_fix, "kind_url": br_kind,
                       "pick": _pick_br}


# De los listados oficiales de tiendas de Tagima (tagima.com.br/pt/lojas) y Michael (onde encontrar).
for _id, _name, _sm in [
        ("akusticamusical", "Akustica Musical", "https://www.akusticamusical.com.br/sitemap.xml"),
        ("rckaudio", "RCK Audio", "https://www.rckaudio.com.br/sitemap.xml"),
        ("tunermusic", "Tuner Music", "https://dcdn-us.mitiendanube.com/stores/001/620/210/themes/common/sitemap.xml.gz"),
        ("lojarockclube", "Rock Clube", "https://acdn-us.mitiendanube.com/stores/006/644/674/themes/common/sitemap.xml.gz"),
        ("shoppingdamusica", "Shopping da Música",
         "https://acdn-us.mitiendanube.com/stores/002/790/962/themes/common/sitemap.xml.gz"),
        ("chinasom", "China Som", "https://www.chinasom.com.br/sitemap/index"),
        ("panoramamusical", "Panorama Musical",
         "https://dcdn-us.mitiendanube.com/stores/006/589/607/themes/common/sitemap.xml.gz"),
        ("musichallcenter", "Music Hall Center",
         "https://dcdn-us.mitiendanube.com/stores/006/471/427/themes/common/sitemap.xml.gz"),
        ("supersonora", "Supersonora", "https://www.supersonora.com.br/sitemap.xml"),
        ("sosom", "Só Som", "https://www.sosom.com.br/sitemap.xml"),
        ("pontodomusico", "Ponto do Músico", "https://www.pontodomusico.com.br/sitemap.xml"),
        ("soprodivinomusical", "Sopro Divino", "https://www.soprodivinomusical.com.br/sitemap.xml.gz"),
        ("armazemdomusico", "Armazém do Músico",
         "https://acdn-us.mitiendanube.com/stores/006/996/172/themes/common/sitemap.xml.gz"),
        ("elomusical", "Elo Musical", "https://www.elomusical.com.br/sitemap.xml"),
        ("audiopoa", "Audio POA", "https://audiopoa.com/sitemap/index"),
        ("fujisom", "Fujisom", "https://www.fujisom.com.br/sitemap.xml"),
        ("apopularaudio", "A Popular Áudio",
         "https://dcdn-us.mitiendanube.com/stores/006/726/228/themes/common/sitemap.xml.gz"),
        ("islmusic", "ISL Music", "https://dcdn-us.mitiendanube.com/stores/007/059/393/themes/common/sitemap.xml.gz"),
        ("opsom", "OP Som", "https://dcdn-us.mitiendanube.com/stores/001/435/423/themes/common/sitemap.xml.gz")]:
    BR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "parse": _parse_ld_loose, "fix": _br_fix, "kind_url": br_kind,
                       "pick": _pick_br}


def _br_price(txt):
    """'R$ 7.317,00' → 7317.0"""
    m = re.search(r"([\d.]+,\d{2})", txt or "")
    return float(m.group(1).replace(".", "").replace(",", ".")) if m else None


def _br_ean(text):
    m = re.search(r"(?<!\d)(789\d{10}|0?\d{12})(?!\d)", text) if re.search(r"(?i)\bean|gtin|c[oó]digo de barras", text) else None
    return m.group(1) if m else None


def _parse_micro_br(soup, text):
    """Microdatos de schema.org en etiquetas o meta (Praise, Serenata, Soco Music)."""
    data = _parse_microdata(soup, text)
    if data.get("price"):
        data["in_stock"] = None if "availability" not in text else data["in_stock"]
        return data
    price = soup.find(attrs={"itemprop": "price"})
    h1 = soup.find("h1")
    if not price or not h1:
        return {"crumbs": []}
    value = price.get("content") or price.get_text(strip=True)
    try:
        value = float(value) if re.fullmatch(r"[\d.]+", value) else _br_price(value)
    except ValueError:
        value = None
    if not value:
        return {"crumbs": []}
    name = h1.get_text(" ", strip=True)
    img = soup.select_one('meta[property="og:image"]')
    return {"crumbs": [], "name": name, "brand_raw": _brand_from_name(name), "price": value, "currency": "BRL",
            "in_stock": None, "image": img.get("content") if img else None, "ean": _br_ean(text)}


def _parse_woo_br(soup, text):
    """WooCommerce sin JSON-LD de producto (Música Mais, Alberto Teclados): el bloque de precio de la ficha. Se quita el
    precio tachado y, de los que quedan (boleto con descuento, tarjeta…), el más alto: el precio normal."""
    h1 = soup.select_one(".product_title, h1")
    box = soup.select_one(".summary p.price, p.price")
    if not h1 or not box:
        return {"crumbs": []}
    for d in box.find_all("del"):
        d.decompose()
    prices = [p for p in (_br_price(a.get_text(" ", strip=True)) for a in box.select(".woocommerce-Price-amount")) if p]
    if not prices:
        return {"crumbs": []}
    name = h1.get_text(" ", strip=True)
    img = soup.select_one('meta[property="og:image"]')
    return {"crumbs": [], "name": name, "brand_raw": _brand_from_name(name), "price": max(prices), "currency": "BRL",
            "in_stock": False if re.search(r"(?i)fora de estoque|esgotado", text) else None,
            "image": img.get("content") if img else None, "ean": _br_ean(text)}


for _id, _name, _sm, _parse in [
        ("praisemusic", "Praise Music", "https://www.praisemusic.com.br/sitemap.xml", _parse_micro_br),
        ("serenata", "A Serenata", "https://www.serenatanet.com.br/sitemap.xml", _parse_micro_br),
        ("socomusic", "Soco Music", "https://www.socomusic.com.br/sitemap.xml", _parse_micro_br),
        ("musicamais", "Música Mais", "https://www.musicamais.com.br/sitemap.xml", _parse_woo_br),
        ("albertoteclados", "Alberto Teclados", "https://albertoteclados.com.br/sitemap.xml", _parse_woo_br)]:
    BR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "parse": _parse, "fix": _br_fix, "kind_url": br_kind,
                       "pick": lambda u: (u.rstrip("/").endswith("/p") and _pick_br(u.rstrip("/")[:-2])) or
                       ("/p" != u[-2:] and _pick_br(u) and not re.search(r"/cordas/(violao|guitarra)[^/]*/?$", u))}


def _pick_vtex(u):
    """Tiendas VTEX: la ficha acaba en /p ("…/guitarra-ibanez-rg121dx/p")."""
    u = u.rstrip("/")
    return u.endswith("/p") and _pick_br(u[:-2])


for _id, _name, _sm in [("x5music", "X5 Music", "https://www.x5music.com.br/sitemap.xml"),
                        ("ninjasom", "Ninja Som", "https://www.ninjasom.com.br/sitemap.xml"),
                        ("supersom", "Super Som", "https://www.supersominstrumentos.com.br/sitemap.xml")]:
    BR_SOURCES[_id] = {"name": _name, "sitemap": _sm, "parse": _parse_ld_loose, "fix": _br_fix, "kind_url": br_kind,
                       "pick": lambda u: _pick_vtex(u) or _pick_br(u)}
BR_SOURCES["ninjasom"]["pick"] = _pick_vtex  # sus demás URLs son listados
BR_SOURCES["serenata"]["pick"] = _pick_vtex

# Las mismas tiendas brasileñas para el equipo (menos Fender Brasil, que solo lista guitarras, y Teclacenter, bloqueada).
BRMAS_SOURCES = {}
for _id, _src in BR_SOURCES.items():
    if _id in ("fenderbr", "teclacenter"):
        continue
    BRMAS_SOURCES[_id] = {**_src, "kind_url": br_mas_kind, "fix": _br_mas_fix, "pick": _pick_br_mas}
BRMAS_SOURCES["musicalcentersom"]["pick"] = lambda u: "/produto/" in u and _pick_br_mas(u)
for _id in ("ninjasom", "serenata", "x5music", "supersom"):
    BRMAS_SOURCES[_id]["pick"] = lambda u: u.rstrip("/").endswith("/p") and _pick_br_mas(u)

# Musical Center Som (WooCommerce): en el sitemap también van categorías y etiquetas; solo las fichas.
BR_SOURCES["musicalcentersom"]["pick"] = lambda u: "/produto/" in u and _pick_br(u)

BR_SOURCES["fenderbr"] = {"name": "Fender Brasil (Pride Music)", "discover": _discover_fender_br, "parse": _parse_fender_br, "fix": _br_fix,
                          "kind_url": br_kind, "pick": lambda u: not re.search(r"(?i)baixo|bass|amplificador|pedal|cabo|correia"
                                                                                r"|encordoamento|palheta|sistema-de-som|monitor|camiseta|bone", u)}


# Waltons (Dublín): la tienda de música grande de Irlanda, precios en euros y JSON-LD en la ficha.
IE_SOURCES["waltons"] = {"name": "Waltons", "sitemap": "https://www.waltons.ie/sitemap.xml", "kind_url": uk_kind,
                         "pick": lambda u: "/product/" in u
                         and (lambda s: s.startswith(tuple(b + "-" for b in _UK_BRANDS)))(u.rstrip("/").rsplit("/", 1)[-1])
                         and not UK_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)}
IE_SOURCES["musicmaker"] = {"name": "Music Maker", "sitemap": "https://www.musicmaker.ie/sitemap.xml",
                            "parse": _parse_musicmaker, "kind_url": uk_kind,
                            "pick": lambda u: (lambda s: s.startswith(tuple(b + "-" for b in _UK_BRANDS)))(u.rsplit("/", 1)[-1])
                            and not UK_SKIP.search(u.replace("-", " ")) and not NOT_PRODUCT.search(u)}


# --- Más tiendas del Reino Unido (libras) e Irlanda (euros) -------------------------------------------------
# Tiendas pequeñas y medianas: la categoría sale del breadcrumb (o del tipo de producto de Shopify) y, si no lo dice,
# del nombre (guitar_kind_for("en")). Las de segunda mano, fuera: no se comparan con las nuevas.
EN_HEADERS = {"Accept-Language": "en-GB,en;q=0.9"}
_EN_USED = re.compile(UK_USED.pattern + r"|2nd[- ]?hand|secondhand|pre-?loved|refurbished|open[- ]?box"
                      r"|ex[- ]?display", re.I)
_EN_NOT_GUITAR = re.compile(r"\bbass\b|ukulele|\buke\b|banjo|mandolin|bouzouki|violin|cello|\bharp\b|guitalele|guitarlele"
                            r"|\bkids?\b.*\bset\b|gift ?(card|voucher)|\bbook\b|tab edition|songbook|sheet music|\bdvd\b"
                            r"|\bacoustics\b|piano|keyboard|\bdrums?\b|saxophone|trumpet|xylophone|sousaphone|speakers?\b|cabinet"
                            r"|\bmixer|mixing|headphones|\bwedge\b|monitor|wireless|\bgrade \d|\bamp(lifier)?\b|\bcombo\b"
                            # Bajos que no dicen "bass" y cabezales de ampli
                            r"|stingray|\bray ?[345]\b|thunderbird|precision|jazz ?bass|\b[pj]-?bass|spectra|stiletto|\bb-?20\d"
                            r"|\b5150\b|\bhead\b"
                            r"|drum ?sticks|nylon tip|brushes|harmonica|lever nylon|octave|phosphor|megapack|sticky|\bpieces\b"
                            r"|clarinet|trombone|flute|cornet|euphonium|\bhorn\b|synth|interface|ear ?plugs|processor|subwoofer|\bfoam\b"
                            r"|normal tension|taylor swift|studies|hymns|guitar collection|\btee\b|t-shirt|socks|greeting card|tubing"
                            r"|washers|machine ?heads?|\bknobs?\b|recorder|resonator|lap steel"
                            r"|80/20|bronze (?:wound|strings|extra|light|medium|\d)|extra light|custom light|super light", re.I)
# Accesorios: los que empiezan por el accesorio ("Graphtech … saddle" no, pero "Fender Trem Cover" sí, por la palabra).
_EN_ACC = re.compile(r"^(?:\S+ ){0,3}(?:hard ?case|gig ?bag|case|strings?|string set|strap|stand|wall hanger|hanger|pickups?"
                     r"|pickup set|tuners?|machine heads|tuning (?:pegs|keys)|scratch ?plate|pickguard|bridge|saddles?|knobs?|nut"
                     r"|neck|body|loaded|wiring|harness|tremolo arm|whammy bar|capo|slide|picks?|plectrums?|polish|cleaner"
                     r"|humidifier|cable|lead|footswitch|pots?|switch|jack plate|output jack|truss rod)\b"
                     r"|\b(?:saddles?|switch|pots?|cover|switch ?plate|surround|machine heads?|truss rod|compatible|replacement"
                     r"|vibramate|bridge pins"
                     r"|cleaner|polish|glaze|footrest|stand|hanger|capo|strings|string set|lacquer|aerosol|simulator|preamp"
                     r"|soundhole|strap|tuners)\b|(?<!with )(?<!w/)(?<!w/ )\bpickup\b", re.I)
# "… with Gig Bag", "… Inc Hardcase": el estuche va con la guitarra; para clasificar, fuera.
_EN_WITH_CASE = re.compile(r"\s*(?:\bwith\b|\bw/|\binc\b\.?|\bincl\b\.?|\bincluding\b|\+|&|,)\s*(?:a\s+|free\s+)?(?:\S+\s+){0,3}?"
                           r"(?:hard ?case|hard ?shell case|gig ?bag|case|bag|hsc|ohsc)\b.*$", re.I)
# Marcas que son casi siempre eléctricas: si el nombre no dice más ("Epiphone Crestwood Custom"), eléctrica.
# (Sin Fender, Yamaha, Ibanez ni Cort: también venden amplis, bajos y sintes con nombres que no lo dicen.)
_EN_ELECTRIC_BRANDS = re.compile(r"^(?:squier|jackson|charvel|esp|ltd|schecter|evh|sterling|chapman|music man|ernie ball music man"
                                 r"|gretsch|prs|epiphone|gibson|g&l|suhr|tokai|danelectro|reverend|patina|eastcoast|kramer|dean"
                                 r"|solar|rickenbacker(?! 4\d{3}))\b", re.I)
_EN_ACOUSTIC_BRANDS = re.compile(r"^(?:lowden|martin|taylor|furch|maton|larrivee|lakewood|breedlove|morris|seagull|faith|sigma"
                                 r"|takamine|yairi|k\. ?yairi|collings|santa cruz|atkin|art ?& ?lutherie|simon ?& ?patrick|norman"
                                 r"|cole clark|alvarez|washburn heritage)\b", re.I)
_EN_ACOUSTIC_WORDS = re.compile(r"acoustic|classical|nylon|dreadnought|jumbo|parlou?r|auditorium|concert|\bom\b|hummingbird|dove"
                                r"|masterbilt|texan|frontier|angelus|songmaker|j-?45|sj-?200|\bcd-?\d|\bfg\w*\d|\bapx|\bga\d|\bac\d", re.I)


def en_kind(crumbs, url="", name=""):
    """'electrica', 'acustica', 'clasica' o None para las tiendas británicas e irlandesas pequeñas."""
    name = _EN_WITH_CASE.sub("", html.unescape(html.unescape(name or ""))).strip()
    crumbs = [html.unescape(html.unescape(c)) for c in crumbs or [] if c]  # "&amp;#8220;" no es un "amp"
    if len(crumbs) > 1 and len(crumbs[-1]) > 15 and (crumbs[-1].lower() in name.lower() or name.lower() in crumbs[-1].lower()):
        crumbs = crumbs[:-1]  # el último es la propia ficha
    bare = re.sub(r"^(?:new|genuine|official)\s+", "", name, flags=re.I)
    if _EN_USED.search(" / ".join(crumbs + [name, url])) or _EN_NOT_GUITAR.search(name) or _EN_ACC.search(bare) \
            or re.search(r"(?<!\d )(?<!\d-)\bstrings?\b|\bneck\s*(?:$|for\b|with scallop)|replacement neck", name, re.I):
        return None
    if re.search(r"semi[- ]?acoustic|semi[- ]?hollow|hollow ?body|thinline|archtop electric", name, re.I):
        return "electrica"
    if re.search(r"\bclassic(al)? guitar|nylon[- ]string guitar", name, re.I):
        return "clasica"
    if re.search(r"\b(ovation|applause|redondo|newporter|malibu)\b", name, re.I) and not re.search(r"\belectric guitar", name, re.I):
        return "acustica"
    leaf = re.sub(r"guitars? (?:&|and) bass(es)?", "", " / ".join(crumbs[-2:]).lower())
    if UK_SKIP.search(leaf) or _EN_NOT_GUITAR.search(leaf.replace("acoustics", "")):  # "Gibson Acoustics"
        return None
    # Shopify: el tipo de producto a veces es solo "Electric" / "Acoustic Guitar".
    text = " ".join(crumbs).lower()
    if re.search(r"guitar", text) or re.fullmatch(r"(electric|acoustic|electro[- ]acoustic|classical)s?", text):
        k = uk_kind(crumbs + ["Guitars"], url, name)
        if k:
            return k
    k = guitar_kind_for("en")([], url, name)
    if k:
        return k
    if _EN_ACOUSTIC_BRANDS.search(bare) and not re.search(r"\belectric guitar|\bbass", name, re.I):
        return "acustica"
    if _EN_ELECTRIC_BRANDS.search(bare) and not _EN_ACOUSTIC_WORDS.search(name):
        return "electrica"
    return None


_EN_PICK = pick_for("en")


def _pick_en(shopify=False, path=None):
    """Fichas con una palabra de guitarra en la URL o que empiezan por una marca de guitarras ("prs-se-custom-24")."""
    def pick(u):
        if shopify and not re.match(r"https?://[^/]+/products/[^/?#]+$", u):  # sin las copias por idioma (/ja/products/…)
            return False
        if path and not re.search(path, u):
            return False
        slug = re.sub(r"\.(html?|asp|php)$", "", u.rstrip("/").rsplit("/", 1)[-1].lower()).replace("_", "-")
        slug = re.sub(r"^\d+-", "", slug)  # PrestaShop: "13369-martin-dx2el…"
        text = slug.replace("-", " ")
        where = "/" + u.split("://", 1)[-1].split("/", 1)[-1]  # sin el dominio ("themusicoutlet.ie" no es un outlet)
        if _EN_USED.search(text) or _EN_NOT_GUITAR.search(text) or NOT_PRODUCT.search(where) or _GEN_NOT_PRODUCT.search(where):
            return False
        return _EN_PICK(where.rstrip("/").rsplit("/", 1)[0] + "/" + slug) or \
            (slug.startswith(tuple(b + "-" for b in _UK_BRANDS)) and not UK_SKIP.search(text)
             and not ES_SKIP.search(_to_es(text, "en")))
    return pick


def _shopify_url(cur, json_feed=True):
    """La ficha de Shopify con la moneda de la tienda: sin "?currency=" sale en la del visitante (dólares desde GitHub)."""
    return lambda u: u.split("?")[0].rstrip("/") + (".json" if json_feed else "") + f"?currency={cur}"


def _parse_shopify_json(soup, text):
    """Ficha de Shopify en JSON (/products/<handle>.json): precio en la moneda de la tienda (el HTML lo da en la del
    visitante, que desde GitHub es dólares), EAN (barcode) y tipo de producto, que hace de categoría."""
    try:
        p = json.loads(text)["product"]
    except (ValueError, KeyError, TypeError):
        return {"crumbs": []}
    variants = p.get("variants") or []
    def sold_out(v):
        return v.get("inventory_management") == "shopify" and v.get("inventory_policy") == "deny" \
            and isinstance(v.get("inventory_quantity"), int) and v["inventory_quantity"] <= 0
    v = next((v for v in variants if not sold_out(v)), variants[0] if variants else None)
    if not v or not v.get("price"):
        return {"crumbs": [p.get("product_type") or ""]}
    tags = p.get("tags") or ""
    tags = ", ".join(tags) if isinstance(tags, list) else tags
    crumbs = [c for c in [p.get("product_type")] if c]
    if _EN_USED.search(tags):
        crumbs.append("Used")
    ean = normalize_id(v.get("barcode") or "")
    ean = ean if ean.isdigit() and len(ean) in (12, 13, 14) and len(ean.lstrip("0")) >= 11 else None  # no códigos internos
    in_stock = (not sold_out(v)) if "inventory_quantity" in v else None
    vendor = p.get("vendor") or ""
    if vendor.lower() not in (p.get("title") or "").lower():  # IT Music pone su nombre de vendedor
        vendor = _brand_from_name(p.get("title"))
    return {"crumbs": crumbs, "name": html.unescape(p.get("title") or "").strip(), "brand_raw": vendor,
            "price": float(v["price"]), "currency": v.get("price_currency") or "GBP", "in_stock": in_stock,
            "image": (p.get("image") or {}).get("src"), "ean": ean}


def _parse_en(cur):
    """JSON-LD (también el que no es JSON válido) o, si no, microdatos; la moneda de la tienda si la ficha no la dice."""
    def parse(soup, text):
        data = _parse_jsonld(soup, "en")
        if not data.get("price"):
            loose = _parse_ld_loose(soup, text)
            if loose.get("price"):
                if not re.search(r'"priceCurrency"', text):
                    loose["currency"] = cur
                data = {**loose, "crumbs": data.get("crumbs") or loose.get("crumbs", [])}
        if not data.get("price"):
            micro = _parse_microdata(soup, text)
            if micro.get("price"):
                if not soup.find(attrs={"itemprop": "priceCurrency"}):
                    micro["currency"] = cur
                data = {**micro, "crumbs": data.get("crumbs") or micro.get("crumbs", [])}
        if data.get("price") and not data.get("currency"):
            data["currency"] = cur
        if isinstance(data.get("brand_raw"), list):  # Rockem: [{"@type": "Brand", "name": "Stagg"}]
            first = (data["brand_raw"] or [None])[0]
            data["brand_raw"] = first.get("name") if isinstance(first, dict) else first
        if data.get("price") and not data.get("brand_raw"):
            data["brand_raw"] = _brand_from_name(data.get("name"))
        if data.get("name"):
            data["name"] = html.unescape(html.unescape(data["name"])).strip()  # "Barnes &amp;amp; Mullins"
            data["name"] = re.sub(r"\s+-\s+[\w.]+\.(?:ie|co\.uk|com)$", "", data["name"])  # "… - soundshop.ie"
        ean = str(data.get("ean") or "")
        if ean and not (ean.isdigit() and len(ean) in (12, 13, 14) and len(ean.lstrip("0")) >= 11):
            data["ean"] = None  # "EASTMANAC108CELTD" y códigos internos
        return data
    return parse


def _parse_savins(soup, text):
    """Savins (PrestaShop, Dublín): microdatos sueltos; precio en el bloque .product-prices, breadcrumb en microdatos."""
    h1 = soup.select_one("h1[itemprop=name]") or soup.find("h1")
    price = soup.select_one(".product-prices [itemprop=price]")
    bc = soup.select_one("[itemtype*=BreadcrumbList]")
    crumbs = [x.get_text(" ", strip=True) for x in bc.select("[itemprop=name]")] if bc else []
    crumbs = [c for c in crumbs[:-1] if c.lower() != "home"]
    if not h1 or not price or not price.get("content"):
        return {"crumbs": crumbs}
    name = h1.get_text(" ", strip=True)
    avail = soup.select_one(".product-prices [itemprop=availability]")
    img = soup.select_one('meta[property="og:image"]')
    return {"crumbs": crumbs, "name": name, "brand_raw": _brand_from_name(name), "price": float(price["content"]),
            "currency": "EUR", "in_stock": ("instock" in avail.get("href", "").lower()) if avail else None,
            "image": img.get("content") if img else None, "ean": None}


def _ror_fix(data, text):
    """ROR: el breadcrumb arrastra los filtros de la ficha ("… / Acoustic Guitars / Strings / 6 / Brand / Martin")."""
    crumbs = list(data.get("crumbs") or [])
    if "Brand" in crumbs:
        crumbs = crumbs[:crumbs.index("Brand")]
    data["crumbs"] = [c for c in crumbs if c not in ("Strings", "Category") and not c.isdigit()]
    return data


def _en_store(name, sitemap, cur, shopify=False, path=None, sub=None, json_feed=True, **extra):
    src = {"name": name, "sitemap": sitemap, "kind_url": en_kind, "pick": _pick_en(shopify, path)}
    if shopify:
        # El .json de la ficha (precio, EAN y tipo de producto) salvo si robots.txt lo prohíbe (Music Street): el HTML.
        src.update(page_url=_shopify_url(cur, json_feed), parse=_parse_shopify_json if json_feed else _parse_en(cur),
                   sub=sub or (lambda l: bool(re.match(r"https?://[^/]+/sitemap_products_", l))))
    else:
        src["parse"] = _parse_en(cur)
        if sub:
            src["sub"] = sub
    src.update(extra)
    return src


for _id, _name, _sm, _kw in [
        ("peach", "Peach Guitars", "https://www.peachguitars.com/sitemap.xml", {"path": r"\.htm$"}),
        ("musicstreet", "Music Street", "https://www.musicstreet.co.uk/sitemap.xml", {"shopify": True, "json_feed": False}),
        ("richtone", "Richtone Music", "https://richtonemusic.co.uk/xmlsitemap.php", {"sub": lambda l: "product" in l}),
        ("gpas", "Guitars Pedals Amps & Stuff", "https://guitarspedalsampsandstuff.co.uk/sitemap_index.xml",
         {"path": r"/product/", "sub": lambda l: "product" in l}),
        ("absolutemusic", "Absolute Music", "https://www.absolutemusic.co.uk/xmlsitemap.php", {"sub": lambda l: "product" in l}),
        ("projectmusic", "Project Music", "https://projectmusic.net/sitemap.xml", {"path": r"-p\.asp$"}),
        ("rguitars", "R Guitars", "https://rguitars.co.uk/sitemap.xml", {"shopify": True}),
        ("fairdeal", "Fair Deal Music", "https://www.fairdealmusic.co.uk/sitemap.xml", {"shopify": True}),
        ("achamilton", "A.C. Hamilton", "https://www.achamilton.co.uk/wp-sitemap.xml",
         {"path": r"/product/", "sub": lambda l: "product" in l}),
        ("guitarmania", "Guitar Mania", "https://www.guitarmania.co.uk/sitemap_index.xml",
         {"path": r"/product/", "sub": lambda l: "product" in l}),
        ("promenade", "Promenade Music", "https://www.promenademusic.co.uk/sitemap_index.xml", {"sub": lambda l: "product" in l}),
        ("reidys", "Reidys", "https://shop.reidys.com/sitemap.xml", {"shopify": True}),
        ("matchetts", "Matchetts Music", "https://matchettsmusic.com/sitemap.xml", {"shopify": True}),
        ("forsyths", "Forsyths", "https://www.forsyths.co.uk/sitemap.xml", {"path": r"/guitars/"}),
        ("astrings", "A Strings", "https://astrings.co.uk/sitemap.xml", {"shopify": True}),
        ("londonguitarstudio", "London Guitar Studio", "https://www.londonguitarstudio.com/sitemap.xml", {"path": r"/p/"}),
        ("guitarbitz", "Guitarbitz", "https://www.guitarbitz.com/sitemap.xml", {"shopify": True}),
        ("giggear", "Gig Gear", "https://www.giggear.co.uk/sitemap.xml", {}),
        ("suttonmusic", "Sutton Music", "https://suttonmusic.co.uk/sitemap.xml", {"shopify": True}),
        ("themusicbank", "The Music Bank", "https://themusicbank.co.uk/sitemap.xml", {"shopify": True}),
        ("wunjo", "Wunjo Guitars", "https://www.wunjoguitars.com/sitemap.xml", {"shopify": True}),
        ("musicbros", "Music Bros", "https://www.musicbros.co.uk/sitemap.xml", {"shopify": True}),
        ("randtmusic", "R&T Music", "https://randtmusic.co.uk/sitemap.xml", {"shopify": True}),
        ("rockem", "Rockem Music", "https://rockemmusic.com/sitemap.xml", {"path": r"/product/"}),
        ("parkland", "Parkland Music", "https://www.parklandmusicstore.co.uk/sitemap.xml", {"shopify": True}),
        ("jamesmusic", "James Music", "https://www.james-music.co.uk/sitemap.xml", {"shopify": True}),
        ("nessmusic", "Ness Music", "https://nessmusic.co.uk/sitemap.xml", {"shopify": True}),
        ("soundgarden", "The Sound Garden", "https://www.thesoundgarden.co.uk/sitemap.xml", {"shopify": True}),
        ("modernmusic", "Modern Music", "https://modernmusic.co.uk/sitemap.xml", {}),
        ("paisley", "Paisley Music", "https://www.paisleymusic.com/sitemap.xml", {}),
        ("millers", "Millers Music", "https://millersmusic.co.uk/sitemap.xml", {"shopify": True})]:
    UK_SOURCES[_id] = _en_store(_name, _sm, "GBP", **_kw)

for _id, _name, _sm, _kw in [
        ("xmusic", "X Music", "https://xmusic.ie/sitemap.xml", {"path": r"/product/"}),
        ("musicminds", "Music Minds", "https://www.musicminds.ie/sitemap.xml", {"path": r"\.html$"}),
        ("savins", "Savins", "https://www.savins.ie/1_index_sitemap.xml", {"path": r"/\d+-[^/]+\.html$", "parse": _parse_savins}),
        ("someneck", "Some Neck Guitars", "https://www.someneckguitars.com/sitemap.xml", {"shopify": True}),
        ("promusica", "Pro Musica", "https://promusica.ie/sitemap_index.xml", {"path": r"/product/"}),
        ("soundshop", "Sound Shop", "https://www.soundshop.ie/sitemap_index.xml", {"path": r"/shop/"}),
        ("everest", "Everest Music", "https://everestmusic.com/sitemap.xml", {}),
        ("musicoutlet", "The Music Outlet", "https://themusicoutlet.ie/wp-sitemap.xml", {"path": r"/product/"}),
        ("ror", "ROR Music", "https://www.ror.ie/sitemap.xml", {"fix": _ror_fix}),
        ("itmusic", "IT Music", "https://itmusic.ie/sitemap.xml", {"shopify": True})]:
    IE_SOURCES[_id] = _en_store(_name, _sm, "EUR", **_kw)


# Gear4music: desde GitHub sus webs de cada país se leen sin problema (no desde el entorno de pruebas). Del sitemap,
# solo el departamento de guitarras y bajos; la categoría sale del breadcrumb de la ficha (JSON-LD con precio y EAN).
def _gear4music(base, kind):
    # Las fichas acaban en su código ("…/Fender-Player-II-Stratocaster-RW/6RC1"); lo demás son categorías y marcas.
    return {"name": "Gear4music", "sitemap": f"{base}/sitemap.xml", "sub": lambda u: "guitar_bass" in u, "kind": kind,
            "pick": lambda u: bool(re.search(r"/[0-9A-Z]{3,6}$", u)) and not re.search(r"(?i)bass|bajo|basse|basso|ukulele", u)
            and not NOT_PRODUCT.search(u)}


SOURCES["gear4music"] = _gear4music("https://www.gear4music.es", _only("electrica", _is_electric))
ACOUSTIC_SOURCES["gear4music"] = _gear4music("https://www.gear4music.es", acoustic_kind)
FR_SOURCES["gear4music"] = _gear4music("https://www.gear4music.fr", fr_kind)
IT_SOURCES["gear4music"] = _gear4music("https://www.gear4music.it", it_kind)
DE_SOURCES["gear4music"] = _gear4music("https://www.gear4music.de", de_kind)
NL_SOURCES["gear4music"] = _gear4music("https://www.gear4music.nl", nl_kind)


# --- Alemania, Austria y Países Bajos: tiendas de las listas de distribuidores de las marcas -----------------------
# Sin categorías fiables: el tipo sale del nombre y de la URL (guitar_kind_for, en alemán o neerlandés y en inglés), con un
# filtro más de accesorios en esos idiomas. "Con estuche", "mit Tonabnehmer"… describen la guitarra: se quitan antes.
_DACH_WITH = re.compile(r"(?:\b(?:inkl\.?|incl\.?|inklusive|inclusief|including|mit|with|w/|met|und|and|en|plus)\s+|\+\s*)"
                        r"(?:(?:hard|soft|form|gig|deluxe|original|premium|luxe|tolex|fender|gibson|ibanez|vintage)[\s-]?)*"
                        r"(?:koffer|case|gig-?bag|tasche|hoes|etui|bag|tonabnehmer|pick-?ups?|element|elektronik|electronics"
                        r"|tuner|stimmgerät|eq)\w*", re.I)
_DACH_SKIP = re.compile(
    r"saiten(?!instrument)|\bsaite\b|\bstrings\b|string ?set|snaren|\bsnaar\b|(?<![\w-])0?\d{2}-\d{2,3}(?![\w-])"
    r"|koffer|gig-?bag|tasche|hoes\b|hoezen|\bcases?\b|\bbag\b|\betui|gurt\b|gurte\b|gitarrengurt|gitarregurt|gitaarband|draagriem|\bstraps?\b"
    r"|tonabnehmer|\bpick-?ups?\b|humbucker|single-?coil|mechanik|mechaniek|machine ?heads?|\bsattel|\bsteg\b|schlagbrett"
    r"|slagplaat|pickguard|ersatzteil|onderde[el]|replacement part|accessor|\bparts?\b|\bbridge\b|brücke|tailpiece|vibrato unit|tremolo arm|vibratohebel"
    r"|ukulele|ukelele|zither|guitarlele|guitalele|mandolin|banjo|bouzouki|\bsaz\b|(?<!am)bass(?!wood|ador)|bässe|\b[45]-?str\b|\b[45]-?saiter|\b[45]-?snarig|\bbas\b|basgita"
    r"|ständer|staender|statief|standaard|\bstand\b|wandhalter|wall ?hanger|hanger|halter|kapodaster|\bcapo\b"
    r"|plektr|plectr|\bpicks?\b|stimmger|stemapparaat|\btuner\b|verstärker|verstaerker|versterker|\bamp\b|combo\b"
    r"|kabel|\bcable\b|pflege|reinig|polish|\bset\b|starter-?set|startersset|bundle|\bpack\b|paket|\bkit\b"
    r"|gutschein|cadeaubon|gift ?card|kopie von|lehrbuch|gitarrenschule|schule\b|songbook|\bnoten\b|\bbuch\b|\bboek\b"
    r"|methode|gebraucht|tweedehands|occasion|b-?ware|b-?stock|vorführ|ausstellung|\bdemo\b|ex-?demo|\bused\b"
    r"|pre-?owned|second ?hand|\bmiete|\bhuur|effekt|pedal|preamp|\beffect|looper|hocker|\bstool|\bstuhl|fußbank|voetbank"
    r"|footrest|#\d{5,}|\b19[4-9]\d$|cradle|cajon|marcus miller|gitarrenbox|topteil|cabinet|\bknobs?\b|\bswitch\b|schalter|\bpoti\b|bürste|brush|besen|\bcover\b|seeburg|klavar|harmonium|\bblf\b|\bpiano|klavier|flügel|lautsprecher|luidspreker|speaker|stütze|stuetze|befeucht|humidif|bevochtig|sticker|poster|shirt|hoodie|socken|socks|sokken|schild\b|magnet|anhänger|schlüssel|keychain|sleutelhanger|miniatur|tasse|becher|\btasse|\bmug\b|\bcd\b(?![- ]?\d)"
    r"|\bdvd\b|kopfhörer|headphone|mikrofon|microfoon|microphone|wireless|interface|ersatz|zubehör|zubehoer|accessoir"
    r"|reparatur|reparatie|einstell|service|versicherung|\bsaitenhalter|slide\b|bottleneck|\bnut\b|\bsaddle"
    # "… für E-Gitarre", "… voor klassieke gitaar": es para la guitarra, no la guitarra
    r"|\b(?:für|fuer|for|voor)\b[^,]{0,25}(?:gitarren?|guitars?|gita(?:a|re)n?)\b"
    # Marcas que solo hacen accesorios (Ernie Ball sí hace guitarras: las Music Man)
    r"|^(?:d'?\s?addario|elixir|dunlop|hercules|k\s?&?\s?m|gator|hiscox|rockcase|rockbag|seymour duncan|dimarzio|emg|schaller"
    r"|gotoh|kyser|shubb|planet waves|pickboy|ernie ball(?! music ?man)|rotosound|savarez|hannabach|la bella|thomastik|gewa (?:pure"
    r"|economy|prestige|premium|flex)|fishman|boss|tc electronic|nux|righton|levy'?s|fender (?:case|gig ?bag|strap|strings"
    r"|picks?|cable)|ibanez (?:powerpad|gig ?bag|case))\b", re.I)

_DACH_GROUP = re.compile(r"(?:git\w*|b[aä]ss\w*|basgita\w*)(?:(?:\s*(?:&|und|en|and|/|,|-|\+)\s*)+(?:git\w*|b[aä]ss\w*|baesse|strings"
                         r"|zubeh\w*|basgita\w*|accessoires|amps?|verst[aä]rker|versterkers|effekte))+", re.I)
# Categorías de otros instrumentos (Yamaha "C2X" es un piano de cola, no una clásica).
_DACH_OTHER = re.compile(r"tasteninstr|klavier|flügel|\bpiano|keyboard|blasinstr|streichinstr|schlagzeug|\bdrums?\b|percussion"
                         r"|orgel|akkordeon|zither|violin|\bviola|cello|toetsinstr|blaasinstr|strijkinstr|slagwerk|\bdj\b"
                         r"|beschallung|recording|bladmuziek|\bnoten\b|cajon|\baudio\b|lautsprecher|luidspreker|speaker", re.I)
# Piezas sueltas: "Fender Stratocaster Neck", "Gibson SG Body" (no "… Roasted Maple Neck" al final de un nombre largo).
_DACH_PART = re.compile(r"^(?:\S+\s+){0,3}(?:neck|body|hals|korpus)\b(?![\s-]*(?:thru|through))", re.I)
# El tipo según la categoría de la tienda (de la más concreta a la más general); las semiacústicas son eléctricas.
_DACH_CAT_TYPES = [("electrica", r"halb[- ]?akust|semi[- ]?akust|half[- ]?akoest|semi[- ]?hollow|hollow|jazzgitarr|archtop"),
                   ("clasica", r"konzert-?gitarr|klassi|flamenc|nylon|concertgita|spaanse"),
                   ("acustica", r"western|akusti|akoesti|acoustic|\bfolk|dreadnought|jumbo|parlou?r|grand auditorium"),
                   ("electrica", r"\be-?gitarr|elektrische gita|electric|elektrisch|single-?cut|double-?cut|solid-?body"
                                 r"|superstrat|\b[stj]-style|\bst-|\bt-modell|offset|headless|\blp-modell")]
# Marcas que solo (o casi solo) hacen eléctricas: "PRS SE CE 24", "Duesenberg Julietta" no dicen qué son.
_ELECTRIC_ONLY = re.compile(r"^(?:prs|paul reed smith|duesenberg|spira|jet|patina|chapman|suhr|tom anderson|nik huber|schecter|jackson"
                            r"|charvel|evh|sterling|hagstrom|rickenbacker|reverend|kiesel|strandberg|mayones|solar|fgn|fujigen"
                            r"|tokai|squier|music ?man|ernie ball music ?man|esp|ltd|e-ii|g&l|friedman|knaggs|gretsch|danelectro"
                            r"|kramer|ormsby|aristides|vola|maybach|harley benton)\b", re.I)
_NOT_ELECTRIC = re.compile(r"acoustic|akusti|akoest|western|dreadnought|jumbo|parlou?r|konzert|concert|klassi|nylon|angelus|tonare"
                           r"|\bse [apt]\d0|\b[apt]20e?\b|jim dandy|rancher|falcon jr|\bcustom 4\d\b", re.I)


def _dach_cat_type(crumbs):
    for c in reversed(crumbs or []):
        for kind, rx in _DACH_CAT_TYPES:
            if re.search(rx, c.lstrip("#"), re.I):
                return kind
    return None


def dach_kind(lang):
    """Clasificador de las tiendas alemanas, austriacas y neerlandesas (lang: "de" o "nl"; también en inglés). Decide, por
    este orden, lo que diga el nombre ("Konzertgitarre"), la categoría de la tienda, el modelo (guitar_kind_for) y la marca."""
    base = guitar_kind_for(lang + "+en")

    def kind(crumbs, url="", name=""):
        name = " ".join(_DACH_WITH.sub(" ", name or "").split())
        slug = _DACH_WITH.sub(" ", _dach_slug(url).replace("-", " ").replace("_", " "))
        # Las categorías también descartan ("E-Bässe", "Zubehör", "Flügel"), pero no "Gitarren & Bässe". Las etiquetas de
        # Shopify ("#…") solo si son de otro instrumento: traen de todo ("hardcase", "outlet"…).
        cats = [_DACH_GROUP.sub(" ", _DACH_WITH.sub(" ", c)) for c in crumbs or [] if not c.startswith("#")]
        if _DACH_SKIP.search(name) or _DACH_PART.search(name) or _DACH_SKIP.search(slug) \
                or any(_DACH_SKIP.search(c) for c in cats) or any(_DACH_OTHER.search(c) for c in crumbs or []):
            return None
        said = _to_es(name, lang + "+en")
        if re.search(r"guitarra clásica|guitarra flamenca|flamenca\W+guitarra", said):
            return "clasica"
        # "Semi-akoestische gitaar" es una electroacústica, salvo en semihuecas eléctricas ("Gretsch G5422TG", "Epiphone ES-335")
        if re.search(r"semi[- ]?ako", name, re.I) and (_ELECTRIC_ONLY.search(name) or re.search(
                r"(?i)epiphone|gibson (?:es|cs)|ibanez (?:as|af|am|sa)\d|\bes-?\d{3}|casino|hollow|archtop|thinline", name)):
            return "electrica"
        if re.search(r"guitarra acústica|electroacústica", said) and "eléctrica" not in said:
            return "acustica"
        if re.search(r"guitarra eléctrica", said) and not re.search(r"acústica|clásica", said):
            return "electrica"
        kind = _dach_cat_type(crumbs) or base(crumbs, "x/" + slug.replace(" ", "-"), name)
        if not kind and _ELECTRIC_ONLY.search(name) and not _NOT_ELECTRIC.search(name + " " + " ".join(crumbs or [])):
            kind = "electrica"
        return kind
    return kind


def _dach_slug(url):
    """Lo último de la URL con el nombre: sin el número de artículo (".../e-gitarre-xy/0054601"), ni ".html", ni "-p-305092"."""
    parts = [p for p in re.sub(r"[?#].*$", "", url).rstrip("/").split("/") if p]
    while len(parts) > 3 and re.fullmatch(r"[0-9]+(?:-[0-9a-f]{32})?|[0-9A-Z]{5,}|[0-9a-f]{32}", parts[-1]):
        parts.pop()
    slug = re.sub(r"\.(html?|php)$", "", parts[-1] if parts else "")
    return re.sub(r"-p-\d+$|_\d{5,}$|-\d{5,}$|^p\d+_", "", slug)


# Marcas de guitarras para preseleccionar URLs sin "Gitarre" (Yamaha, Gewa y Stagg hacen de todo: solo con su modelo).
_DACH_BRANDS = tuple(b.replace("-", " ") + " " for b in tuple(x for x in _UK_BRANDS if x not in ("gewa", "stagg")) + ("harley-benton", "hora", "lakewood", "furch",
                                                                        "hanika", "duesenberg", "warwick", "framus", "fgn",
                                                                        "maybach", "patina", "richwood", "aria", "tokai",
                                                                        "spira", "jet", "suhr", "tom-anderson", "nik-huber",
                                                                        "rickenbacker", "eko", "lag", "la-mancha", "juan-salvador",
                                                                        "valencia", "sx", "gretsch", "d-angelico", "eastman"))


def _pick_dach(lang, base, path=None, shopify=False):
    """Fichas de una tienda: de su dominio (algunos sitemaps traen espejos y webs de pruebas), con la ruta de las fichas
    (path) y que por la URL parezcan una guitarra o empiecen por una marca de guitarras."""
    base = base.rstrip("/")
    rx = re.compile(path) if path else None

    def pick(u):
        if not u.startswith(base + "/") or (rx and not rx.search(u)) or (shopify and not re.match(re.escape(base) + r"/products/", u)):
            return False
        if NOT_PRODUCT.search(u) or _GEN_NOT_PRODUCT.search(u.replace("/products/", "/")):
            return False
        slug = _DACH_WITH.sub(" ", _dach_slug(u).replace("-", " ").replace("_", " ").lower())
        es = _to_es(slug, lang + "+en")
        if _DACH_SKIP.search(slug) or ES_SKIP.search(es):
            return False
        if slug.startswith("yamaha "):
            return bool(_ES_PICK.search(es) or _YAMAHA_GUITAR.search(slug))
        return bool(_ES_PICK.search(es)) or slug.startswith(_DACH_BRANDS)
    return pick


_YAMAHA_GUITAR = re.compile(r"^yamaha (?:pacifica|revstar|rs[sep]?|pac|c|cg|cx|ncx|ntx|cs|gc|f|fs|fg|fgx|fsx|apx|cpx|ll|ls|lj|ac"
                            r"|aj|storia|jr|slg|csf|tag|gl)\s?\d")


def _parse_shopware(soup, text):
    """Shopware 6 sin JSON-LD de producto: microdatos (precio, moneda, EAN y marca) del bloque del producto; el nombre, del h1
    (el primer itemprop=name de la página es la marca o el menú)."""
    crumbs = []
    for el in soup.select('[itemtype$="BreadcrumbList"] [itemprop=name]'):
        c = el.get_text(" ", strip=True) or el.get("content") or ""
        if c and (not crumbs or crumbs[-1] != c):
            crumbs.append(c)
    product = soup.find(attrs={"itemtype": re.compile(r"schema\.org/Product$")})
    h1 = soup.select_one("h1.product-detail-name") or soup.find("h1")
    if not product or not h1:
        return {"crumbs": crumbs}

    def prop(node, name):
        el = node.find(attrs={"itemprop": name}) if node else None
        if el is None:
            return None
        return (el.get("content") or el.get("href") or el.get_text(" ", strip=True) or "").strip() or None

    offer = product.find(attrs={"itemprop": "offers"}) or product
    price = parse_price(prop(offer, "price") or prop(offer, "lowPrice"))
    name = " ".join(h1.get_text(" ", strip=True).split())
    if crumbs and crumbs[-1].lower() == name.lower():
        crumbs = crumbs[:-1]
    if not price or not name:
        return {"crumbs": crumbs}
    brand = product.find(attrs={"itemprop": "brand"})
    brand = (brand.get("content") or prop(brand, "name") or brand.get_text(" ", strip=True)) if brand else None
    ean = normalize_id(prop(product, "gtin13") or prop(product, "gtin") or prop(product, "gtin14") or "")
    avail = prop(offer, "availability")
    image = soup.find("meta", attrs={"property": "og:image"})
    return {"crumbs": crumbs, "name": name, "brand_raw": (brand or "").strip() or _brand_from_name(name), "price": price,
            "currency": normalize_currency(prop(offer, "priceCurrency")) or "EUR", "in_stock": parse_availability(avail),
            "image": image.get("content") if image else None, "ean": ean if len(ean) in (12, 13, 14) else None}


def _parse_shopify_json(soup, text):
    """Ficha de Shopify leída en /products/<handle>.json?currency=EUR: desde GitHub (EE. UU.) algunas tiendas dan el precio
    en dólares si no se pide la moneda (Dirk Witte); trae el EAN (barcode), el tipo de producto y las etiquetas, que hacen
    de categoría."""
    p = json.loads(text).get("product") or {}
    variants = [v for v in p.get("variants") or [] if parse_price(v.get("price"))]
    crumbs = [p["product_type"]] if p.get("product_type") else []
    if not variants or not p.get("title"):
        return {"crumbs": crumbs}
    tags = p.get("tags") or ""
    tags = ", ".join(tags) if isinstance(tags, list) else tags
    crumbs = ([f"#{tags}"] if tags else []) + crumbs
    v = min(variants, key=lambda v: parse_price(v["price"]))
    ean = normalize_id(v.get("barcode") or "")
    image = (p.get("image") or {}).get("src") or next((i.get("src") for i in p.get("images") or []), None)
    return {"crumbs": crumbs, "name": p["title"], "brand_raw": p.get("vendor"), "price": parse_price(v["price"]),
            "currency": normalize_currency(v.get("price_currency")) or "EUR", "in_stock": None, "image": image,
            "ean": ean if len(ean) in (12, 13, 14) and ean.isdigit() else None}


def _shopify(name, base, lang):
    return {"name": name, "sitemap": f"{base}/sitemap.xml", "parse": _parse_shopify_json, "kind_url": dach_kind(lang),
            "fetch": lambda u: u.split("?")[0] + ".json", "pick": _pick_dach(lang, base, shopify=True), "fix": _dach_fix,
            "shop": {"base": base, "lang": lang + "+en", "shopify": True}}


def _real_ean(ean):
    """EAN/UPC con dígito de control correcto, que no sea de uso interno (prefijo 2) ni un número de la tienda con ceros."""
    e = re.sub(r"\D", "", str(ean))
    e = e.zfill(13) if len(e) == 12 else e
    if len(e) not in (13, 14) or e.startswith("2") or re.match(r"^0?\d0{5}", e):
        return False
    digits = [int(c) for c in e]
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits[:-1])))
    return (10 - total % 10) % 10 == digits[-1]


def _dach_fix(data, text):
    """Limpieza común: entidades HTML en nombre y categorías, variables de plantilla sin rellenar ("~PR-Hersteller_StripHtml~",
    Musik Dressler), el nombre de la tienda al final ("… - KEY-WI MUSIC") y la marca, si falta, del nombre. En WooCommerce,
    las categorías del producto van en las clases de su bloque ("product_cat-e-gitarren")."""
    name = re.sub(r"~[^~\s]*~\s*", "", html.unescape(data.get("name") or ""))
    data["name"] = re.sub(r"\s+[-–|]\s+key-wi music$", "", name.strip(), flags=re.I) or data.get("name")
    brand = re.sub(r"~[^~\s]*~", "", data.get("brand_raw") or "").strip()
    # La tienda o el distribuidor como marca ("Music All In", "algam DACH GmbH"): fuera, también del principio del nombre.
    if re.fullmatch(r"(?i)music all in|tfoa|key-wi(?: music)?|algam dach gmbh|musifacts", brand):
        data["name"] = re.sub(rf"^{re.escape(brand)}\s+", "", data["name"], flags=re.I)
        brand = ""
    data["brand_raw"] = brand or (_brand_from_name(data["name"]) if data.get("name") else None)
    if data.get("ean") and not _real_ean(data["ean"]):
        data["ean"] = None  # códigos internos de la tienda ("1", "7000000086424", "1000000083644")
    tag = re.search(r'<(?:div|article)\b[^>]*\bid="product-\d+"[^>]*>', text)
    cats = re.findall(r"\bproduct_cat-([a-z0-9-]+)", tag.group(0)) if tag else []
    crumbs = [html.unescape(c) for c in data.get("crumbs") or []] + cats
    if not crumbs and text.lstrip()[:1] == "<":
        # Sin breadcrumb en JSON-LD: el de microdatos (Magna Music) o la categoría de su analítica (Klundert, "item_category").
        soup = BeautifulSoup(text, "html.parser")
        for el in soup.select('[itemtype$="BreadcrumbList"] [itemprop=name]'):
            c = el.get_text(" ", strip=True) or el.get("content") or ""
            if c and c not in crumbs:
                crumbs.append(c)
        if not crumbs:
            crumbs = [html.unescape(m) for m in re.findall(r'"item_category\d?"\s*:\s*"([^"]{2,60})"', text)[:3]]
    data["crumbs"] = crumbs
    return data


def _path_crumbs(url):
    """La ruta de la URL como categorías (".../gitarre-bass/gitarre/e-gitarre/19493/…")."""
    return [p for p in re.sub(r"^https?://[^/]+", "", url).strip("/").split("/")[:-1] if not p.isdigit()]


def _store(name, sitemap, lang, path=None, parse=None, base=None, path_crumbs=False, sub=None):
    base = base or re.match(r"https?://[^/]+", sitemap).group(0)
    # "shop": dónde están las fichas, para preseleccionar otras (el equipo, equipo_sources) con otro filtro.
    src = {"name": name, "sitemap": sitemap, "kind_url": dach_kind(lang), "pick": _pick_dach(lang, base, path),
           "fix": _dach_fix, "shop": {"base": base, "path": path, "lang": lang + "+en"}}
    if parse:
        src["parse"] = parse
    if path_crumbs:  # sin breadcrumb en la ficha: la ruta de la URL lo dice
        src["crumbs"] = _path_crumbs
    if sub:
        src["sub"] = sub
    return src


for _cat, _id, _src in [
        # JSON-LD de producto (con EAN casi todas)
        (DE_SOURCES, "promusictools", _store("Pro Music Tools", "https://www.promusictools.com/sitemap.xml", "de", r"/p/",
                                                  # solo el sitemap de fichas en alemán (los demás: inglés, categorías, marcas)
                                                  sub=lambda u: u == "https://www.promusictools.com/products-sitemap.xml")),
        (DE_SOURCES, "zoundhouse", _store("Zoundhouse", "https://www.zoundhouse.de/sitemap.xml", "de")),
        (DE_SOURCES, "shop2rock", _store("Shop2Rock", "https://www.shop2rock.de/sitemap.xml", "de", r"/gitarre-bass/")),
        (DE_SOURCES, "lange", _store("Musikhaus Lange", "https://musikhaus-lange.de/sitemap.xml", "de", r"/product/")),
        (DE_SOURCES, "imm", _store("IMM Professional", "https://imm-professional.de/sitemap_index.xml", "de")),
        (DE_SOURCES, "dressler", _store("Musik Dressler", "https://www.musik-dressler.de/toprank-sitemap_deutsch0.xml", "de")),
        (DE_SOURCES, "soundofmusic", _store("Sound of Music", "https://www.sound-of-music.de/sitemap_index.xml", "de", r"/shop/")),
        (DE_SOURCES, "insound", _store("Insound", "https://www.insound.de/sitemap.xml", "de", r"/gitarre-bass/gitarre/",
                                    path_crumbs=True)),
        (DE_SOURCES, "wittl", _store("Musik Wittl", "https://musik-wittl.de/sitemap.xml", "de")),
        (DE_SOURCES, "musikebert", _shopify("Musik Ebert", "https://www.musik-ebert.de", "de")),
        (DE_SOURCES, "actionmusic", _shopify("Action Music", "https://action-music.eu", "de")),
        (AT_SOURCES, "musikpaul", _store("Musik Paul", "https://musikpaul.at/sitemap.xml", "de", r"/produkt/")),
        (AT_SOURCES, "hammerschmidt", _store("Musikhaus Hammerschmidt", "https://www.musikhaus-hammerschmidt.at/sitemap_index.xml",
                                             "de", r"/shop/gitarren-baesse/(?:e-gitarren|westerngitarren|konzertgitarren"
                                                   r"|akustikgitarren|gitarren)")),
        (AT_SOURCES, "keywi", _store("Key-Wi Music", "https://www.keywi.com/sitemap_index.xml", "de", r"/produkt/")),
        (AT_SOURCES, "danys", _shopify("Dany's Music Shop", "https://danysmusicshop.at", "de")),
        (NL_SOURCES, "magnamusic", _store("Magna Music", "https://www.magnamusic.nl/sitemap.xml", "nl", r"/producten/\d+/")),
        (NL_SOURCES, "klundert", _store("Klundert Music", "https://www.klundertmusic.nl/sitemap_nl.xml", "nl")),
        (NL_SOURCES, "gooise", _store("Gooise Gitaren", "https://www.gooise-gitaren.nl/sitemap.xml", "nl", r"/contents/nl/p\d+_")),
        (NL_SOURCES, "dijkman", _store("Dijkman Muziek", "https://www.dijkmanmuziek.nl/1_index_sitemap.xml", "nl")),
        (NL_SOURCES, "alphenaar", _store("Alphenaar", "https://alphenaar.com/sitemap.xml", "nl")),
        (NL_SOURCES, "vanderzwaag", _store("Van der Zwaag Muziek", "https://www.vanderzwaagmuziek.nl/sitemap_index.xml", "nl",
                                           r"/product/")),
        (NL_SOURCES, "musicallin", _shopify("Music All In", "https://musicallin.nl", "nl")),
        (NL_SOURCES, "tfoa", _shopify("TFOA", "https://www.tfoa.eu", "nl")),
        (NL_SOURCES, "dijkmans", _shopify("Dijkmans Guitars", "https://dijkmansguitars.com", "nl")),
        # Shopware 6 con microdatos
        (DE_SOURCES, "mjguitars", _store("MJ Guitars", "https://www.mjguitars.de/sitemap.xml", "de", r"\.html$", parse=_parse_shopware)),
        (DE_SOURCES, "musictown", _store("Music Town", "https://music-town.de/sitemap.xml", "de", r"[^/]$", parse=_parse_shopware)),
        (DE_SOURCES, "musikbeck", _store("Musik Beck", "https://www.musikbeck.de/sitemap.xml", "de", parse=_parse_shopware)),
        (DE_SOURCES, "dornbusch", _store("Musikhaus am Dornbusch", "https://www.musikhausamdornbusch.de/sitemap.xml", "de", r"[^/]$",
                                         parse=_parse_shopware)),
        (DE_SOURCES, "soundland", _store("Soundland", "https://www.soundland.de/sitemap.xml", "de", r"/gitarre/",
                                         parse=_parse_shopware)),
        (DE_SOURCES, "zoelch", _store("Musikhaus Zölch", "https://www.musikhaus-zoelch.de/sitemap.xml", "de",
                                      r"(?i)/zupfinstrumente/(?:e-gitarren|westerngitarren|konzertgitarren|akustikgitarren"
                                      r"|halbakustik|jazzgitarren|semi|gitarren)", parse=_parse_shopware)),
        (DE_SOURCES, "soundaktuell", _store("Soundaktuell Guitars", "https://soundaktuellguitars.de/sitemap.xml", "de", r"[^/]$",
                                            parse=_parse_shopware)),
        (DE_SOURCES, "markstein", _store("Musikhaus Markstein", "https://www.markstein.de/sitemap.xml", "de", r"[^/]$",
                                         parse=_parse_shopware)),
        (AT_SOURCES, "schagerl", _store("Schagerl", "https://schagerl.com/sitemap.xml", "de", r"/p/", parse=_parse_shopware)),
        (AT_SOURCES, "roxor", _store("Roxor Store", "https://www.roxorstore.at/sitemap.xml", "de", r"[^/]$", parse=_parse_shopware)),
        (NL_SOURCES, "johdeheer", _store("Joh. de Heer", "https://www.johdeheer.nl/sitemap.xml", "nl", r"/artikel/",
                                         parse=_parse_shopware))]:
    _cat[_id] = _src


# --- Equipo por país (catálogos "<país>mas": bajos, amplis, pedales, teclados, micros, estuches y accesorios) ----------
# Las mismas tiendas que las guitarras del país. Las categorías, la URL y el nombre se traducen al español (_to_es con
# equipo=True: _TO_ES_EQUIPO y _TO_ES) y se clasifican con los clasificadores de España (mas_kind y equipo_kind) y sus
# tipos; lo que el clasificador de guitarras de la tienda reconoce como guitarra no entra. Cada tienda preselecciona sus
# fichas por la URL con _pick_equipo_for (no con el filtro de guitarras) y el nombre traducido se añade al final de las
# categorías (_equipo_fix): de ahí salen los tipos (BASS_TYPES, AMP_TYPES…), igual que en Brasil ("brmas").
#
# Cómo añadir un país (p. ej. Francia → catálogo "frmas" en data/catalog/frmas/):
#   1. _TO_ES_EQUIPO["fr"]: vocabulario de equipo del idioma → español (ya hay de, nl, fr, it, pt y en; afinarlo con fichas
#      reales del paso 5).
#   2. EQUIPO_COUNTRIES["fr"]: tiendas de guitarras del país (FR_SOURCES), idioma ("fr+en"), ficheros en el idioma del país
#      y, por tienda, "shops" (dónde están sus fichas: "base", "path" de la URL de las fichas, "shopify"; las tiendas
#      hechas con _store/_shopify ya lo traen en "shop") o "exclude" (con el motivo: tiendas que descubren sus fichas por
#      las categorías de guitarras, como Thomann, Woodbrass o Gear4music). Una tienda sin lo uno ni lo otro da error.
#   3. scraper/intl.py: SITES["fr"]["extra_catalogs"] = ["frmas"] y las páginas nuevas en SITES["fr"]["kinds"]; en T["fr"],
#      "kinds" (títulos), "nouns" (qué se cuenta en cada categoría), "allWord" y los tipos en ["js"]["types"].
#   4. .github/workflows/catalog.yml: "frmas" en la matriz y en las opciones de "solo".
#   5. Prueba sin tocar data/: python -m scraper.catalog --cat frmas --only <tienda> --limit 40 --records-out /tmp/x.json
#      y revisar "kind", "type" y "name" de cada ficha del lote (status "not_guitar": descartada).

# Preselección por la URL (ya en español): palabras de equipo, o marcas que solo hacen equipo (fichas sin esas palabras).
_EQ_PICK = re.compile(
    r"\bbajo|\bbass|amplificador|\bampli\b|\bamps?\b|\bcubo\b|cabezal|pantalla|cabinet|valvular|pedal|multiefect|overdrive"
    r"|distors|distortion|\bfuzz|delay|reverb|chorus|flanger|phaser|tr[eé]molo|vibrato|\bwah|looper|compres|booster|octav"
    r"|preamp|teclado|piano|sintetiz|synth|controlador midi|workstation|micr[oó]fono|inal[aá]mbrico|estuche|funda|gig ?bag"
    r"|\bcases?\b|\bbags?\b|cuerdas|\bstrings?\b|\bp[uú]as?\b|\bpicks?\b|plectr|plektr|correa|\bstraps?\b|cable|cejilla|\bcapo\b"
    r"|afinador|\btuner|soporte|\bstands?\b|colgador|pastilla|\bpickups?\b|humbucker|clavijas|golpeador|pickguard|limpieza"
    r"|polish|\bslide\b", re.I)
_EQ_PICK_SKIP = re.compile(
    r"bater[ií]a|drum|platillo|snare|hi-?hat|\btoms?\b|cajon|percus|\bkick|fu(?:ß|ss)maschine|\bsticks?\b|schl[aä]gel|beater"
    r"|\bfell\b|violin|viola\b|cello|geige|\bsax|trompet|posaun|klarinet|fl[oö]te|flauta|\bhorn\b|tuba|\bbl[aä]tter?\b"
    r"|mundst|ukulele|ukelele|mandolin|banjo|harfe|zither|akkordeon|harmonika|licht|leuchte|\bled\b|dmx|nebel|laser|traverse"
    r"|\bdj\b|mischpult|mixer|libro|gutschein|geschenk|\bshirt|hoodie|tasse|poster|sticker|usado|b-?ware|gebraucht"
    r"|ausstellung|vorf[uü]hr|\bmiete\b|reparatur|service|\bxlr\b|cinch|speicherkarte|altavoz|subwoofer|\brack|in ear"
    r"|recorder|beschallung|\bpa\b", re.I)
_EQ_BRANDS = tuple(b + " " for b in (
    "boss", "mxr", "electro harmonix", "ehx", "strymon", "tc electronic", "walrus audio", "jhs", "earthquaker", "keeley",
    "line 6", "line6", "fractal", "kemper", "neural dsp", "marshall", "orange", "blackstar", "laney", "mesa boogie", "engl",
    "ampeg", "markbass", "hartke", "aguilar", "darkglass", "eden", "ebs", "nord", "korg", "roland", "casio", "kawai", "moog",
    "arturia", "novation", "shure", "sennheiser", "neumann", "rode", "akg", "audio technica", "beyerdynamic", "hiscox",
    "gator", "rockcase", "rockbag", "d addario", "daddario", "elixir", "ernie ball", "dunlop", "rotosound", "seymour duncan",
    "dimarzio", "emg", "source audio", "mooer", "nux", "hotone", "zoom", "digitech", "eventide", "two notes", "victory",
    "friedman", "bogner", "diezel", "hughes kettner", "hughes & kettner", "vox", "ibanez tube", "positive grid", "headrush"))
# Fichas que no son un producto suelto: lotes, sets de iniciación, segunda mano.
_EQ_DROP = re.compile(
    r"\bkit\b|starter|bundle|paket|komplett-?set|usado|\bset (?:de )?(?:guitarra|bajo)"
    # otros instrumentos (sus fundas, soportes, cuerdas…) y regalos
    r"|klarinet|\bklar\b|\bbl[aä]tt(?:er)?\b|\breeds?\b|saxo|posaun|tuba|euphonium|trompet|\bhorn|fl[oö]te|querfl|violin|geige"
    r"|viola\b|cello|ukulele|ukelele|\btenor (?:bag|funda)|bariton soporte|banjo|mandolin|harfe|zither|klangschale|sansula|kalimba|boomwhack|cajon"
    r"|bater[ií]a|platillo|orchester|notenpult|\bpult\b|socken|socks|t-?shirt|hoodie|tasse|becher|schl[uü]ssel|keyring"
    r"|anh[aä]nger|pendant|poster|sticker|aufkleber|geschenk|gutschein|(?:single|double|twin|doppel)[- ]?pedal", re.I)
# Estuches y fundas: solo los de guitarra, bajo, amplis, pedales o teclados (no los de flautas, mesas de mezclas o racks).
_EQ_CASE_FOR = re.compile(r"guitarr|guitar|gitarr|\bbajo|\bbass|western|dreadnought|jumbo|parlou?r|\bclassic|cl[aá]sica"
                          r"|el[eé]ctrica|ac[uú]stica|strat|\btele|les ?paul|\blp\b|\bsg\b|\bes-?3|flying ?v|explorer|jazz|precision"
                          r"|amplificador|\bamp|combo|cubo|cabezal|pantalla|pedal"
                          r"|ibanez|fender|gibson|epiphone|gretsch|squier|ortega|schecter|\bprs\b|\besp\b|\bltd\b|jackson|charvel"
                          r"|hagstrom|martin|taylor|warwick|rockbag|rockcase|hiscox|\bsks\b|tkl|gator g", re.I)
# El nombre dice que es una guitarra ("Yamaha AC5M Westerngitarre … mit Tonabnehmer") y no algo para ella.
_EQ_GUITAR_NAME = re.compile(r"guitarra (?:el[eé]ctrica|ac[uú]stica|cl[aá]sica)|electroac[uú]stica|\b(?:stratocaster|telecaster"
                             r"|les paul|jazzmaster|jaguar)\b", re.I)
_EQ_FOR_GUITAR = re.compile(r"\bpara\b|amplificador|\bcubo\b|cabezal|pantalla|pedal|efecto|multiefect|estuche|funda|cuerdas|\bstrings?\b|correa|soporte|cable|p[uú]as?\b|cejilla|afinador"
                            r"|colgador|limpieza|golpeador \w+ (?:para|de)|clavijas|repuesto|\bcase\b|\bbag\b|hardcase|softcase|gig ?bag"
                            r"|\bstrap|\bstand\b", re.I)
# Categorías de otros instrumentos o de otras cosas ("Ständer für Blasinstrumente", "Klangschalen - Taschen").
_EQ_DROP_CAT = re.compile(r"blasinstrument|holzblas|blechblas|\bbrass\b|streichinstrument|ukulele|meditation|esoter|klangschal"
                          r"|notenst|notenpult|\bdj\b|licht|souvenir|geschenk|kalimba|sansula|percussion|batería|otros saiteninstr"
                          r"|andere saiteninstr|tasten ?accesorios|accesorios para tasten", re.I)
# Marcas de pedales: "Darkglass Microtubes B7K", "Electro-Harmonix Bass Metaphors" son pedales de bajo, no bajos.
_EQ_PEDAL_BRANDS = re.compile(r"^(?:electro[- ]?harmonix|ehx|darkglass|mxr|tc electronic|strymon|walrus|jhs|earthquaker|keeley"
                              r"|source audio|tech ?21|zoom|boss|digitech|eventide|mooer|nux|hotone|joyo|wampler|xotic|fulltone"
                              r"|tone city|caline|donner|behringer|danelectro|ibanez (?:ts|tube screamer)|dunlop|origin effects)\b", re.I)
# "Gitarren & Bässe", "Gitarre & Bass Zubehör": categorías que agrupan; no dicen que sea de bajo (quedan en "guitarra")
_EQ_GROUP = re.compile(r"\b(?:guitarras?|bajos?)(?:(?:\s*(?:&|y|und|and|e|et|en|/|,|\+|-)\s*)+(?:guitarras?|bajos?|accesorios))+", re.I)


def _eq_slug(url):
    """El nombre de la ficha en la URL, aunque detrás venga un número o "pd/189186" (Musikhaus Korn)."""
    parts = [p for p in re.sub(r"[?#].*$", "", url).split("/")[3:] if p]
    named = [p for p in parts if re.search(r"[a-zA-Z]{2}[^/]*[-_][^/]*[a-zA-Z]", p)]
    slug = re.sub(r"\.(html?|php)$", "", named[-1] if named else (parts[-1] if parts else ""))
    return re.sub(r"-p-\d+$|_\d{5,}$|-\d{5,}$|^p\d+_", "", slug).replace("-", " ").replace("_", " ")


def _pick_equipo_for(lang, base, path=None, shopify=False):
    """Fichas de equipo de una tienda: de su dominio (base), con la ruta de sus fichas (path) y que por la URL parezcan
    equipo (en español tras _to_es) o empiecen por una marca que solo hace equipo."""
    base = base.rstrip("/")
    rx = re.compile(path) if path else None

    def pick(u):
        if not u.startswith(base + "/") or (rx and not rx.search(u)) or (shopify and not re.match(re.escape(base) + r"/products/", u)):
            return False
        if NOT_PRODUCT.search(u) or _GEN_NOT_PRODUCT.search(u.replace("/products/", "/")):
            return False
        slug = _to_es(_eq_slug(u), lang, equipo=True)
        return not _EQ_PICK_SKIP.search(slug) and (bool(_EQ_PICK.search(slug)) or slug.startswith(_EQ_BRANDS))
    return pick


def _eq_name(name, lang):
    """El nombre en español; "Klassikgitarre-Saiten" → "guitarra clásica cuerdas" (con guion sería "12-cuerdas")."""
    return re.sub(r"(?<=[^\W\d])-(?=[^\W\d])", " ", _to_es(name, lang, equipo=True))


def equipo_kind_for(lang, guitar=None):
    """'bajo', 'ampli', 'pedal', 'teclado', 'micro', 'estuche', 'varios' o None, en el idioma de la tienda (lang: "de+en").
    guitar(crumbs, url, name): el clasificador de guitarras de la tienda; si dice que es una guitarra, no es equipo."""
    def kind(crumbs, url="", name=""):
        es_name = _eq_name(name, lang)
        # sin las etiquetas de Shopify (traen de todo) ni lo que añade _equipo_fix
        crumbs = [c for c in crumbs or [] if not c.startswith(("#", _EQ_MARK))]
        cats = [" ".join(_EQ_GROUP.sub(" guitarra ", _to_es(c, lang, equipo=True)).split()) for c in crumbs]
        cats = [c for c in cats if c]
        if _EQ_DROP.search(es_name) or NOT_PRODUCT.search(name or "") or any(_EQ_DROP_CAT.search(c) for c in cats) \
                or _EQ_GUITAR_NAME.search(es_name) and not _EQ_FOR_GUITAR.search(es_name) \
                or cats and _EQ_GUITAR_NAME.search(cats[-1]) and not _EQ_PICK.search(cats[-1]) \
                and not _EQ_FOR_GUITAR.search(cats[-1]):  # "Westerngitarren - 6-Saitig", no "Gurte für E-Gitarren"
            return None
        slug = "x/" + _to_es(_eq_slug(url), lang, equipo=True)
        found = mas_kind(cats, slug, es_name) or equipo_kind(cats, slug, es_name)
        if not found and cats:
            # El nombre a secas no lo dice ("Ernie Ball 2090 Paradigm .010-.050"); las categorías sí ("E-Gitarrensaiten").
            said = " ".join(cats[-2:] + [es_name])
            found = mas_kind(cats, slug, said) or equipo_kind(cats, slug, said)
        # Lo que el clasificador de guitarras de la tienda da por guitarra no es un accesorio ni un estuche ("Westerngitarre
        # … Tonabnehmer, inkl. Koffer"); un ampli o un pedal sí lo es aunque su categoría diga "für E-Gitarren".
        if found in ("varios", "estuche") and guitar and guitar(crumbs, url, name):
            return None
        if found == "estuche" and not _EQ_CASE_FOR.search(" / ".join([es_name, slug] + cats[-1:])):
            return None
        if found == "bajo" and _EQ_PEDAL_BRANDS.search(es_name):
            return "pedal"
        # Un previo o un simulador en "Effektgeräte" ("Victory V1 The Duchess Pedal", "Mooer GE 1000 Amp Modeling") es un pedal
        if found == "ampli" and re.search(r"pedal|multiefect|efecto|distors|overdrive", " / ".join(cats[-2:])) \
                and not re.search(r"amplificador|cubo|cabezal|pantalla", " / ".join(cats[-2:])):
            return "pedal"
        return found
    return kind


_EQ_MARK = "· "


def _equipo_fix(fix, lang):
    """La limpieza de la tienda y, al final de las categorías, el nombre y la última categoría traducidos: de ahí salen
    los tipos (guitar_type mira la última; "Mesa/Boogie 1x12 Mini Rectifier" es una caja por "1x12er Gitarrenboxen").
    "Gitarren- und Bass-Effekte" no dice que sea de bajo: esas agrupaciones se quitan."""
    def f(data, text):
        data = fix(data, text) if fix else data
        crumbs = [c for c in data.get("crumbs") or [] if not c.startswith("#")]
        if data.get("name"):
            data["crumbs"] = list(data.get("crumbs") or []) + [
                _EQ_MARK + " / ".join([_eq_name(data["name"], lang)] + [_EQ_GROUP.sub(" guitarra ", _eq_name(c, lang)) for c in crumbs[-1:]])]
        return data
    return f


def equipo_sources(sources, lang, shops=None, exclude=None):
    """Fuentes del catálogo de equipo de un país a partir de las de sus guitarras (ver EQUIPO_COUNTRIES)."""
    out = {}
    for sid, src in sources.items():
        if sid in (exclude or {}):
            continue
        shop = {**src.get("shop", {}), **(shops or {}).get(sid, {})}
        if not shop.get("base") or ("discover" in src and "sitemap" not in shop):
            raise ValueError(f"equipo: {sid} sin 'shop' (base y ruta de sus fichas) en 'shops'; o en 'exclude', con el motivo")
        lang_ = shop.get("lang", lang)
        guitar = src.get("kind_url") or (lambda c, u, n, k=src["kind"]: k(c))
        new = {k: v for k, v in src.items() if k not in ("kind", "crumbs", "discover", "shop")}
        new.update(kind_url=equipo_kind_for(lang_, guitar), fix=_equipo_fix(src.get("fix"), lang_),
                   pick=_pick_equipo_for(lang_, shop["base"], shop.get("path"), shop.get("shopify")))
        for key in ("sitemap", "sub"):
            if key in shop:
                new[key] = shop[key]
        out[sid] = new
    return out


# País → su catálogo de equipo ("<país>mas"). "sources": las tiendas de guitarras del país; "files": categoría → JSON (y
# página: intl.SITES[país]["kinds"]); "max_price": tope por categoría en la moneda del país (un "estuche" más caro es un
# instrumento con su estuche); "shops": dónde están las fichas de cada tienda si no lo dice su "shop" o si la ruta de
# sus guitarras no vale para el equipo (path None: todo el dominio); "exclude": tiendas que no entran, y por qué.
EQUIPO_COUNTRIES = {
    "de": {"sources": DE_SOURCES, "lang": "de+en", "site": "de", "max_price": {"estuche": 800, "varios": 500},
           "files": {"bajo": "baesse.json", "ampli": "verstaerker.json", "pedal": "effektpedale.json",
                     "teclado": "keyboards.json", "micro": "mikrofone.json", "estuche": "koffer-taschen.json",
                     "varios": "zubehoer.json"},
           "shops": {"session": {"base": "https://www.session.de", "path": r"/products/[^/]+/?$"},
                     "hermann": {"base": "https://www.musikhaus-hermann.de", "path": r"-\d{4,6}/$"},
                     # sus guitarras salen de una sección; el equipo está en otras
                     "shop2rock": {"path": r"/[^/]+/[^/]+\.html$"}, "insound": {"path": r"/\d+/[^/]+\.html$"},
                     "soundland": {"path": r"-p-\d+$"}, "zoelch": {"path": r"[^/]$"}},
           "exclude": {"korn": "sin breadcrumb y con muchas fichas retiradas en el sitemap (sin precio ni JSON-LD de producto): "
                               "de 228 000 URL, unas 45 000 pasarían el filtro y la mitad no tienen precio",
                       "thomann": "descubre sus fichas por las categorías de guitarras (cat_allProducts_GF_…)",
                       "woodbrass": "descubre sus fichas por las colecciones Shopify de guitarras",
                       "gear4music": "su sitemap solo se lee en el departamento de guitarras (guitar_bass); 403 fuera de GitHub"}},
}


PORTUGUESE_TYPES = [("Lisboa", r"lisboa"), ("Coimbra", r"coimbra"), ("Porto", r"\bporto\b")]

ACOUSTIC_TYPES = [("12 cuerdas", r"12 cuerdas|12-string|12-saiter|zwölfsait|\b12\b"),
                  ("Tamaño reducido", r"reducid|travel|viaje|reise|\bmini\b|3/4|1/2|baby|little|junior|\bgs mini|\bjr\d?\b"),
                  ("Parlor", r"parlou?r"), ("Jumbo", r"jumbo|\bsj-?200|\bj-?45|\bj-?200"),
                  ("Dreadnought", r"dreadnought|\bd-?\d{1,2}\b|\bdread|\bhd-?\d"),
                  ("Auditorio / Concierto", r"auditori|concierto|concert|\bom\b|\b000|grand|folk|korpusgr|\bga\b|\bgs\b|orchestra"),
                  ("Roundback", r"roundback|ovation")]
CLASSICAL_TYPES = [("Flamenca", r"flamenc"),
                   ("Tamaño reducido", r"\b[137]/[248]\b|reducid|junior|cadete|se[nñ]orita|requinto|kinder"),
                   ("Electroclásica", r"electro|el[eé]ctricas? cl|tonabnehmer|\bce\b|\bcw\b|\bcx\b|ncx|cutaway|\bcwe\b"),
                   ("Clásica", r".")]

# Tipos comunes a partir del breadcrumb (Numemusic: "Modelos ST"; Session: "ST-Gitarren").
TYPES = [("ST", r"\bst\b|st-gitarren|strat"), ("T", r"modelos t\b|formato t\b|\bt-gitarren|tele"),
         ("Single cut", r"single.?cut"), ("Double cut", r"double.?cut"),
         ("Double cut", r"modelos sg\b"), ("Semihueca", r"hollow|semi|jazz|resonanz|archtop|modelos es\b"),
         ("Moderna / Metal", r"heavy|metal|superstrat|moderne|[78] cuerdas|[78]-saiter"),
         ("Offset / Retro", r"offset|retro|jazzmaster|jaguar|mustang")]

# Si la categoría de la tienda no dice la forma, se deduce del nombre o de la URL (Numemusic: "guitarra-electrica-st-…").
NAME_TYPES = [("T", r"tele(caster)?\b|\btl\b"),
              ("ST", r"strat(ocaster)?\b|\bst\b|pacifica|soloist|san dimas|so-cal|super.?st"),
              ("Offset / Retro", r"jazzmaster|jaguar|mustang|duo-?sonic|surfcaster|meteora|offset|retro"),
              ("Semihueca", r"\bes-?\d{3}|casino|hollow|archtop|artcore|streamliner|\bcuerpo.hueco"),
              ("Single cut", r"les paul|\blp\b|\bec-?\d|single.?cut|eclipse|nighthawk|\bjet\b"),
              ("Double cut", r"\bsg\b|custom ?2[24]|\bce ?2[24]|double.?cut"),
              ("Moderna / Metal", r"explorer|flying ?v|firebird|thunderbird|phoenix|headless|warrior|ravendark|"
                                  r"\bmetal\b|[78].?(cuerdas|string)|baritone")]
TYPES_BY_KIND = {"electrica": TYPES, "acustica": ACOUSTIC_TYPES, "clasica": CLASSICAL_TYPES,
                 "teclado": KEYBOARD_TYPES, "pedal": PEDAL_TYPES, "portuguesa": PORTUGUESE_TYPES,
                 # Sin el "resto" del final: si la categoría no lo dice, el tipo sale del nombre (NAME_TYPES_BY_KIND).
                 "bajo": BASS_TYPES[:-1], "ampli": AMP_TYPES[:-1], "estuche": CASE_TYPES[:-1], "micro": MICRO_TYPES[:-1], "varios": VARIOS_TYPES[:-1]}
NAME_TYPES_BY_KIND = {"electrica": NAME_TYPES, "acustica": ACOUSTIC_TYPES, "clasica": CLASSICAL_TYPES,
                      "teclado": KEYBOARD_TYPES, "pedal": PEDAL_TYPES, "portuguesa": PORTUGUESE_TYPES,
                      "bajo": BASS_TYPES, "ampli": AMP_TYPES, "estuche": CASE_TYPES, "micro": MICRO_TYPES, "varios": VARIOS_TYPES}

# Catálogos: carpeta, fuentes y fichero de la web por categoría.
CATALOGS = {
    "electrica": {"dir": DIR, "sources": SOURCES, "files": {"electrica": "products.json"}},
    "acustica": {"dir": DIR / "acusticas", "sources": ACOUSTIC_SOURCES,
                 "files": {"acustica": "acusticas.json", "clasica": "clasicas.json"}},
    "equipo": {"dir": DIR / "equipo", "sources": EQUIPO_SOURCES,
               "files": {"teclado": "teclados.json", "pedal": "pedales.json"}},
    # Bajos, amplificadores, estuches y micrófonos (España).
    "mas": {"dir": DIR / "mas", "sources": MAS_SOURCES,
            "files": {"bajo": "bajos.json", "ampli": "amplis.json", "estuche": "estuches.json", "micro": "micros.json",
                      "varios": "varios.json"}},
    # Portugal: aún sin páginas propias (guitle.com/pt/ llegará después); solo los JSON del catálogo.
    "pt": {"dir": DIR / "pt", "sources": PT_SOURCES, "site": "pt",
           "files": {"electrica": "eletricas.json", "acustica": "acusticas.json", "clasica": "classicas.json",
                     "portuguesa": "portuguesas.json"}},
    # Francia: igual, guitle.com/fr/ llegará después.
    "fr": {"dir": DIR / "fr", "sources": FR_SOURCES, "site": "fr",
           "files": {"electrica": "electriques.json", "acustica": "folk.json", "clasica": "classiques.json"}},
    "it": {"dir": DIR / "it", "sources": IT_SOURCES, "site": "it",
           "files": {"electrica": "elettriche.json", "acustica": "acustiche.json", "clasica": "classiche.json"}},
    # Reino Unido: precios en libras (las tiendas los dan en GBP; "cur" es la moneda que se acepta).
    "uk": {"dir": DIR / "uk", "sources": UK_SOURCES, "site": "uk", "cur": "GBP", "headers": EN_HEADERS,
           "files": {"electrica": "electric.json", "acustica": "acoustic.json", "clasica": "classical.json"}},    "de": {"dir": DIR / "de", "sources": DE_SOURCES, "site": "de",
           "files": {"electrica": "e-gitarren.json", "acustica": "westerngitarren.json", "clasica": "konzertgitarren.json"}},    "br": {"dir": DIR / "br", "sources": BR_SOURCES, "site": "br", "cur": "BRL", "min_price": 300,
           "files": {"electrica": "guitarras.json", "acustica": "violoes.json", "clasica": "violoes-nylon.json"}},
    # Brasil: equipo. Mismas tiendas; sin el filtro de nombres de las guitarras (aquí los accesorios sí entran).
    "brmas": {"dir": DIR / "brmas", "sources": BRMAS_SOURCES, "site": "br", "cur": "BRL", "min_price": 10, "name_skip": None,
              # En reales: un "case" de más de R$ 3.000 o un "acessório" de más de R$ 2.500 es un instrumento con su case.
              "max_price": {"estuche": 3000, "varios": 2500},
              "files": {"bajo": "baixos.json", "ampli": "amplificadores.json", "pedal": "pedais.json", "teclado": "teclados.json",
                        "micro": "microfones.json", "estuche": "cases.json", "varios": "acessorios.json"}},    "ie": {"dir": DIR / "ie", "sources": IE_SOURCES, "site": "ie", "headers": EN_HEADERS,
           "files": {"electrica": "electric.json", "acustica": "acoustic.json", "clasica": "classical.json"}},
    "at": {"dir": DIR / "at", "sources": AT_SOURCES, "site": "at",
           "files": {"electrica": "e-gitarren.json", "acustica": "westerngitarren.json", "clasica": "konzertgitarren.json"}},
    "nl": {"dir": DIR / "nl", "sources": NL_SOURCES, "site": "nl",
           "files": {"electrica": "elektrische-gitaren.json", "acustica": "akoestische-gitaren.json", "clasica": "klassieke-gitaren.json"}},
}
# Equipo de cada país de EQUIPO_COUNTRIES: "demas" → data/catalog/demas/, en la web del país (intl.SITES[...]["extra_catalogs"]).
for _code, _eq in EQUIPO_COUNTRIES.items():
    CATALOGS[_code + "mas"] = {"dir": DIR / f"{_code}mas", "site": _eq["site"], "cur": _eq.get("cur", "EUR"),
                               "sources": equipo_sources(_eq["sources"], _eq["lang"], _eq.get("shops"), _eq.get("exclude")),
                               # sin el filtro de nombres de las guitarras (aquí los accesorios sí entran)
                               "name_skip": None, "max_price": _eq.get("max_price", MAX_PRICE), "files": _eq["files"],
                               **({"min_price": _eq["min_price"]} if _eq.get("min_price") else {})}
CATALOG = CATALOGS["electrica"]


def use(cat):
    """Elige el catálogo con el que trabajan el resto de funciones."""
    global DIR, SOURCES, CATALOG
    CATALOG = CATALOGS[cat]
    DIR, SOURCES = CATALOG["dir"], CATALOG["sources"]


LEFT = re.compile(r"\b(lh|left[- ]?hand(ed)?|lefthand|left|zurd[oa]s?)\b|\d+lh\b", re.I)

# Marcas en mayúsculas o con variantes → nombre canónico.
BRAND_SUFFIX = re.compile(r"\s+(guitars?|españa|spain|europe)$", re.I)
BRANDS = {"squier by fender": "Squier", "squier": "Squier", "prs": "PRS", "esp": "ESP", "ltd": "LTD", "evh": "EVH",
          "esp ltd": "LTD", "ltd guitars": "LTD", "esp guitars": "ESP", "ernie ball music man": "Music Man", "music man": "Music Man", "d'angelico": "D'Angelico",
          "sterling by music man": "Sterling", "gibson electric": "Gibson", "gibson acoustic": "Gibson",
          "gibson custom": "Gibson", "c.f. martin & co": "Martin", "c.f. martin": "Martin", "cf martin": "Martin", "prs se": "PRS", "prs (paul reed smith)": "PRS", "paul reed smith": "PRS"}


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
    """'PRS GUITARS', 'Prs Guitars', 'D’Angelico Guitars', 'Guild España' → 'PRS', 'D'Angelico', 'Guild'."""
    raw = BRAND_SUFFIX.sub("", re.sub(r"\s+", " ", (raw or "").replace("\u2019", "'")).strip())
    if raw.lower() in BRANDS:
        return BRANDS[raw.lower()]
    return raw.title() if raw.isupper() and len(raw) > 3 else raw


def _smart_case(name):
    """'HELLCAT VI IVORY PEARL' → 'Hellcat VI Ivory Pearl' (códigos con números y siglas cortas se quedan)."""
    if not name.isupper():
        return name
    keep = re.compile(r"\d|-|^(?:[A-Z]{1,2}|I{1,3}|IV|VI{0,3}|HSS|HSH|SSS|SSH|QMT?|FMT|NOS|EMG|LTD|PRS|ESP|EVH|USA)$")
    return " ".join(w if keep.search(w) else w.capitalize() for w in name.split())


def clean_name(name, brand_raw, brand):
    """'SQUIER BY FENDER Classic Vibe…' → 'Squier Classic Vibe…'."""
    name = re.sub(r"<[^>]+>", " ", html.unescape(name or ""))  # Egitana mete <b>…</b> en algunos nombres
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"\s+guitarra (el[eé]ctrica|electroac[uú]stica|ac[uú]stica|cl[aá]sica|electrocl[aá]sica|flamenca)(?=\s|$)", "",
                  name, flags=re.I)
    name = _smart_case(name)
    if brand_raw:  # "PRS PRS SE Custom 24" → "PRS SE Custom 24"
        name = re.sub(rf"^({re.escape(brand_raw)}\s+)+", brand_raw + " ", name, flags=re.I)
    if brand_raw and name.lower().startswith(brand_raw.lower()):
        name = brand + name[len(brand_raw):]
    elif brand and not name.lower().startswith(brand.lower()):
        name = f"{brand} {name}"
    return name


# "Guitarra folk" / "Guitares folk" en Portugal y Francia es cualquier acústica de acero, no una forma.
GENERIC_FOLK = re.compile(r"guit(?:arras?|ares?) folk", re.I)


def type_from_name(name, url="", kind="electrica"):
    text = GENERIC_FOLK.sub("", name.lower() + " " + url.rsplit("/", 1)[-1].replace("-", " "))
    for label, pat in NAME_TYPES_BY_KIND[kind]:
        if re.search(pat, text):
            return label
    return "Otras"


# Códigos de modelo con acabado (Ibanez RG450QMB-SPB): si dos fichas con el mismo EAN traen códigos distintos,
# una tienda tiene el EAN mal y no son el mismo producto.
MODEL_CODE = re.compile(r"\b[a-z]{1,6}\d+[a-z0-9]*-[a-z]{2,4}\b")
NAME_SYNONYMS = {"strat": "stratocaster", "tele": "telecaster", "am": "american", "pro": "professional", "lp": "les paul",
                 "std": "standard", "rw": "rosewood", "mn": "maple", "lr": "laurel", "lrl": "laurel", "eb": "ebony",
                 "bk": "black", "blk": "black", "wh": "white", "wht": "white"}


def _tokens(o):
    name = o["name"].lower().replace((o.get("brand") or "").lower(), "")
    return {t for w in re.findall(r"[a-z0-9]+", name) for t in NAME_SYNONYMS.get(w, w).split()}


# Emparejado por nombre para tiendas sin EAN (Egitana). Los nombres largos ("Rosewood Fingerboard") se
# reducen a la forma corta de Numemusic ("RW") y se comparan palabras.
FINGERBOARDS = [(r"rosewood( fingerboard| fretboard)?", "rw"), (r"maple( fingerboard| fretboard)", "mn"),
                (r"laurel( fingerboard| fretboard)?|\blr\b", "lrl"), (r"ebony( fingerboard| fretboard)", "eb"),
                (r"pau ferro( fingerboard| fretboard)?", "pf")]
# Colores y acabados en español (Egitana) → inglés, como los nombran Numemusic y Session.
COLOR_ES = {"negro": "black", "negra": "black", "blanco": "white", "blanca": "white", "rojo": "red", "roja": "red",
            "azul": "blue", "verde": "green", "gris": "gray", "grey": "gray", "naranja": "orange", "amarillo": "yellow",
            "morado": "purple", "violeta": "violet", "rosa": "pink", "plateado": "silver", "plata": "silver",
            "dorado": "gold", "oro": "gold", "marron": "brown", "marrón": "brown", "transparente": "transparent",
            "satinado": "satin", "satinada": "satin", "metalico": "metallic", "metálico": "metallic", "nieve": "snow",
            "crema": "cream", "cielo": "sky", "brillante": "gloss", "mate": "matte", "fresno": "ash", "caoba": "mahogany",
            "nogal": "walnut", "cereza": "cherry", "vino": "wine", "oscuro": "dark", "oscura": "dark", "claro": "light",
            "perla": "pearl", "noche": "night", "medianoche": "midnight", "escarlata": "scarlet", "bosque": "forest",
            "profundo": "deep", "natural": "natural"}
# Modelos y acabados abreviados (Thomann: "Am Pro Clsc Tele", "Player II Strat MN AQB") → nombre completo, como Numemusic.
NAME_CODES = {"am": "american", "clsc": "classic", "anniv": "anniversary", "av": "american vintage", "mod": "modified",
              "cv": "classic vibe", "sat": "satin", "primergrey": "primer gray",
              "3ts": "3 color sunburst", "3cs": "3 color sunburst", "3 tone sunburst": "3 color sunburst",
              "2ts": "2 color sunburst", "2cs": "2 color sunburst", "owt": "olympic white", "owh": "olympic white",
              "pwt": "polar white", "olp": "olympic pearl", "aqb": "aquatone blue", "car": "candy apple red",
              "lpb": "lake placid blue", "sfg": "sea foam green", "frd": "fiesta red", "aw": "arctic white",
              "vw": "vintage white", "hcs": "heritage cherry sunburst", "hc": "heritage cherry", "vs": "vintage sunburst",
              "ebo": "ebony", "tbs": "tobacco burst", "wr": "wine red", "nat": "natural", "nt": "natural",
              "sb": "sunburst", "csb": "cherry sunburst", "bkm": "black metallic", "pm": "pale moon", "lg": "liquid gold",
              "btb": "butterscotch blonde", "elb": "electric blue", "ssy": "sunshine yellow", "dsk": "dusk"}
NAME_STOPWORDS = {"fingerboard", "fretboard", "guitar", "guitarra", "electrica", "eléctrica", "electric", "with", "con",
                  "w", "and", "y", "the", "series", "guitars", "wpg", "bpg", "tpg", "mpg", "c", "estuche", "funda", "gigbag"}


def name_tokens(name, brand):
    n = name.lower().replace("\u2019", "'")
    for b in {brand.lower(), "squier by fender", "fender squier", "esp ltd"} if brand else ():
        n = n.replace(b, " ")
    for pat, short in FINGERBOARDS:
        n = re.sub(pat, " " + short + " ", n)
    n = re.sub(r"(\d)-(color|tone)\b", r"\1 \2", n)
    for code, full in NAME_CODES.items():
        n = re.sub(rf"\b{code}\b", full, n)
    words = re.findall(r"[a-záéíóúñ0-9]+", n)
    return {NAME_SYNONYMS.get(COLOR_ES.get(w, w), COLOR_ES.get(w, w)) for w in words if w not in NAME_STOPWORDS}


# Palabras que cambian de modelo: si una ficha las tiene y la otra no, no son la misma guitarra.
MODEL_WORDS = {"ii", "iii", "iv", "v", "vi", "hss", "hh", "sss", "hsh", "ssh", "h", "fr", "ht", "lh", "left", "lefthand",
               "zurda", "zurdo", "thinline", "mini", "junior", "jr", "deluxe", "baritone", "custom", "special", "plus",
               "pro", "professional", "elite", "ultra", "limited", "ltd", "relic", "closet", "nos", "journeyman",
               "signature", "evertune", "multiscale", "headless", "hollow", "semi", "sh", "tremolo", "bigsby", "stoptail"}


def _numbers(tokens):
    return {t for t in tokens if re.search(r"\d", t) or t in MODEL_WORDS}


def name_match_score(a_name, b_name, brand):
    """0-1. Cero si no coinciden los números de modelo (60s/70s, II/III, 24/22…) o los códigos de acabado."""
    ta, tb = name_tokens(a_name, brand), name_tokens(b_name, brand)
    if _numbers(ta) != _numbers(tb):
        return 0.0
    ca, cb = set(MODEL_CODE.findall(a_name.lower())), set(MODEL_CODE.findall(b_name.lower()))
    if ca and cb:
        # Mismo código de modelo y acabado (Ibanez AZ24S2-BK): misma guitarra; distinto: otra.
        return 1.0 if ca & cb else 0.0
    return len(ta & tb) / max(1, len(ta | tb))


NAME_MATCH_MIN = 0.75     # parecido mínimo para unir una ficha sin EAN a un producto
NAME_MATCH_MARGIN = 0.1   # y con ventaja clara sobre el segundo candidato


# Referencia de fábrica en una palabra (Yamaha PACP12M, Ibanez JBM27; EC-256 cuenta como EC256).
PLAIN_CODE = re.compile(r"\b([a-z]{2,6})(\d+[a-z]{0,4})\b")


def _plain_codes(name):
    lower = re.sub(r"\b([a-z]{2,6})-(?=\d)", r"\1", name.lower())
    return {m.group(0): (m.group(1), re.match(r"\d+", m.group(2)).group()) for m in PLAIN_CODE.finditer(lower)}


def _plain_codes_differ(a, b):
    """Referencias de serie distinta (PACP12M ≠ PACSP12M). Se dan por iguales: una contenida en otra
    (SS30 ≈ CTSS30HS), las mismas letras con errata en los números (RSS02T ≈ RSS20T) y una letra de menos
    al principio con los mismos números (PA311HYNS ≈ PAC311H, EART60M ≈ EARTH60M)."""
    ca, cb = _plain_codes(a), _plain_codes(b)
    if not ca or not cb:
        return False

    def alike(x, y):
        (lx, nx), (ly, ny) = ca[x], cb[y]
        return x in y or y in x or lx == ly or (nx == ny and (lx.startswith(ly) or ly.startswith(lx)))
    return not any(alike(x, y) for x in ca for y in cb)


def same_product(a, b):
    ca, cb = set(MODEL_CODE.findall(a["name"].lower())), set(MODEL_CODE.findall(b["name"].lower()))
    if ca and cb and not ca & cb:
        return False
    if _plain_codes_differ(a["name"], b["name"]):
        return False
    ta, tb = _tokens(a), _tokens(b)
    return len(ta & tb) / max(1, len(ta | tb)) >= 0.1


def tidy(o):
    """Normalización al construir (se aplica también a fichas ya leídas): marca, nombre, tipo y zurdas."""
    o = dict(o)
    if "<" in o.get("name", ""):  # leída antes de limpiar las etiquetas HTML del nombre
        o["name"] = clean_name(o["name"], o.get("brand"), o.get("brand"))
    brand = canonical_brand(o.get("brand"))
    if o.get("brand") and brand != o["brand"] and o["name"].startswith(o["brand"]):
        o["name"] = brand + o["name"][len(o["brand"]):]
    if brand == "ESP" and re.search(r"\bltd\b", o["name"], re.I):
        brand = "LTD"  # Egitana pone las LTD bajo ESP; Numemusic y Session, como LTD
    o["name"] = re.sub(rf"^({re.escape(o.get('brand') or brand)}\s+)+", (o.get("brand") or brand) + " ", o["name"], flags=re.I)
    o["brand"] = brand
    o["kind"] = o.get("kind") or "electrica"
    if not o.get("type") or o["type"] in ("Otras", "Offset"):
        o["type"] = "Offset / Retro" if o.get("type") == "Offset" else type_from_name(o["name"], o["url"], o["kind"])
    elif o["kind"] in ("ampli", "estuche") and type_from_name(o["name"], o["url"], o["kind"]).startswith("Para "):
        o["type"] = type_from_name(o["name"], o["url"], o["kind"])  # "Para bajo" en el nombre manda sobre "Combos"
    elif o["type"] == "Clásica":  # tipo genérico: el nombre puede concretarlo (flamenca, electroclásica, 3/4…)
        o["type"] = type_from_name(o["name"], o["url"], "clasica")
    o["lh"] = bool(LEFT.search(o["name"]) or LEFT.search(o["url"].rsplit("/", 1)[-1].replace("-", " ")))
    return o


def guitar_type(crumbs, kind="electrica"):
    # Eléctricas: la última categoría ("Modelos ST"); acústicas y clásicas: las dos últimas ("Westerngitarren / Dreadnought").
    if kind not in GUITAR_KINDS:  # teclados y pedales: la última categoría ("Pedales de delay")
        leaf = crumbs[-1].lower() if crumbs else ""
    else:
        leaf = (crumbs[-1] if kind == "electrica" else " / ".join(crumbs[-2:])).lower() if crumbs else ""
    leaf = re.sub(r"cl[aá]sicas y flamencas", "", leaf)  # categoría mixta de Numemusic: no dice si es flamenca
    leaf = GENERIC_FOLK.sub("", leaf)
    for label, pat in TYPES_BY_KIND[kind]:
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
    locs = [html.unescape(re.sub(r"^<!\[CDATA\[|\]\]>$", "", l.strip())) for l in re.findall(r"<loc>\s*(.*?)\s*</loc>", text)]
    if "<" not in text:  # sitemap en texto: una URL por línea (Michenaud)
        locs = [l.strip() for l in text.split() if l.startswith("http")]
    if "<sitemapindex" in text and depth < 2:
        out, failed = [], 0
        for loc in locs:
            if sub is None or sub(loc):
                try:
                    out += sitemap_urls(fetcher, loc, None, depth + 1)
                except Exception as exc:  # noqa: BLE001 - un sitemap parcial caído no tumba el resto
                    failed += 1
                    print(f"[sitemap] {loc}: {exc}", flush=True)
        if failed and not out:
            raise RuntimeError(f"sitemap {url}: todos los parciales fallan")
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


def _parse_jsonld(soup, store_id):
    product, crumbs = _product_node(soup)
    offer = jsonld.extract(soup, [], store_id)
    if not product or not offer:
        return {"crumbs": crumbs}
    brand_raw = product.get("brand")
    if isinstance(brand_raw, list):  # WooCommerce con varias marcas: ["Ibanez"] (Discosom, Tons e Melodias)
        brand_raw = brand_raw[0] if brand_raw else None
    brand_raw = brand_raw.get("name") if isinstance(brand_raw, dict) else brand_raw
    ean = next((normalize_id(product.get(k)) for k in ("gtin13", "gtin", "gtin12", "gtin14") if product.get(k)), None)
    mpn = normalize_id(product.get("mpn"))
    if not ean and mpn.isdigit() and len(mpn) in (12, 13, 14):
        ean = mpn  # Alfasoni publica el EAN como mpn
    if crumbs and product.get("name") and crumbs[-1].strip().lower() in product["name"].lower():
        crumbs = crumbs[:-1]  # el último elemento es el propio producto, no una categoría
    # Referencia de fábrica de Fender (y Squier, Gretsch, Jackson, Charvel, EVH): 10 cifras empezando por 0
    # (Session la pone en mpn; Musicopolix, en sku). Une el PVP de es.fender.com (scraper.pvp) con el EAN.
    ref = next((r for r in (normalize_id(product.get("mpn")), normalize_id(product.get("sku"))) if re.fullmatch(r"0\d{9}", r)), None)
    return {"crumbs": crumbs, "name": product.get("name"), "brand_raw": brand_raw, "price": offer["price"],
            "currency": offer["currency"], "in_stock": offer["in_stock"], "image": offer.get("image"), "ean": ean,
            "ref": ref}


def read_page(fetcher, store_id, url, now):
    src = SOURCES[store_id]
    rec = {"store": store_id, "url": url, "checked": now, "status": "error"}
    try:
        # "fetch" / "page_url": otra URL con los datos de la ficha (Shopify: /products/<handle>.json, con el precio en la
        # moneda de la tienda); la oferta sigue siendo la ficha.
        page = src["fetch"](url) if "fetch" in src else src["page_url"](url) if "page_url" in src else url
        allowed, info = fetcher.allowed(page)
        if not allowed:
            rec["status"] = "robots_disallowed"
            return rec
        resp = fetcher.get(page)
        if resp.status_code in (404, 410):
            rec["status"] = "gone"
            return rec
        if resp.status_code not in src.get("ok_status", (200,)) or is_challenge(resp):
            rec.update(status="blocked_403" if resp.status_code == 403 or is_challenge(resp) else "error",
                       http_status=resp.status_code)
            return rec
        soup = BeautifulSoup(resp.text, "html.parser")
        data = src["parse"](soup, resp.text) if "parse" in src else _parse_jsonld(soup, store_id)
        if "fix" in src:
            data = src["fix"](data, resp.text)
        if not data["crumbs"] and "crumbs" in src:
            data["crumbs"] = src["crumbs"](url)  # tiendas sin breadcrumb: la categoría de la URL (MAT)
        kind = src["kind_url"](data["crumbs"], url, data.get("name")) if "kind_url" in src else src["kind"](data["crumbs"])
        if not kind:
            rec["status"] = "not_guitar"
            return rec
        if data.get("price") is None:
            rec["status"] = "no_price"
            return rec
        brand = canonical_brand(data["brand_raw"])
        rec.update(status="ok" if data["currency"] == CATALOG.get("cur", "EUR") else "wrong_currency",
                   ean=data["ean"].lstrip("0") if data.get("ean") else None, brand=brand,
                   name=clean_name(data["name"], data["brand_raw"], brand), kind=kind, type=guitar_type(data["crumbs"], kind),
                   price=data["price"], currency=data["currency"], in_stock=data["in_stock"], image=data.get("image"))
        if data.get("ref"):
            rec["ref"] = data["ref"]
    except requests.RequestException as exc:
        rec["note"] = type(exc).__name__
    except Exception as exc:  # noqa: BLE001 - una ficha rara no para el lote
        rec["note"] = f"{type(exc).__name__}: {exc}"[:200]
    return rec


def due_urls(store_id, urls, offers, now):
    """Orden de visita: nunca leídas, luego las más antiguas. Las que no son guitarra esperan 60 días."""
    skip_before = (datetime.fromisoformat(now) - timedelta(days=RECHECK_SKIPPED_DAYS)).isoformat()
    no_price_before = (datetime.fromisoformat(now) - timedelta(days=RECHECK_NO_PRICE_DAYS)).isoformat()
    fresh, old = [], []
    for url in urls:
        o = offers.get(url)
        if o is None:
            fresh.append(url)
        elif o.get("status") in ("not_guitar", "gone") and o["checked"] > skip_before:
            continue
        elif o.get("status") == "no_price" and o["checked"] > no_price_before:
            continue
        else:
            old.append((o["checked"], url))
    return fresh + [u for _, u in sorted(old)]


def scan_store(store_id, offers, minutes, limit):
    src = SOURCES[store_id]
    fetcher = Fetcher(src.get("delay", DELAY))
    fetcher.session.headers.update(CATALOG.get("headers", {}))  # Reino Unido e Irlanda: en inglés (A Strings traduce)
    now = now_iso()
    out = {"store": store_id, "sitemap": None, "records": []}
    try:
        urls = src["discover"](fetcher) if "discover" in src else sitemap_urls(fetcher, src["sitemap"], src.get("sub"))
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
        if rec.get("http_status") == 429:
            print(f"[{store_id}] 429: la tienda pide parar; se sigue mañana", flush=True)
            break
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
            if rec["status"] == "ok" and rec.get("price") is not None:
                # Sin EAN (Egitana, Thomann) el histórico va por URL; al construir se junta con el de su producto.
                series = history.setdefault(rec.get("ean") or "url:" + rec["url"], {}).setdefault(rec["store"], [])
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


def series_for(keys, history):
    """{tienda: [[día, precio], ...]} de un producto juntando sus claves de histórico (EAN y URLs sin EAN)."""
    out = {}
    for k in keys:
        for store, pts in history.get(k, {}).items():
            out.setdefault(store, pts)
    return out


MANUAL_DAYS = 3  # un precio añadido a mano (captura) se muestra como mucho estos días


def _manual_offers():
    """Precios añadidos a mano (data/manual_offers.json), solo los de los últimos MANUAL_DAYS días."""
    data = load(ROOT / "data" / "manual_offers.json", {})
    since = (datetime.now(timezone.utc) - timedelta(days=MANUAL_DAYS)).date().isoformat()
    return [o for o in data.get("offers", []) if o.get("price") and o.get("date", "") >= since], data.get("stores", {})


def _attach_manual(products, manual):
    """Añade cada precio a mano a su guitarra (por EAN, o por nombre y marca si no hay EAN)."""
    for m in manual:
        ean = normalize_id(m.get("ean") or "").lstrip("0")
        target = next((p for p in products if ean and p.get("ean") == ean), None)
        if target is None and m.get("name"):
            scored = sorted(((name_match_score(m["name"], p["name"], p.get("brand") or ""), i) for i, p in enumerate(products)
                             if (p.get("brand") or "").lower() == (m.get("brand") or "").lower()), reverse=True)
            if scored and scored[0][0] >= NAME_MATCH_MIN:
                target = products[scored[0][1]]
        if target is None or any(i["s"] == m["store"] for i in target["items"]):
            continue
        target["items"].append({"s": m["store"], "p": float(m["price"]), "u": affiliates.wrap(m["store"], m["url"]),
                                "st": m.get("in_stock"), "d": m["date"], "m": True})
        target["items"].sort(key=lambda i: i["p"])


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
        if not ean or i.get("price") is None or store.get("reference"):
            continue
        out.setdefault(ean, []).append({"s": i["store"], "p": i["price"], "u": affiliates.wrap(i["store"], i.get("url")),
                                        "st": i.get("in_stock"), "d": (i.get("price_date") or "")[:10]})
    # Ficha de las guitarras seguidas, para las que no aparecen en ninguna tienda del catálogo.
    info = {by_sku[p["sku"]]: p for p in latest.get("products", []) if p["sku"] in by_sku and p.get("category", "guitarra") == "guitarra"}
    return out, {s: stores[s]["name"] for s in stores}, {v: k for k, v in by_sku.items()}, info


def _products(kind, offers, history, curated, sku_by_ean, curated_info):
    """Productos de una categoría: agrupa las fichas por EAN (o nombre) y les añade tiendas de seguimiento."""
    from .thumbs import existing, slenderness  # import aquí: thumbs importa este módulo
    groups = {}
    for o in offers:
        if o.get("status") != "ok" or o.get("price") is None or NOT_PRODUCT.search(o["name"]):
            continue
        if o["price"] < MIN_PRICE.get(kind, 0):
            continue  # accesorio colado (cejillas, armónicas…) cuyo nombre no dice lo que es
        groups.setdefault(o.get("ean") or "url:" + o["url"], []).append(tidy(o))
    # Fichas sin EAN (Egitana): se unen al producto con EAN cuyo nombre coincide sin dudas.
    by_brand = {}
    for key, group in groups.items():
        if not key.startswith("url:"):
            ref = next((o for o in group if o["store"] == "numemusic"), group[0])
            by_brand.setdefault(ref["brand"], []).append((ref["name"], key))
    for key in [k for k in groups if k.startswith("url:")]:
        o = groups[key][0]
        scored = sorted(((name_match_score(o["name"], name, o["brand"]), k) for name, k in by_brand.get(o["brand"], [])),
                        reverse=True)
        if scored and scored[0][0] >= NAME_MATCH_MIN and (len(scored) == 1 or scored[0][0] - scored[1][0] >= NAME_MATCH_MARGIN):
            target = groups[scored[0][1]]
            if o["store"] not in {x["store"] for x in target}:
                target.append(o)
                del groups[key]
    # Mismo EAN pero producto distinto (EAN mal puesto en una tienda) → se separan. Solo el primer grupo,
    # el de Numemusic si está, conserva el EAN (histórico y cruce con las tiendas de seguimiento).
    clusters = []
    for key, group in groups.items():
        # Nombre y foto preferidos: Numemusic (tienda española, nombres completos).
        group.sort(key=lambda o: (o["store"] != "numemusic", o["price"]))
        parts = []
        for o in group:
            target = next((p for p in parts if same_product(p[0], o)), None)
            if target is None:
                parts.append([o])
            else:
                target.append(o)
        clusters += [(i == 0, part) for i, part in enumerate(parts)]
    # Las fichas separadas (EAN mal puesto) se unen a otro producto con su mismo código de modelo y marca.
    by_code = {}
    for keeps_ean, part in clusters:
        codes = MODEL_CODE.findall(part[0]["name"].lower())
        if keeps_ean and len(codes) == 1:
            by_code.setdefault((part[0]["brand"], codes[0]), part)
    kept = []
    for keeps_ean, part in clusters:
        codes = MODEL_CODE.findall(part[0]["name"].lower())
        home = by_code.get((part[0]["brand"], codes[0])) if not keeps_ean and len(codes) == 1 else None
        if home is not None and not {o["store"] for o in home} & {o["store"] for o in part}:
            home += part
        else:
            kept.append((keeps_ean, part))
    clusters = kept
    products = []
    for keeps_ean, group in clusters:
        main = group[0]
        ean = main.get("ean") if keeps_ean else None
        items = [{"s": o["store"], "p": o["price"], "u": affiliates.wrap(o["store"], o["url"]), "st": o.get("in_stock"),
                  "d": o["checked"][:10]}
                 for o in group]
        # Tiendas de seguimiento que el catálogo aún no ha leído para este producto.
        seen = {o["store"] for o in group}
        items += [c for c in curated.get(ean, []) if c["s"] not in seen] if ean else []
        items.sort(key=lambda i: i["p"])
        # Claves de histórico del producto: su EAN y la URL de cada ficha sin EAN.
        hk = ([ean] if ean else []) + ["url:" + o["url"] for o in group if not o.get("ean")]
        series = series_for(hk, history)
        days = {d for s in series.values() for d, _ in s}
        low = min((p for s in series.values() for _, p in s), default=None) if len(days) > 1 else None
        # Tipo: el más concreto entre las tiendas.
        types = [o["type"] for o in group if o.get("type") and o["type"] != "Otras"]
        prod = {"id": ean or main["url"], "ean": ean, "name": main["name"], "brand": main.get("brand"),
                "type": types[0] if types else "Otras", "img": next((o["image"] for o in group if o.get("image")), None),
                "items": items, "low": low}
        if hk != [ean]:
            prod["hk"] = hk
        if any(o["lh"] for o in group):
            prod["lh"] = True
        # Miniatura: entre las fotos de todas las tiendas, la que muestra la guitarra entera (la más esbelta).
        # Un primer plano del cuerpo (poco esbelto) no se usa: mejor sin foto que una que rompe la cuadrícula.
        thumbs = [t for t in (existing(o.get("image")) for o in group) if t]
        if kind not in GUITAR_KINDS:
            if thumbs:
                prod["th"] = thumbs[0]  # teclados y pedales: la primera foto (la de Numemusic si está)
        else:
            best = max(thumbs, key=slenderness) if thumbs else None
            if best and slenderness(best) >= MIN_SLENDERNESS:
                prod["th"] = best
        if ean in sku_by_ean:
            prod["sku"] = sku_by_ean[ean]
        products.append(prod)
    # Guitarras de seguimiento que no están en las tiendas del catálogo (p. ej. solo en Thomann).
    present = {p["ean"] for p in products if p["ean"]}
    for ean, p in curated_info.items():
        if ean in present or not curated.get(ean):
            continue
        items = sorted(curated[ean], key=lambda i: i["p"])
        prod = {"id": ean, "ean": ean, "name": p["name"], "brand": p.get("brand"),
                "type": type_from_name(p["name"], kind=kind), "img": p.get("image"), "items": items, "low": None,
                "sku": p["sku"]}
        if p.get("thumb"):
            prod["th"] = p["thumb"]
        products.append(prod)
    products.sort(key=lambda p: (-len(p["items"]), p["name"]))
    return products


def build(offers=None, history=None):
    offers = offers if offers is not None else load(DIR / "offers.json", {})
    history = history if history is not None else load(DIR / "history.json", {})
    curated, store_names, sku_by_ean, curated_info = _curated_offers()
    manual, manual_names = _manual_offers()
    names = {s: SOURCES[s]["name"] for s in SOURCES} | store_names | manual_names
    # Una ficha sin EAN que ya está en seguimiento (Thomann) saldría duplicada: se deja solo la de seguimiento.
    # Las que tienen EAN se quedan (traen la foto); la de seguimiento no se repite en la misma tienda.
    followed = {i["url"] for s in load(ROOT / "stores.json", []) for i in s.get("items", [])}
    for kind, fname in CATALOG["files"].items():
        mine = [o for o in offers.values() if (o.get("kind") or "electrica") == kind
                and (o.get("ean") or o["url"] not in followed)
                # Teclados y pedales: un accesorio leído antes de afinar el filtro tampoco entra.
                and (kind in GUITAR_KINDS or not (MAS_DROP if kind in MAS_KINDS else EQUIPO_SKIP).search(o.get("name") or ""))
                and (o.get("price") or 0) <= CATALOG.get("max_price", MAX_PRICE).get(kind, float("inf"))
                and not (kind == "estuche" and WITH_CASE.search(o.get("name") or ""))
                and not (kind == "micro" and _MIC_ACC.search(o.get("name") or ""))
                and not (kind == "varios" and _NOT_GUITAR_ACC.search(o.get("name") or ""))]
        spain = CATALOG.get("site", "es") == "es"
        if CATALOG.get("min_price"):  # en otra moneda, el mínimo de MIN_PRICE (en euros) no sirve
            mine = [o for o in mine if (o.get("price") or 0) >= CATALOG["min_price"]]
        if not spain:
            skip = CATALOG.get("name_skip", {"pt": PT_NAME_SKIP, "fr": FR_NAME_SKIP, "it": IT_NAME_SKIP, "uk": UK_NAME_SKIP,
                                              "de": DE_NAME_SKIP, "br": BR_NAME_SKIP, "ie": UK_NAME_SKIP, "at": DE_NAME_SKIP,
                                              "nl": UK_NAME_SKIP}[CATALOG["site"]])
            if skip:
                mine = [o for o in mine if not skip.search(o.get("name") or "")]
        # Las tiendas de seguimiento (products.json) y los precios a mano son de España (eléctricas).
        extra = (curated, sku_by_ean, curated_info) if kind == "electrica" and spain else ({}, {}, {})
        products = _products(kind, mine, history, *extra)
        if spain:
            _attach_manual(products, manual)
        for p in products:
            p["slug"] = pages.slug_for(p)
        used = {i["s"] for p in products for i in p["items"]}
        write(DIR / fname, {"updated": now_iso(), "kind": kind, "stores": {s: names.get(s, s) for s in sorted(used)},
                            "products": products})
        multi = sum(len({i["s"] for i in p["items"]}) > 1 for p in products)
        print(f"catálogo {kind}: {len(products)} guitarras, {multi} en más de una tienda", flush=True)
        if not spain:
            continue  # otros países: su web (scraper.intl) se genera al final
        pages.write_pages(kind, products, names)
        curated_records = load(ROOT / "data" / "history.json", []) if kind == "electrica" else []
        deals.build(kind, products, history, curated_records, names)
    if CATALOG.get("site", "es") == "es":
        pages.write_hubs()
    else:
        from . import intl
        intl.write_site(CATALOG["site"])


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", choices=sorted(CATALOGS), default="electrica", help="catálogo (carpeta y tiendas)")
    parser.add_argument("--only", help="tiendas separadas por comas")
    parser.add_argument("--minutes", type=float, default=50, help="tope de tiempo por tienda")
    parser.add_argument("--limit", type=int, help="máximo de fichas por tienda")
    parser.add_argument("--records-out", help="guarda el lote en este fichero (CI)")
    parser.add_argument("--merge", help="fusiona en la carpeta del catálogo un lote de --records-out")
    parser.add_argument("--build", action="store_true", help="solo regenera los JSON de la web")
    args = parser.parse_args(argv)
    use(args.cat)
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
