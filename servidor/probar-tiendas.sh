#!/usr/bin/env bash
# ¿Dejan las tiendas de discos consultar desde IONOS? (antes de pasar aquí las consultas por código). Solo lectura,
# una petición por tienda, con 3 s entre una y otra. 200 = bien; 403/429/503 = bloqueo.
E=0887828031719; U=887828031719
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
for url in "https://www.ibs.it/x/e/$E" "https://www.lafeltrinelli.it/x/e/$E" "https://www.mondadoristore.it/x/p/$E" \
  "https://www.discotecalaziale.com/${E}_x" "https://www.jpc.de/s/$E" \
  "https://www.flur.pt/search/suggest.json?q=$U" "https://www.impericon.com/pt/search/suggest.json?q=$E" \
  "https://www.velvetmusic.nl/search/suggest.json?q=$E" "https://recordsonvinyl.nl/search/suggest.json?q=$E" \
  "https://3345.nl/search/suggest.json?q=$E" "https://towerrecords.ie/search/suggest.json?q=$E" \
  "https://goldendiscs.ie/search/suggest.json?q=$E" "https://spindizzyrecords.com/search/suggest.json?q=$E" \
  "https://freebirdrecords.com/search/suggest.json?q=$U"; do
  r=$(curl -s -L -m 30 -A "$UA" -o /tmp/t.out -w '%{http_code} %{size_download}' "$url")
  echo "$r  $url  $(grep -c -i -E '"price"|ld\+json|"handle"' /tmp/t.out) señales"
  sleep 3
done
rm -f /tmp/t.out
