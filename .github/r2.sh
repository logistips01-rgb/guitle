#!/usr/bin/env bash
# La web generada va directa al bucket R2 (la sirve el Worker) en vez de guardarse en git. Lo usan catalog.yml y
# scrape.yml después de fusionar la lectura:
#   bash .github/r2.sh git-add RUTAS…  añade a git las RUTAS de datos y lo generado que aún se guarda en git
#   bash .github/r2.sh publicar        sube a R2 lo generado en este trabajo y avisa a IndexNow de lo nuevo
# Lo que va a R2 está también en .github/r2-exclude.txt, para que r2.yml no lo toque ni lo borre.
set -euo pipefail

R2_SITES="pt fr it uk de br ie at nl be"  # webs de países que van a R2
R2_ES=1        # 1: también las páginas de España (g/*.html, marca/, tipo/, presupuesto/, marcas.html, sitemap.xml)
R2_IMG=1       # 1: también las miniaturas (img/p/); en git queda su lista, data/thumbs.json

ALL_SITES=$(python -c "from scraper.intl import SITES; print(' '.join(SITES))")
in_r2() { case " $R2_SITES " in *" $1 "*) return 0 ;; esac; return 1; }

git_add() {
  python -m scraper.thumbs --index  # las miniaturas nuevas de img/p/, a la lista
  git add "$@" data/thumbs.json
  if [ "$R2_IMG" = 0 ]; then git add img/p/; fi
  if [ "$R2_ES" = 1 ]; then
    git add g/_*.txt  # listas de fichas por categoría: el sitemap de España sale de ellas
  else
    git add g/ marca/ tipo/ presupuesto/ marcas.html sitemap.xml
  fi
  for d in sitemap-*.xml $ALL_SITES; do
    s=${d#sitemap-}; s=${s%.xml}
    if in_r2 "$s" || [ ! -e "$d" ]; then continue; fi
    git add "$d"
  done
}

rclone_ready() {
  if ! command -v rclone >/dev/null; then
    curl -fsSLO https://downloads.rclone.org/v1.68.2/rclone-v1.68.2-linux-amd64.zip
    unzip -q rclone-v1.68.2-linux-amd64.zip && sudo install rclone-v1.68.2-linux-amd64/rclone /usr/local/bin/
    rm -rf rclone-v1.68.2-linux-amd64*
  fi
  export RCLONE_CONFIG_R2_TYPE=s3 RCLONE_CONFIG_R2_PROVIDER=Cloudflare RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
  export RCLONE_CONFIG_R2_ENDPOINT="https://${R2_ACCOUNT,,}.r2.cloudflarestorage.com"
}

# up MODO ORIGEN DESTINO [opciones]: solo sube lo que cambia (MD5); anota las .html nuevas o cambiadas.
up() {
  local mode=$1 src=$2 dst=$3 log="$RUNNER_TEMP/r2-log.txt"; shift 3
  if [ "$mode" = sync ]; then
    rclone sync "$src" "r2:guitle/$dst" --checksum --fast-list --transfers 32 --checkers 32 \
      --combined "$RUNNER_TEMP/r2-comb.txt" --stats-log-level NOTICE "$@"
    { grep -E '^[+*] .*\.html$' "$RUNNER_TEMP/r2-comb.txt" || true; } | cut -c3- | sed "s#^#$dst/#" >> "$URLS"
  else  # copy no admite --combined: lo copiado sale del registro
    rclone copy "$src" "r2:guitle/$dst" --checksum --fast-list --transfers 32 --checkers 32 \
      -v --log-file "$log" --stats 0 "$@"
    { grep -oE 'INFO  : [^:]+\.html: Copied' "$log" || true; } | sed -E "s#^INFO  : (.*): Copied#$dst/\1#" >> "$URLS"
    rm -f "$log"
  fi
}

one() {  # un fichero suelto de la raíz
  if [ ! -f "$1" ]; then return 0; fi
  rclone copyto "$1" "r2:guitle/$1" --checksum
  case $1 in *.html) echo "$1" >> "$URLS" ;; esac
}

publicar() {
  rclone_ready
  URLS="$RUNNER_TEMP/r2-urls.txt"; : > "$URLS"
  for s in $R2_SITES; do
    if [ ! -f "$s/index.html" ]; then continue; fi  # este trabajo no ha generado esa web
    n=$( { find "$s" -type f || true; } | wc -l)
    # Una web a medias no se sube: borraría en R2 las páginas que le faltan. Tope de borrado, por si acaso.
    if [ "$n" -lt 50 ]; then echo "::warning::web $s con solo $n ficheros: no se sube"; continue; fi
    up sync "$s" "$s" --max-delete 3000
    one "sitemap-$s.xml"
  done
  if [ "$R2_ES" = 1 ]; then
    # Fichas: cada trabajo genera solo las de sus categorías, así que se copian (nunca se borran, como en git).
    if compgen -G "g/*.html" >/dev/null; then up copy g g --include "*.html"; fi
    for d in marca tipo presupuesto; do  # se generan enteras en cada lectura de España
      n=$( { find "$d" -name '*.html' 2>/dev/null || true; } | wc -l)  # sin la carpeta (trabajo de otro país): 0
      if [ "$n" -ge 10 ]; then up sync "$d" "$d" --max-delete 500; fi
    done
    one marcas.html
    one sitemap.xml
  fi
  if [ "$R2_IMG" = 1 ] && compgen -G "img/p/*.webp" >/dev/null; then
    # Solo hay en disco las de esta lectura (las demás están ya en R2): sin listar el bucket, una a una.
    rclone copy img/p r2:guitle/img/p --no-traverse --checksum --transfers 32 --stats-log-level NOTICE
  fi
  echo "R2: $(wc -l < "$URLS") páginas nuevas o cambiadas"
  python -m scraper.indexnow --files "$URLS" || true
  # Lo que sigue en git (datos, portada…) lo sube r2.yml; un commit hecho desde un workflow no lo lanza solo.
  gh workflow run r2.yml --ref "$GITHUB_REF_NAME" || echo "::warning::no se pudo lanzar r2.yml"
}

# Quita de data/thumbs.json las miniaturas que no están en R2 ni en disco (una subida que falló): así se vuelven a bajar
# en vez de quedar rotas en la web. La lista del bucket se lee una vez por trabajo.
reparar() {
  rclone_ready
  local list="$RUNNER_TEMP/r2-img.txt"
  if [ ! -s "$list" ]; then rclone lsf r2:guitle/img/p --files-only --fast-list > "$list"; fi
  [ "$(wc -l < "$list")" -gt 1000 ] || { echo "::warning::lista de R2 vacía o corta: no se repara"; return 0; }
  python - "$list" <<'PY'
import json, sys
from pathlib import Path
have = set(Path(sys.argv[1]).read_text().split())
path = Path("data/thumbs.json")
idx = json.loads(path.read_text())
gone = [k for k in idx if k not in have and not Path("img/p", k).exists()]
for k in gone:
    del idx[k]
path.write_text("{\n" + ",\n".join(f'"{k}":{v}' for k, v in sorted(idx.items())) + "\n}\n")
print(f"miniaturas: {len(gone)} apuntadas pero sin subir a R2; se volverán a bajar")
PY
}

case "${1:-}" in
  git-add) shift; git_add "$@" ;;
  publicar) publicar ;;
  reparar) reparar ;;
  *) echo "uso: $0 git-add RUTAS… | publicar | reparar" >&2; exit 2 ;;
esac
