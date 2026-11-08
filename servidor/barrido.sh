#!/usr/bin/env bash
# Barrido diario del servidor de casa: lecturas que bloquean a los servidores de GitHub (de momento CDGO, para los
# discos de Portugal y España). Sube solo sus datos; la lectura diaria de GitHub (musica.yml) los publica.
set -uo pipefail
cd "$HOME/guitle" || exit 1
echo "== $(date '+%F %T') barrido"
git fetch -q origin claude/friendly-fermat-yycain && git reset -q --hard origin/claude/friendly-fermat-yycain
timeout 90m "$HOME/guitle-venv/bin/python" -m scraper.musica --pais pt --minutes 80
for i in 1 2 3 4 5; do
  git add data/musica/pt/consultas.json
  git diff --cached --quiet && { echo "sin cambios"; break; }
  git commit -q -m "data: CDGO desde el servidor de casa $(date +%F)"
  if git push -q origin HEAD:claude/friendly-fermat-yycain; then echo "subido"; break; fi
  # alguien subió antes: se rehace sobre lo último conservando las consultas de hoy
  cp data/musica/pt/consultas.json /tmp/consultas-pt.json
  git fetch -q origin claude/friendly-fermat-yycain && git reset -q --hard origin/claude/friendly-fermat-yycain
  cp /tmp/consultas-pt.json data/musica/pt/consultas.json
  sleep $((10 * i))
done
