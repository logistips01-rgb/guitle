"""IPC de Argentina (INDEC, nivel general nacional, mensual) para la gráfica "precio sin inflación" de las fichas de
guitle.com/ar/ (producto.js). Fuente: API de series de tiempo de datos.gob.ar, serie 148.3_INIVELNAL_DICI_M_26.
Escribe data/ipc-ar.json: {"meses": {"AAAA-MM": índice}, "ultimo": "AAAA-MM", "tasa": inflación del último mes}.
Para los meses que el INDEC aún no ha publicado, producto.js usa esa última inflación mensual (y lo dice).
Uso: python -m scraper.ipc_ar   (lo lanza .github/workflows/ipc-ar.yml cada semana)
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ipc-ar.json"
URL = ("https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&start_date=2025-01-01"
       "&limit=1000&format=json")


def main():
    data = requests.get(URL, timeout=60, headers={"User-Agent": "guitle/1.0 (+https://guitle.com)"}).json()["data"]
    meses = {d[:7]: round(v, 4) for d, v in data if v}
    keys = sorted(meses)
    if len(keys) < 2:
        raise SystemExit("IPC: la API no ha dado datos suficientes")
    out = {"meses": meses, "ultimo": keys[-1], "tasa": round(meses[keys[-1]] / meses[keys[-2]] - 1, 5)}
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"IPC: {len(meses)} meses, último {out['ultimo']}, inflación mensual {out['tasa'] * 100:.1f} %")


if __name__ == "__main__":
    main()
