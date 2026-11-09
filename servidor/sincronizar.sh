#!/usr/bin/env bash
# Paso "sincronizar": copia (o pone al día) la web desde R2 a /srv/guitle/r2. Corre en segundo plano en el servidor
# (systemd-run), porque la primera copia (12,6 GB, 1,3 millones de ficheros) tarda más que la conexión de GitHub.
# Carpeta a carpeta y sin --fast-list: con la lista entera de R2 de golpe (1,3 millones) rclone se comía la memoria
# (2 GB) y el sistema lo mataba. Las fichas sueltas de los países (<país>/g/) no se copian: en R2 son viejas.
# Credenciales de R2: en /root/.config/rclone/rclone.conf (solo root), puestas por el paso desde los secretos.
set -euo pipefail
if systemctl is-active --quiet guitle-sync guitle-copia; then echo "ya hay una copia en marcha"; exit 0; fi
cp /root/guitle-sync.sh /opt/guitle/guitle-sync.sh && chmod +x /opt/guitle/guitle-sync.sh
systemctl start --no-block guitle-copia.service
echo "copia lanzada (log: /var/log/guitle-sync.log)"
