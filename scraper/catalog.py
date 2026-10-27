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
MIN_SLENDERNESS = 1.7      # alto/ancho mínimo de la miniatura de una guitarra entera (un primer plano ronda 1)

NOT_PRODUCT = re.compile(r"b-stock|bstock|outlet|usad[ao]|segunda-mano|gebraucht|pre-owned|\bused\b|demo|vorfuehr|gutschein|stock[ -]b\b", re.I)

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


def _discover_thomann(fetcher, codes):
    urls = set()
    for code in codes:
        for pg in range(1, THOMANN_MAX_PAGES + 1):
            url = f"{THOMANN}cat_GK_{code}.html?ls=100&pg={pg}"
            if not fetcher.allowed(url)[0]:
                break
            resp = fetcher.get(url)
            if resp.status_code == 429:
                raise RuntimeError("HTTP 429")
            if resp.status_code != 200:
                break
            found = {THOMANN + h.split("?")[0] for h in re.findall(r'class="product__content[^"]*"\s+href="([^"]+\.htm)[?"]', resp.text)}
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
}

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
TYPES_BY_KIND = {"electrica": TYPES, "acustica": ACOUSTIC_TYPES, "clasica": CLASSICAL_TYPES}
NAME_TYPES_BY_KIND = {"electrica": NAME_TYPES, "acustica": ACOUSTIC_TYPES, "clasica": CLASSICAL_TYPES}

# Catálogos: carpeta, fuentes y fichero de la web por categoría.
CATALOGS = {
    "electrica": {"dir": DIR, "sources": SOURCES, "files": {"electrica": "products.json"}},
    "acustica": {"dir": DIR / "acusticas", "sources": ACOUSTIC_SOURCES,
                 "files": {"acustica": "acusticas.json", "clasica": "clasicas.json"}},
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
          "sterling by music man": "Sterling", "prs se": "PRS", "prs (paul reed smith)": "PRS", "paul reed smith": "PRS"}


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
    name = re.sub(r"\s+", " ", name or "").strip()
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


def type_from_name(name, url="", kind="electrica"):
    text = name.lower() + " " + url.rsplit("/", 1)[-1].replace("-", " ")
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
# Acabados abreviados (Thomann: "Player II Strat MN AQB") → nombre completo, como Numemusic.
COLOR_CODES = {"3ts": "3 color sunburst", "3cs": "3 color sunburst", "3 tone sunburst": "3 color sunburst",
               "2ts": "2 color sunburst", "2cs": "2 color sunburst", "owt": "olympic white", "pwt": "polar white",
               "aqb": "aquatone blue", "car": "candy apple red", "lpb": "lake placid blue", "sfg": "sea foam green",
               "frd": "fiesta red", "aw": "arctic white", "vw": "vintage white", "hcs": "heritage cherry sunburst",
               "hc": "heritage cherry", "vs": "vintage sunburst", "ebo": "ebony", "tbs": "tobacco burst",
               "wr": "wine red", "nat": "natural", "sb": "sunburst", "csb": "cherry sunburst", "bkm": "black metallic"}
NAME_STOPWORDS = {"fingerboard", "fretboard", "guitar", "guitarra", "electrica", "eléctrica", "electric", "with", "con",
                  "w", "and", "y", "the", "series", "guitars", "wpg", "bpg", "tpg", "mpg"}


def name_tokens(name, brand):
    n = name.lower().replace("\u2019", "'")
    for b in {brand.lower(), "squier by fender", "fender squier", "esp ltd"} if brand else ():
        n = n.replace(b, " ")
    for pat, short in FINGERBOARDS:
        n = re.sub(pat, " " + short + " ", n)
    n = re.sub(r"(\d)-(color|tone)\b", r"\1 \2", n)
    for code, full in COLOR_CODES.items():
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


def same_product(a, b):
    ca, cb = set(MODEL_CODE.findall(a["name"].lower())), set(MODEL_CODE.findall(b["name"].lower()))
    if ca and cb and not ca & cb:
        return False
    ta, tb = _tokens(a), _tokens(b)
    return len(ta & tb) / max(1, len(ta | tb)) >= 0.1


def tidy(o):
    """Normalización al construir (se aplica también a fichas ya leídas): marca, nombre, tipo y zurdas."""
    o = dict(o)
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
    leaf = (crumbs[-1] if kind == "electrica" else " / ".join(crumbs[-2:])).lower() if crumbs else ""
    leaf = re.sub(r"cl[aá]sicas y flamencas", "", leaf)  # categoría mixta de Numemusic: no dice si es flamenca
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
    locs = [re.sub(r"^<!\[CDATA\[|\]\]>$", "", l.strip()) for l in re.findall(r"<loc>\s*(.*?)\s*</loc>", text)]
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
    return {"crumbs": crumbs, "name": product.get("name"), "brand_raw": brand_raw, "price": offer["price"],
            "currency": offer["currency"], "in_stock": offer["in_stock"], "image": offer.get("image"), "ean": ean}


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
        kind = src["kind"](data["crumbs"])
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
    names = {s: SOURCES[s]["name"] for s in SOURCES} | store_names
    # Fichas que ya están en seguimiento (con su EAN): no se duplican desde el catálogo.
    followed = {i["url"] for s in load(ROOT / "stores.json", []) for i in s.get("items", [])}
    for kind, fname in CATALOG["files"].items():
        mine = [o for o in offers.values() if (o.get("kind") or "electrica") == kind and o["url"] not in followed]
        # Las tiendas de seguimiento (products.json) son de eléctricas.
        extra = (curated, sku_by_ean, curated_info) if kind == "electrica" else ({}, {}, {})
        products = _products(kind, mine, history, *extra)
        for p in products:
            p["slug"] = pages.slug_for(p)
        used = {i["s"] for p in products for i in p["items"]}
        write(DIR / fname, {"updated": now_iso(), "kind": kind, "stores": {s: names.get(s, s) for s in sorted(used)},
                            "products": products})
        multi = sum(len({i["s"] for i in p["items"]}) > 1 for p in products)
        print(f"catálogo {kind}: {len(products)} guitarras, {multi} en más de una tienda", flush=True)
        pages.write_pages(kind, products, names)
        curated_records = load(ROOT / "data" / "history.json", []) if kind == "electrica" else []
        deals.build(kind, products, history, curated_records, names)
    pages.write_hubs()


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
