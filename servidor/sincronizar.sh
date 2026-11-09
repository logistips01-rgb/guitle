#!/usr/bin/env bash
# Paso "sincronizar": copia (o pone al día) la web desde R2 a /srv/guitle/r2. Corre en segundo plano en el servidor
# (systemd-run), porque la primera copia (12,6 GB, 1,3 millones de ficheros) tarda más que la conexión de GitHub.
# Las fichas sueltas de los países (<país>/g/) no se copian: en R2 son viejas (de antes de las cajas).
# Credenciales de R2: en /root/.config/rclone/rclone.conf (solo root), puestas por el paso desde los secretos.
set -euo pipefail
if systemctl is-active --quiet guitle-sync; then echo "ya hay una copia en marcha"; exit 0; fi
systemd-run --unit=guitle-sync --collect bash -c '
  rclone sync r2:guitle /srv/guitle/r2 --fast-list --transfers 32 --checkers 32 \
    --exclude "/[a-z][a-z]/g/**" --exclude "/_sync/**" --stats 60s --stats-one-line --log-file /var/log/guitle-sync.log --log-level NOTICE
  chown -R caddy:caddy /srv/guitle/r2
  date -u +%FT%TZ > /srv/guitle/ultima-copia'
echo "copia lanzada (log: /var/log/guitle-sync.log)"
