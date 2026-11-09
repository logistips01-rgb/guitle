"""Lo que en Cloudflare hace el Worker (cloudflare/worker.js), en el servidor propio: Caddy sirve los ficheros de la
copia de R2 (/srv/guitle/r2) y le pasa a este programa lo que no es un fichero suelto:
  - fichas de los países (<país>/g/<slug>.html), que van en cajas (<país>/_g/<nnnn>.json.gz);
  - secciones en cajas (discos: records/, disques/, dischi/, discos/ → _r/);
  - fichas de España (g/<slug>.html): solo las de hoy (g/_indice.txt.gz); las retiradas, a la de hoy del mismo
    producto (301) o "ya no está disponible" (410);
  - lo que no existe: 301 a la ficha de hoy si es una dirección vieja, o 410 / 404.
Solo biblioteca estándar. Escucha en 127.0.0.1:8081 (servicio guitle-fichas).
"""
import gzip
import json
import re
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path("/srv/guitle/r2")
CAJAS, CAJAS_R = 2048, 512
SECCIONES = {"records": {"uk"}, "disques": {"fr"}, "dischi": {"it"}, "discos": {"", "pt"}}
EAN = re.compile(r"-(\d{8,14})$")

GONE = {
    "es": ("Esta guitarra ya no está disponible", "Ver otros precios"),
    "pt": ("Este produto já não está disponível", "Ver outros preços"), "br": ("Este produto não está mais disponível", "Ver outros preços"),
    "fr": ("Ce produit n'est plus disponible", "Voir d'autres prix"), "lu": ("Ce produit n'est plus disponible", "Voir d'autres prix"),
    "it": ("Questo prodotto non è più disponibile", "Vedi altri prezzi"), "de": ("Dieses Produkt ist nicht mehr erhältlich", "Weitere Preise ansehen"),
    "at": ("Dieses Produkt ist nicht mehr erhältlich", "Weitere Preise ansehen"), "ch": ("Dieses Produkt ist nicht mehr erhältlich", "Weitere Preise ansehen"),
    "nl": ("Dit product is niet meer verkrijgbaar", "Bekijk andere prijzen"), "be": ("Dit product is niet meer verkrijgbaar", "Bekijk andere prijzen"),
    "pl": ("Ten produkt nie jest już dostępny", "Zobacz inne ceny"), "se": ("Den här produkten finns inte längre", "Se andra priser"),
    "no": ("Dette produktet er ikke lenger tilgjengelig", "Se andre priser"), "dk": ("Dette produkt findes ikke længere", "Se andre priser"),
    "cz": ("Tento produkt už není k dispozici", "Zobrazit další ceny"), "sk": ("Tento produkt už nie je k dispozícii", "Zobraziť ďalšie ceny"),
    "hu": ("Ez a termék már nem elérhető", "További árak"), "ro": ("Acest produs nu mai este disponibil", "Vezi alte prețuri"),
    "bg": ("Този продукт вече не е наличен", "Вижте други цени"), "gr": ("Αυτό το προϊόν δεν είναι πλέον διαθέσιμο", "Δείτε άλλες τιμές"),
    "fi": ("Tämä tuote ei ole enää saatavilla", "Katso muita hintoja"), "mx": ("Este producto ya no está disponible", "Ver otros precios"),
    "ar": ("Este producto ya no está disponible", "Ver otros precios"),
}


def fnv(text):
    h = 0x811C9DC5
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


_boxes, _lock = OrderedDict(), threading.Lock()


def box(rel):
    """Una caja abierta ({clave: html}), en memoria las 64 últimas; se relee si cambia el fichero."""
    path = ROOT / rel
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    with _lock:
        hit = _boxes.get(rel)
        if hit and hit[0] == mtime:
            _boxes.move_to_end(rel)
            return hit[1]
    pages = json.loads(gzip.decompress(path.read_bytes()))
    with _lock:
        _boxes[rel] = (mtime, pages)
        while len(_boxes) > 64:
            _boxes.popitem(last=False)
    return pages


_idx = {}


def indice(code):
    """Fichas de hoy de un país ({"s", "e", "n"}): <país>/_g/indice.json, o g/_indice.txt.gz en España. 10 min."""
    hit = _idx.get(code)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    idx = None
    try:
        if code == "es":
            lines = gzip.decompress((ROOT / "g" / "_indice.txt.gz").read_bytes()).decode("utf-8").split("\n")[1:]
            slugs = [s for s in lines if s]
            if len(slugs) >= 20000:  # una lista a medias taparía fichas buenas
                e, n = {}, {}
                for s in slugs:
                    m = EAN.search(s)
                    if m:
                        e.setdefault(m.group(1).lstrip("0"), s)
                    n.setdefault(EAN.sub("", s), s)
                idx = {"s": set(slugs), "e": e, "n": n}
        else:
            idx = json.loads((ROOT / code / "_g" / "indice.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        idx = None
    _idx[code] = (time.time(), idx)
    return idx


def moved(idx, slug):
    if not idx:
        return None
    m = EAN.search(slug)
    base = EAN.sub("", slug)
    found = (m and idx["e"].get(m.group(1).lstrip("0"))) or idx["n"].get(base) or idx["n"].get(re.sub(r"-[^-]+$", "", base))
    return found if found and found != slug else None


class H(BaseHTTPRequestHandler):
    server_version = "guitle"

    def log_message(self, *a):
        pass

    def send(self, status, body=b"", ctype="text/html; charset=utf-8", headers=None):
        self.send_response(status)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def page(self, html):
        self.send(200, html.encode("utf-8"), headers={"cache-control": "public, max-age=600", "x-content-type-options": "nosniff"})

    def redirect(self, to):
        self.send(301, headers={"location": to})

    def gone(self, code):
        msg, link = GONE.get(code, ("This product is no longer available", "See other prices"))
        home = "/" if code == "es" else f"/{code}/"
        html = (f'<!doctype html><html lang="{code}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
                f'initial-scale=1"><meta name="robots" content="noindex"><title>{msg} · guitle</title><div style="font-family:'
                f'system-ui,sans-serif;max-width:560px;margin:60px auto;padding:0 20px;text-align:center"><p style="font-size:'
                f'1.3rem;font-weight:700">{msg}</p><p><a href="{home}" style="display:inline-block;padding:10px 18px;border-radius:'
                f'999px;background:#2a78d6;color:#fff;text-decoration:none">{link} →</a></p></div></html>')
        self.send(410, html.encode("utf-8"), headers={"cache-control": "public, max-age=3600"})

    def not_found(self):
        self.send(404, b'<!doctype html><meta charset="utf-8"><title>No encontrado \xc2\xb7 guitle</title>'
                       b'<p style="font-family:system-ui;padding:40px">Esta p\xc3\xa1gina no existe. <a href="/">Volver a guitle</a></p>')

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            key = unquote(self.path.split("?", 1)[0]).lstrip("/")
        except Exception:  # noqa: BLE001
            return self.not_found()
        if key == "" or key.endswith("/"):  # "/discos/" → "discos/index.html" (las portadas de sección van en cajas)
            key += "index.html"
        # Secciones en cajas (discos)
        m = re.match(r"^(?:([a-z]{2})/)?((records|disques|dischi|discos)/.+\.html)$", key)
        if m and (m.group(1) or "") in SECCIONES[m.group(3)]:
            code = m.group(1) or ""
            pages = box(f"{code + '/' if code else ''}_r/{fnv(m.group(2)) % CAJAS_R:04x}.json.gz")
            if pages and isinstance(pages.get(m.group(2)), str):
                return self.page(pages[m.group(2)])
            return self.not_found()
        # Fichas de los países, en cajas
        m = re.match(r"^([a-z]{2})/g/([^/]+)\.html$", key)
        if m:
            code, slug = m.groups()
            pages = box(f"{code}/_g/{fnv(slug) % CAJAS:04x}.json.gz")
            if pages and isinstance(pages.get(slug), str):
                return self.page(pages[slug])
            to = moved(indice(code), slug)
            return self.redirect(f"/{code}/g/{to}.html") if to else self.gone(code)
        # Fichas de España: solo las de hoy
        m = re.match(r"^g/([^/]+)\.html$", key)
        if m:
            slug, idx = m.group(1), indice("es")
            path = ROOT / "g" / f"{slug}.html"
            if path.exists() and (idx is None or slug in idx["s"]):
                return self.page(path.read_text(encoding="utf-8"))
            to = moved(idx, slug)
            return self.redirect(f"/g/{to}.html") if to else self.gone("es")
        return self.not_found()


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8081), H).serve_forever()
