# Dónde nos quedamos (30-10-2026)

## Publicado (en la rama claude/friendly-fermat-yycain)
- Tiendas nuevas de los directorios de marcas en los 9 países fuera de Brasil.
- Equipo (bajos, amplis, pedales, teclados, micros, estuches, varios) en todos los países: España (mas), Brasil (brmas),
  Alemania (demas), Francia (frmas), Italia (itmas), Portugal (ptmas), Reino Unido (ukmas), Irlanda (iemas),
  Países Bajos (nlmas) y Austria (atmas). Mecanismo genérico `EQUIPO_COUNTRIES` en scraper/catalog.py.
- Miniaturas en paralelo por tienda (scraper/thumbs.py). Portada en móvil como mootle.

## Cloudflare (30-10-2026, hecho)
- guitle.com usa los DNS de Cloudflare (cuenta hola@guitle.com; dominio registrado en DonDominio, correo sigue allí).
- La web se sirve desde el bucket R2 "guitle" con el Worker cloudflare/worker.js (rutas guitle.com/* y www, y
  prueba.guitle.com). r2.yml sube a R2 lo que cambia en cada envío; cloudflare.yml despliega el Worker.
- Secretos en GitHub: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, CLOUDFLARE_API_TOKEN.
- Volver atrás: nubes de los 4 registros A y www en gris → vuelve GitHub Pages.

## Pendiente
- Que GitHub deje de crecer: subir páginas/fotos generadas a R2 desde la propia lectura y dejar de guardarlas en git
  (las miniaturas de img/p/ hay que comprobarlas contra R2 para no volver a bajarlas). Luego apagar GitHub Pages.
- Rehacer el historial de la rama para bajar los ~835 MB: solo con confirmación expresa del usuario (no se deshace).
- Equipo de Brasil (brmas): tanda de lectura bajada a 75 min; comprobar que guarda en la próxima lectura.
- Probar desde GitHub las tiendas que bloquean (Bettin, Music Centre, B Sharp, Gear4music.de, Guitarpoint, Musikhammer,
  Schreeven…) antes de descartarlas.
- Directorios de ESP, Cort y Martin (se leen desde GitHub).
- Siguiente tanda de países con 10 agentes; luego Latinoamérica (cada país con su web y su moneda, envíos entre ellos).
- Panel "Crecimiento de guitle": regenerarlo tras cada fase.
- El usuario lanza el catálogo con "todos" a mano (yo no puedo lanzarlo: 403).
