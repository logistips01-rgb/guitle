# guitle — rastreador de precios de guitarras y audio

- `products.json`: productos por SKU del fabricante, con `brand`, `category`, EAN (verifica que la URL es el producto correcto) y PVP de respaldo.
- `stores.json`: tiendas, método preferido (`jsonld` | `meta` | `css`), selector CSS opcional y `{sku, url}`.
- `scraper/`: un módulo por método de extracción; `run.py` prueba primero el método declarado y luego el resto.
- `data/history.json`: todas las ejecuciones (precio, moneda, stock, status, método…).
- `data/latest.json`: último estado por tienda/producto, con mínimo histórico.
- `data/manual.json`: precios apuntados a mano para tiendas bloqueadas, p. ej.
  `[{"date": "2026-10-26", "store": "kirstein", "sku": "0140552506", "price": 799, "in_stock": true}]`.
  Se incorporan al histórico en la siguiente ejecución, marcados como `manual`.
- `data/coupons.json`: cupones de descuento por tienda; la página los aplica al precio, al mejor precio y al pack. Ejemplo:
  `[{"store": "thomann", "code": "OTONO10", "percent": 10, "brands": ["Fender"], "categories": ["guitarra"], "min_purchase": 300, "valid_until": "2026-11-30"}]`
  (`percent` o `amount` en euros; `brands`, `categories`, `min_purchase` y `valid_until` son opcionales; caducados se ignoran).
- `index.html`: página para GitHub Pages (Chart.js desde CDN).

Status posibles: `ok`, `no_price`, `blocked_403`, `error`, `wrong_currency`, `robots_disallowed`, `sku_mismatch`.

## Añadir productos, marcas o tiendas

1. Producto: añade una línea a `products.json` con `sku` (referencia del fabricante, numérica o alfanumérica),
   `brand`, `category` (p. ej. `guitarra`, `altavoz`), `name`, `ean` si lo sabes y `pvp` de respaldo.
2. Tienda nueva: añádela a `stores.json`; si existe, solo añade `{sku, url}` en su `items`.
3. PVP automático: la web oficial de la marca se declara como tienda con `"reference": true`;
   su precio diario pasa a ser el PVP del producto (si falla, se usa el de `products.json`).
4. Prueba antes de dejarlo en el cron: `python -m scraper.run --dry-run --only <tienda>`.

## Uso local

```sh
pip install -r requirements.txt
python -m scraper.run --dry-run            # informe sin tocar data/
python -m scraper.run --only thomann       # solo algunas tiendas, guardando
python -m http.server                      # y abrir http://localhost:8000
```

## Cron

`.github/workflows/scrape.yml` corre a las 09:00 Europe/Madrid (dos crons UTC + filtro de hora)
y commitea `data/` aunque todas las tiendas fallen. Solo se ejecuta desde la rama por defecto.
