#!/usr/bin/env bash
# Paso "sincronizar": copia (o pone al día) la web desde R2 a /srv/guitle/r2. Corre en segundo plano en el servidor
# (systemd-run), porque la primera copia (12,6 GB, 1,3 millones de ficheros) tarda más que la conexión de GitHub.
# Carpeta a carpeta y sin --fast-list: con la lista entera de R2 de golpe (1,3 millones) rclone se comía la memoria
# (2 GB) y el sistema lo mataba. Las fichas sueltas de los países (<país>/g/) no se copian: en R2 son viejas.
# Credenciales de R2: en /root/.config/rclone/rclone.conf (solo root), puestas por el paso desde los secretos.
set -euo pipefail
if systemctl is-active --quiet guitle-sync; then echo "ya hay una copia en marcha"; exit 0; fi
cat > /root/guitle-sync.sh <<'EOF'
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
EOF
chmod +x /root/guitle-sync.sh
systemd-run --unit=guitle-sync --collect -p MemoryMax=1200M /root/guitle-sync.sh
echo "copia lanzada (log: /var/log/guitle-sync.log)"
