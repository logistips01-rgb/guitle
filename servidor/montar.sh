#!/usr/bin/env bash
# Paso "montar": instala fichas.py como servicio (guitle-fichas) y la configuración de Caddy. Se puede repetir.
set -euo pipefail
mkdir -p /srv/guitle/r2 /opt/guitle
cp /root/fichas.py /opt/guitle/fichas.py
cat > /etc/systemd/system/guitle-fichas.service <<'EOF'
[Unit]
Description=guitle: fichas en cajas, discos y direcciones viejas (lo que en Cloudflare hace el Worker)
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/guitle/fichas.py
Restart=always
RestartSec=2
User=caddy
Group=caddy

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now guitle-fichas
systemctl restart guitle-fichas
cp /root/Caddyfile /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
systemctl reload caddy || systemctl restart caddy
sleep 2
systemctl is-active guitle-fichas caddy
curl -s -o /dev/null -w "portada %{http_code}\n" http://127.0.0.1/ || true
echo "montar: listo"
