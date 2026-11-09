#!/usr/bin/env bash
set -uo pipefail
LOG=/var/log/guitle-sync.log
OPTS=(--transfers 16 --checkers 8 --buffer-size 0 --use-mmap --stats 120s --stats-one-line --log-file "$LOG" --log-level NOTICE)
echo "$(date -u +%FT%TZ) empieza" >> "$LOG"
ok=1
# Ficheros sueltos de la raíz (portada, páginas, sitemaps…)
rclone sync r2:guitle /srv/guitle/r2 --max-depth 1 --exclude "/*/**" "${OPTS[@]}" || ok=0
for d in $(rclone lsf r2:guitle --dirs-only | tr -d /); do
  case "$d" in _sync|img) continue ;; esac  # img/: aparte, abajo
  extra=()
  [[ "$d" =~ ^[a-z][a-z]$ ]] && extra=(--exclude "/g/**")  # fichas sueltas viejas de los países
  echo "$(date -u +%FT%TZ) $d" >> "$LOG"
  rclone sync "r2:guitle/$d" "/srv/guitle/r2/$d" "${extra[@]}" "${OPTS[@]}" || ok=0
done
# Fotos (img/p/, 658.000 en una carpeta): listarlas en R2 se come la memoria del servidor. Se bajan las que falten según
# la lista de la web (data/thumbs.json, ya copiada); una foto no cambia nunca (su nombre es la huella de la imagen).
echo "$(date -u +%FT%TZ) img (por lista)" >> "$LOG"
python3 - > /tmp/faltan-fotos.txt <<'PY'
import json, os
root = "/srv/guitle/r2"
try:
    names = json.load(open(f"{root}/data/thumbs.json"))
except Exception:
    names = {}
have = set(os.listdir(f"{root}/img/p")) if os.path.isdir(f"{root}/img/p") else set()
for n in names:
    if n not in have:
        print(f"img/p/{n}")
PY
echo "$(date -u +%FT%TZ) fotos que faltan: $(wc -l < /tmp/faltan-fotos.txt)" >> "$LOG"
if [ -s /tmp/faltan-fotos.txt ]; then
  rclone copy r2:guitle /srv/guitle/r2 --files-from /tmp/faltan-fotos.txt --no-traverse --transfers 32 --checkers 8 \
    --buffer-size 0 --stats 300s --stats-one-line --log-file "$LOG" --log-level NOTICE || ok=0
fi
# El resto de img/ (img/mapa…), sin p/
rclone sync r2:guitle/img /srv/guitle/r2/img --exclude "/p/**" "${OPTS[@]}" || ok=0
chown -R caddy:caddy /srv/guitle/r2
if [ "$ok" = 1 ]; then date -u +%FT%TZ > /srv/guitle/ultima-copia; echo "$(date -u +%FT%TZ) termina bien" >> "$LOG"
else echo "$(date -u +%FT%TZ) termina con errores" >> "$LOG"; fi
