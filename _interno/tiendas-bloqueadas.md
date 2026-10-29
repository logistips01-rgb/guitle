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
| Kaufland | kaufland.es | Antibots (Cloudflare) | Marketplace alemán; sale en idealo con Thomann y Gear4music. Mirar su programa de afiliados. |

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

## Reino Unido

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| GAK | gak.co.uk | Antibots | Tienda grande (Brighton). Prioridad alta. |
| Gear4music | gear4music.com | Antibots | Pendiente de Awin (mismo feed para todos los países). |
| Coda Music | coda-music.com | Antibots | |
| PMT | pmtonline.co.uk | Sin datos | Se puede leer, pero no publica sitemap: habría que recorrer categorías. |
| Peach Guitars | peachguitars.com | Sin datos | Fichas sin datos estructurados de producto. |
| Guitar Village | guitarvillage.co.uk | Sin datos | El sitemap solo trae el blog. |
| Rimmers Music | rimmersmusic.co.uk | Sin datos | Shopify sin colecciones de guitarras. |
| Music Matter | musicmatter.co.uk | Sin conexión | A revisar. |

## Brasil

| Tienda | Web | Motivo | Notas |
|---|---|---|---|
| Made in Brazil | madeinbrazil.com.br | Antibots | Tienda grande de São Paulo. Prioridad alta. |
| Magazine Luiza | magazineluiza.com.br | 403 | Generalista con programa de afiliados. |
| Mercado Livre | mercadolivre.com.br | Sin datos | Marketplace; tiene programa de afiliados con API. |
| Amazon Brasil | amazon.com.br | Pendiente de afiliados | Darse de alta en Amazon Associados Brasil. |
| Gang Instrumentos | gang.com.br | Sin datos | El sitemap no trae fichas de guitarras. |
| Teclacenter | teclacenter.com.br | Antibots desde GitHub | Desde fuera de GitHub se lee bien (1.000+ guitarras); pedir feed. |
| Musical Express | musicalexpress.com.br | Sin conexión | Tampoco responde desde GitHub (29-oct). |
| Playtech | playtech.com.br | Sin conexión | Tampoco responde desde GitHub (29-oct). |
| Contemporânea | contemporanea.com.br | Sin conexión | Tampoco responde desde GitHub (29-oct). |
| Izzo Musical | izzomusical.com.br | Sin conexión | Tampoco responde desde GitHub (29-oct). |

## México, Estados Unidos, Canadá y Latinoamérica

Mercado casi todo en marketplaces: la vía buena es la API de afiliados de Mercado Libre (México, Argentina, Colombia, Chile) y
Amazon Associates de cada país (amazon.com.mx, amazon.com, amazon.ca), más los programas de las tiendas grandes.

| País | Tienda | Web | Motivo | Notas |
|---|---|---|---|---|
| Estados Unidos | Sweetwater | sweetwater.com | Antibots | La más grande; programa de afiliados propio. |
| Estados Unidos | Guitar Center | guitarcenter.com | Antibots | Programa de afiliados (Impact). |
| Estados Unidos | zZounds | zzounds.com | Antibots | |
| Estados Unidos | American Musical Supply | americanmusical.com | 403 | |
| Estados Unidos | Musician's Friend | musiciansfriend.com | Se puede leer | Única legible; montar cuando haya más. |
| Canadá | Long & McQuade | long-mcquade.com | Sin datos | Se puede leer, pero sin sitemap. |
| México | Veerkamp | veerkamponline.com | Se puede leer | Shopify; única legible (Casa Veerkamp prohíbe en robots.txt). |
| México | Gonher | gonher.com.mx | Sin datos | El sitemap no trae fichas. |
| Chile | Audiomusica | audiomusica.com | Se puede leer | La grande de Chile; probar. |
| Chile | Casa Amarilla | casaamarilla.cl | Antibots | |
| Argentina | Todo Música | todomusica.com.ar | Sin datos | Sin sitemap. |
