#!/usr/bin/env bash
# Paso "dominio": SOLO después de cambiar el DNS de guitle.com a este servidor (registros A con nube gris en
# Cloudflare). Pone la configuración con guitle.com y www (https automático) y comprueba el certificado.
set -euo pipefail
ip=$(getent ahostsv4 guitle.com | awk '{print $1; exit}')
echo "guitle.com apunta a: $ip"
cp /root/Caddyfile.dominio /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
systemctl reload caddy || systemctl restart caddy
sleep 20
curl -s -o /dev/null -w "https guitle.com: %{http_code}\n" --resolve guitle.com:443:127.0.0.1 https://guitle.com/ || true
journalctl -u caddy --no-pager -n 15 | grep -i -E "certificate|obtain|error" | tail -8 || true
echo "dominio: listo"
