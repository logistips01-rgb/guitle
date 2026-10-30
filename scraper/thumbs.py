"""Miniaturas uniformes de las fotos de producto (img/p/).

Cada tienda fotografía a su manera (guitarra tumbada, lienzo apaisado con la guitarra en vertical, mucho
margen…). Aquí se recorta el fondo blanco, se pone la guitarra en vertical con el cuerpo abajo y se guarda a
un alto fijo, para que en la web todas se vean igual.

Uso:
    python -m scraper.thumbs [--limit 300] [--minutes 20] [--cat pt]
"""
import argparse
import hashlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageChops, ImageOps

from .catalog import load
from .fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "img" / "p"
HEIGHT = 360
WHITE = 244  # canal más oscuro por encima de esto = fondo blanco
ROTATE_CATEGORIES = {"guitarra", "bajo"}


def name_for(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16] + ".webp"


def existing(url):
    """Nombre de la miniatura si ya existe (para los JSON de la web)."""
    return name_for(url) if url and (DIR / name_for(url)).exists() else None


def slenderness(name):
    """Alto/ancho de una miniatura: una guitarra entera es esbelta (>2); un primer plano, no."""
    with Image.open(DIR / name) as im:
        return im.height / im.width


def _erase_lines(mask):
    """Borra rayas finas (bordes o separadores de 1-3 px que algunas tiendas dibujan en la foto).

    Una columna o fila casi llena de "tinta" y aislada es una raya; el mástil de una guitarra también es
    largo, pero mucho más ancho.
    """
    from PIL import ImageDraw
    w, h = mask.size
    draw = ImageDraw.Draw(mask)
    for axis, n, length in ((0, w, h), (1, h, w)):
        full = [mask.crop((i, 0, i + 1, h) if axis == 0 else (0, i, w, i + 1)).histogram()[255] > 0.5 * length
                for i in range(n)]
        i = 0
        while i < n:
            if full[i]:
                j = i
                while j < n and full[j]:
                    j += 1
                if j - i <= 3:
                    draw.rectangle((i, 0, j - 1, h) if axis == 0 else (0, i, w, j - 1), fill=0)
                i = j
            else:
                i += 1
    return mask


def _main_block(mask, axis):
    """(inicio, fin) del bloque con más "tinta" a lo largo de un eje, separando por franjas en blanco.

    Quita logos o textos que algunas tiendas ponen junto a la foto (p. ej. la marca de agua de Thomann).
    """
    w, h = mask.size
    n = h if axis == 1 else w
    counts = [mask.crop((0, i, w, i + 1) if axis == 1 else (i, 0, i + 1, h)).histogram()[255] for i in range(n)]
    gap = max(2, n // 200)
    blocks, start, blank = [], None, 0
    for i, c in enumerate(counts + [0] * gap):
        if c:
            if start is None:
                start = i
            blank = 0
        elif start is not None:
            blank += 1
            if blank >= gap:
                end = i - blank + 1
                blocks.append((sum(counts[start:end]), start, end))
                start, blank = None, 0
    if not blocks:
        return 0, n
    _, start, end = max(blocks)
    return start, end


def _ink(mask, box):
    return mask.crop(box).histogram()[255]


def normalize(data, rotate=True, height=HEIGHT):
    im = ImageOps.exif_transpose(Image.open(BytesIO(data)))
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    rgb = bg.convert("RGB")
    # Fondo = blanco casi puro en los tres canales. Se mira el canal más oscuro, no el brillo: así un cuerpo
    # blanco crema (Olympic White, Vintage White…) no se confunde con el fondo.
    r, g, b = rgb.split()
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    mask = darkest.point(lambda v: 255 if v < WHITE else 0)
    bbox = mask.getbbox()
    if not bbox:
        return None
    rgb, mask = rgb.crop(bbox), mask.crop(bbox)
    if max(rgb.size) > 600:  # proyecciones sobre una copia pequeña: rápido y suficiente
        scale = 600 / max(rgb.size)
        small = mask.resize((max(1, round(mask.width * scale)), max(1, round(mask.height * scale))))
    else:
        scale, small = 1, mask
    small = _erase_lines(small.copy())
    y0, y1 = _main_block(small, 1)
    x0, x1 = _main_block(small.crop((0, y0, small.width, y1)), 0)
    # Sin salirse de la imagen: un recorte fuera de los bordes se rellena de negro (y deja una raya).
    box = (max(0, round(x0 / scale)), max(0, round(y0 / scale)),
           min(rgb.width, round(x1 / scale)), min(rgb.height, round(y1 / scale)))
    rgb, mask = rgb.crop(box), mask.crop(box)
    if rotate:
        w, h = rgb.size
        if w > h * 1.15:  # tumbada → vertical
            rgb = rgb.rotate(90, expand=True, fillcolor="white")
            mask = mask.rotate(90, expand=True)
        w, h = rgb.size
        if h > w and _ink(mask, (0, 0, w, h // 2)) > 1.15 * _ink(mask, (0, h // 2, w, h)):
            rgb = rgb.rotate(180)  # el cuerpo (la mitad con más "tinta") va abajo
    w, h = rgb.size
    pad = max(2, h // 40)
    canvas = Image.new("RGB", (w + 2 * pad, h + 2 * pad), "white")
    canvas.paste(rgb, (pad, pad))
    canvas = canvas.resize((max(1, round(canvas.width * height / canvas.height)), height), Image.LANCZOS)
    out = BytesIO()
    canvas.save(out, "WEBP", quality=78, method=6)
    return out.getvalue()


def wanted(cat=None):
    """(url, girar) de las fotos que usa la web: productos seguidos y catálogo. cat: solo las de ese catálogo."""
    out = {}
    latest = load(ROOT / "data" / "latest.json", {})
    category = {p["sku"]: p.get("category", "guitarra") for p in latest.get("products", [])}
    for i in latest.get("items", []) if cat in (None, "electrica") else []:  # todas las fotos de cada producto
        if i.get("image"):
            out[i["image"]] = category.get(i["sku"], "guitarra") in ROTATE_CATEGORIES
    # Todas las tiendas de todos los catálogos (eléctricas, acústicas y clásicas), para elegir la mejor foto.
    if cat:
        from .catalog import CATALOGS
        paths = [CATALOGS[cat]["dir"] / "offers.json"]
    else:
        paths = sorted((ROOT / "data" / "catalog").rglob("offers.json"))
    for path in paths:
        for o in load(path, {}).values():
            if o.get("status") == "ok" and o.get("image"):
                # Las guitarras se ponen en vertical; teclados y pedales se dejan como vienen.
                out.setdefault(o["image"], (o.get("kind") or "electrica") in {"electrica", "acustica", "clasica", "portuguesa"})
    return out


def _one(fetcher, url, rotate):
    """La miniatura de una foto: "ok", "failed" o "skip" (robots.txt no la deja)."""
    try:
        src = url
        if not fetcher.allowed(src)[0]:
            # Muchas tiendas prohíben URLs con parámetros (?ts=…): la misma imagen sin ellos suele estar permitida.
            src = url.split("?")[0]
            if src == url or not fetcher.allowed(src)[0]:
                return "skip"
        resp = fetcher.get(src)
        if resp.status_code != 200 or not resp.headers.get("content-type", "").startswith("image"):
            return "failed"
        data = normalize(resp.content, rotate)
        if not data:
            return "failed"
        (DIR / name_for(url)).write_bytes(data)
        return "ok"
    except Exception as exc:  # noqa: BLE001 - una foto rara no para el resto
        print(f"[thumb] {url[:80]}: {type(exc).__name__}", flush=True)
        return "failed"


def run(limit=300, minutes=20, cat=None, workers=8):
    """Las fotos se piden por tienda (dominio) en paralelo: cada tienda, de una en una y con su pausa de 1-2 s, como
    siempre; lo que cambia es que varias tiendas avanzan a la vez."""
    DIR.mkdir(parents=True, exist_ok=True)
    todo = [(u, r) for u, r in wanted(cat).items() if not (DIR / name_for(u)).exists()]
    by_host = {}
    for url, rotate in todo:
        by_host.setdefault(urlparse(url).netloc, []).append((url, rotate))
    deadline = time.monotonic() + minutes * 60
    counts = {"ok": 0, "failed": 0, "skip": 0}
    lock = threading.Lock()

    def host(items):
        fetcher = Fetcher(delay=(1.0, 2.0))
        for url, rotate in items:
            with lock:
                if time.monotonic() > deadline or counts["ok"] + counts["failed"] >= limit:
                    return
            res = _one(fetcher, url, rotate)
            with lock:
                counts[res] += 1

    # Las tiendas con más fotos primero, para que no queden para el final.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(host, sorted(by_host.values(), key=len, reverse=True)))
    pending = max(0, len(todo) - sum(counts.values()))
    print(f"miniaturas: {counts['ok']} nuevas, {counts['failed']} fallidas, {pending} pendientes "
          f"({len(by_host)} tiendas)", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--minutes", type=float, default=20)
    parser.add_argument("--cat", help="solo las fotos de este catálogo (scraper.catalog --cat)")
    args = parser.parse_args(argv)
    run(args.limit, args.minutes, args.cat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
