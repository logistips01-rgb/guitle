#!/usr/bin/env bash
# Paso "estado": cómo va la copia y el servidor.
systemctl is-active guitle-sync guitle-fichas caddy || true
tail -3 /var/log/guitle-sync.log 2>/dev/null || true
cat /srv/guitle/ultima-copia 2>/dev/null || echo "sin copia completa todavía"
du -sh /srv/guitle/r2 2>/dev/null; df -h / | tail -1
for p in / /fr/ /g/ "/fr/g/" /discos/ /stats.html; do curl -s -o /dev/null -w "$p %{http_code}\n" "http://127.0.0.1$p"; done
