# Dónde nos quedamos (30-10-2026)

## Publicado (en la rama claude/friendly-fermat-yycain)
- Tiendas nuevas de los directorios de marcas en los 9 países fuera de Brasil.
- Equipo (bajos, amplis, pedales, teclados, micros, estuches, varios) en todos los países: España (mas), Brasil (brmas),
  Alemania (demas), Francia (frmas), Italia (itmas), Portugal (ptmas), Reino Unido (ukmas), Irlanda (iemas),
  Países Bajos (nlmas) y Austria (atmas). Mecanismo genérico `EQUIPO_COUNTRIES` en scraper/catalog.py.
- Miniaturas en paralelo por tienda (scraper/thumbs.py). Portada en móvil como mootle.

## Pendiente
- Imágenes a Cloudflare R2 (la web pasa de 1 GB): espera a que el usuario cree la cuenta/bucket y guarde la clave en
  GitHub Secrets.
- Probar desde GitHub las tiendas que bloquean (Bettin, Music Centre, B Sharp, Gear4music.de, Guitarpoint, Musikhammer,
  Schreeven…) antes de descartarlas.
- Directorios de ESP, Cort y Martin (se leen desde GitHub).
- Siguiente tanda de países con 10 agentes; luego Latinoamérica (cada país con su web y su moneda, envíos entre ellos).
- Panel "Crecimiento de guitle": regenerarlo tras cada fase.
- El usuario lanza el catálogo con "todos" a mano (yo no puedo lanzarlo: 403).
