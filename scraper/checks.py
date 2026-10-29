"""Comprobaciones de sentido común del catálogo, cada noche después de la lectura.

Busca lo que un usuario vería raro y avisa (data/checks.json y avisos en el registro de GitHub Actions):
  - precio sin IVA: el de una tienda × 1,21 es casi exactamente el de las demás (fallo de MAT del 27/10);
  - precio fuera de lugar: una tienda un 25 % o más por debajo de la mediana de las otras (3 o más tiendas);
  - fotos perdidas: guitarras que tenían miniatura en la última versión publicada y ya no;
  - guitarras sin su página g/<slug>.html.

    python -m scraper.checks
"""
import json
import subprocess
import sys
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
FILES = {"electrica": "data/catalog/products.json", "acustica": "data/catalog/acusticas/acusticas.json",
         "clasica": "data/catalog/acusticas/clasicas.json", "teclado": "data/catalog/equipo/teclados.json",
         "pedal": "data/catalog/equipo/pedales.json", "bajo": "data/catalog/mas/bajos.json",
         "ampli": "data/catalog/mas/amplis.json", "estuche": "data/catalog/mas/estuches.json",
         "micro": "data/catalog/mas/micros.json"}
LOW = 0.75  # por debajo del 75 % de la mediana de las demás tiendas, se revisa


def _published(path):
    """La versión del fichero en el último commit (lo que había antes de esta lectura)."""
    out = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)["products"] if out.returncode == 0 else []
    except json.JSONDecodeError:
        return []


def check():
    issues = []
    for kind, path in FILES.items():
        if not (ROOT / path).exists():
            continue  # catálogo nuevo que aún no se ha leído
        products = json.loads((ROOT / path).read_text(encoding="utf-8"))["products"]
        before = {p["id"]: p for p in _published(path)}
        for p in products:
            items = [i for i in p["items"] if not i.get("m")]
            for i in items:
                others = [o["p"] for o in items if o["s"] != i["s"]]
                if len(others) < 2:
                    continue
                mid = median(others)
                # Un precio sin IVA casi nunca es redondo (660,33 €), pero con el 21 % sí (799 €).
                gross = i["p"] * 1.21
                # Y un precio de tienda con céntimos acaba en 5 o 0 (185,95 €); uno sin IVA, no.
                cents = round(i["p"] * 100) % 100
                if (cents % 5 and abs(gross - round(gross)) < 0.02 and abs(gross - mid) / mid < 0.03):
                    issues.append({"kind": kind, "type": "sin_iva", "store": i["s"], "name": p["name"], "slug": p["slug"],
                                   "price": i["p"], "median": mid})
                elif len(others) >= 2 and i["p"] < mid * LOW:
                    issues.append({"kind": kind, "type": "fuera_de_lugar", "store": i["s"], "name": p["name"],
                                   "slug": p["slug"], "price": i["p"], "median": mid})
            old = before.get(p["id"])
            if old and old.get("th") and not p.get("th"):
                issues.append({"kind": kind, "type": "foto_perdida", "name": p["name"], "slug": p["slug"]})
            if not (ROOT / "g" / f"{p['slug']}.html").exists():
                issues.append({"kind": kind, "type": "sin_pagina", "name": p["name"], "slug": p["slug"]})
    return issues


def main():
    issues = check()
    (ROOT / "data" / "checks.json").write_text(json.dumps(issues, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    counts = {}
    for i in issues:
        counts[i["type"]] = counts.get(i["type"], 0) + 1
    print(f"[checks] {len(issues)} avisos {counts}", flush=True)
    for i in issues[:40]:
        print(f"::warning::{i['type']} · {i.get('store', '')} · {i['name']} · {i.get('price', '')} (mediana {i.get('median', '')})",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
