"""Publicación diaria en Instagram (@guitle.es): elige el contenido del día con los precios reales, genera las
imágenes (brand/social.js) y las publica con la API de Instagram.

Cada día: un post en el feed, alternando
  - "chollo": la guitarra con la mejor rebaja (mínimo histórico > bajada real > bajada de hoy > bajo PVP > más barata
    que en el resto de tiendas), en post 4:5;
  - "top": carrusel con 5 guitarras populares (las que más tiendas venden) de un rango de precio, rotando categoría y
    rango;
un Reel con el mismo contenido animado (brand/reel.js; reel.mp4 sirve también para TikTok) y varias stories
con los chollos del día. No repite guitarras publicadas hace poco (mira los textos ya publicados).

Instagram descarga las imágenes de una URL pública: se suben al repo (social/<fecha>/) y se usa la URL raw del commit.
La API va por graph.instagram.com con el token que inyecta el proxy del entorno (no hay token en el repo).

Uso:
    python -m scraper.instagram             # genera social/<fecha>/ sin publicar (para revisar)
    python -m scraper.instagram --publish   # genera, sube a la rama actual y publica
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import median

import requests

from .catalog import load
from .fetch import Fetcher
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
TOPS = [("electrica", 0, 300), ("acustica", 0, 300), ("electrica", 300, 700), ("clasica", 0, 250),
        ("electrica", 700, 1200), ("acustica", 300, 800), ("electrica", 1200, 2500), ("clasica", 250, 700)]
MIN_PRICE = 120      # por debajo suelen ser packs, juguetes o errores de catálogo
MIN_STORES = 3       # para hablar de "el mejor precio" tiene que haber con qué comparar
STORIES = 3          # chollos en stories cada día
HASHTAGS = {"electrica": "#guitarraelectrica", "acustica": "#guitarraacustica", "clasica": "#guitarraclasica"}


def eur(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return (s[:-3] if s.endswith(",00") else s) + " €"


ACRONYMS = {"LTD", "ESP", "EVH", "PRS", "SG", "HSS", "HH", "SSS", "RW", "MN", "EB", "LH", "CE", "FR", "II", "III", "IV", "USA", "MIM", "BPG"}


def tidy(name):
    """Nombres en mayúsculas de algunas tiendas ("LES PAUL STANDARD") → "Les Paul Standard"."""
    words = name.split()
    upper = [w for w in words if w.isalpha() and w.isupper() and len(w) > 2]
    if len(upper) < len(words) / 2:
        return name
    return " ".join(w if w in ACRONYMS or not (w.isalpha() and w.isupper()) else w.capitalize() for w in words)


def tag(s):
    return "#" + re.sub(r"[^0-9a-záéíóúñ]", "", s.lower())


# --- Datos ---------------------------------------------------------------------------------------------------

def products():
    """Guitarras del catálogo con foto, en stock en varias tiendas y con su mejor precio."""
    pvp = load(ROOT / "data/catalog/pvp.json", {}).get("prices", {})
    out = []
    for kind, path in CATALOGS.items():
        cat = load(path, {})
        stores = cat.get("stores", {})
        for p in cat.get("products", []):
            items = sorted((i for i in p.get("items", []) if i.get("p") and i.get("st") is not False), key=lambda i: i["p"])
            if not p.get("img") or len({i["s"] for i in items}) < MIN_STORES or items[0]["p"] < MIN_PRICE:
                continue
            best = items[0]
            prices = [i["p"] for i in items]
            ref = pvp.get(p.get("sku") or "", [])
            out.append({"slug": p["slug"], "name": tidy(p["name"]), "brand": p.get("brand") or "", "kind": kind,
                        "img": p["img"], "price": best["p"], "store": stores.get(best["s"], best["s"]),
                        "stores": len({i["s"] for i in items}), "median": median(prices[1:]), "max": prices[-1],
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


def rank_deals(prods, recent):
    """Chollos del día de mejor a peor, sin guitarras ya publicadas y sin repetir marca seguida."""
    hist = deals_by_slug()
    scored = []
    for p in prods:
        if p["name"] in recent:
            continue
        if p["slug"] in hist:
            prio, pct, why = hist[p["slug"]]
        elif p["pvp"] and p["price"] <= p["pvp"] * 0.85:
            prio, pct = 1, (1 - p["price"] / p["pvp"]) * 100
            why = f"{pct:.0f} % por debajo del PVP oficial ({eur(p['pvp'])})"
        elif p["price"] <= p["median"] * 0.9:
            prio, pct = 0, (1 - p["price"] / p["median"]) * 100
            why = f"{eur(p['median'] - p['price'])} menos que en el resto de tiendas"
        else:
            continue
        if pct > 60:  # rebajas tan grandes suelen ser un error de emparejamiento, no un chollo
            continue
        scored.append(((prio, pct + min(p["stores"], 10)), {**p, "why": why, "pct": round(pct)}))
    scored.sort(key=lambda x: x[0], reverse=True)
    out, brands = [], []
    for _, p in scored:
        if brands[-1:] == [p["brand"]]:
            continue
        out.append(p)
        brands.append(p["brand"])
    return out


def top_of(prods, kind, lo, hi, recent):
    """5 guitarras populares (más tiendas) del rango, como mucho una por marca."""
    pool = sorted((p for p in prods if p["kind"] == kind and lo <= p["price"] < hi),
                  key=lambda p: (p["name"] in recent, -p["stores"], p["price"]))
    out, brands = [], set()
    for p in pool:
        if p["brand"] not in brands:
            out.append(p)
            brands.add(p["brand"])
        if len(out) == 5:
            break
    return sorted(out, key=lambda p: p["price"])


# --- Instagram ------------------------------------------------------------------------------------------------

def api(method, path, **params):
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
    mid = api("POST", f"{user}/media_publish", creation_id=cid)["id"]
    return api("GET", mid, fields="permalink").get("permalink")


# --- Plan del día ----------------------------------------------------------------------------------------------

def photo(p, fetcher, dest):
    """Foto en alta resolución, recortada y en vertical (como las miniaturas de la web)."""
    data = None
    for url in dict.fromkeys([p["img"], p["img"].split("?")[0]]):  # sin parámetros si robots.txt los prohíbe
        try:
            if fetcher.allowed(url)[0]:
                resp = fetcher.get(url)
                data = normalize(resp.content, True, 1400) if resp.status_code == 200 else None
        except Exception:
            data = None
        if data:
            break
    thumb = ROOT / "img" / "p" / name_for(p["img"])
    if not data and thumb.exists():  # miniatura de la web (360 px): peor calidad, pero mejor que nada
        data = thumb.read_bytes()
    if data:
        dest.write_bytes(data)
    return data is not None


def with_photos(cands, n, fetcher, folder, prefix):
    out = []
    for p in cands:
        if any(o["brand"] == p["brand"] for o in out[-2:]):  # sin la misma marca seguida
            continue
        f = folder / f"{prefix}{len(out) + 1}.webp"
        if photo(p, fetcher, f):
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
            f"🔎 Compara su precio en guitle.com (enlace en la bio).\n"
            f"Precio del {fecha}; puede cambiar.\n\n"
            f"#guitarra {HASHTAGS[deal['kind']]} {tag(deal['brand'])} #chollos #guitarristas #ofertas")}
        stories = stories[1:]
    else:
        kind, lo, hi = TOPS[(n // 2) % len(TOPS)]
        picks = with_photos(top_of(prods, kind, lo, hi, recent), 5, fetcher, folder, "top-")
        plural = KIND_NAMES[kind][1]
        rango = f"por menos de {eur(hi)}" if lo == 0 else f"de {eur(lo)} a {eur(hi)}"
        title = f"5 {plural} {rango}"
        lines = "\n".join(f"{i}️⃣ {p['name']}: {eur(p['price'])} en {p['store']}" for i, p in enumerate(picks, 1))
        post = {"type": "top", "title": title, "kind": kind, "picks": picks, "caption": (
            f"🎸 {title[0].upper() + title[1:]}: las más vendidas en las tiendas, con su mejor precio de hoy 👇\n\n"
            f"{lines}\n\n"
            f"¿Con cuál te quedas? Te leemos en comentarios 💬\n"
            f"🔎 Compara precios en guitle.com (enlace en la bio). Precios del {fecha}.\n\n"
            f"#guitarra {HASHTAGS[kind]} #guitarristas #comprarguitarra "
            + " ".join(dict.fromkeys(tag(p["brand"]) for p in picks)))}
        stories = stories[:STORIES]
    data = {"date": day.isoformat(), "fecha": fecha, "post": post, "stories": stories[:STORIES]}
    (folder / "plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "social.js"), str(folder)], check=True, cwd=ROOT)
    subprocess.run(["node", str(ROOT / "brand" / "reel.js"), str(folder)], check=True, cwd=ROOT)
    return folder, data


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true", help="sube las imágenes a la rama actual y publica")
    ap.add_argument("--date", help="AAAA-MM-DD (por defecto, hoy)")
    args = ap.parse_args(argv)
    day = date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc).date()
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
    if len(slides) == 1:
        done["post"] = publish(user, container(user, image_url=base + slides[0], caption=data["post"]["caption"]))
    else:
        kids = [container(user, image_url=base + s, is_carousel_item="true") for s in slides]
        done["post"] = publish(user, container(user, media_type="CAROUSEL", children=",".join(kids),
                                               caption=data["post"]["caption"]))
    if (folder / "reel.mp4").exists():  # el vídeo tarda más en procesarse: hasta 5 minutos
        done["reel"] = publish(user, container(user, tries=100, media_type="REELS", video_url=base + "reel.mp4",
                                               caption=data["post"]["caption"], share_to_feed="true"))
    for s in sorted(folder.glob("story-*.jpg")):
        done["stories"].append(publish(user, container(user, media_type="STORIES", image_url=base + s.name)))
    (folder / "published.json").write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
    git("add", rel)
    git("commit", "-q", "-m", f"social: publicado {day.isoformat()}")
    git("push", "-q", "origin", f"HEAD:{branch}")
    print(json.dumps(done, indent=1))


if __name__ == "__main__":
    main()
