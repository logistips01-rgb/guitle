# Estado comercial de guitle

Actualizado: 13-11-2026. Fuentes: ROADMAP.md, _interno/ (correos de Fnac y Tradedoubler, tiendas-bloqueadas.md,
pendiente/ESTADO.md), scraper/afiliados.py, scraper/intl.py, scraper/musica.py, scraper/catalog.py, data/affiliates.json
y tiendas.html.

Reglas: aquí solo van IDs públicos (los que salen en los enlaces de la web), nunca claves; las claves están en GitHub
Secrets y las guarda Manuel. Nada sale hacia fuera sin que Manuel lo apruebe. **(?)** = dato que no está en el repo y
que tiene que confirmar Manuel.

Estados: **activo** · **solicitado** · **rechazado** · **por pedir** · **borrador** (redactado y sin enviar).

## 1. Redes y programas de afiliación

| Programa | País / web | Idioma | Estado | Fecha | ID público | Próximo paso | Fecha próximo paso |
|---|---|---|---|---|---|---|---|
| Amazon Afiliados | ES (y PT, que enlaza a amazon.es) | es | activo | (?) | `guitle-21` | Informe de ventas a mano en stats.html (panel de afiliados) | 01-12-2026 (noviembre entero) |
| Amazon Afiliados | FR (y LU) | fr | activo | (?) | `guitle00-21` | Igual: informe mensual | 01-12-2026 |
| Amazon Afiliados | IT | it | activo | (?) | `guitle0e-21` | Igual: informe mensual | 01-12-2026 |
| Amazon Afiliados | UK e IE | en | activo | (?) | `guitle08-21` | Igual: informe mensual | 01-12-2026 |
| Amazon Afiliados | mootle | es | activo | (?) | `mootle-21` | Se separa en el mismo informe | 01-12-2026 |
| Amazon Afiliados | DE (amazon.de): DE, AT, CH y botón en CZ, SK, HU, RO, BG, GR, FI, DK, NO | de | por pedir (prioritario) | — | — | Alta de Manuel siguiendo amazon-altas.md | Semana del 16-11 |
| Amazon Associados | BR | pt-BR | por pedir | — | — | Parece exigir CPF/CNPJ y banco brasileño: confirmar si es viable | 2027 |
| Amazon | NL, PL, SE, BE (marketplaces propios) | nl/pl/sv/fr | por pedir | — | — | Una a una según visitas (regla de 3 ventas en 180 días por cuenta) | Enero 2027 |
| Amazon | MX (amazon.com.mx), AR (amazon.com) | es-LA | por pedir | — | — | Requisitos para extranjeros por confirmar | 2027 |
| eBay Partner Network | Todos los eBay (guitle) | en | activo | (?) | campid `5339241544` | Hito del 20/11 (detalle (?)); ganancias por API en afiliados.yml si están las claves EPN_* | 20-11-2026 |
| Awin (cuenta de editor) | guitle y mootle | — | activo | 27-10-2026 (solicitud) | Publisher ID `3136285` | Revisar solicitudes pendientes dentro de Awin | 17-11-2026 |
| Awin → Cultura | FR | fr | activo | (?) | (anunciante en Awin) | Ya en web: catálogo de instrumentos y discos por su fichero; prioridad en la guía de Navidad | Seguimiento semanal |
| Awin → Fnac | ES | es | rechazado | ~01-11-2026 (?) | — | Nueva solicitud con el correo de _interno/correo-fnac-afiliacion.md + visitas de noviembre (SimilarWeb) | 02-12-2026 a 05-12-2026 |
| Awin → Fnac | FR | fr | rechazado (?) | (?) | — | Igual que ES, carta en francés (el código ya está preparado para su fichero) | 02-12-2026 a 05-12-2026 |
| Awin → Zavvi | FR | fr | (?) | (?) | — | El código ya lo espera; confirmar si se pidió | 17-11-2026 |
| Awin → Gear4music | ES, PT, FR, IT, UK | en | solicitado (?) | (?) | — | Un solo fichero sirve para todos los países; recordar si no hay respuesta | 17-11-2026 |
| Awin → Music Store | DE, FR… | de | por pedir | — | — | Solicitar dentro de Awin (bloquea la lectura con 403) | Semana del 16-11 |
| Awin → Kirstein | DE, IT | de | por pedir | — | — | Ídem (ROADMAP: "redes tipo Awin") | Semana del 16-11 |
| Tradedoubler | guitle y mootle | es | solicitado | Alta "hace unas semanas" (?) | Usuario hola@guitle.com | ¿Se envió el correo del 07-11 (_interno/correo-tradedoubler.md)? Si no hay respuesta, reenviarlo | 18-11-2026 |
| Thomann (programa propio) | Todos | de/en | por pedir | — | — | Solicitud; Thomann ya sale en casi todos los países | Semana del 16-11 |
| Albabike (mootle) | ES | es | activo | (?) | (?) | Nada por ahora | — |
| Mercado Libre | MX, AR, CO, CL | es-LA | por pedir | — | — | Solo cuando haya webs de Latinoamérica con catálogo | 2027 |
| Magazine Luiza | BR | pt-BR | por pedir | — | — | Ídem | 2027 |

## 2. Tiendas: altas, feeds y colaboraciones

| Tienda | País | Idioma | Tipo | Estado | Fecha | Próximo paso | Fecha próximo paso |
|---|---|---|---|---|---|---|---|
| iGuitar Music | (?) | (?) | Propuesta de colaboración | (?) — no hay documento en el repo | (?) | Que Manuel me pase la propuesta o el estado; la guardo en _interno/comercial/ | 16-11-2026 |
| Evenstad Musikk | NO | no | Alta de tienda | Ya se lee su web (catálogo de Noruega) | (?) | Confirmar qué se habló; ofrecer acuerdo directo o feed (tiendas.html) | 18-11-2026 |
| Stars Music | FR (y BE) | fr | Alta de tienda | Ya se lee su web (FR y BE) | (?) | Ídem; preguntar si tienen programa de afiliados | 18-11-2026 |
| Madrid Hifi | ES | es | Feed | solicitado (lo pasaron a marketing) | 27-10 y 30-10-2026 | Recordatorio corto con enlace a guitle.com/tiendas.html (vencía el 10-11) | 17-11-2026 |
| StrumentiMusicali.net | IT | it | Feed / afiliación | por pedir (403) | — | Carta en italiano pidiendo feed; prioridad alta | Semana del 23-11 |
| GAK | UK | en | Feed / afiliación | por pedir (antibots) | — | Carta en inglés; prioridad alta | Semana del 23-11 |
| Made in Brazil | BR | pt-BR | Feed | por pedir (antibots) | — | Carta; prioridad alta | Diciembre |
| Teclacenter | BR | pt-BR | Feed | por pedir (bloquea desde GitHub) | — | Carta pidiendo feed | Diciembre |
| Musicis | IT | it | Feed | por pedir (antibots desde 30-10) | — | Pedir feed si sigue bloqueando | Diciembre |
| Resto de tiendas bloqueadas | varios | varios | Feed | por pedir | — | Ver _interno/tiendas-bloqueadas.md; después de Navidad | Enero 2027 |

## 3. Visitas a tiendas (kit: tarjeta, dossier, hoja resumen)

| Pieza | Estado | Próximo paso |
|---|---|---|
| Tarjeta | (?) — no está en el repo | Confirmar si existe; si no, borrador de texto |
| Dossier | En Claude Docs: "guitle · Dossier del proyecto" (para Zaragoza Activa) | Actualizar cifras (hoy: +659.000 productos, 229 tiendas, 24 países con catálogo según data/resumen.json) |
| Hoja resumen | (?) | Una cara, basada en tiendas.html |
| Lista de tiendas a visitar (Zaragoza) | por hacer | Proponer 5-8 tiendas de Zaragoza para la semana del 30-11 |

## 4. Publicidad

| Qué | Estado | Presupuesto | Próximo paso |
|---|---|---|---|
| Prueba pequeña en Black Friday | Apuntada en ROADMAP (sale del bolsillo, antes del alta de autónomo) | Dentro de 50 €/mes total (infraestructura ≤ 10 €). Nada > 1 $ sin visto bueno | Propuesta concreta a Manuel antes del 20-11 |

## 5. Avisos

- **Cifras para cartas:** data/resumen.json (13-11) dice 24 países con catálogo; los borradores dicen "27 países" (24
  de Europa + BR, MX, AR). Antes de enviar nada, confirmar la cifra que se puede demostrar ese día.
- **Afiliación de tiendas en la web:** data/affiliates.json no tiene ninguna tienda con plantilla; Cultura funciona
  porque sus enlaces vienen ya del fichero de Awin. Cuando entre un programa nuevo, la sesión técnica añade su plantilla.
- **Comisiones:** afiliados.yml lee Awin y eBay cada mañana y manda el resumen los lunes a hola@guitle.com; Amazon se
  sube a mano en stats.html.

## Registro de correos (enviados y recibidos)

Cada correo se guarda junto a su contacto en _interno/comercial/<contacto>/AAAA-MM-DD-asunto.md.

| Fecha | Contacto | Sentido | Resumen | Fichero |
|---|---|---|---|---|
| 06-11-2026 | Fnac ES | borrador | Nueva solicitud tras el rechazo | _interno/correo-fnac-afiliacion.md |
| 07-11-2026 | Tradedoubler | borrador (¿enviado?) | Estado de la solicitud de editor | _interno/correo-tradedoubler.md |
