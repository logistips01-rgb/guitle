"""Publicación diaria en Instagram (@guitle.es): elige el contenido del día con los precios reales, genera las
imágenes (brand/social.js) y las publica con la API de Instagram.

Cada día: un post en el feed, alternando
  - "chollo": la guitarra con la mejor rebaja (mínimo histórico > bajada real > bajada de hoy > bajo PVP > más barata
    que en el resto de tiendas), en post 4:5;
  - "top": carrusel con 5 guitarras populares (las que más tiendas venden) de un rango de precio, rotando categoría y
    rango;
un Reel con el mismo contenido animado (brand/reel.js; no se publica solo: el usuario le pone música y lo sube,
y sirve también para TikTok) y stories con los chollos del día, a mediodía y por la tarde (--tarde). No repite guitarras publicadas hace poco (mira los textos ya publicados).

Instagram descarga las imágenes de una URL pública: se suben al repo (social/<fecha>/) y se usa la URL raw del commit.
La API va por graph.instagram.com con el token que inyecta el proxy del entorno (no hay token en el repo).

Uso:
    python -m scraper.instagram             # genera social/<fecha>/ sin publicar (para revisar)
    python -m scraper.instagram --publish   # genera, sube a la rama actual y publica
    python -m scraper.instagram --tarde [--publish]      # stories de la tarde con otros chollos
    python -m scraper.instagram --arranque [--publish]   # presentación y "¿Cómo funciona?" con las cifras de hoy
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median

import requests

from .catalog import load
from .fetch import Fetcher
from . import musica_libre as musica
from .thumbs import name_for, normalize

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "social"
API = "https://graph.instagram.com/v23.0"
REPO_RAW = "https://raw.githubusercontent.com/logistips01-rgb/guitle"
CATALOGS = {"electrica": ROOT / "data/catalog/products.json",
            "acustica": ROOT / "data/catalog/acusticas/acusticas.json",
            "clasica": ROOT / "data/catalog/acusticas/clasicas.json"}
KIND_NAMES = {"electrica": ("eléctrica", "eléctricas"), "acustica": ("acústica", "acústicas"), "clasica": ("clásica", "clásicas")}
# Rangos de los tops, en el orden en que rotan (uno cada dos días).
TOPS = [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
        ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)]
MIN_PRICE = 150      # franja de precios que pide el usuario (y por debajo suelen ser packs o errores de catálogo)
MAX_PRICE = 750
MIN_STORES = 3       # para hablar de "el mejor precio" tiene que haber con qué comparar
STORIES = 3          # chollos en stories en cada tanda (mediodía y tarde)
ETIQUETAR = False    # etiquetas y menciones de marcas: apagadas tras la caída de alcance del 2-11-2026 (se pueden volver a encender)
REEL_AUTO = True     # los Reels se publican solos, con música libre de derechos (scraper/musica_libre.py) mezclada en el vídeo
HASHTAGS = {"electrica": "#guitarraelectrica", "acustica": "#guitarraacustica", "clasica": "#guitarraclasica"}


def eur(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return (s[:-3] if s.endswith(",00") else s) + " €"


ACRONYMS = {"LTD", "ESP", "EVH", "PRS", "SG", "HSS", "HH", "SSS", "RW", "MN", "EB", "LH", "CE", "FR", "II", "III", "IV", "USA", "MIM", "BPG"}


def tidy(name):
    """Nombres en mayúsculas de algunas tiendas ("LES PAUL STANDARD") → "Les Paul Standard"."""
    name = name.strip().rstrip(".")
    words = name.split()
    upper = [w for w in words if w.isalpha() and w.isupper() and len(w) > 2]
    if len(upper) < len(words) / 2:
        return name
    return " ".join(w if w in ACRONYMS or not (w.isalpha() and w.isupper()) else w.capitalize() for w in words)


def tag(s):
    return "#" + re.sub(r"[^0-9a-záéíóúñ]", "", s.lower())


# --- Datos ---------------------------------------------------------------------------------------------------

MAX_SALTO = 1.35  # la siguiente tienda puede costar como mucho un 35 % más que la más barata


def products(lo=MIN_PRICE, hi=MAX_PRICE, catalogs=None):
    """Guitarras del catálogo con foto, en stock en varias tiendas y con su mejor precio (España por defecto)."""
    pvp = load(ROOT / "data/catalog/pvp.json", {}).get("prices", {}) if catalogs is None else {}
    out = []
    for kind, path in (catalogs or CATALOGS).items():
        cat = load(path, {})
        # Frescura: el último día con lecturas en el catálogo y el anterior (como los chollos de la web)
        ultima = max((str(i.get("d"))[:10] for p in cat.get("products", []) for i in p.get("items", []) if i.get("d")),
                     default=datetime.now(timezone.utc).date().isoformat())
        fresco = (date.fromisoformat(ultima) - timedelta(days=1)).isoformat()
        stores = cat.get("stores", {})
        for p in cat.get("products", []):
            # Solo ofertas en stock y leídas en los 2 últimos días: un stock de hace días puede haberse agotado (Alteisa, 8-11)
            items = sorted((i for i in p.get("items", []) if i.get("p") and i.get("st") is not False
                            and str(i.get("d") or fresco)[:10] >= fresco), key=lambda i: i["p"])
            if not p.get("img") or len({i["s"] for i in items}) < MIN_STORES or not lo <= items[0]["p"] <= hi:
                continue
            best = items[0]
            prices = [i["p"] for i in items]
            # Rebaja increíble (la más barata, más de un 35 % por debajo de la siguiente tienda): suele ser un precio de
            # reclamo sin stock real (Alteisa, Pacifica, 8-11); se cambia la guitarra
            if min(i["p"] for i in items if i["s"] != best["s"]) > MAX_SALTO * best["p"]:
                continue
            ref = pvp.get(p.get("sku") or "", [])
            out.append({"slug": p["slug"], "name": tidy(p["name"]), "brand": p.get("brand") or "", "kind": kind,
                        "img": p["img"], "th": p.get("th"), "thimg": p.get("thimg"), "price": best["p"], "store": stores.get(best["s"], best["s"]),
                        "stores": len({i["s"] for i in items}), "median": median(prices[1:]), "max": prices[-1],
                        "next": min(i["p"] for i in items if i["s"] != best["s"]),
                        "rows": [[stores.get(i["s"], i["s"]), i["p"]] for i in {i["s"]: i for i in reversed(items)}.values()][::-1],
                        "pvp": ref[-1][1] if ref else None})
    return out


def deals_by_slug():
    """Chollos con histórico (scraper/deals.py): slug → (prioridad, % de rebaja, texto)."""
    out = {}
    for kind in CATALOGS:
        d = load(ROOT / f"data/deals-{kind}.json", {})
        for r in d.get("records", []):
            out[r["slug"]] = (4, -r["vs_avg"], f"Mínimo histórico: {abs(r['vs_avg']):.0f} % por debajo de su media")
        for r in d.get("real_drops", []):
            out.setdefault(r["slug"], (3, -r["vs_avg"], f"Bajada real: {abs(r['vs_avg']):.0f} % por debajo de su media"))
        for r in d.get("today", []):
            pct = -r["vs_yesterday"] / (r["price"] - r["vs_yesterday"]) * 100
            out.setdefault(r["slug"], (2, pct, f"Rebajada hoy: {eur(-r['vs_yesterday'])} menos que ayer"))
    return out


def monetiza(tienda):
    """eBay y Amazon: Manuel cobra comisión por sus ventas, así que sus chollos se anuncian primero (10-11)."""
    t = (tienda or "").lower()
    return "ebay" in t or "amazon" in t


def rank_deals(prods, recent, menos=None):
    """Chollos del día de mejor a peor, sin guitarras ya publicadas y sin repetir marca seguida.
    menos(diferencia) da el texto de "X menos que en cualquier otra tienda" en otro idioma y moneda (solo hay
    histórico y PVP de España)."""
    hist = deals_by_slug() if menos is None else {}
    scored = []
    for p in prods:
        if p["name"] in recent:
            continue
        if p["slug"] in hist:
            prio, pct, why = hist[p["slug"]]
        elif p["pvp"] and p["price"] <= p["pvp"] * 0.85:
            prio, pct = 1, (1 - p["price"] / p["pvp"]) * 100
            why = f"{pct:.0f} % por debajo del PVP oficial ({eur(p['pvp'])})"
        elif p["price"] <= p["next"] * 0.9:  # frente a la siguiente tienda más barata, no a la media
            prio, pct = 0, (1 - p["price"] / p["next"]) * 100
            why = menos(p["next"] - p["price"]) if menos else f"{eur(p['next'] - p['price'])} menos que en cualquier otra tienda"
        else:
            continue
        if pct > 60:  # rebajas tan grandes suelen ser un error de emparejamiento, no un chollo
            continue
        # Primero los chollos de eBay y Amazon (comisión), luego el resto
        scored.append(((monetiza(p["store"]), prio, pct + min(p["stores"], 10)), {**p, "why": why, "pct": round(pct)}))
    scored.sort(key=lambda x: x[0], reverse=True)
    out, brands = [], []
    for _, p in scored:
        if brands[-1:] == [p["brand"]]:
            continue
        out.append(p)
        brands.append(p["brand"])
    return out


def top_of(prods, kind, lo, hi, recent, n=15):
    """Guitarras populares (más tiendas) del rango, como mucho una por marca, de más a menos popular. Se piden de
    sobra porque algunas fotos no se pueden descargar; el post se queda con las 5 primeras que tienen foto."""
    # Solo las de foto revisada (las demás se descartan luego en with_photos y harían perder su marca entera)
    pool = sorted((p for p in prods if p["kind"] == kind and lo <= p["price"] < hi and foto_revisada(p)),
                  key=lambda p: (p["name"] in recent, -p["stores"], p["price"]))
    out, brands = [], set()
    for p in pool:
        if p["brand"] not in brands:
            out.append(p)
            brands.add(p["brand"])
        if len(out) == n:
            break
    return out


# --- Instagram ------------------------------------------------------------------------------------------------

TOKEN = None  # token de la cuenta en la que se publica; sin él, INSTAGRAM_TOKEN_ES o el del proxy (@guitle.es)


def api(method, path, **params):
    token = TOKEN or os.environ.get("INSTAGRAM_TOKEN_ES")
    if token:
        params["access_token"] = token
    r = requests.request(method, f"{API}/{path}", params=params if method == "GET" else None,
                         data=params if method == "POST" else None, timeout=60)
    j = r.json()
    if "error" in j:
        raise RuntimeError(f"{path}: {j['error'].get('message')}")
    return j


def recent_captions(user, limit=60):
    try:
        return "\n".join(m.get("caption", "") for m in api("GET", f"{user}/media", fields="caption", limit=limit)["data"])
    except Exception as exc:  # sin acceso a la API (p. ej. en local): no se filtra
        print(f"aviso: no se leen las publicaciones anteriores ({exc})", file=sys.stderr)
        return ""


def container(user, tries=40, **params):
    if params.get("media_type") == "REELS":
        # Portada: el fotograma de 1,5 s (la primera escena ya entera, con su guitarra), no el primero, que sale casi vacío
        params.setdefault("thumb_offset", "1500")
    cid = api("POST", f"{user}/media", **params)["id"]
    for _ in range(tries):
        status = api("GET", cid, fields="status_code").get("status_code")
        if status == "FINISHED":
            return cid
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"contenedor {cid}: {status}")
        time.sleep(3)
    raise RuntimeError(f"contenedor {cid}: no termina")


def publish(user, cid):
    try:
        mid = api("POST", f"{user}/media_publish", creation_id=cid)["id"]
    except RuntimeError:
        # A veces Instagram responde «Fatal» pero publica igual: si el contenedor ya está publicado, se da por bueno
        for _ in range(4):
            time.sleep(15)
            try:
                if api("GET", cid, fields="status_code").get("status_code") == "PUBLISHED":
                    break
            except RuntimeError:
                pass
        else:
            raise
        mid = api("GET", f"{user}/media", fields="id", limit=1)["data"][0]["id"]
    return api("GET", mid, fields="permalink").get("permalink")


# --- Etiquetas de las marcas (para que las vean y, con suerte, republiquen) ----------------------------------------

def _norm(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).lower().strip()


MARCAS = {_norm(k): v for k, v in load(ROOT / "social/marcas.json", {}).get("cuentas", {}).items() if v}


def cuentas(items):
    """Cuentas de Instagram (comprobadas en social/marcas.json) de las marcas de esas guitarras, sin repetir (máx. 20)."""
    out = []
    if not ETIQUETAR:
        return out
    for p in items:
        h = MARCAS.get(_norm(p.get("brand")))
        if h and h not in out:
            out.append(h)
    return out[:20]


def marcas_post(post, i=None):
    """Guitarras de la imagen i del post (None = todas): portada del top con todas, cada diapositiva con la suya."""
    picks = post.get("picks") or []
    todas = picks + ([post["deal"]] if post.get("deal") else [])
    if i is None:
        return todas
    if post.get("type") == "top" and picks:
        return picks if i == 0 else picks[i - 1:i]
    return todas if i == 0 else []


def marcas_reel(sub):
    return marcas_post(load(sub / "plan.json", {}).get("post") or {})


def menciones(caption, handles):
    return f"{caption}\n\n" + " ".join("@" + h for h in handles) if handles else caption


def container_etiq(user, handles, **params):
    """Como container(), con las marcas etiquetadas; si Instagram no acepta la etiqueta, se publica sin ella."""
    if handles:
        foto = "video_url" not in params
        tags = [{"username": h, **({"x": round((i + 1) / (len(handles) + 1), 2), "y": 0.45} if foto else {})}
                for i, h in enumerate(handles)]
        try:
            return container(user, user_tags=json.dumps(tags), **params)
        except RuntimeError as exc:
            print(f"aviso: sin etiquetas de marca ({exc})", file=sys.stderr)
    return container(user, **params)


# --- Plan del día ----------------------------------------------------------------------------------------------

def photo(p, fetcher, dest, rotate=True):
    """Foto en alta resolución, recortada y en vertical (como las miniaturas de la web)."""
    data = None
    src = foto_src(p) or p["img"]
    for url in dict.fromkeys([src, src.split("?")[0]]):  # sin parámetros si robots.txt los prohíbe
        try:
            if fetcher.allowed(url)[0]:
                resp = fetcher.get(url)
                data = normalize(resp.content, rotate, 1400) if resp.status_code == 200 else None
        except Exception:
            data = None
        if data:
            break
    thumb = ROOT / "img" / "p" / name_for(src)
    if not data and thumb.exists():  # miniatura de la web (360 px): peor calidad, pero mejor que nada
        data = thumb.read_bytes()
    if data:
        dest.write_bytes(data)
    return data is not None


_REVISADAS = None


def foto_src(p):
    """Dirección de la foto en grande que corresponde a la miniatura revisada (th = sha1 de esa dirección): la de la
    ficha (img) o, si la web eligió la foto de otra tienda, la de esa tienda (thimg). None si no hay ninguna."""
    from .thumbs import name_for
    th = p.get("th")
    if not th:
        return None
    if p.get("img") and name_for(p["img"]) == th:
        return p["img"]
    # thimg: la foto grande de la que sale la miniatura (otra tienda); si la miniatura se rehízo
    # (data/fotos-rehechas.json) su nombre ya no es el sha1 de thimg, pero sigue siendo la misma foto
    return p.get("thimg") or None


def foto_revisada(p):
    """La foto solo vale si es la que la web eligió y revisó como miniatura (campo th): así nunca sale una guitarra
    cortada o de espaldas (data/fotos-revisadas.json: 1 = de espaldas, 2 = cortada). La foto en grande es la de la
    ficha (img) o la de la tienda de la que sale la miniatura (thimg, cuando el catálogo la da)."""
    global _REVISADAS
    if not foto_src(p):
        return False
    if _REVISADAS is None:
        _REVISADAS = load(ROOT / "data" / "fotos-revisadas.json", {})
    return _REVISADAS.get(p["th"]) not in (1, 2)


def with_photos(cands, n, fetcher, folder, prefix, forma="vertical"):
    """Las n primeras con foto revisada y descargada. forma: "vertical" (guitarras y bajos: se gira a vertical y se
    descartan las que no lo son), "ancho" (amplis, teclados: sin girar y descartando las verticales, que suelen ser
    guitarras o bajos mal clasificados) o "libre" (pedales, micrófonos: sin girar)."""
    from PIL import Image
    out = []
    for p in cands:
        if not foto_revisada(p):
            continue
        if any(o["brand"] == p["brand"] for o in out[-2:]):  # sin la misma marca seguida
            continue
        f = folder / f"{prefix}{len(out) + 1}.webp"
        if photo(p, fetcher, f, rotate=forma == "vertical"):
            w, h = Image.open(f).size
            if (forma == "vertical" and w / h > 0.7) or (forma == "ancho" and w / h < 0.8):  # foto torcida o mal recortada (la guitarra no queda en vertical): se descarta
                f.unlink()
                continue
            out.append({**p, "photo": f.name})
        if len(out) == n:
            break
    return out


def plan(day, recent):
    folder = OUT / day.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    prods = products()
    fetcher = Fetcher(delay=(0.5, 1.0))
    deals = rank_deals(prods, recent)
    stories = with_photos(deals, STORIES + 1, fetcher, folder, "chollo-")
    fecha = f"{day.day} de {['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][day.month - 1]}"
    n = day.toordinal()
    if n % 2 == 0 and stories:
        deal = stories[0]
        post = {"type": "chollo", "deal": deal, "caption": (
            f"🔥 Chollo de hoy: {deal['name']}\n"
            f"💶 {eur(deal['price'])} en {deal['store']}, comparada en {deal['stores']} tiendas.\n"
            f"📉 {deal['why']}.\n\n"
            f"👉 Todos los chollos de hoy, a un toque: enlace en la bio.\n"
            f"Precio del {fecha}; puede cambiar.\n\n"
            f"#guitarra {HASHTAGS[deal['kind']]} {tag(deal['brand'])} #chollos #guitarristas #ofertas")}
        stories = stories[1:]
    else:
        kind, lo, hi = TOPS[(n // 2) % len(TOPS)]
        picks = sorted(with_photos(top_of(prods, kind, lo, hi, recent), 5, fetcher, folder, "top-"), key=lambda p: p["price"])
        plural = KIND_NAMES[kind][1]
        rango = f"por menos de {eur(hi)}" if lo == 0 else f"de {eur(lo)} a {eur(hi)}"
        title = f"{len(picks)} {plural} {rango}"
        lines = "\n".join(f"{i}️⃣ {p['name']}: {eur(p['price'])} en {p['store']}" for i, p in enumerate(picks, 1))
        post = {"type": "top", "title": title, "kind": kind, "picks": picks, "caption": (
            f"🎸 {title[0].upper() + title[1:]}: las más vendidas en las tiendas, con su mejor precio de hoy 👇\n\n"
            f"{lines}\n\n"
            f"¿Con cuál te quedas? Te leemos en comentarios 💬\n"
            f"👉 Todos los chollos de hoy, a un toque: enlace en la bio. Precios del {fecha}.\n\n"
            f"#guitarra {HASHTAGS[kind]} #guitarristas #comprarguitarra "
            + " ".join(dict.fromkeys(tag(p["brand"]) for p in picks)))}
        stories = stories[:STORIES]
    data = {"date": day.isoformat(), "fecha": fecha, "post": post, "stories": stories[:STORIES]}
    (folder / "plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "social.js"), str(folder)], check=True, cwd=ROOT)
    daily_reels(day, folder, recent + "\n" + "\n".join(p["name"] for p in data["stories"]), prods, fetcher)
    return folder, data


def git(*args):
    if args[0] == "push":  # el workflow de precios también hace commits en la rama: se integran y se reintenta
        for attempt in range(4):
            if subprocess.run(["git", *args], cwd=ROOT, capture_output=True).returncode == 0:
                return ""
            branch = args[-1].split(":")[-1]
            subprocess.run(["git", "pull", "-q", "--no-rebase", "--no-edit", "origin", branch], cwd=ROOT, check=True)
            time.sleep(2 ** attempt)
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


# --- Presentación (relanzamiento con las cifras del día) --------------------------------------------------------

ARRANQUE = ROOT / "brand" / "png" / "arranque"
PAISES = {"pt": "Portugal", "fr": "Francia", "it": "Italia", "de": "Alemania", "uk": "Reino Unido", "ie": "Irlanda",
          "nl": "Países Bajos", "at": "Austria", "br": "Brasil"}
SHOWCASE = ["Player II Telecaster MN 3-Color", "Les Paul Standard 50s", "RG550", "Casino", "Player II Stratocaster MN Aquatone",
            "SG Standard"]
EXAMPLE = "Fender Player II Stratocaster RW Polar White"


def arranque(day, publish_now):
    """Presentación y carrusel "¿Cómo funciona?" con las guitarras, tiendas y países de hoy (brand/arranque.js)."""
    paises = load(ROOT / "data/catalog/paises.json", {})
    stores = sorted({n.replace(" (eBay)", "") for path in CATALOGS.values() for n in load(path, {}).get("stores", {}).values()})
    others = sorted((c for c in paises if c in PAISES), key=lambda c: -paises[c].get("guitars", 0))
    prods = sorted(products(120, 100000), key=lambda p: -p["stores"])  # escaparate: todas las gamas
    fetcher = Fetcher(delay=(0.5, 1.0))
    src = ARRANQUE / "src"
    src.mkdir(parents=True, exist_ok=True)
    showcase = []
    for i, name in enumerate(SHOWCASE):
        p = next((p for p in prods if name in p["name"]), None)
        if p and photo(p, fetcher, src / f"g{i}.webp"):
            showcase.append(f"g{i}.webp")
    raw = next(p for p in load(CATALOGS["electrica"], {})["products"] if p["name"] == EXAMPLE)
    names = load(CATALOGS["electrica"], {})["stores"]
    items, seen = [], set()
    for i in sorted((i for i in raw["items"] if i.get("p") and i.get("st") is not False), key=lambda i: i["p"]):
        if i["s"] not in seen:
            seen.add(i["s"])
            items.append({"store": names.get(i["s"], i["s"]), "price": i["p"]})
    photo({"img": raw["img"]}, fetcher, src / "ejemplo.webp")
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    datos = {"guitars": paises.get("es", {}).get("guitars") or sum(len(load(p, {}).get("products", [])) for p in CATALOGS.values()),
             "stores": stores, "countries": [PAISES[c] for c in others], "showcase": showcase,
             "example": {"name": tidy(raw["name"]), "brand": raw.get("brand", ""), "img": "ejemplo.webp", "items": items},
             "day": f"{day.day} de {meses[day.month - 1]} de {day.year}"}
    (ARRANQUE / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "arranque.js")], check=True, cwd=ROOT)
    n = f"{datos['guitars']:,}".replace(",", ".")
    paises_txt = ", ".join(datos["countries"][:-1]) + " y " + datos["countries"][-1]
    cap1 = (f"¡Hola! Somos guitle 🎸\nCada día comparamos el precio de {n} guitarras en {len(stores)} tiendas para que sepas "
            f"dónde está más barata la que quieres. Y también en {paises_txt}.\n"
            "Aquí publicamos cada día chollos de verdad, tops por precio y los descuentos falsos que conviene evitar.\n"
            "👉 Busca tu guitarra en guitle.com (enlace en la bio)\n\n"
            "#guitarra #guitarraelectrica #guitarraacustica #fender #gibson #ibanez #guitarristas #chollos")
    cap2 = ("¿Cómo funciona guitle? 👇\n"
            f"1️⃣ Revisamos cada día el precio de {n} guitarras en {len(stores)} tiendas.\n"
            "2️⃣ Te enseñamos dónde está más barata, con su histórico de precios.\n"
            "3️⃣ Publicamos aquí los mejores chollos, cada día.\n"
            "Síguenos y activa las notificaciones 🔔 Enlace en la bio.\n\n"
            "#guitarra #guitarraelectrica #comparadordeprecios #chollos #guitarristas")
    print(json.dumps({"guitarras": n, "tiendas": len(stores), "paises": datos["countries"], "fotos": len(showcase)},
                     ensure_ascii=False))
    if not publish_now:
        print("Sin publicar. Imágenes en brand/png/arranque/jpg/")
        return
    rel = ARRANQUE.relative_to(ROOT).as_posix()
    git("add", rel)
    git("commit", "-q", "-m", f"social: presentación actualizada {day.isoformat()}")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    git("push", "-q", "origin", f"HEAD:{branch}")
    base = f"{REPO_RAW}/{git('rev-parse', 'HEAD')}/{rel}/jpg/"
    for _ in range(20):
        if requests.head(base + "1-presentacion.jpg", timeout=30).status_code == 200:
            break
        time.sleep(5)
    user = api("GET", "me", fields="user_id")["user_id"]
    done = {"presentacion": publish(user, container(user, image_url=base + "1-presentacion.jpg", caption=cap1))}
    kids = [container(user, image_url=base + f"2-carrusel-{i}.jpg", is_carousel_item="true") for i in range(1, 5)]
    done["carrusel"] = publish(user, container(user, media_type="CAROUSEL", children=",".join(kids), caption=cap2))
    print(json.dumps(done, indent=1))


# --- Reels del día (no se publican solos: el usuario les pone música y los sube) ----------------------------------

BLACK_FRIDAY = date(2026, 11, 27)


def dia_bf(day):
    """La cuenta atrás del Black Friday sale cada 5 días (faltan 25, 20, 15, 10) y a diario la última semana."""
    days = (BLACK_FRIDAY - day).days
    return 0 < days and (days <= 7 or days % 5 == 0)


def reel_top(day, folder, prods, recent, fetcher, fecha):
    """Reel de la franja de las 17:37 los días sin cuenta atrás: top 5 por precio (otro rango que el del post)."""
    # Cambia cada día y nunca coincide con el top del carrusel del post (ese rota cada 2 días)
    i = (day.toordinal() + 4) % len(TOPS)
    if i == (day.toordinal() // 2) % len(TOPS):
        i = (i + 1) % len(TOPS)
    kind, lo, hi = TOPS[i]
    sub = folder / "reel-2-top"
    sub.mkdir(parents=True, exist_ok=True)
    # Ciclo de categorías (scraper/equipo.py): un día guitarras, otro amplis, bajos, teclados, pedales, micrófonos…
    from . import equipo
    rama = equipo.rama_del_dia(day)
    if rama != "guitarras":
        hecho = equipo.plan("es", rama, day, recent, fetcher, sub, eur, (MIN_PRICE, MAX_PRICE), fecha)
        if hecho:
            _reel(folder, "reel-2-top", hecho[0], fecha, hecho[1])
            return
        for f in sub.glob("g*.webp"):  # sin 3 buenas ofertas en la rama: top de guitarras
            f.unlink()
    picks = sorted(with_photos(top_of(prods, kind, lo, hi, recent), 5, fetcher, sub, "g"), key=lambda p: p["price"])
    if len(picks) < 3:
        return
    rango = f"por menos de {eur(hi)}" if lo == 0 else f"de {eur(lo)} a {eur(hi)}"
    title = f"{len(picks)} {KIND_NAMES[kind][1]} {rango}"
    lines = "\n".join(f"{i}️⃣ {p['name']}: {eur(p['price'])} en {p['store']}" for i, p in enumerate(picks, 1))
    _reel(folder, "reel-2-top", {"type": "top", "title": title, "hook": "Top por precio", "picks": picks}, fecha,
          f"🎸 {title[0].upper() + title[1:]}: las más vendidas en las tiendas, con su mejor precio de hoy 👇\n\n{lines}\n\n"
          f"¿Con cuál te quedas? 💬\n👉 Todos los chollos de hoy, a un toque: enlace en la bio. Precios del {fecha}.\n\n"
          f"#guitarra {HASHTAGS[kind]} #guitarristas #comprarguitarra " + " ".join(dict.fromkeys(tag(p["brand"]) for p in picks)))
LABELS = {"electrica": "Eléctrica", "acustica": "Acústica", "clasica": "Clásica"}


def _reel(folder, name, post, fecha, caption, n=0):
    sub = folder / name
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "plan.json").write_text(json.dumps({"fecha": fecha, "post": post, "stories": []}, ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
    (sub / "texto.txt").write_text(caption + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "reel.js"), str(sub)], check=True, cwd=ROOT)
    # Un tema distinto por Reel y por día, rotando por la lista
    n = sum(map(ord, fecha)) * 3 + int(name[5]) - 1 if name[:5] == "reel-" and name[5:6].isdigit() else n
    credito = musica.poner(sub / "reel.mp4", n)
    (sub / "texto.txt").write_text(f"{caption}\n\n{credito}\n", encoding="utf-8")


def publish_reels(user, day, names):
    """Publica los Reels del día (ya subidos al repo con su música) y devuelve sus enlaces."""
    sha = git("rev-parse", "HEAD")
    out = []
    for name in names:
        sub = OUT / day.isoformat() / name
        if not (sub / "reel.mp4").exists():
            continue
        url = f"{REPO_RAW}/{sha}/{sub.relative_to(ROOT).as_posix()}/reel.mp4"
        for _ in range(20):
            if requests.head(url, timeout=30).status_code == 200:
                break
            time.sleep(5)
        caption = (sub / "texto.txt").read_text(encoding="utf-8").strip()
        handles = cuentas(marcas_reel(sub))
        out.append(publish(user, container_etiq(user, handles, tries=100, media_type="REELS", video_url=url,
                                                caption=menciones(caption, handles), share_to_feed="true")))
    return out


def daily_reels(day, folder, recent, prods, fetcher):
    """Tres Reels: chollos por categoría, cuenta atrás del Black Friday y uno sobre guitle (rota de tema)."""
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    fecha = f"{day.day} de {meses[day.month - 1]}"
    for name in ("reel-1-chollos", "reel-3-guitle"):
        (folder / name).mkdir(parents=True, exist_ok=True)
    # 1. Chollos: 2 eléctricas, 1 acústica y 1 clásica
    deals, picks = rank_deals(prods, recent), []
    for k in ["electrica", "electrica", "acustica", "clasica"]:
        for p in deals:
            if p["kind"] == k and all(p["slug"] != q["slug"] and p["brand"] != q["brand"] for q in picks):
                got = with_photos([p], 1, fetcher, folder / "reel-1-chollos", f"g{len(picks)}-")
                if got:
                    picks.append({**got[0], "label": LABELS[k]})
                    break
    if picks:
        icons = ["🎸", "⚡", "🪵", "🎼"]
        lines = "\n".join(f"{icons[i]} {p['label']}: {p['name']} a {eur(p['price'])} en {p['store']} ({p['why'][0].lower() + p['why'][1:]})"
                          for i, p in enumerate(picks))
        _reel(folder, "reel-1-chollos", {"type": "top", "title": f"chollos de {MIN_PRICE} a {MAX_PRICE} €", "hook": "Chollos de hoy",
                                          "picks": picks}, fecha,
              f"🔥 Chollos de hoy entre {MIN_PRICE} y {MAX_PRICE} € 👇\n\n{lines}\n\n¿Cuál te llevarías? 💬\n"
              f"👉 Todos los chollos de hoy, a un toque: enlace en la bio. Precios del {fecha}; pueden cambiar.\n\n"
              "#guitarra #guitarraelectrica #guitarraacustica #guitarraclasica #chollos #guitarristas #ofertas "
              + " ".join(dict.fromkeys(tag(p["brand"]) for p in picks)))
    # 2. Black Friday: el precio de hoy de una guitarra popular, para comprobar después si la rebaja es real
    days = (BLACK_FRIDAY - day).days
    if not dia_bf(day):
        reel_top(day, folder, prods, recent, fetcher, fecha)
    else:
        (folder / "reel-2-black-friday").mkdir(parents=True, exist_ok=True)
        kind = ["electrica", "acustica", "electrica", "clasica"][day.toordinal() % 4]
        pool = sorted((p for p in prods if p["kind"] == kind and p["name"] not in recent and p["stores"] >= 4),
                      key=lambda p: -p["stores"])
        got = with_photos(pool, 1, fetcher, folder / "reel-2-black-friday", "g")
        if got:
            p = got[0]
            _reel(folder, "reel-2-black-friday", {"type": "bf", "days": days, "deal": p}, fecha,
                  f"⏳ Faltan {days} {'día' if days == 1 else 'días'} para el Black Friday.\n"
                  f"📌 Apunta este precio: {p['name']} a {eur(p['price'])} hoy en {p['store']} (en otras tiendas, de {eur(p['next'])} a {eur(p['max'])}).\n"
                  "El 27 de noviembre te diremos si su rebaja es real o es un descuento inflado. Guárdalo y síguenos 👀\n\n"
                  f"#blackfriday #blackfriday2026 #guitarra {HASHTAGS[p['kind']]} {tag(p['brand'])} #chollos #guitarristas")
    # 3. Sobre guitle
    paises = load(ROOT / "data/catalog/paises.json", {})
    n = f"{paises.get('es', {}).get('guitars', 0):,}".replace(",", ".")
    stores = sorted({x.replace(" (eBay)", "") for path in CATALOGS.values() for x in load(path, {}).get("stores", {}).values()})
    showcase = with_photos(sorted(prods, key=lambda p: -p["stores"]), 5, fetcher, folder / "reel-3-guitle", "g")
    ex = max((p for p in prods if p["stores"] >= 5 and p["max"] <= 1.45 * p["price"] and foto_revisada(p)), key=lambda p: p["max"] - p["price"])
    # Portada con guitarra (nunca solo texto): la comparada en «misma guitarra», y la fila de guitarras en los demás
    foto_ex = with_photos([ex], 1, fetcher, folder / "reel-3-guitle", "ex")
    fila = {"type": "guitars", "photos": [p["photo"] for p in showcase]} if showcase else None
    portada_ex = {"type": "photo", "photo": foto_ex[0]["photo"]} if foto_ex else fila
    rows = ex["rows"][:3] + ex["rows"][-1:] if len(ex["rows"]) > 4 else ex["rows"]
    rows = [[f"Tienda {'ABCD'[i]}", r[1]] for i, r in enumerate(rows)]  # en los Reels sobre guitle, tiendas sin nombre
    topics = [
        ("¿Qué es guitle?", [
            {"hook": "guitle", "title": "¿Qué es guitle?", "sub": "El comparador de precios de guitarras",
             "visual": {"type": "guitars", "photos": [p["photo"] for p in showcase]}},
            {"title": f"{n} guitarras en {len(stores)} tiendas", "sub": "Revisamos todos los precios, cada día", "size": 120},
            {"title": "Te decimos dónde está más barata", "sub": "Gratis y sin registrarte", "size": 120}],
         f"🎸 ¿Qué es guitle? El comparador de precios de guitarras: {n} guitarras en {len(stores)} tiendas, revisadas cada día.\n"
         "Busca la tuya y mira dónde está más barata. Gratis y sin registrarte.\n🔎 guitle.com (enlace en la bio)\n\n"
         "#guitarra #guitarraelectrica #guitarristas #comparadordeprecios #musica"),
        ("Misma guitarra, distinto precio", [
            {"hook": "¿Sabías que…?", "title": "La misma guitarra puede costar mucho más según la tienda", "visual": portada_ex},
            {"title": ex["name"], "size": 76, "visual": {"type": "prices", "rows": rows}},
            {"title": f"{eur(ex['max'] - ex['price'])} de diferencia", "sub": "Compara antes de comprar", "size": 130}],
         f"😮 La misma guitarra, {eur(ex['max'] - ex['price'])} de diferencia según la tienda: {ex['name']}, de {eur(ex['price'])} a {eur(ex['max'])} hoy.\n"
         "Por eso existe guitle: comparamos cada guitarra en todas las tiendas, cada día.\n🔎 guitle.com (enlace en la bio)\n\n"
         f"#guitarra {HASHTAGS[ex['kind']]} {tag(ex['brand'])} #comparadordeprecios #guitarristas"),
        ("Descuentos inflados", [
            {"hook": "Ojo en Black Friday", "title": "Hay descuentos que son mentira", "visual": fila},
            {"title": "Suben el precio… y luego lo «rebajan»", "sub": "Ejemplo", "size": 96,
             "visual": {"type": "chart", "points": [899, 899, 899, 999, 999, 999, 899, 899],
                        "marks": [[1, "899 €", "#1f9d55"], [4, "999 €", "#d64545"], [7, "«−10 %»", "#d64545"]]}},
            {"title": "guitle lo detecta con el histórico de precios", "sub": "Míralo antes de comprar en guitle.com"}],
         "⚠️ Ojo con los descuentos inflados: algunas tiendas suben el precio unas semanas antes y luego lo «rebajan»… al precio de siempre.\n"
         "En guitle guardamos el precio de cada guitarra cada día, así que lo ves al momento.\n🔎 guitle.com (enlace en la bio)\n\n"
         "#blackfriday #guitarra #guitarristas #chollos #descuentos"),
        ("¿Es buen momento?", [
            {"hook": "Antes de comprar", "title": "¿Es buen momento para comprarla?", "visual": fila},
            {"title": "Mira su histórico de precios", "sub": "Ejemplo", "size": 100,
             "visual": {"type": "chart", "points": [829, 829, 799, 829, 789, 789, 769, 749],
                        "marks": [[0, "829 €", "#52514e"], [7, "Hoy: mínimo", "#1f9d55"]]}},
            {"title": "En guitle tienes el histórico de cada guitarra", "sub": "Gratis, en su ficha de guitle.com"}],
         "📉 ¿Es buen momento para comprar esa guitarra? Mira su histórico de precios: si hoy está en su mínimo, ¡a por ella!\n"
         "En guitle lo tienes gratis en la ficha de cada guitarra.\n🔎 guitle.com (enlace en la bio)\n\n"
         "#guitarra #guitarristas #comprarguitarra #chollos"),
        ("10 países", [
            {"hook": "¿Y fuera de España?", "title": f"Comparamos guitarras en {len(paises)} países", "visual": fila},
            {"title": "Mira cuánto cuesta fuera", "size": 100,
             "visual": {"type": "chips", "items": ["España"] + [PAISES[c] for c in sorted(paises, key=lambda c: -paises[c].get('guitars', 0)) if c in PAISES]}},
            {"title": "Todo en guitle.com", "sub": "Gratis y sin registrarte", "size": 120}],
         f"🌍 guitle no es solo España: comparamos precios de guitarras en {len(paises)} países: España, "
         + ", ".join(PAISES[c] for c in paises if c in PAISES) + ".\n🔎 guitle.com (enlace en la bio)\n\n"
         "#guitarra #guitarristas #comparadordeprecios #europa"),
    ]
    title, slides, caption = topics[day.toordinal() % len(topics)]
    _reel(folder, "reel-3-guitle", {"type": "guitle", "topic": title, "slides": slides}, fecha, caption)


# --- Stories de la tarde ---------------------------------------------------------------------------------------

def tarde(day, publish_now):
    """Segunda tanda de stories: otros chollos del día, sin repetir los de mediodía ni los de días anteriores."""
    folder = OUT / day.isoformat() / "tarde"
    if publish_now and (folder / "published.json").exists():
        print(f"{folder.relative_to(ROOT).as_posix()} ya se publicó")
        return
    user = api("GET", "me", fields="user_id")["user_id"] if publish_now else "me"
    recent = recent_captions(user)
    for f in (sorted(OUT.glob("*/plan.json"))[-10:] + sorted(OUT.glob("*/tarde/plan.json"))[-10:]
              + sorted(OUT.glob("*/reel-*/plan.json"))[-30:]):
        d = load(f, {})
        post = d.get("post") or {}
        recent += "\n" + "\n".join(p["name"] for p in d.get("stories", []) + post.get("picks", []))
        if post.get("deal"):
            recent += "\n" + post["deal"]["name"]
    folder.mkdir(parents=True, exist_ok=True)
    stories = with_photos(rank_deals(products(), recent), STORIES, Fetcher(delay=(0.5, 1.0)), folder, "chollo-")
    if not stories:
        print("Sin chollos nuevos para la tarde")
        return
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    data = {"date": day.isoformat(), "fecha": f"{day.day} de {meses[day.month - 1]}", "post": None, "stories": stories}
    (folder / "plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "social.js"), str(folder)], check=True, cwd=ROOT)
    print(json.dumps([p["name"] for p in stories], ensure_ascii=False))
    if not publish_now:
        return
    rel = folder.relative_to(ROOT).as_posix()
    git("add", rel)
    git("commit", "-q", "-m", f"social: stories de la tarde {day.isoformat()}")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    git("push", "-q", "origin", f"HEAD:{branch}")
    base = f"{REPO_RAW}/{git('rev-parse', 'HEAD')}/{rel}/"
    for _ in range(20):
        if requests.head(base + "story-1.jpg", timeout=30).status_code == 200:
            break
        time.sleep(5)
    done = [publish(user, container_etiq(user, cuentas(stories[i:i + 1]), media_type="STORIES", image_url=base + s.name))
            for i, s in enumerate(sorted(folder.glob("story-*.jpg")))]
    reels = publish_reels(user, day, ["reel-3-guitle", "reel-2-black-friday"]) if REEL_AUTO else []
    (folder / "published.json").write_text(json.dumps({"stories": done, "reels": reels}, indent=1) + "\n", encoding="utf-8")
    git("add", rel)
    git("commit", "-q", "-m", f"social: publicadas las stories de la tarde {day.isoformat()}")
    git("push", "-q", "origin", f"HEAD:{branch}")
    print(json.dumps(done, indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true", help="sube las imágenes a la rama actual y publica")
    ap.add_argument("--date", help="AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--arranque", action="store_true", help="presentación y carrusel con las cifras de hoy")
    ap.add_argument("--tarde", action="store_true", help="segunda tanda de stories con otros chollos del día")
    ap.add_argument("--reel", choices=["reel-2", "reel-3"], help="publica solo ese Reel del día, sin stories (reel-2: Black Friday o top; reel-3: guitle)")
    args = ap.parse_args(argv)
    day = date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc).date()
    if args.arranque:
        return arranque(day, args.publish)
    if args.tarde:
        return tarde(day, args.publish)
    if args.reel:
        hechos_dir = [d for d in sorted((OUT / day.isoformat()).glob(f"{args.reel}-*")) if (d / "reel.mp4").exists()]
        if not hechos_dir:
            print(f"No hay ningún {args.reel}-* generado hoy")
            return
        args.reel = hechos_dir[0].name
        hecho = OUT / day.isoformat() / "reels-publicados.json"
        d = load(hecho, {})
        if str(d.get(args.reel, "")).startswith("https://"):
            print(f"{args.reel} ya se publicó: {d[args.reel]}")
            return
        if not args.publish:
            print(f"Sin publicar: {OUT / day.isoformat() / args.reel}")
            return
        user = api("GET", "me", fields="user_id")["user_id"]
        caption = (OUT / day.isoformat() / args.reel / "texto.txt").read_text(encoding="utf-8").strip()
        prev = next((m["permalink"] for m in api("GET", f"{user}/media", fields="caption,permalink,timestamp", limit=10)["data"]
                     if m.get("timestamp", "")[:10] == day.isoformat() and (m.get("caption") or "")[:60] == caption[:60]), None)
        d[args.reel] = prev or (publish_reels(user, day, [args.reel]) or [None])[0]
        hecho.write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8")
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        git("add", hecho.relative_to(ROOT).as_posix())
        git("commit", "-q", "-m", f"social: publicado {args.reel} {day.isoformat()}")
        git("push", "-q", "origin", f"HEAD:{branch}")
        print(json.dumps(d, indent=1))
        return
    if args.publish and (OUT / day.isoformat() / "published.json").exists():
        print(f"social/{day.isoformat()} ya se publicó")
        return
    user = api("GET", "me", fields="user_id")["user_id"] if args.publish else None
    recent = recent_captions(user or "me")
    folder, data = plan(day, recent)
    rel = folder.relative_to(ROOT).as_posix()
    print(json.dumps({"post": data["post"]["type"], "caption": data["post"]["caption"],
                      "stories": [s["name"] for s in data["stories"]]}, ensure_ascii=False, indent=1))
    if not args.publish:
        print(f"Sin publicar. Imágenes en {rel}/")
        return
    git("add", rel)
    git("commit", "-q", "-m", f"social: publicación de Instagram {day.isoformat()}")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    git("push", "-q", "origin", f"HEAD:{branch}")
    base = f"{REPO_RAW}/{git('rev-parse', 'HEAD')}/{rel}/"
    for _ in range(20):  # la URL raw tarda unos segundos en existir
        if requests.head(base + "post-1.jpg", timeout=30).status_code == 200:
            break
        time.sleep(5)
    slides = sorted(p.name for p in folder.glob("post-*.jpg"))
    done = {"post": None, "reel": None, "stories": []}
    caption = menciones(data["post"]["caption"], cuentas(marcas_post(data["post"])))
    if len(slides) == 1:
        done["post"] = publish(user, container_etiq(user, cuentas(marcas_post(data["post"], 0)), image_url=base + slides[0],
                                                    caption=caption))
    else:
        kids = [container_etiq(user, cuentas(marcas_post(data["post"], i)), image_url=base + s, is_carousel_item="true")
                for i, s in enumerate(slides)]
        done["post"] = publish(user, container(user, media_type="CAROUSEL", children=",".join(kids), caption=caption))
    if REEL_AUTO:  # el de chollos a mediodía; el de guitle y el de Black Friday, con las stories de la tarde
        done["reel"] = publish_reels(user, day, ["reel-1-chollos"])
    for i, s in enumerate(sorted(folder.glob("story-*.jpg"))):
        done["stories"].append(publish(user, container_etiq(user, cuentas(data["stories"][i:i + 1]), media_type="STORIES",
                                                            image_url=base + s.name)))
    (folder / "published.json").write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
    git("add", rel)
    git("commit", "-q", "-m", f"social: publicado {day.isoformat()}")
    git("push", "-q", "origin", f"HEAD:{branch}")
    print(json.dumps(done, indent=1))


if __name__ == "__main__":
    main()
