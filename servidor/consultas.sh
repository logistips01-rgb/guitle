#!/usr/bin/env bash
# Instala en el servidor las consultas de discos por código de barras (prueba en paralelo con GitHub, noviembre de
# 2026): copia ligera del repositorio en /srv/guitle-consultas, Python con requests y un temporizador diario
# (guitle-consultas.timer, 11:05 UTC) que lanza consultas-dia.sh. El token (GH_RELOJ_TOKEN) lo ha dejado servidor.yml.
set -euo pipefail
T=$(cat /root/.config/guitle/gh-token)
D=/srv/guitle-consultas
apt-get install -y -qq git python3-venv >/dev/null
if [ ! -d "$D/.git" ]; then
  git clone -q --depth 1 --filter=blob:none --sparse -b claude/friendly-fermat-yycain \
    "https://x-access-token:$T@github.com/logistips01-rgb/guitle.git" "$D"
fi
cd "$D"
git remote set-url origin "https://x-access-token:$T@github.com/logistips01-rgb/guitle.git"
git sparse-checkout set --no-cone /scraper/ /data/musica/ /requirements.txt /servidor/
git config user.name "guitle-servidor"; git config user.email "servidor@guitle.com"
chmod 700 "$D/.git"
[ -x /srv/guitle-consultas-venv/bin/python ] || python3 -m venv /srv/guitle-consultas-venv
/srv/guitle-consultas-venv/bin/pip install -q requests beautifulsoup4
install -m 755 /root/consultas-dia.sh /usr/local/bin/guitle-consultas-dia.sh
cat > /etc/systemd/system/guitle-consultas.service <<'UNIT'
[Unit]
Description=guitle: consultas de discos por código (prueba en paralelo con GitHub)
[Service]
Type=oneshot
Nice=10
ExecStart=/usr/local/bin/guitle-consultas-dia.sh
TimeoutStartSec=4h
UNIT
cat > /etc/systemd/system/guitle-consultas.timer <<'UNIT'
[Unit]
Description=guitle: consultas de discos, cada día a las 11:05 UTC
[Timer]
OnCalendar=*-*-* 11:05:00 UTC
Persistent=true
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now guitle-consultas.timer
systemctl list-timers guitle-consultas.timer --no-pager | head -3
echo "instalado; primera vuelta corta de prueba (Irlanda, 2 min):"
cd "$D" && timeout 300 /srv/guitle-consultas-venv/bin/python -m scraper.musica --pais ie --consultas --minutes 2 2>&1 | tail -5
git status --short | head
git checkout -q -- data/musica 2>/dev/null || true
