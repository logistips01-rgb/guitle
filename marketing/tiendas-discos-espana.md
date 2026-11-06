# Tiendas de discos de España para el comparador de discos (6-11-2026)

Comprobado una a una (robots.txt, plataforma y si cada disco lleva su código de barras), con pocas peticiones y sin
saltarse ningún bloqueo. Fnac y El Corte Inglés no se leen: si se quieren, por afiliación (Awin u otra red).

| Tienda | Ciudad | Web | Plataforma | EAN | Catálogo | Cómo |
|---|---|---|---|---|---|---|
| Discos Supersonic | Santander | discossupersonicsantander.com | Shopify | Sí (`variants[].barcode`) | ~15–20 mil | Tal cual en `scraper/musica.py` (STORES["es"]) |
| El Genio Equivocado | Barcelona | egebotiga.com | WooCommerce | Sí (en `sku`) | 10.272 | Lector de WooCommerce (Store API `/wp-json/wc/store/v1/products`) |
| Discos Alta Fidelidad | Oviedo | discosaltafidelidad.es | WooCommerce | Sí (en `sku`) | 3.067 | Lector de WooCommerce |
| Revolver Records | Barcelona | revolverrecords.es | WooCommerce | No | 10.305 | Solo por artista + título + formato (2.ª fase) |
| Discos Bora Bora | Granada | discosborabora.com | WooCommerce | No | 8.720 | 2.ª fase |
| MaxVinilos | — | maxvinilos.com | WooCommerce | No | 4.586 | Electrónica; 2.ª fase |
| BCore Disc | Barcelona | bcstore.bcoredisc.com | WooCommerce | No | 2.910 | 2.ª fase |
| Discos EGA | — | discosega.es | PrestaShop | ? | ? | Leer fichas (mirar `gtin13` en microdatos) |
| La Casa del Disco | Madrid | lacasadeldisco.es | PrestaShop | ? | ? | Igual |
| Marilians | Madrid | marilians.com | PrestaShop | ? | ? | Igual |

Sin venta online leíble: La Gramola (Zaragoza, solo tienda física y Facebook), Discos Babel, Bajo el Volcán (robots
bloquea), La Metralleta (segunda mano, Odoo), Disco 100, Discos Paradiso, Marcapasos, Totemtanz; Elefant, Subterfuge
y Ultra-Local son sellos (Bandcamp).

**Para arrancar España:** Supersonic (ya) + un lector de WooCommerce para El Genio Equivocado y Alta Fidelidad
(~30 mil discos con EAN en 3 tiendas) + el botón de Amazon España.
