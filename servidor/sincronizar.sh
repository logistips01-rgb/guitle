#!/usr/bin/env bash
# Paso "sincronizar": copia (o pone al día) la web desde R2 a /srv/guitle/r2. Corre en segundo plano en el servidor
# (systemd-run), porque la primera copia (12,6 GB, 1,3 millones de ficheros) tarda más que la conexión de GitHub.
# Carpeta a carpeta y sin --fast-list: con la lista entera de R2 de golpe (1,3 millones) rclone se comía la memoria
# (2 GB) y el sistema lo mataba. Las fichas sueltas de los países (<país>/g/) no se copian: en R2 son viejas.
# Credenciales de R2: en /root/.config/rclone/rclone.conf (solo root), puestas por el paso desde los secretos.
set -euo pipefail
# Una copia en marcha se para y se vuelve a lanzar con lo nuevo (rehace la lista: no repite lo ya copiado)
systemctl stop guitle-copia.service guitle-sync.service 2>/dev/null || true
pkill -f "rclone copy r2:guitle" 2>/dev/null || true
cp /root/guitle-sync.sh /opt/guitle/guitle-sync.sh && chmod +x /opt/guitle/guitle-sync.sh
cp /root/fotos.py /opt/guitle/fotos.py
systemctl start --no-block guitle-copia.service
echo "copia lanzada (log: /var/log/guitle-sync.log)"
