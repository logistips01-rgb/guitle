#!/usr/bin/env bash
# Para el reloj viejo de GitHub (reloj.yml) que siga encendido o en cola, con el token del servidor. Una vez.
python3 - <<'PY'
import json, urllib.request
t = open("/root/.config/guitle/gh-token").read().strip()
H = {"Authorization": f"Bearer {t}", "Accept": "application/vnd.github+json", "User-Agent": "guitle-reloj"}
base = "https://api.github.com/repos/logistips01-rgb/guitle/actions"
for st in ("in_progress", "queued", "pending", "waiting"):
    runs = json.load(urllib.request.urlopen(urllib.request.Request(f"{base}/workflows/reloj.yml/runs?status={st}", headers=H), timeout=30))["workflow_runs"]
    for r in runs:
        urllib.request.urlopen(urllib.request.Request(f"{base}/runs/{r['id']}/cancel", method="POST", headers=H), timeout=30)
        print("parado reloj de GitHub", r["id"], st)
print("listo")
PY
