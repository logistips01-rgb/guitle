#!/usr/bin/env python3
"""Reloj de guitle en el servidor de IONOS (antes, .github/workflows/reloj.yml siempre encendido en GitHub).

Lo lanza cada minuto guitle-reloj.timer. GitHub retrasa sus tareas programadas de minutos a horas; este reloj pide a
GitHub que lance cada tarea a su hora (workflow_dispatch, arranca en segundos). Antes de lanzar mira que no se haya
lanzado ya desde su hora (por la programación de GitHub o por una vuelta anterior): nada se duplica. Pasada su hora,
la lanza si aún no se ha hecho en 3 horas. El token (GH_RELOJ_TOKEN, solo Actions y Contents de guitle) está en
/root/.config/guitle/gh-token, que solo puede leer root.
"""
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO, RAMA = "logistips01-rgb/guitle", "claude/friendly-fermat-yycain"
TOKEN = Path("/root/.config/guitle/gh-token").read_text().strip()
HECHAS = Path("/var/lib/guitle/reloj-hechas.json")  # lo lanzado en las últimas horas, por si la API tarda en verlo
# (hora UTC "HH:MM", workflow, entradas, título del run que cuenta como "ya hecho" o None = cualquiera)
TAREAS = [
    ("03:17", "catalog.yml", {"tanda": "17 3 * * *"}, "catalog 17 3 * * *"),
    ("11:17", "catalog.yml", {"tanda": "17 11 * * *"}, "catalog 17 11 * * *"),
    ("19:17", "catalog.yml", {"tanda": "17 19 * * *"}, "catalog 17 19 * * *"),
    ("04:13", "papelera.yml", {}, None),
    ("09:23", "congruencia.yml", {}, None),
    ("15:41", "musica.yml", {}, None),
    ("07:37", "buzon.yml", {}, None),
] + [(f"{h:02d}:43", "catalog-respaldo.yml", {}, None) for h in range(0, 24, 4)]
VENTANA = timedelta(hours=3)


def api(path, body=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}", method="POST" if body else "GET",
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "guitle-reloj"})
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read()
    return json.loads(txt) if txt else {}


def ya_hecha(wf, desde, titulo):
    runs = api(f"actions/workflows/{wf}/runs?per_page=30&created=>={desde:%Y-%m-%dT%H:%M:%SZ}")["workflow_runs"]
    return any(r["event"] in ("schedule", "workflow_dispatch") and (titulo is None or r.get("display_title") == titulo)
               for r in runs)


def main():
    ahora = datetime.now(timezone.utc)
    try:
        hechas = {k: v for k, v in json.loads(HECHAS.read_text()).items() if v > time.time() - 6 * 3600}
    except (OSError, ValueError):
        hechas = {}
    for hhmm, wf, entradas, titulo in TAREAS:
        h, m = map(int, hhmm.split(":"))
        hora = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
        if hora > ahora:
            hora -= timedelta(days=1)
        clave = f"{wf}|{hora.isoformat()}|{titulo}"
        if clave in hechas or not (hora <= ahora < hora + VENTANA):
            continue
        try:
            if not ya_hecha(wf, hora, titulo):
                api(f"actions/workflows/{wf}/dispatches", {"ref": RAMA, "inputs": entradas})
                print(f"{ahora:%F %H:%M} lanzada {wf} {entradas or ''} ({(ahora - hora).total_seconds() / 60:.0f} min tras su hora)")
            hechas[clave] = time.time()
        except Exception as e:  # noqa: BLE001 - se reintenta el minuto siguiente
            print(f"{ahora:%F %H:%M} {wf}: {e}")
    HECHAS.parent.mkdir(parents=True, exist_ok=True)
    HECHAS.write_text(json.dumps(hechas))


if __name__ == "__main__":
    main()
