#!/usr/bin/env bash
# Paso "actualizar": instala los programas del servidor de servidor/ (fichas.py, fotos.py, guitle-sync.sh, salud.sh)
# sin tocar la configuración, reinicia las fichas y lanza una copia desde R2.
set -euo pipefail
install -m 644 /root/fichas.py /opt/guitle/fichas.py
install -m 644 /root/fotos.py /opt/guitle/fotos.py
install -m 755 /root/guitle-sync.sh /opt/guitle/guitle-sync.sh
install -m 755 /root/salud.sh /opt/guitle/salud.sh
systemctl restart guitle-fichas
sleep 2
systemctl is-active guitle-fichas caddy
curl -s -o /dev/null -w "fichas: %{http_code}\n" http://127.0.0.1:8081/fr/g/no-existe.html
systemctl start --no-block guitle-copia.service
echo "copia lanzada; actualizar: listo"
