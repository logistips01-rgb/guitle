#!/usr/bin/env bash
# ¿Deja CDGO (discos de Portugal y España) consultar desde el servidor de IONOS? A GitHub lo bloquea. Solo lectura:
# tres fichas por código de barras, con 5 s entre una y otra (su robots.txt), y si traen precio.
for e in 0887828031719 0602537349296 5099969945120; do
  code=$(curl -s -m 30 -A "Mozilla/5.0 (compatible; guitle/1.0; +https://guitle.com)" -o /tmp/cdgo.html -w '%{http_code}' "https://cdgo.com/detalhe/$e/x")
  precio=$(grep -o 'product-price-value[^<]*<[^>]*>[^<]*' /tmp/cdgo.html | head -1 | sed 's/<[^>]*>//g;s/.*>//' | tr -s ' ')
  echo "CDGO $e: HTTP $code, $(wc -c < /tmp/cdgo.html) bytes, precio: ${precio:-no}"
  sleep 5
done
rm -f /tmp/cdgo.html
