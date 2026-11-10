#!/usr/bin/env bash
# Paso "vigilar": que el servidor se cuide solo.
#   - Caddy se reinicia solo si se cae (fichas.py ya lo hacía: Restart=always);
#   - guitle-salud.timer: cada 5 minutos reinicia lo que no responda y escribe el parte de salud (salud.sh);
#   - la configuración de Caddy con el dominio, con la ruta /salud-servidor.json.
set -euo pipefail
install -m 755 /root/salud.sh /opt/guitle/salud.sh
mkdir -p /etc/systemd/system/caddy.service.d /srv/guitle/salud
cat > /etc/systemd/system/caddy.service.d/10-guitle.conf <<'EOF'
[Service]
Restart=always
RestartSec=3
EOF
cat > /etc/systemd/system/guitle-salud.service <<'EOF'
[Unit]
Description=guitle: chequeo de salud
[Service]
Type=oneshot
ExecStart=/opt/guitle/salud.sh
EOF
cat > /etc/systemd/system/guitle-salud.timer <<'EOF'
[Unit]
Description=guitle: chequeo de salud cada 5 minutos
[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now guitle-salud.timer
# Configuración con el dominio (la que está en uso desde el 10/11/2026)
# Se valida ANTES de copiarla: una configuración mala no llega a usarse.
caddy validate --config /root/Caddyfile.dominio --adapter caddyfile 2>&1 | tail -1
cp /root/Caddyfile.dominio /etc/caddy/Caddyfile
systemctl reload caddy || systemctl restart caddy
/opt/guitle/salud.sh
sleep 2
cat /srv/guitle/salud/salud-servidor.json; echo
curl -s -o /dev/null -w "https guitle.com: %{http_code}\n" --resolve guitle.com:443:127.0.0.1 https://guitle.com/
curl -s -o /dev/null -w "salud: %{http_code}\n" --resolve guitle.com:443:127.0.0.1 https://guitle.com/salud-servidor.json
systemctl show caddy -p Restart; systemctl list-timers guitle-salud.timer --no-pager | head -2
echo "vigilar: listo"
