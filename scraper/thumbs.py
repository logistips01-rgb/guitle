"""Miniaturas uniformes de las fotos de producto (img/p/).

Cada tienda fotografía a su manera (guitarra tumbada, lienzo apaisado con la guitarra en vertical, mucho
margen…). Aquí se recorta el fondo blanco, se pone la guitarra en vertical con el cuerpo abajo y se guarda a
un alto fijo, para que en la web todas se vean igual.

Uso:
    python -m scraper.thumbs [--limit 300] [--minutes 20] [--cat pt]
"""
import argparse
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageChops, ImageOps

from .catalog import is_pack, load
from .fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "img" / "p"
HEIGHT = 360
WHITE = 244  # canal más oscuro por encima de esto = fondo blanco
ROTATE_CATEGORIES = {"guitarra", "bajo"}


def name_for(url, pack=False):
    """Nombre de la miniatura. Los packs tienen la suya (la foto entera), distinta de la de una guitarra sola."""
    return hashlib.sha1((("pack:" if pack else "") + url).encode()).hexdigest()[:16] + ".webp"


# Miniaturas ya hechas y su alto/ancho: las fotos están en R2 (no en git), así que la lista dice cuáles hay sin
# tenerlas en disco. index() la completa con las nuevas de img/p/.
INDEX = ROOT / "data" / "thumbs.json"
_index = None


def _load_index():
    global _index
    if _index is None:
        _index = load(INDEX, {})
    return _index


def existing(url, pack=False):
    """Nombre de la miniatura si ya existe (para los JSON de la web)."""
    if not url:
        return None
    name = name_for(url, pack)
    # Rehechas (rehacer): la nueva lleva otro nombre, para que la vieja cortada no siga en la caché de nadie.
    new = _renames().get(name)
    if new and (new in _load_index() or (DIR / new).exists()):
        return new
    return name if name in _load_index() or (DIR / name).exists() else None


RENAMES = ROOT / "data" / "fotos-rehechas.json"
_renames_cache = None


def _renames():
    global _renames_cache
    if _renames_cache is None:
        _renames_cache = load(RENAMES, {})
    return _renames_cache


def slenderness(name):
    """Alto/ancho de una miniatura: una guitarra entera es esbelta (>2); un primer plano, no."""
    if (DIR / name).exists():
        with Image.open(DIR / name) as im:
            return im.height / im.width
    return _load_index().get(name, 0)


def index():
    """Añade a data/thumbs.json las miniaturas de img/p/ que aún no están. Devuelve cuántas."""
    idx, new = _load_index(), 0
    for f in DIR.glob("*.webp") if DIR.exists() else []:
        if f.name not in idx:
            try:
                with Image.open(f) as im:
                    idx[f.name] = round(im.height / im.width, 4)
                new += 1
            except Exception as exc:  # noqa: BLE001 - una foto rota no se apunta (se rehará)
                print(f"[thumb] {f.name}: {type(exc).__name__}", flush=True)
    # Una entrada por línea y en orden: en git, cada lectura solo añade líneas.
    INDEX.write_text("{\n" + ",\n".join(f'"{k}":{v}' for k, v in sorted(idx.items())) + "\n}\n", encoding="utf-8")
    print(f"miniaturas: {len(idx)} en la lista ({new} nuevas)", flush=True)
    return new


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
    if rotate != "pack":
        # Pack (rotate="pack"): la foto entera (guitarra, ampli, funda…), sin quedarse con la pieza más grande ni girarla.
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
    if rotate is True:
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
    """{url: girar} de las fotos que usa la web: productos seguidos y catálogo; girar = "pack" para la foto entera de un
    pack. cat: solo las de ese catálogo."""
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
                # Las guitarras se ponen en vertical; teclados y pedales se dejan como vienen; un pack, entero.
                out.setdefault(o["image"], "pack" if is_pack(o)
                               else (o.get("kind") or "electrica") in {"electrica", "acustica", "clasica", "portuguesa"})
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
        (DIR / name_for(url, rotate == "pack")).write_bytes(data)
        return "ok"
    except Exception as exc:  # noqa: BLE001 - una foto rara no para el resto
        print(f"[thumb] {url[:80]}: {type(exc).__name__}", flush=True)
        return "failed"


def cortada(data):
    """¿Miniatura cortada? Una guitarra entera acaba en curvas por los cuatro lados; si un lado de su silueta es una
    línea recta larga (la pala, el cuerpo o media guitarra cortados), está cortada."""
    im = Image.open(BytesIO(data)).convert("RGB")
    r, g, b = im.split()
    d = ImageChops.darker(ImageChops.darker(r, g), b)
    w, h = d.size
    px = d.load()
    ink = lambda x, y: px[x, y] < 235
    cols = [x for x in range(w) if sum(ink(x, y) for y in range(h)) > 2]
    rows = [y for y in range(h) if sum(ink(x, y) for x in range(w)) > 2]
    if not cols or not rows:
        return True
    x0, x1, y0, y1 = cols[0], cols[-1], rows[0], rows[-1]

    def run_(seq):
        best = cur = 0
        for v in seq:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        return best
    side = max(run_([ink(x, y) for y in range(h)]) for x in (x0, x0 + 1, x1 - 1, x1)) / (y1 - y0 + 1)
    end = max(run_([ink(x, y) for x in range(w)]) for y in (y0, y0 + 1, y1 - 1, y1)) / (x1 - x0 + 1)
    return side > 0.12 or end > 0.6


_ok_cache = {}


def thumb_ok(name, guitar=True):
    """¿Miniatura buena para la portada? La de disco (recién hecha) o la publicada en guitle.com. Una guitarra: sin
    bordes rectos largos (cortada) y alta y estrecha (ancha es un detalle o un recorte). Si no se puede mirar, vale."""
    key = (name, guitar)
    if key not in _ok_cache:
        try:
            path = DIR / name
            if path.exists():
                data = path.read_bytes()
            else:
                import requests
                r = requests.get(f"https://guitle.com/img/p/{name}", timeout=15)
                r.raise_for_status()
                data = r.content
            im = Image.open(BytesIO(data))
            _ok_cache[key] = not guitar or (not cortada(data) and im.width <= 0.6 * im.height)
        except Exception:  # noqa: BLE001
            _ok_cache[key] = True
    return _ok_cache[key]


def thumbs_ok(names, guitar=True, workers=12):
    """thumb_ok de muchas a la vez: {nombre: buena}."""
    names = list(dict.fromkeys(names))
    with ThreadPoolExecutor(workers) as ex:
        return dict(zip(names, ex.map(lambda n: thumb_ok(n, guitar), names)))


MALAS = ROOT / "data" / "fotos-malas.txt"


def rehacer(workers=8):
    """Rehace las miniaturas de data/fotos-malas.txt (de la foto actual de la tienda, con el recorte de hoy) y quita
    de la lista las que ya salen enteras; las que siguen cortadas se quedan fuera de la portada."""
    from concurrent.futures import ThreadPoolExecutor
    lines = MALAS.read_text(encoding="utf-8").splitlines()
    bad = {l.strip() for l in lines if l.strip() and not l.startswith("#")}
    src = {name_for(u, r == "pack"): (u, r) for u, r in wanted().items()}
    DIR.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(delay=(1.0, 2.0))
    fixed, still = set(), set()

    def one(name):
        if name not in src:
            return name, "sin foto"
        url, rot = src[name]
        if _one(fetcher, url, rot) != "ok":
            return name, "no se pudo bajar"
        data = (DIR / name).read_bytes()
        (DIR / name).unlink()  # la vieja (cortada) no se toca en R2: la nueva va con otro nombre
        if cortada(data) or (rot is True and Image.open(BytesIO(data)).width > 0.6 * Image.open(BytesIO(data)).height):
            return name, "sigue cortada"  # una guitarra es alta y estrecha: ancha es un detalle o un recorte
        (DIR / (name[:-5] + "-2.webp")).write_bytes(data)
        return name, "ok"
    with ThreadPoolExecutor(workers) as ex:
        for name, res in ex.map(one, sorted(bad)):
            print(f"[rehacer] {name}: {res}", flush=True)
            (fixed if res == "ok" else still).add(name)
    renames = load(RENAMES, {})
    renames.update({n: n[:-5] + "-2.webp" for n in fixed})
    RENAMES.write_text(json.dumps(renames, sort_keys=True, indent=0), encoding="utf-8")
    MALAS.write_text("\n".join([l for l in lines if l.startswith("#")] + sorted(still)) + "\n", encoding="utf-8")
    print(f"[rehacer] rehechas {len(fixed)}, siguen fuera de portada {len(still)}", flush=True)


def run(limit=300, minutes=20, cat=None, workers=8):
    """Las fotos se piden por tienda (dominio) en paralelo: cada tienda, de una en una y con su pausa de 1-2 s, como
    siempre; lo que cambia es que varias tiendas avanzan a la vez."""
    DIR.mkdir(parents=True, exist_ok=True)
    todo = [(u, r) for u, r in wanted(cat).items() if not existing(u, r == "pack")]
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
    parser.add_argument("--index", action="store_true", help="solo apuntar en data/thumbs.json las de img/p/")
    parser.add_argument("--rehacer", action="store_true", help="rehacer las de data/fotos-malas.txt")
    args = parser.parse_args(argv)
    if args.rehacer:
        rehacer()
    elif args.index:
        index()
    else:
        run(args.limit, args.minutes, args.cat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
