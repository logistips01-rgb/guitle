# Ideas de futuro

Fase actual: rastreador personal (catálogo a mano, cron diario, página con buscador).

## Comparador web (cuando deje de ser solo para uso propio)

- **Catálogo grande automático.** Recorrer cada día los listados por marca de las tiendas que no bloquean
  (Thomann, Musicopolix, Alfasoni) y guardar todas las guitarras con su precio: una página de listado
  trae decenas de productos por petición. Pasar de ~20 productos a cientos o miles.
  - Reto principal: emparejar el mismo producto entre tiendas (EAN cuando lo haya; si no, marca + modelo + acabado normalizados).
- **Búsqueda tipo Google** sobre ese catálogo (la página actual ya filtra en el navegador; con miles de
  productos convendría un índice precalculado o un backend).
- **Backend / base de datos** (p. ej. Firebase) cuando el JSON en el repo se quede corto.

## Fuentes de datos

- **Feeds de afiliados:** Thomann (programa propio), Music Store y Kirstein (redes tipo Awin), Amazon (API de afiliados).
  Método `"feed"` en `stores.json`, cruzando por EAN.
- **Tiendas bloqueadas por anti-bot** (Kirstein, Music Store, Unión Musical, Madrid HiFi): pedir acceso para
  un bot identificado (`guitle-pricebot/1.0`). Mientras tanto, `data/manual.json`.
- **PVP oficial automático** de Gibson y Epiphone desde sus webs, como ya se hace con Fender. Ibanez: PVP manual.

## Catálogo

- Más tiendas para Epiphone, Ibanez y Gibson (ahora solo Thomann).
- Verificar SKUs de Gibson (marcados "sin verificar" en `products.json`).
- SKU y PVP de la Fender Player II Telecaster HH RW Black.
- Altavoces: decidir tipo (monitores de estudio, PA, pantallas de guitarra) y tiendas.
- Pendiente: `matguitars`, `auvisa`, `gear4music`, `drunkat` (URLs a null en `stores.json`).

## Proyecto aparte: tienda en Andorra (en estudio)

Idea: tienda física en Andorra con escaparate online y "reserva y recoge". Para quien compra o recoge allí,
con el mismo margen que la tienda más barata de la UE se podría vender un ~13-14 % más barato (IGI 4,5 % frente a IVA 21 %).

- Envíos a España NO tienen ventaja: importación con IVA español sobre el valor completo (la franquicia de
  viajero, ~900 €, solo aplica a mercancía que lleva el propio cliente; por encima se declara el exceso).
- No existe tienda Fender Andorra (fender.com/es-AD da 404); Fender Portugal tiene el mismo precio que España.
- Pendiente de estudiar: mercado (turismo de compras), acceso a distribuidores y precio de compra (decisivo),
  costes (local, stock, residencia), requisitos legales (SL 3.000 €, autorización de inversión extranjera,
  local físico, licencia del comú, CASS, IGI, residencia por cuenta propia) con gestoría andorrana.
- guitle sirve para fijar precios frente a la competencia europea.
