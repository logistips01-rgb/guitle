# guitle — rastreador de precios Fender

- `products.json`: productos por SKU Fender (EAN para verificar que la URL es el producto correcto, PVP oficial).
- `stores.json`: tiendas, método preferido (`jsonld` | `meta` | `css`), selector CSS opcional y `{sku, url}`.
- `scraper/`: un módulo por método de extracción; `run.py` prueba primero el método declarado y luego el resto.
- `data/history.json`: todas las ejecuciones (precio, moneda, stock, status, método…).
- `data/latest.json`: último estado por tienda/producto, con mínimo histórico.
- `data/manual.json`: precios apuntados a mano para tiendas bloqueadas, p. ej.
  `[{"date": "2026-10-26", "store": "kirstein", "sku": "0140552506", "price": 799, "in_stock": true}]`.
  Se incorporan al histórico en la siguiente ejecución, marcados como `manual`.
- `index.html`: página para GitHub Pages (Chart.js desde CDN).

Status posibles: `ok`, `no_price`, `blocked_403`, `error`, `wrong_currency`, `robots_disallowed`, `sku_mismatch`.

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
