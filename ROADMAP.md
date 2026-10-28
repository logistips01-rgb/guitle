# Ideas de futuro

Fase actual: rastreador personal (catálogo a mano, cron diario, página con buscador).

## Comparador web (cuando deje de ser solo para uso propio)

- **Catálogo grande automático (piloto en marcha: guitarras eléctricas, `scraper/catalog.py`, `catalogo.html`).**
  Sitemaps de Numemusic (~2.000 eléctricas) y Session (~3.100 candidatas), fichas leídas por lotes cada noche
  (workflow `catalog`, ~50 min por tienda) y emparejadas por EAN, cruzando también con las tiendas de seguimiento.
  - Siguiente: Egitana (no publica EAN: emparejar por marca + modelo + acabado), Thomann/Alfasoni/Musicopolix,
    y después bajos, amplis, pedales, teclados y micros con el mismo sistema.
  - Miniaturas uniformes en `img/p/` (`scraper/thumbs.py`): recorte, guitarra en vertical, sin logos de tienda.
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

## Líneas de negocio (ideas apuntadas)

- **Renting musical.** Alquiler de instrumentos con cuota mensual (guitarras, bajos, amplis, teclados), con
  opción de compra descontando lo pagado. Encaja con quien empieza y no sabe si seguirá, y con colegios y
  escuelas. guitle aporta el precio de mercado para calcular cuotas y valor residual.
  - Stock (decidido el 27/10/2026): al arrancar, 80-90 % guitarras **reacondicionadas** de "Compramos tu guitarra"
    (casi no pierden valor: ~60 % de margen anual frente a ~21 % con una nueva). Nuevas solo para el plan con
    opción de compra, una gama "estreno" con cuota algo mayor y modelos muy pedidos. Con precio de distribuidor
    (SL), revisar la proporción.
  - Ejemplo de cuotas (Fender Standard Stratocaster, 517 €): flexible 39 €/mes (mínimo 3 meses), anual 29 €/mes,
    con opción de compra 35 €/mes; fianza 100 €. Antes de arrancar: contrato, seguro de instrumentos y cobro
    domiciliado; revisar el IVA de bienes usados (REBU) con un gestor.
- **Personalización con grabado láser** (apuntado el 28/10/2026). Producto de regalo (nombre o dibujo), poca inversión
  y mucho margen. Por fases: 1) accesorios y golpeadores (púas, correas de cuero, placas de estuche, golpeadores de
  acrílico/aluminio/madera; NUNCA golpeadores de PVC: desprenden cloro); 2) grabado en la trasera de la pala de
  nuestras guitarras (segunda mano o nuevas) como extra al comprar; 3) guitarras de clientes, con aceptación firmada
  del diseño y del riesgo, prueba previa y seguro. El láser atraviesa barnices de brillo: mejor en satinado o madera
  vista. Máquina: diodo 10-20 W (400-1.200 €) o CO₂ de sobremesa (1.500-3.000 €), extracción de humos y carcasa
  cerrada (viable en el garaje). Precios orientativos: púa/correa 5-20 €, golpeador 40-80 €, pala 30-60 €. Nunca
  logos de marcas ajenas. Más adelante: mejoras (pastillas, golpeadores, ajustes) y configurador a medida con piezas
  con licencia y un luthier colaborador.
- **Cursos de guitarra.** Online y/o presenciales (en la tienda). Se cruzan con el resto: alumno que empieza
  → renting o primera guitarra recomendada en guitle → accesorios.

- **Segunda mano: "Compramos tu guitarra"** (dominio `compramostuguitarra.es`, redirigido a una sección de
  guitle). Compra de instrumentos usados a particulares → stock para el renting y para la compra-venta.
  - Tasador en la web: el precio nuevo de calle que ya calcula guitle × % según estado (p. ej. 40-60 %),
    y formulario con fotos para recibir ofertas.
  - **Propuesta de valor** frente a Wallapop, Milanuncios y Reverb (mercados entre particulares, con estafas
    frecuentes): compramos al momento con tasación transparente (los datos de guitle) y vendemos revisada, con
    factura y 1 año de garantía. Sin estafas ni quedar con desconocidos. Antes de lanzar, revisar si alguna
    tienda española ya lo hace en serio.
  - **Visión: portal europeo de guitarras reacondicionadas** (modelo Back Market): 1) España con stock propio;
    2) abrir la plataforma a talleres y luthiers certificados con normas de guitle (escala de estado, revisión
    obligatoria, fotos reales, garantía mínima), comisión por venta (~10-15 %), sin stock; 3) Europa país a país con
    talleres locales. Por resolver: envíos asegurados en estuche (~30-60 € en la UE), devoluciones de 14 días y
    garantía de usados según país, IVA de bienes usados entre países, idiomas.
  - **Guitarra como parte del pago** (decidido el 28/10/2026), como en coches y motos: en cualquier compra en la tienda
    de guitle (segunda mano, nueva cuando seamos tienda oficial, renting con opción de compra). Se tasa un 20-25 %
    por debajo del precio entre particulares y se revende revisada y con garantía (1 año) a precio de mercado:
    p. ej. guitarra de 500 € → se toma por 375-400 €, revisión ~30 €, venta a 500-550 € → ~70-145 € de margen.
    Lo que no se venda en 1-2 meses pasa al renting. Requisitos: DNI y propiedad del vendedor, libro registro de
    compraventa de usados si lo exige la comunidad, IVA de bienes usados (REBU) con el gestor.
  - **Tienda oficial y distribución (con volumen):** ser dealer oficial de alguna marca (Fender, Yamaha y Gibson venden
    directo a tiendas, no dan distribución) y distribuidor de alguna marca mediana sin distribuidor fuerte en España.
    Precio competitivo pero nunca a pérdida (prohibido; y la marca puede cortar el suministro). La tienda, separada
    del comparador y marcada como "tienda de guitle", con el orden siempre por precio real.
  - Redirección: reenvío 301 en el registrador del dominio hacia `https://guitle.com/vende/`
    (GitHub Pages admite un solo dominio propio por web, por eso se redirige en el registrador).
  - Pendiente legal: registro/libro de compra-venta de objetos usados (en España suele exigirse
    comunicación a la policía o a la comunidad autónoma; depende de la comunidad donde se dé de alta).

## Orden de trabajo acordado

1. Revisar la carga completa de guitarras eléctricas en el catálogo.
2. Sumar Egitana, Thomann y el resto de tiendas al catálogo.
3. Acústicas y españolas (clásicas). **En marcha:** `acusticas.html` y `clasicas.html`, catálogo `--cat acustica`
   (data/catalog/acusticas/), mismas tiendas y una sola lectura para las dos secciones.
4. Bajos, amplis, pedales, teclados y micros, y accesorios/consumibles: cables, púas, cuerdas, correas,
   pies de guitarra y de micro, fundas, afinadores, cejillas… (el margen de afiliación y de tienda está aquí).

## Mensajes de marca (solo lo que se pueda demostrar)

- Nada de "el más grande" o "el número 1" sin pruebas (publicidad engañosa). Sí: "más de 7.000 guitarras
  comparadas", "comparador especializado en guitarras con histórico de precios", "te decimos si un descuento es real".
- Pendiente (hacia el 10/11/2026): muestreo a mano de 20-30 guitarras populares, guitle frente a idealo el mismo
  día y con capturas. Si sale bien: "en X de cada 10 guitarras guitle encuentra un precio más bajo".
- Más adelante: comprobar si guitle es "el mayor comparador especializado en guitarras de España", con pruebas
  fechadas, antes de decirlo.

## Arranque del negocio: España

Decisión: se empieza en España (online). La tienda física en Andorra queda aparcada para más adelante.
Forma jurídica: se arranca como **autónomo** (solo comisiones de afiliación, sin stock ni ventas). La SL se
constituirá cuando empiecen la compra-venta de segunda mano y el renting (stock, contratos, responsabilidad).

### Ayudas y financiación (revisado el 27/10/2026; promotor en Zaragoza capital, por cuenta ajena)

- **Ahora:** entrar en un programa de Zaragoza Activa (no exige alta). Dossier del proyecto en Claude Docs
  ("guitle · Dossier del proyecto"); actualizar sus cifras antes de la cita.
- **Ayuda municipal a emprendedores** (Zaragoza, hasta 6.000 €, 80 % de gastos corrientes justificados: cuotas de
  autónomo, gestoría, servicios, publicidad a confirmar): exige alta (≤ 3 años), domicilio fiscal en Zaragoza y
  haber pasado por un programa municipal. Solo cuentan los gastos del periodo del proyecto, ya de alta: la
  publicidad de antes del alta sale del bolsillo (prueba pequeña en Black Friday).
- **Ayuda municipal al nuevo autónomo** (3.000–10.000 € según inversión): exige local independiente en Zaragoza
  (ni vivienda ni coworking) y 2 años de actividad; plazo de alta de 2026 cerrado. Encaja en 2027 con el local de
  segunda mano y renting. También cubre el relevo de un negocio existente.
- **INAEM (Aragón):** solo para desempleados; no aplica.
- **Con la SL:** certificado de empresa emergente (ENISA), préstamos ENISA (mínimo 25.000 €, fondos propios 1:1),
  SODIAR (microcréditos 2.500–10.000 €) y NEOTEC. Los plazos de "startup" cuentan desde la constitución: no
  constituirla antes de tener tracción.
- **Garaje** (casa de Villanueva de Gállego, acceso propio a la calle): almacén y taller del stock; afectarlo como
  autónomo o alquilarlo a la SL; licencia en el Ayuntamiento de Villanueva; mirar su referencia catastral.

## Expansión internacional (guitle.com)

El precio depende del país del comprador (IVA del país de destino y portes): cada país necesita sus tiendas y sus
precios, no solo la web traducida.

1. **Más tiendas europeas que envían a España:** Bax-shop, Muziker, Star's Music (primero); después Musik Produktiv,
   Just Music, Hieber Lindberg, Musikhaus Korn, Station Music, Michenaud, Univers Sons, Max Music, Strumenti Musicali,
   Mogar, Scavino, Salão Musical.
2. **Idiomas y países** (decidido el 27/10/2026): hasta el Black Friday, todo en España. Después, por este orden:
   **Portugal** (Egitana es portuguesa; Numemusic y Thomann envían; sirve para montar el sistema de países),
   **Francia e Italia**, y luego **Alemania** (el mayor mercado y el más competido). Cada país: web traducida
   (guitle.com/pt, /fr…), precios de sus tiendas o de su versión local, afiliados de ese país (en Awin cada país es
   un programa) y páginas propias para Google. Antes se prepara la estructura (textos en un fichero por idioma).
3. **Selector de país en Europa:** tiendas, precios con el IVA del país y portes de cada país. Reino Unido aparte
   (fuera de la UE: aduanas): Gear4music, Andertons, PMT, Guitar Guitar, Dawsons.
4. **Fase final: Estados Unidos y Latinoamérica.**
   - EE. UU.: precios en USD sin impuestos (el sales tax depende del estado). Sweetwater, Guitar Center,
     Musician's Friend, zZounds, Reverb (también usado), Amazon US. Afiliación: programas propios y Impact/CJ.
   - Latinoamérica: Mercado Libre (tiene API pública y programa de afiliados) y Amazon MX/BR, más las tiendas
     locales de cada país (México, Argentina, Chile, Colombia…); moneda e impuestos de cada país.
5. **Después: Asia** (Japón, Corea, sudeste asiático…): mercados con mucha guitarra y tiendas y marketplaces
   propios (p. ej. Rakuten y Amazon JP en Japón); idioma, moneda e impuestos de cada país.

## Proyecto aparte: tienda en Andorra (aparcado, se valorará más adelante)

Idea: tienda física en Andorra con escaparate online y "reserva y recoge". Para quien compra o recoge allí,
con el mismo margen que la tienda más barata de la UE se podría vender un ~13-14 % más barato (IGI 4,5 % frente a IVA 21 %).

- Envíos a España NO tienen ventaja: importación con IVA español sobre el valor completo (la franquicia de
  viajero, ~900 €, solo aplica a mercancía que lleva el propio cliente; por encima se declara el exceso).
- No existe tienda Fender Andorra (fender.com/es-AD da 404); Fender Portugal tiene el mismo precio que España.
- Pendiente de estudiar: mercado (turismo de compras), acceso a distribuidores y precio de compra (decisivo),
  costes (local, stock, residencia), requisitos legales (SL 3.000 €, autorización de inversión extranjera,
  local físico, licencia del comú, CASS, IGI, residencia por cuenta propia) con gestoría andorrana.
- guitle sirve para fijar precios frente a la competencia europea.
