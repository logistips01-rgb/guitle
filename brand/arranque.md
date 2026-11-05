# Arranque en Instagram

Imágenes en `brand/png/arranque/` (se regeneran con `node brand/arranque.js`, ver cabecera del script).
Publicar en este orden. Instagram pone la última arriba a la izquierda, así que la primera fila
quedará "chollo · cómo funciona · presentación".

## 1. Presentación — `1-presentacion.png`

> ¡Hola! Somos guitle 🎸
> Revisamos cada día los precios de las guitarras en las tiendas de Europa para que sepas dónde está más barata la que quieres.
> Aquí publicaremos los chollos y bajadas de precio del día.
> 👉 Busca tu guitarra en guitle.com (enlace en la bio)
>
> #guitarra #guitarraelectrica #fender #gibson #epiphone #ibanez #guitarristas #chollos

## 2. Carrusel "Cómo funciona" — `2-carrusel-1.png` … `2-carrusel-4.png`

> ¿Cómo funciona guitle? 👇
> 1️⃣ Revisamos cada día el precio de cada guitarra en las tiendas.
> 2️⃣ Te enseñamos dónde está más barata, con su histórico de precios.
> 3️⃣ Publicamos aquí los mejores chollos.
> Síguenos y activa las notificaciones 🔔 Enlace en la bio.
>
> #guitarra #guitarraelectrica #comparadordeprecios #chollos #guitarristas

## 3. Primer chollo — `brand/png/post-plantilla.png`

Regenerar el mismo día de publicarlo (`python brand/generar.py …`) para que el precio sea el real.

> 🔥 Chollo de hoy: {modelo} a {precio} en {tienda}.
> Compara su precio en el resto de tiendas en guitle.com (enlace en la bio).
>
> #fender #stratocaster #guitarraelectrica #chollos

## Story — `3-story-ya-estamos-aqui.png`

Añadir en la app el sticker de **Enlace** a `https://guitle.com` en el hueco bajo las guitarras.

## Destacadas — `4-destacada-*.png`

Crear tres destacadas ("Chollos", "Cómo funciona", "Tiendas") y usar estas imágenes como portada.
Para "Cómo funciona" se pueden subir las diapositivas del carrusel como stories.

## Cartel del destacado "Chollos" — `5-cartel-chollos.png`

Primera story del destacado: explica qué hay dentro y que cada precio es del día de su story.
