"""Prueba diaria de que los precios de guitle son los de la tienda (.github/workflows/congruencia.yml).

Elige una guitarra o equipo de cada tienda de cada país (leída en las últimas 30 h, para probar el lector y no el
retraso) y un disco de CDGO; scraper/congruencia.js abre cada ficha en un navegador y mira si el precio que enseña
guitle sale en la página tal como la ve el cliente. Lo que no cuadra va a data/congruencia.json y a los avisos de
stats.html. Así se encontraron Partitura (+21 % de IVA de más) y Zingla ("Consultar" con precio) el 8/11/2026.

    python -m scraper.congruencia --pick filas.json
"""
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "data" / "catalog"
ES_DIRS = {"", "acusticas", "equipo", "mas"}


def country(rel_dir):
    """'' / 'acusticas' / 'mas' → 'es'; 'fr' / 'frmas' → 'fr'."""
    if rel_dir in ES_DIRS:
        return "es"
    return rel_dir[:-3] if rel_dir.endswith("mas") else rel_dir


def pick(seed=None):
    rnd = random.Random(seed or datetime.now(timezone.utc).date().isoformat())
    since = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    rows, done = [], set()
    for p in sorted(CAT.rglob("offers.json")):
        rel = str(p.parent.relative_to(CAT)) if p.parent != CAT else ""
        c = country(rel)
        try:
            offers = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        by = {}
        for o in offers.values():
            # Solo con stock: los agotados se enseñan con su último precio (decisión de Manuel, 8/11/2026) y muchas
            # tiendas no ponen precio a lo agotado; saldrían como "distintos" cada día.
            if (o.get("status") == "ok" and o.get("price") and not o.get("down_since") and o.get("in_stock") is not False
                    and o.get("checked", "") >= since and o.get("url", "").startswith("http")):
                by.setdefault(o["store"], []).append(o)
        for store, os_ in sorted(by.items()):
            if (c, store) in done:
                continue
            done.add((c, store))
            o = rnd.choice(os_)
            rows.append({"pais": c, "tienda": store, "url": o["url"], "precio": o["price"],
                         "moneda": o.get("currency", "EUR"), "leido": o["checked"][:16], "nombre": o.get("name", "")})
    cdgo = json.loads((ROOT / "data" / "musica" / "pt" / "consultas.json").read_text(encoding="utf-8")).get("cdgo", {})
    recent = [v for v in cdgo.values() if len(v) > 3 and v[0] >= since[:10]]
    if recent:
        v = rnd.choice(recent)
        rows.append({"pais": "pt", "tienda": "cdgo", "url": v[3], "precio": v[1], "moneda": "EUR", "leido": v[0],
                     "nombre": v[4]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", required=True, help="fichero de salida con las fichas a probar")
    a = ap.parse_args()
    rows = pick()
    Path(a.pick).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print(f"congruencia: {len(rows)} fichas de {len({r['pais'] for r in rows})} países", flush=True)


if __name__ == "__main__":
    main()
