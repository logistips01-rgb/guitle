"""Miniaturas uniformes de las fotos de producto (img/p/).

Cada tienda fotografía a su manera (guitarra tumbada, lienzo apaisado con la guitarra en vertical, mucho
margen…). Aquí se recorta el fondo blanco, se pone la guitarra en vertical con el cuerpo abajo y se guarda a
un alto fijo, para que en la web todas se vean igual.

Uso:
    python -m scraper.thumbs [--limit 300] [--minutes 20]
"""
import argparse
import hashlib
import sys
import time
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from .catalog import load
from .fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "img" / "p"
HEIGHT = 360
WHITE = 235  # más claro que esto se considera fondo
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


def normalize(data, rotate=True):
    im = ImageOps.exif_transpose(Image.open(BytesIO(data)))
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    rgb = bg.convert("RGB")
    mask = rgb.convert("L").point(lambda v: 255 if v < WHITE else 0)
    bbox = mask.getbbox()
    if not bbox:
        return None
    rgb, mask = rgb.crop(bbox), mask.crop(bbox)
    if max(rgb.size) > 600:  # proyecciones sobre una copia pequeña: rápido y suficiente
        scale = 600 / max(rgb.size)
        small = mask.resize((max(1, round(mask.width * scale)), max(1, round(mask.height * scale))))
    else:
        scale, small = 1, mask
    y0, y1 = _main_block(small, 1)
    x0, x1 = _main_block(small.crop((0, y0, small.width, y1)), 0)
    box = tuple(round(v / scale) for v in (x0, y0, x1, y1))
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
    canvas = canvas.resize((max(1, round(canvas.width * HEIGHT / canvas.height)), HEIGHT), Image.LANCZOS)
    out = BytesIO()
    canvas.save(out, "WEBP", quality=78, method=6)
    return out.getvalue()


def wanted():
    """(url, girar) de las fotos que usa la web: productos seguidos y catálogo."""
    out = {}
    latest = load(ROOT / "data" / "latest.json", {})
    category = {p["sku"]: p.get("category", "guitarra") for p in latest.get("products", [])}
    for i in latest.get("items", []):  # todas las fotos de cada producto, para poder elegir la mejor
        if i.get("image"):
            out[i["image"]] = category.get(i["sku"], "guitarra") in ROTATE_CATEGORIES
    for o in load(ROOT / "data" / "catalog" / "offers.json", {}).values():  # todas las tiendas, para elegir la mejor
        if o.get("status") == "ok" and o.get("image"):
            out.setdefault(o["image"], True)
    return out


def run(limit=300, minutes=20):
    DIR.mkdir(parents=True, exist_ok=True)
    todo = [(u, r) for u, r in wanted().items() if not (DIR / name_for(u)).exists()]
    fetcher = Fetcher(delay=(1.0, 2.0))
    deadline = time.monotonic() + minutes * 60
    done = failed = 0
    for url, rotate in todo[:limit]:
        if time.monotonic() > deadline:
            break
        try:
            src = url
            if not fetcher.allowed(src)[0]:
                # Muchas tiendas prohíben URLs con parámetros (?ts=…): la misma imagen sin ellos suele estar permitida.
                src = url.split("?")[0]
                if src == url or not fetcher.allowed(src)[0]:
                    continue
            resp = fetcher.get(src)
            if resp.status_code != 200 or not resp.headers.get("content-type", "").startswith("image"):
                failed += 1
                continue
            data = normalize(resp.content, rotate)
            if data:
                (DIR / name_for(url)).write_bytes(data)
                done += 1
        except Exception as exc:  # noqa: BLE001 - una foto rara no para el resto
            failed += 1
            print(f"[thumb] {url[:80]}: {type(exc).__name__}", flush=True)
    print(f"miniaturas: {done} nuevas, {failed} fallidas, {max(0, len(todo) - done - failed)} pendientes", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--minutes", type=float, default=20)
    args = parser.parse_args(argv)
    run(args.limit, args.minutes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
