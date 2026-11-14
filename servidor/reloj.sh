#!/usr/bin/env bash
# Instala el reloj en el servidor (servidor/reloj.py, cada minuto) y lo prueba una vez. El token lo deja servidor.yml
# en /root/.config/guitle/gh-token antes de llamar a este paso.
set -euo pipefail
[ -s /root/.config/guitle/gh-token ] || { echo "falta el token (GH_RELOJ_TOKEN)"; exit 1; }
install -m 755 /root/reloj.py /usr/local/bin/guitle-reloj.py
cat > /etc/systemd/system/guitle-reloj.service <<'UNIT'
[Unit]
Description=guitle: lanza las tareas de GitHub a su hora
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/bin/guitle-reloj.py
UNIT
cat > /etc/systemd/system/guitle-reloj.timer <<'UNIT'
[Unit]
Description=guitle: reloj cada minuto
[Timer]
OnCalendar=*-*-* *:*:05
AccuracySec=5s
Persistent=true
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now guitle-reloj.timer
systemctl start guitle-reloj.service
sleep 2
journalctl -u guitle-reloj.service -n 5 --no-pager -o cat || true
systemctl list-timers guitle-reloj.timer --no-pager | head -3
# Prueba del token sin enseñarlo: ¿ve el repositorio y sus tareas?
python3 - <<'PY'
import json, urllib.request
t = open("/root/.config/guitle/gh-token").read().strip()
r = urllib.request.Request("https://api.github.com/repos/logistips01-rgb/guitle/actions/workflows?per_page=1",
                           headers={"Authorization": f"Bearer {t}", "User-Agent": "guitle-reloj"})
print("token: ve", json.load(urllib.request.urlopen(r, timeout=30))["total_count"], "tareas de GitHub")
PY
