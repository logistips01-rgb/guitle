#!/usr/bin/env bash
# Chequeo de salud del servidor de guitle.com, cada 5 minutos (guitle-salud.timer, lo instala vigilar.sh):
#   - si la web o el programa de las fichas no responden, se reinician (y se apunta);
#   - escribe /srv/guitle/salud/salud-servidor.json (guitle.com/salud-servidor.json), que enseña stats.html:
#     disco, memoria, última copia, reinicios de las últimas 24 h y avisos.
set -u
OUT=/srv/guitle/salud
LOG=$OUT/reinicios.log
mkdir -p "$OUT"
now=$(date -u +%FT%TZ)

ok() { curl -s -o /dev/null -m 15 -w '%{http_code}' "$1" | grep -qE '^(200|301|410)$'; }

# La web (Caddy) y las fichas (fichas.py): una ficha de un país va por los dos.
if ! ok "http://127.0.0.1/"; then
  systemctl restart caddy; echo "$now caddy" >> "$LOG"
fi
if ! ok "http://127.0.0.1:8081/fr/g/no-existe.html"; then
  systemctl restart guitle-fichas; echo "$now fichas" >> "$LOG"
fi

python3 - "$OUT" "$LOG" <<'PY'
import json, os, shutil, sys, time
from datetime import datetime, timezone, timedelta
out, log = sys.argv[1], sys.argv[2]
now = datetime.now(timezone.utc)
disk = shutil.disk_usage("/")
mem = {}
for line in open("/proc/meminfo"):
    k, v = line.split(":")
    mem[k] = int(v.split()[0]) // 1024
try:
    copia = open("/srv/guitle/ultima-copia").read().strip()
except OSError:
    copia = ""
cut = (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
try:
    reinicios = [l.split() for l in open(log) if l.split() and l.split()[0] >= cut]
except OSError:
    reinicios = []
avisos = []
libre = 100 * disk.free / disk.total
if libre < 15:
    avisos.append(f"Disco casi lleno: queda un {libre:.0f} %")
if mem.get("MemAvailable", 0) < 200:
    avisos.append(f"Poca memoria libre: {mem.get('MemAvailable', 0)} MB")
if copia:
    horas = (now - datetime.fromisoformat(copia.replace("Z", "+00:00"))).total_seconds() / 3600
    if horas > 6:
        avisos.append(f"La copia de seguridad desde R2 no termina bien desde hace {horas:.0f} h")
if len(reinicios) >= 3:
    avisos.append(f"{len(reinicios)} reinicios en 24 h")
load = os.getloadavg()[0]
data = {"actualizado": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "disco_libre_pct": round(libre, 1),
        "disco_libre_gb": round(disk.free / 1e9, 1), "memoria_libre_mb": mem.get("MemAvailable"),
        "carga": round(load, 2), "ultima_copia": copia, "reinicios_24h": [" ".join(r) for r in reinicios][-10:],
        "avisos": avisos}
tmp = os.path.join(out, ".salud.tmp")
with open(tmp, "w") as f:
    json.dump(data, f, ensure_ascii=False)
os.chmod(tmp, 0o644)
os.replace(tmp, os.path.join(out, "salud-servidor.json"))
PY
