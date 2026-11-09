#!/usr/bin/env bash
set -uo pipefail
LOG=/var/log/guitle-sync.log
OPTS=(--transfers 16 --checkers 8 --buffer-size 0 --use-mmap --stats 120s --stats-one-line --log-file "$LOG" --log-level NOTICE)
echo "$(date -u +%FT%TZ) empieza" >> "$LOG"
ok=1
# Ficheros sueltos de la raíz (portada, páginas, sitemaps…)
rclone sync r2:guitle /srv/guitle/r2 --max-depth 1 --exclude "/*/**" "${OPTS[@]}" || ok=0
for d in $(rclone lsf r2:guitle --dirs-only | tr -d /); do
  case "$d" in _sync) continue ;; esac
  extra=()
  [[ "$d" =~ ^[a-z][a-z]$ ]] && extra=(--exclude "/g/**")  # fichas sueltas viejas de los países
  echo "$(date -u +%FT%TZ) $d" >> "$LOG"
  rclone sync "r2:guitle/$d" "/srv/guitle/r2/$d" "${extra[@]}" "${OPTS[@]}" || ok=0
done
chown -R caddy:caddy /srv/guitle/r2
if [ "$ok" = 1 ]; then date -u +%FT%TZ > /srv/guitle/ultima-copia; echo "$(date -u +%FT%TZ) termina bien" >> "$LOG"
else echo "$(date -u +%FT%TZ) termina con errores" >> "$LOG"; fi
