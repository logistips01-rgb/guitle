# Tiendas que no podemos leer (para contacto manual)

Tiendas que bloquean la lectura automática o la piden en otras condiciones. No se saltan protecciones: la vía es
pedirles un feed de productos (CSV/XML con EAN, precio, stock y URL) o entrar por su programa de afiliados (Awin,
Tradedoubler…), que suele incluir el feed. Esta carpeta (`_interno/`) no se publica en la web.

Motivos: **403** = nos deniega el acceso · **antibots** = página de comprobación (Cloudflare u otra) ·
**429** = nos frena por demasiadas peticiones · **sin conexión** = no responde desde nuestro entorno de pruebas
(a revisar desde GitHub, puede que sí funcione allí) · **sin datos** = se lee, pero sin precio o sin fichas útiles.

## España

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| Madrid Hifi | madridhifi.com | Solicitud enviada | Han pasado la solicitud a marketing; solo queremos su feed. |
| Gear4music | gear4music.es | Pendiente de Awin | Usar el feed de Awin (sirve también para PT, FR, IT…). |

## Portugal

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| Musifex | musifex.pt | Sin EAN, lectura pendiente | Odoo; se puede leer por categorías, falta montarlo. |

## Francia

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| Fnac | fnac.com | 403 | Generalista; tiene programa de afiliados. |
| Cultura | cultura.com | 403 | Generalista. |
| Sonovente | sonovente.com | 403 | Tienda de música grande. |
| Music Store | musicstore.com/fr_FR | 403 | Alemana con web en francés; programa de afiliados. |
| Bax-shop | bax-shop.fr | 406 | Neerlandesa con web en francés. |
| Muziker | muziker.fr | 429 | Nos frena en el sitemap. |
| Kytary | kytary.fr | Sin conexión | A revisar. |
| Musikia | musikia.fr | Sin conexión | A revisar. |
| Planète Musique | planetemusique.fr | Sin conexión | A revisar. |
| Hollywood Music | hollywoodmusic.fr | Sin conexión | A revisar. |
| Gear4music | gear4music.fr | Pendiente de Awin | Mismo feed que en España. |

## Italia

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| StrumentiMusicali.net | strumentimusicali.net | 403 | La mayor tienda online italiana (100.000 artículos). Prioridad alta. |
| Gino Guitars | ginoguitars.com | Antibots | Boutique de guitarras muy valorada. |
| Mama's Music | mamasmusicstore.it | 403 | |
| Lucky Music | luckymusic.com | 403 | |
| Music Shop Europe | musicshopeurope.it | 403 | |
| Fanfara | fanfara.it | Sin conexión | A revisar. |
| Rock Shop | rockshop.it | Sin conexión | A revisar. |
| Strumenti Musicali | strumentimusicali.it | Sin conexión | A revisar. |
| Chitarre Online | chitarre-online.it | Sin conexión | A revisar. |
| La Favorita Musica | lafavoritamusica.it | Sin conexión | A revisar. |
| Aiello Music Shop | aiellomusicshop.it | Sin conexión | A revisar. |
| Casa della Musica | casadellamusica.it | Sin conexión | A revisar. |
| Banda Roma | bandaroma.it | Sin conexión | A revisar. |
| Mondo Musica | mondomusicastore.it | Sin conexión | A revisar. |
| Kirstein | kirstein.de/it | 403 | Alemana con web en italiano; programa de afiliados. |
| Muziker | muziker.it | 429 | |
| Gear4music | gear4music.it | Pendiente de Awin | Mismo feed que en España. |
