"""Histórico diario de visitas y clics (todas las webs de guitle juntas), para informes y pruebas de tráfico.

Cada madrugada suma los contadores de c.js de los días que faltan (Firestore, colección "c": AAAA-MM-DD_v, _r_<origen>,
_t_<tienda>~<país>) y guarda un documento por día, "resumen_AAAA-MM-DD", en la misma colección: solo lo puede leer el
titular (reglas de "c"), igual que el resto de estadísticas. stats.html lo enseña en una tabla y lo descarga en CSV.
Los días cerrados no se tocan más; el de ayer se rehace (por las visitas que llegan pasada la medianoche).

Uso: FIREBASE_SA=... python -m scraper.resumen_visitas   (lo lanza .github/workflows/resumen-visitas.yml)
"""
import json
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .alerts import DOCS, session

MAX_READS = 30000  # por vuelta: el plan gratuito de Firestore da 50.000 lecturas al día


def _int(v):
    return int(float(v.get("integerValue") or v.get("doubleValue") or 0))


def _run(s, start, end, limit=None):
    """Documentos de "c" con id entre start (incluido) y end (excluido), en orden."""
    base = DOCS.split("/v1/", 1)[1]  # projects/…/databases/(default)/documents
    q = {"structuredQuery": {"from": [{"collectionId": "c"}],
                             "where": {"compositeFilter": {"op": "AND", "filters": [
                                 {"fieldFilter": {"field": {"fieldPath": "__name__"}, "op": "GREATER_THAN_OR_EQUAL",
                                                  "value": {"referenceValue": f"{base}/c/{start}"}}},
                                 {"fieldFilter": {"field": {"fieldPath": "__name__"}, "op": "LESS_THAN",
                                                  "value": {"referenceValue": f"{base}/c/{end}"}}}]}},
                             "orderBy": [{"field": {"fieldPath": "__name__"}}]}}
    if limit:
        q["structuredQuery"]["limit"] = limit
    r = s.post(f"{DOCS}:runQuery", json=q, timeout=(20, 120))
    r.raise_for_status()
    return [x["document"] for x in r.json() if "document" in x]


def summary(docs, day):
    out = {"fecha": day, "visitas": 0, "clics": 0, "google": 0, "instagram": 0, "otros_origenes": 0, "directo": 0}
    for d in docs:
        key = d["name"].rsplit("/", 1)[-1][len(day) + 1:]
        n = _int(d.get("fields", {}).get("n", {}))
        if key == "v":
            out["visitas"] += n
        elif key.startswith("t_"):
            out["clics"] += n
        elif key.startswith("r_"):
            ref = key[2:]
            if ref == "directo":
                out["directo"] += n
            elif "google" in ref:
                out["google"] += n
            elif "instagram" in ref:
                out["instagram"] += n
            else:
                out["otros_origenes"] += n
    return out


def main():
    print("[resumen] conectando con Firestore", flush=True)
    s = session()
    today = datetime.now(ZoneInfo("Europe/Madrid")).date()
    print("[resumen] leyendo los días ya resumidos", flush=True)
    done = {d["name"].rsplit("/", 1)[-1][len("resumen_"):] for d in _run(s, "resumen_", "resumen_~")}
    print(f"[resumen] {len(done)} días ya resumidos; buscando el primer día con visitas", flush=True)
    first = _run(s, "2000", "3", limit=1)
    if not first:
        print("[resumen] aún no hay visitas")
        return
    day = date.fromisoformat(first[0]["name"].rsplit("/", 1)[-1][:10])
    reads, written = 0, 0
    while day < today and reads < MAX_READS:
        key = day.isoformat()
        if key not in done or day == today - timedelta(days=1):
            docs = _run(s, key + "_", key + "_~")
            reads += len(docs) + 1
            row = summary(docs, key)
            s.patch(f"{DOCS}/c/resumen_{key}", json={"fields": {
                k: ({"stringValue": v} if k == "fecha" else {"integerValue": str(v)}) for k, v in row.items()}},
                timeout=60).raise_for_status()
            written += 1
            print(json.dumps(row, ensure_ascii=False), flush=True)
        day += timedelta(days=1)
    print(f"[resumen] {written} días guardados, {reads} lecturas", flush=True)


if __name__ == "__main__":
    main()
