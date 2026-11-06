"""Fichas en cajas: las fichas de producto de cada país (<país>/g/<slug>.html) se guardan agrupadas en 2.048 cajas
comprimidas (<país>/_g/<nnnn>.json.gz, {slug: html}) en vez de una a una. El Worker (cloudflare/worker.js) saca de su
caja la ficha que le piden: la misma página, byte a byte.

Por qué: en R2 cada fichero subido es una escritura de pago (clase A). Con una ficha por fichero, un cambio de diseño
reescribe cientos de miles; con cajas, como mucho 2.048 por país. Las cajas se escriben siempre igual (claves ordenadas,
gzip sin fecha), así que una caja solo cambia, y solo se sube, si cambia alguna de sus fichas.

La caja de una ficha: FNV-1a de 32 bits del slug (UTF-8) módulo CAJAS; el Worker hace la misma cuenta.
Uso: python -m scraper.cajas uk [fr …]   (lo lanza .github/r2.sh antes de subir cada país)
"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAJAS = 2048


def fnv(text):
    h = 0x811C9DC5
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


def caja(slug):
    return f"{fnv(slug) % CAJAS:04x}"


def empaquetar(code):
    """Escribe las cajas del país con sus fichas de hoy; devuelve (fichas, cajas escritas o cambiadas)."""
    src, out = ROOT / code / "g", ROOT / code / "_g"
    boxes = {}
    for f in src.glob("*.html"):
        boxes.setdefault(caja(f.stem), {})[f.stem] = f.read_text(encoding="utf-8")
    if not boxes:
        return 0, 0
    out.mkdir(exist_ok=True)
    changed = 0
    for name, pages in boxes.items():
        data = gzip.compress(json.dumps(pages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"),
                             compresslevel=9, mtime=0)
        path = out / f"{name}.json.gz"
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            changed += 1
    for old in out.glob("*.json.gz"):  # cajas que se han quedado sin fichas
        if old.name[:-8] not in boxes:
            old.unlink()
    return sum(len(p) for p in boxes.values()), changed


CAJAS_R = 512  # secciones como la de discos (<país>/records/): todas sus páginas, en 512 cajas (<país>/_r/)


def empaquetar_carpeta(code, sub):
    """Todas las páginas de <país>/<sub>/ (también las de subcarpetas, p. ej. records/artist/) en <país>/_r/; la clave de
    cada página es su ruta dentro del país ("records/x.html") y su caja, FNV de esa clave módulo CAJAS_R."""
    src, out = ROOT / code / sub, ROOT / code / "_r"
    boxes = {}
    for f in src.rglob("*.html"):
        key = f.relative_to(ROOT / code).as_posix()
        boxes.setdefault(f"{fnv(key) % CAJAS_R:04x}", {})[key] = f.read_text(encoding="utf-8")
    if not boxes:
        return 0, 0
    out.mkdir(exist_ok=True)
    changed = 0
    for name, pages in boxes.items():
        data = gzip.compress(json.dumps(pages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"),
                             compresslevel=9, mtime=0)
        path = out / f"{name}.json.gz"
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            changed += 1
    for old in out.glob("*.json.gz"):
        if old.name[:-8] not in boxes:
            old.unlink()
    return sum(len(p) for p in boxes.values()), changed


if __name__ == "__main__":
    if sys.argv[1:2] == ["--carpeta"]:
        n, changed = empaquetar_carpeta(sys.argv[2], sys.argv[3])
        print(f"cajas {sys.argv[2]}/{sys.argv[3]}: {n} páginas ({changed} cajas escritas)", flush=True)
        sys.exit(0)
    for code in sys.argv[1:]:
        n, changed = empaquetar(code)
        print(f"cajas {code}: {n} fichas en {len(list((ROOT / code / '_g').glob('*.json.gz'))) if n else 0} cajas "
              f"({changed} escritas)", flush=True)
