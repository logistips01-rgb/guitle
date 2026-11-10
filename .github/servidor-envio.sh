#!/usr/bin/env bash
# Manda al servidor propio de guitle.com (IONOS) lo que un trabajo acaba de publicar en R2, en el momento, para que la
# web no espere a la copia de cada 2 horas (guitle-copia.timer, que se queda de respaldo). Va directo desde el disco
# del trabajo por SSH (rsync): no lee nada de R2, así que no gasta operaciones.
#   bash .github/servidor-envio.sh SUBIDOS [BORRADOS]
# SUBIDOS y BORRADOS: una ruta por línea, relativas a la raíz (las mismas que en R2 y en /srv/guitle/r2).
# Nunca hace fallar el trabajo: si el servidor no responde, avisa y la copia de cada 2 horas lo recoge.
set -uo pipefail

HOST=31.70.175.136
DEST=/srv/guitle/r2
up=${1:-}; gone=${2:-}

if [ -z "${SERVIDOR_SSH_KEY:-}" ]; then echo "servidor: sin llave (SERVIDOR_SSH_KEY), no se envía"; exit 0; fi
if [ ! -s "$up" ] && [ ! -s "$gone" ]; then echo "servidor: nada que enviar"; exit 0; fi

dir=$(mktemp -d)
key="$dir/llave"
# La llave puede venir sin saltos de línea o con los de Windows: se rehace como la quiere OpenSSH (igual que servidor.yml).
python3 - "$SERVIDOR_SSH_KEY" > "$key" <<'PY'
import re, sys, textwrap
k = sys.argv[1].replace("\r", "")
m = re.search(r"-----BEGIN OPENSSH PRIVATE KEY-----(.*?)-----END OPENSSH PRIVATE KEY-----", k, re.S)
body = re.sub(r"\s+", "", m.group(1)) if m else re.sub(r"\s+", "", k)
print("-----BEGIN OPENSSH PRIVATE KEY-----")
print("\n".join(textwrap.wrap(body, 70)))
print("-----END OPENSSH PRIVATE KEY-----")
PY
chmod 600 "$key"
SSH="ssh -i $key -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$dir/known"

# Solo rutas normales dentro de la web (nada de "..", ni absolutas), sin repetir.
limpia() { grep -vE '(^/|(^|/)\.\.(/|$))' "$1" 2>/dev/null | grep -v '^$' | LC_ALL=C sort -u; }

ok=1
# rsync hace falta en los dos lados; en el servidor lo pone base.sh, y si faltara se instala aquí.
timeout 180 $SSH "root@$HOST" 'command -v rsync >/dev/null || DEBIAN_FRONTEND=noninteractive apt-get install -y -qq rsync >/dev/null' 2>/dev/null || true
if [ -s "$up" ]; then
  limpia "$up" > "$dir/up"
  n=$(wc -l < "$dir/up")
  # rsync escribe cada fichero aparte y lo cambia de nombre al final: nadie ve uno a medias.
  if timeout 1200 rsync -a --files-from="$dir/up" --ignore-missing-args --chown=caddy:caddy --chmod=D755,F644 \
       -e "$SSH" ./ "root@$HOST:$DEST/" 2> "$dir/err"; then
    echo "servidor: $n ficheros enviados"
  else
    ok=0; echo "::warning::servidor: no se pudieron enviar $n ficheros ($(tail -2 "$dir/err" | tr '\n' ' ')); los recoge la copia de cada 2 horas"
  fi
fi
if [ -s "$gone" ]; then
  limpia "$gone" > "$dir/gone"
  n=$(wc -l < "$dir/gone")
  if timeout 300 $SSH "root@$HOST" "cd $DEST && xargs -d '\n' rm -f --" < "$dir/gone" 2> "$dir/err"; then
    echo "servidor: $n ficheros borrados"
  else
    ok=0; echo "::warning::servidor: no se pudieron borrar $n ficheros; los recoge la copia de cada 2 horas"
  fi
fi
rm -rf "$dir"
[ "$ok" = 1 ] && echo "servidor: al día"
exit 0
