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
# Copia desde R2: cada 2 horas (a y 45), solo lo que cambia. Lo nuevo de cada lectura llega como mucho en 2 horas.
cp /root/guitle-sync.sh /opt/guitle/guitle-sync.sh && chmod +x /opt/guitle/guitle-sync.sh
cp /root/fotos.py /opt/guitle/fotos.py
cat > /etc/systemd/system/guitle-copia.service <<'EOF'
[Unit]
Description=guitle: copia de la web desde R2
[Service]
Type=oneshot
ExecStart=/opt/guitle/guitle-sync.sh
MemoryMax=1200M
Nice=10
EOF
cat > /etc/systemd/system/guitle-copia.timer <<'EOF'
[Unit]
Description=guitle: copia desde R2 cada 2 horas
[Timer]
OnCalendar=*-*-* 0/2:45:00
Persistent=true
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now guitle-copia.timer
# Con el dominio ya activo (paso "dominio"), su configuración: la de solo IP lo dejaría sin https.
if grep -q "guitle.com, www.guitle.com" /etc/caddy/Caddyfile 2>/dev/null; then cp /root/Caddyfile.dominio /etc/caddy/Caddyfile
else cp /root/Caddyfile /etc/caddy/Caddyfile; fi
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
systemctl reload caddy || systemctl restart caddy
sleep 2
systemctl is-active guitle-fichas caddy
curl -s -o /dev/null -w "portada %{http_code}\n" http://127.0.0.1/ || true
echo "montar: listo"
