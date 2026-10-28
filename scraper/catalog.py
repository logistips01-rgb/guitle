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
import gzip
import html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from . import affiliates, analytics, deals, jsonld, pages
from .common import normalize_id
from .fetch import DELAY, Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "catalog"
RECHECK_SKIPPED_DAYS = 60  # fichas que no son guitarra: no se vuelven a pedir en este tiempo
RECHECK_NO_PRICE_DAYS = 14  # fichas de guitarra sin precio (no disponibles): se miran cada dos semanas
DROP_AFTER_DAYS = 30       # ofertas que desaparecen del sitemap y no se han leído en este tiempo
MIN_PRICE = {"electrica": 60, "acustica": 40, "clasica": 35,  # por debajo no es una guitarra (ni infantil)
             "teclado": 40, "pedal": 20, "portuguesa": 150}
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


def _discover_shopify(fetcher, base, collections):
    """Fichas de unas colecciones de Shopify (products.json, 250 por página)."""
    urls = set()
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
            urls |= {f"{base}/products/{p['handle']}" for p in products}
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
                 "teclado": KEYBOARD_TYPES, "pedal": PEDAL_TYPES, "portuguesa": PORTUGUESE_TYPES}
NAME_TYPES_BY_KIND = {"electrica": NAME_TYPES, "acustica": ACOUSTIC_TYPES, "clasica": CLASSICAL_TYPES,
                      "teclado": KEYBOARD_TYPES, "pedal": PEDAL_TYPES, "portuguesa": PORTUGUESE_TYPES}

# Catálogos: carpeta, fuentes y fichero de la web por categoría.
CATALOGS = {
    "electrica": {"dir": DIR, "sources": SOURCES, "files": {"electrica": "products.json"}},
    "acustica": {"dir": DIR / "acusticas", "sources": ACOUSTIC_SOURCES,
                 "files": {"acustica": "acusticas.json", "clasica": "clasicas.json"}},
    "equipo": {"dir": DIR / "equipo", "sources": EQUIPO_SOURCES,
               "files": {"teclado": "teclados.json", "pedal": "pedales.json"}},
    # Portugal: aún sin páginas propias (guitle.com/pt/ llegará después); solo los JSON del catálogo.
    "pt": {"dir": DIR / "pt", "sources": PT_SOURCES, "site": "pt",
           "files": {"electrica": "eletricas.json", "acustica": "acusticas.json", "clasica": "classicas.json",
                     "portuguesa": "portuguesas.json"}},
    # Francia: igual, guitle.com/fr/ llegará después.
    "fr": {"dir": DIR / "fr", "sources": FR_SOURCES, "site": "fr",
           "files": {"electrica": "electriques.json", "acustica": "folk.json", "clasica": "classiques.json"}},
}
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
        allowed, info = fetcher.allowed(url)
        if not allowed:
            rec["status"] = "robots_disallowed"
            return rec
        resp = fetcher.get(url)
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
        rec.update(status="ok" if data["currency"] == "EUR" else "wrong_currency",
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
                and (kind in GUITAR_KINDS or not EQUIPO_SKIP.search(o.get("name") or ""))]
        spain = CATALOG.get("site", "es") == "es"
        if not spain:
            skip = {"pt": PT_NAME_SKIP, "fr": FR_NAME_SKIP}[CATALOG["site"]]
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
