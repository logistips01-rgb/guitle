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

## URGENTE: bloqueos de LaLiga (31-10-2026, confirmado por el usuario)
- En España las operadoras bloquean IPs de Cloudflare durante los partidos (orden judicial de LaLiga): guitle.com da
  ERR_TIMED_OUT en España los fines de semana. Datos y fotos pueden seguir en R2; hay que servir la web por otra red
  (propuesta: Bunny.net, ~1–2 €/mes, origen R2) o por el servidor propio (Hetzner). Preparar plan con números y pasos
  (qué hago yo, qué DNS cambia el usuario, prueba antes del cambio) y enseñárselo antes de tocar nada.
- Confirmado con hayahora.futbol (31/10, 23:30): guitle.com bloqueada en Movistar y DIGI (188.114.96.5 y .97.5).
- DECISIÓN DEL USUARIO (31/10, noche): no pagar nada más. Quiere un servidor en casa para los bloqueos y Cloudflare el
  resto del tiempo (Oracle gratuito queda como alternativa si lo de casa no encaja). Lo estudia; MEJORA PENDIENTE:
  - Ordenador de casa encendido de viernes tarde a lunes mañana (hibernar/despertar programado: tareas de Windows,
    rtcwake en Linux, Wake on RTC en BIOS o enchufe inteligente).
  - Al arrancar: Caddy (HTTPS gratuito) + copia completa de la web desde R2 (rclone, ~10 GB la primera vez; luego solo
    lo cambiado, cada 15 min) y aviso de "listo". Si sobra tiempo, lecturas extra (runner propio).
  - Vigilancia (GitHub, cada 15 min) con los datos de hayahora.futbol: si bloquean las IPs de guitle y la casa está
    lista, el DNS de guitle.com pasa a la IP de casa (token de Cloudflare); al levantarse el bloqueo, vuelve. Si la casa
    no responde, no salta. Antes de apagarse el lunes, devolver el DNS a Cloudflare. Aviso al usuario en cada salto.
  - Antes de montarlo: operadora de casa (DIGI → comprobar CGNAT), equipo y sistema, acceso al router (puertos 80/443).

## Mejora pendiente (solo apuntada; no hacer hasta que el usuario lo diga): "Avísame cuando haya stock"
- En la ficha de un producto agotado en todas las tiendas, "Avísame cuando haya stock" en vez del aviso de precio.
- Reutiliza los avisos de precio (Firestore "alertas", producto.js, alerta.html, scraper/alerts.py): target 0 = aviso de
  stock, que cabe en las reglas actuales (sin tocar firestore.rules). alerts.py avisa una vez cuando una tienda vuelve a
  tener stock, con tienda, precio y enlace. Enseñar la ficha antes de publicar.

## Mejora pendiente: catálogos más ligeros en el móvil (explicársela otra vez al usuario antes de hacerla)
- La portada ya lee un resumen de 100 KB (data/portada.json) en vez de los catálogos enteros (antes ~22 MB; con 4G
  tardaba ~20 s). Las páginas de catálogo (catalogo.html, acusticas.html…) siguen bajando su lista entera para buscar y
  filtrar: products.json pesa ~7,8 MB (~1,1 MB comprimido), varios segundos con 4G.
- Propuesta: una lista ligera para la cuadrícula (nombre, foto, marca, tipo, precio mínimo, nº de tiendas) y los
  detalles de cada guitarra (tiendas, enlaces, histórico) solo al abrirla. Enseñarla antes de publicar.

## Cloudflare Workers (31-10-2026)
- El 31/10 se agotaron las 100.000 visitas diarias del plan gratuito de Workers (error 1027): cada miniatura pasa por el
  Worker y IndexNow avisó de cientos de miles de páginas tras el cambio del menú. El usuario activó Workers Paid (5 $/mes,
  10 M de visitas al mes). IndexNow ya avisa como mucho de 300 páginas por vez.
- Mejora pendiente (opcional, para poder volver al plan gratuito): servir img/p/ desde un dominio propio del bucket R2
  (img.guitle.com, sin Worker) y cambiar las rutas /img/p/ de la web.

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
