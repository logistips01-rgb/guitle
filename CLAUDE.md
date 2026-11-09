# guitle — normas para Claude

## Idioma

- En este entorno se habla **siempre en español**: respuestas, resúmenes, avisos de tareas programadas y mensajes de
  commit. Aunque la tarea o el código estén en otro idioma, a Manuel se le escribe en español.

## Redes sociales (Instagram, TikTok)

- Los Reels se publican **siempre con música libre de derechos** mezclada en el vídeo (`scraper/musica_libre.py`: temas de
  Kevin MacLeod, incompetech.com, licencia CC BY 4.0) y **citando siempre al autor** en el texto de la publicación
  (línea `🎵 "<tema>" Kevin MacLeod (incompetech.com) · CC BY 4.0`). Nunca un Reel sin audio ni con música con derechos.
- Todo lo publica Claude de forma automática; al usuario no se le mandan Reels ni publicaciones para subir a mano.
- No usar voces sintéticas en los vídeos: texto y subtítulos en pantalla.
- **Portada siempre con guitarra** (Manuel, 9-11): ninguna publicación empieza con fondo de color y solo texto. La
  primera escena de cada Reel lleva la guitarra de la que se habla (o una fila de guitarras) y la portada del Reel es
  el fotograma de 1,5 s (`thumb_offset`), con la escena ya entera.
- Precios reales del día, comprobados tienda por tienda; si una rebaja o una foto parecen raras, se cambia la guitarra.
- Rango de precios de chollos y tops: 150–750 €.
- **Amazon** (afiliados en Reino Unido y Francia; en la web, botón de Amazon en cada disco) se puede nombrar en redes, con
  sus normas: 1) avisar de la afiliación en la publicación («Como afiliado de Amazon, obtenemos ingresos por las compras
  que cumplen los requisitos» / «En tant que Partenaire Amazon, nous réalisons un bénéfice sur les achats remplissant les
  conditions requises» / «As an Amazon Associate we earn from qualifying purchases»); 2) nunca precios de Amazon en
  imágenes ni textos (un post no se actualiza): solo «también en Amazon»; 3) nunca el logo de Amazon, solo el nombre.
- **Nunca nombres de tiendas reales en las publicaciones de presentación** ("¿Cómo funciona guitle?", "¿Qué es guitle?",
  promoción, Reels sobre guitle): "Tienda A, B, C…" y "25 tiendas" sin lista. En los chollos y tops del día sí se dice
  dónde está más barata cada guitarra.

## Discos en @guitle.uk (guitle.com/uk/records)

- `scraper/discos_ig.py` + `brand/discos.js`: martes y jueves «Same record, £X cheaper», viernes «Vinyl deal of the
  week» (post y story, tarea de las 18:52). Solo artistas conocidos (lista FAMOSOS), discos con stock en 2+ tiendas y
  diferencias creíbles (el caro ≤ 1,45 × el barato). Etiquetas: #vinyl #vinylrecords #vinylcollection #recordcollector
  #vinyldeals #ukvinyl.
- Tono de comprador a comprador: «comparamos precios de las tiendas de discos de Reino Unido», nunca que leemos sus
  webs. Solo «más barato en X», nunca «caro en Y».
- La API no permite poner el sticker de enlace en las stories: dicen «link in bio».

## Pendiente: publicación de Instagram en GitHub Actions

- Hoy la publican sesiones de Claude (tareas programadas a las 13:07, 17:37 y 21:23, Madrid), que gastan el límite de
  uso de Claude: el 3-11 se agotó y no salieron las franjas de la tarde.
- Plan acordado con Manuel (4-11): pasar las tres franjas a un workflow de GitHub Actions que ejecute los mismos scripts
  (`scraper.instagram`, `scraper.paises`, `scraper.panel`) con los tokens como secretos del repo
  (`INSTAGRAM_TOKEN_ES/FR/IT/DE/UK/BR` y los de los países nuevos). Después, apagar las tareas de la sesión de Claude.
- Se hace **después del fin de semana del 7-8 de noviembre**: Manuel va a crear más cuentas de países y los tokens
  cambiarán. Cuando las tenga: añadir cada país a `scraper/paises.py` (PAISES) y a `social/cuentas.json`, que Manuel
  ponga todos los secretos en GitHub (Settings → Secrets and variables → Actions; nunca por el chat) y también en el
  entorno de Claude, y entonces montar y probar el workflow.
- **@guitle.ie y @guitle.nl: aplazadas** (Manuel, 8-11: «de momento no las vamos a crear»). No pedir sus tokens ni
  contarlas como pendientes; sus Reels de presentación se quedan guardados en `social/pendientes.json`.
- Cuentas nuevas previstas (aún sin crear el 4-11; nombres por confirmar; en `social/cuentas.json` llevan `"creada": false`, que hay que quitar al crearlas): @guitle.pt, @guitle.ie y @guitle.nl ya están en `scraper/paises.py` y `social/cuentas.json`;
  sus Reels de presentación esperan en `social/pendientes.json`. Faltan sus tokens y añadirlas a las franjas diarias.
  Irlanda: el catálogo casi no tiene guitarras en 3+ tiendas, así que no salen chollos ni tops hasta mejorar el
  emparejado de fichas de `data/catalog/ie/`. México y Argentina: sin catálogo todavía.
