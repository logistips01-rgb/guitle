# Dónde nos quedamos (31-10-2026)

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

## Hecho el 30/31-10-2026
- La web generada (webs de países, fichas de España, miniaturas) ya no va a git: cada lectura la sube a R2 (.github/r2.sh);
  en git quedan los datos (~300 ficheros). r2.yml se lanza tras cada commit de las lecturas.
- fotos.yml: baja las miniaturas que faltan entre lecturas (40 min de margen antes de la siguiente).
- Contador de visitas: solo personas (3 s visible + gesto). El lector respeta el Crawl-delay del robots.txt.
- Bélgica (be/bemas): primera lectura lanzada por .github/nuevos.txt; meterla en la vuelta programada tras ella.
- Búsqueda de tiendas de Bélgica, Suiza, Polonia, Suecia, Dinamarca y Noruega: informes en el scratchpad de la sesión
  (resumen: CH 13 legibles, NO 11, PL 13, SE 8, BE 3+9, DK 5).

## Packs (31-10-2026)
- Sección propia publicada (packs.html y una página por país); foto entera del pack (thumbs.py, modo "pack").
- Pendiente: decidir si los kits para montar (Harley Benton "Electric Guitar Kit") van en packs o en eléctricas.
- Siguiente idea del usuario, "pack guitle": por cada pack, el mismo contenido en piezas sueltas más baratas de cualquier
  tienda. Pasos: guardar el contenido del pack (de su descripción, en la misma lectura); buscar guitarra y ampli por
  modelo y lo genérico (funda, correa, cable, púas, afinador) lo más barato equivalente; avisar de portes y de
  "modelo equivalente" cuando la guitarra solo exista en pack. Enseñar un ejemplo antes de publicar.

## Afiliación (seguimiento)
- Madrid Hifi y Awin: solicitadas el 27/10; correos a tiendas el 30/10. Si no hay respuesta hacia el 10/11, recordatorio
  corto (lo redacto, lo envía el usuario desde hola@guitle.com) con la página "Para tiendas" (pendiente de hacer y enseñar).

## Pendiente
- Apagar GitHub Pages.
- Rehacer el historial de la rama para bajar los ~835 MB: solo con confirmación expresa del usuario (no se deshace).
- Equipo de Brasil e Italia (brmas, itmas): tanda de 75 min; comprobar que guardan en la lectura de las 03:17 UTC del 31/10.
- Probar desde GitHub las tiendas que bloquean (Bettin, Music Centre, B Sharp, Gear4music.de, Guitarpoint, Musikhammer,
  Schreeven…) antes de descartarlas.
- Directorios de ESP, Cort y Martin (se leen desde GitHub).
- Siguiente tanda de países con 10 agentes; luego Latinoamérica (cada país con su web y su moneda, envíos entre ellos).
- Panel "Crecimiento de guitle": regenerarlo tras cada fase.
- Lanzar a mano: no puedo (403); se lanza por push a rutas (nuevos.txt, fotos.yml).

## Mejora pendiente: repositorio privado (proteger el código) — cuando el usuario lo diga
- Motivo: proteger el código (guitle va a crecer). Ya hay LICENSE "todos los derechos reservados" mientras tanto.
- Problema: en privado, GitHub Actions solo da 2.000 min/mes gratis; las lecturas gastan cientos de miles → hace falta
  un servidor propio como runner (sus minutos no cuentan).
- Plan acordado: Hetzner Cloud (cuenta con hola@guitle.com, nunca Aldelis), proyecto "guitle". 30 €/mes le parece
  mucho: objetivo ~8-10 €/mes con un x86 de 4 vCPU / 8 GB (Ubuntu 24.04, Alemania) y ~8 runners. Antes: limpieza del
  repo (checkout ligero) y juntar trabajos (guitarras + equipo de cada país en uno) para que bastan menos runners;
  la regla de 20 h ya acorta las lecturas. ARM (~6-7 €) posible si se prueba. Guion cloud-config (sin claves en el repo) que instala ~16-20
  runners con etiqueta "guitle"; el token de registro lo copia el usuario de Settings → Actions → Runners (caduca en
  1 h) al crear el servidor. Workflows a runs-on: [self-hosted, guitle] (necesitan sudo, setup-python, setup-node, rclone).
- Antes de pasar las lecturas: probar desde la IP del servidor que las tiendas responden igual (Fender solo respondía
  desde GitHub). Reinicio automático de runners y aviso en stats si no hay lecturas.
- Cuando todo funcione: repositorio a privado (oculta también el historial); GitHub Pages deja de hacer falta.
- Bloquear el entrenamiento de IA en la web: Cloudflare → políticas de IA → Formación: Bloquear (búsqueda y agentes
  siguen permitidos). Pendiente de que el usuario decida.
