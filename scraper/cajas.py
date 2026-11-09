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
import re
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
    indice(out, [slug for pages in boxes.values() for slug in pages])
    return sum(len(p) for p in boxes.values()), changed


EAN_TAIL = re.compile(r"-(\d{8,14})$")


def indice(out, slugs):
    """<país>/_g/indice.json: para las direcciones viejas de fichas que ya no existen (Google las tenía: 1.089 errores 404
    en noviembre de 2026). El Worker busca la ficha de hoy por el código de barras del final de la dirección ("e") o por
    la dirección sin él ("n"), y redirige (301); si no, responde "ya no está disponible" (410)."""
    e, n = {}, {}
    for slug in sorted(slugs):
        m = EAN_TAIL.search(slug)
        if m:
            e.setdefault(m.group(1).lstrip("0"), slug)
        n.setdefault(EAN_TAIL.sub("", slug), slug)
    data = json.dumps({"e": e, "n": n}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    path = out / "indice.json"
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


CAJAS_R = 512  # secciones como la de discos (<país>/records/): todas sus páginas, en 512 cajas (<país>/_r/)


def empaquetar_carpeta(code, sub):
    """Todas las páginas de <país>/<sub>/ (también las de subcarpetas, p. ej. records/artist/) en <país>/_r/; la clave de
    cada página es su ruta dentro del país ("records/x.html") y su caja, FNV de esa clave módulo CAJAS_R."""
    home = ROOT if code == "es" else ROOT / code  # España, en la raíz: discos/ y _r/
    src, out = home / sub, home / "_r"
    boxes = {}
    for f in src.rglob("*.html"):
        key = f.relative_to(home).as_posix()
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
