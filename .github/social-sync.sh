#!/usr/bin/env bash
# Pone la rama de Instagram al día con los precios de la rama por defecto (data/ y páginas generadas mandan las suyas).
# Uso: bash social/sync.sh   (desde la raíz del repo, antes de python -m scraper.instagram)
set -e
BRANCH=claude/exciting-cerf-q48nxa
DEFAULT=claude/friendly-fermat-yycain
git fetch -q origin "$BRANCH" "$DEFAULT"
git checkout -q "$BRANCH"
# Si la rama se rehízo con el historial corto (.github/workflows/historial.yml, cada semana), la copia local ya no
# comparte historia con la del servidor: se parte de la del servidor (aquí todo se sube siempre al acabar).
if ! git merge-base HEAD "origin/$BRANCH" >/dev/null 2>&1; then git reset -q --hard "origin/$BRANCH"; fi
git pull -q --no-rebase --no-edit origin "$BRANCH"
if ! git merge -q --no-edit -X theirs "origin/$DEFAULT" >/dev/null 2>&1; then
  # Conflictos de borrado/modificación en archivos generados: se queda la versión de la rama por defecto
  for f in $(git diff --name-only --diff-filter=U); do
    if git cat-file -e "origin/$DEFAULT:$f" 2>/dev/null; then git checkout -q --theirs -- "$f" && git add "$f"; else git rm -q "$f"; fi
  done
  git commit -q --no-edit
fi
git push -q origin "$BRANCH"
