#!/usr/bin/env bash
# Consultas de discos por código desde el servidor (en prueba): cada país a la vez, 100 minutos, y se suben solo los
# consultas-servidor.json (GitHub sigue con las suyas; se comparan unos días antes de quitárselas).
set -uo pipefail
D=/srv/guitle-consultas
cd "$D" || exit 1
echo "== $(date -u '+%F %T') consultas"
git fetch -q --depth 1 origin claude/friendly-fermat-yycain && git reset -q --hard origin/claude/friendly-fermat-yycain
for p in it de nl ie pt; do
  timeout 110m /srv/guitle-consultas-venv/bin/python -m scraper.musica --pais "$p" --consultas --minutes 100 > "/var/log/guitle-consultas-$p.log" 2>&1 &
done
wait
for p in it de nl ie pt; do echo "$p: $(grep -h 'consultados' /var/log/guitle-consultas-$p.log | tr '\n' ' ')"; done
for i in 1 2 3 4 5; do
  git add data/musica/*/consultas-servidor.json
  git diff --cached --quiet && { echo "sin cambios"; break; }
  git commit -q -m "data: consultas de discos desde el servidor $(date -u +%F)"
  git push -q origin HEAD:claude/friendly-fermat-yycain && { echo "subido"; break; }
  mkdir -p /tmp/cs && for f in data/musica/*/consultas-servidor.json; do mkdir -p "/tmp/cs/$(dirname "$f")"; cp "$f" "/tmp/cs/$f"; done
  git fetch -q --depth 1 origin claude/friendly-fermat-yycain && git reset -q --hard origin/claude/friendly-fermat-yycain
  cp -r /tmp/cs/data/musica/. data/musica/
  sleep $((15 * i))
done
