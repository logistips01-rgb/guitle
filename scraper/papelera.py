"""Papelera de fotos (img/p/): las miniaturas que ya no usa ninguna ficha se apuntan con fecha en data/papelera.json y,
si en 30 días nadie las vuelve a usar, se borran de R2, del servidor propio y de la lista data/thumbs.json.

  - No se mueve nada: apuntarlas no cuesta operaciones de R2, y borrar en R2 es gratis.
  - "Usada" = su nombre aparece en algún fichero de data/ (catálogos de todos los países, chollos, portada, discos…).
  - Si una ficha vuelve a necesitar una foto ya borrada, la miniatura se rehace sola (su nombre sale de la dirección de
    la imagen); el informe lo dice igualmente (data/papelera-informe.json, en stats.html) para ver qué ha pasado.

    python -m scraper.papelera                (apunta y escribe el informe; lista en BORRAR lo que toca borrar)
    python -m scraper.papelera --confirmar F  (tras borrar en R2 los nombres de F: los quita de thumbs.json)
"""
import argparse
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path

from . import thumbs

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAPELERA = DATA / "papelera.json"          # {día en que se apuntó: [fotos]} (agrupado: la mitad de tamaño)
BORRADAS = DATA / "papelera-borradas.json"  # {foto: día en que se borró}, los últimos 90 días
INFORME = DATA / "papelera-informe.json"
DIAS = 30
POR_DIA = 40000   # como mucho, por día (las más antiguas primero)
TOPE = 0.6        # si la papelera pasa del 60 % de las fotos, algo va mal: no se borra nada
SKIP = {"thumbs.json", "papelera.json", "papelera-borradas.json", "papelera-informe.json", "fotos-malas.txt",
        "coleccion-fuera.txt", "fotos-revisadas.json", "fotos-rehechas.json"}
NAME = re.compile(rb"[0-9a-f]{16}\.webp")


def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=0, sort_keys=True) + "\n", encoding="utf-8")


def _load_pap():
    return {k: d for d, ks in _load(PAPELERA, {}).items() for k in ks}


def _save_pap(pap):
    by = {}
    for k, d in pap.items():
        by.setdefault(d, []).append(k)
    PAPELERA.write_text("{\n" + ",\n".join(f'"{d}":{json.dumps(sorted(ks), separators=(",", ":"))}' for d, ks in sorted(by.items()))
                        + "\n}\n", encoding="utf-8")


def usadas():
    out = set()
    for root, _, files in os.walk(DATA):
        for f in files:
            if f not in SKIP:
                try:
                    out.update(m.decode() for m in NAME.findall(Path(root, f).read_bytes()))
                except OSError:
                    pass
    return out


def pedidas(borradas):
    """Fichas cuya foto (por la dirección de su imagen) es una ya borrada: se rehará, pero se cuenta en el informe."""
    out = []
    for path in DATA.glob("catalog/**/*.json"):
        if any(x in path.name for x in ("offers", "history", "pvp", "paises")):
            continue
        d = _load(path, {})
        for p in d.get("products", []) if isinstance(d, dict) else []:
            img = p.get("img")
            if img and thumbs.name_for(img) in borradas:
                out.append({"ficha": p.get("slug"), "nombre": p.get("name"), "foto": thumbs.name_for(img),
                            "borrada": borradas[thumbs.name_for(img)], "catalogo": str(path.relative_to(DATA))})
    return out


def run(hoy=None):
    hoy = hoy or date.today().isoformat()
    idx = _load(DATA / "thumbs.json", {})
    used = usadas()
    pap = _load_pap()
    borradas = {k: v for k, v in _load(BORRADAS, {}).items() if v >= (date.fromisoformat(hoy) - timedelta(days=90)).isoformat()}
    rescatadas = [k for k in pap if k in used]
    for k in rescatadas:
        del pap[k]
    nuevas = [k for k in idx if k not in used and k not in pap]
    for k in nuevas:
        pap[k] = hoy
    corte = (date.fromisoformat(hoy) - timedelta(days=DIAS)).isoformat()
    borrar = sorted((d, k) for k, d in pap.items() if d <= corte and k in idx)
    borrar = [k for _, k in borrar[:POR_DIA]]
    if len(pap) > TOPE * max(1, len(idx)):
        print(f"::error::papelera con {len(pap)} de {len(idx)} fotos: demasiadas, no se borra nada", flush=True)
        borrar = []
    _save_pap(pap)
    _save(BORRADAS, borradas)
    ped = pedidas(borradas)
    informe = {"actualizado": hoy, "fotos": len(idx), "usadas": len(used & set(idx)), "en_papelera": len(pap),
               "nuevas_hoy": len(nuevas), "rescatadas_hoy": len(rescatadas), "a_borrar_hoy": len(borrar),
               "borradas_90_dias": len(borradas), "pedidas_tras_borrar": len(ped), "pedidas": ped[:100]}
    _save(INFORME, informe)
    (ROOT / "BORRAR.txt").write_text("".join(f"img/p/{k}\n" for k in borrar), encoding="utf-8")
    print(f"papelera: {len(idx)} fotos, {len(pap)} en la papelera (+{len(nuevas)} hoy, {len(rescatadas)} rescatadas), "
          f"{len(borrar)} a borrar hoy, {len(ped)} fichas pidieron una ya borrada", flush=True)
    return borrar


def confirmar(lista, hoy=None):
    """Las de la lista ya se han borrado de R2: fuera de thumbs.json y de la papelera, apuntadas como borradas."""
    hoy = hoy or date.today().isoformat()
    names = [l.strip().rsplit("/", 1)[-1] for l in Path(lista).read_text(encoding="utf-8").splitlines() if l.strip()]
    idx, pap, borradas = _load(DATA / "thumbs.json", {}), _load_pap(), _load(BORRADAS, {})
    for k in names:
        idx.pop(k, None)
        pap.pop(k, None)
        borradas[k] = hoy
    (DATA / "thumbs.json").write_text("{\n" + ",\n".join(f'"{k}":{v}' for k, v in sorted(idx.items())) + "\n}\n",
                                      encoding="utf-8")
    _save_pap(pap)
    _save(BORRADAS, borradas)
    inf = _load(INFORME, {})
    inf["borradas_hoy"] = len(names)
    inf["borradas_90_dias"] = len(borradas)
    _save(INFORME, inf)
    print(f"papelera: {len(names)} fotos borradas y quitadas de la lista", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirmar", help="fichero con lo que ya se ha borrado de R2")
    a = ap.parse_args()
    confirmar(a.confirmar) if a.confirmar else run()
