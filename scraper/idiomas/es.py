# Español de México (es) · México · MXN. Tuteo ("tú"), como la mayoría de las tiendas de música en línea mexicanas.
# Vocabulario de México/Latinoamérica: "correo", "en línea", "dar clic", "precio de lista"; sin "vosotros" ni "chollos".
# Plurales: "nouns", "guitars", "storesWord", "many", "store"/"stores" (arriba y en js) van en plural ("1,234 guitarras",
# "3 tiendas"); "store" del js se usa con 1 tienda en la ficha ("1 tienda"). "desc" usa "en {n} {stores}".
# Los porcentajes van pegados ("15%"), como es costumbre en México.

MONEY_NOTE = ("Signo de peso delante, coma para los miles y sin centavos: '$12,999' "
              "(código: f\"${round(v):,}\").")

KINDS_LANG = {"electrica": "guitarras-electricas", "acustica": "guitarras-acusticas", "clasica": "guitarras-clasicas",
              "pack": "paquetes", "bajo": "bajos", "ampli": "amplificadores", "pedal": "pedales",
              "teclado": "teclados", "micro": "microfonos", "estuche": "estuches-fundas", "varios": "accesorios"}

PACK_LANG = ("Paquetes de guitarra", "Paquetes", "Busca entre los paquetes: modelo, marca, con amplificador…", "paquetes",
             {"Eléctrica": "Eléctrica", "Acústica": "Acústica"})

T_LANG = {
    "tagline": "guitarras al mejor precio", "homeLabel": "guitle, inicio",
    "homeTitle": "guitle · comparador de precios de guitarras",
    "homeDesc": "guitle compara precios de guitarras eléctricas, acústicas y clásicas en las tiendas que venden en México, "
                "con el historial de precios de cada modelo.",
    "h1": "Tu guitarra <span>al mejor precio</span><small>Comparador de precios de guitarras</small>",
    "searchPh": "Busca: strat, les paul, yamaha, ibanez…", "searchBtn": "Buscar", "searchLabel": "Buscar una guitarra",
    "guitars": "guitarras", "storesWord": "tiendas", "catalog": "Catálogo",
    "dealsH": "Las mayores diferencias de precio entre tiendas", "dealsBadge": "−{p}% vs. la más cara",
    "catsH": "Explora por categoría", "soon": "próximamente", "storesH": "Tiendas que comparamos",
    "howH": "¿Cómo funciona?",
    "steps": ["Todos los días revisamos el precio, la disponibilidad y la foto de cada guitarra en las tiendas que venden en México.",
              "Guardamos el historial de precios para que veas si un precio es realmente bueno o si suele estar más bajo.",
              "Si quieres, te avisamos por correo cuando baje el precio."],
    "affiliate": "Algunos enlaces a tiendas son de afiliado: si compras, guitle puede recibir una comisión, sin ningún costo extra para ti.",
    "legal": "Aviso legal", "privacy": "Privacidad", "cookies": "Cookies", "otherCountries": "guitle en otros países:",
    "updated": "Datos actualizados: {d}", "home": "Inicio",
    "kinds": {"electrica": ("Guitarras eléctricas", "Eléctricas", "Busca entre las eléctricas: modelo, marca, color…"),
              "acustica": ("Guitarras acústicas", "Acústicas", "Busca entre las acústicas: modelo, marca, madera…"),
              "clasica": ("Guitarras clásicas", "Clásicas", "Busca entre las clásicas: modelo, marca, flamenca…"),
              "bajo": ("Bajos eléctricos y acústicos", "Bajos", "Busca entre los bajos: modelo, marca, 5 cuerdas…"),
              "ampli": ("Amplificadores de guitarra y bajo", "Amplificadores", "Busca entre los amplificadores: modelo, marca, combo, cabezal…"),
              "pedal": ("Pedales de efectos", "Efectos", "Busca entre los efectos: modelo, marca, tipo de efecto…"),
              "teclado": ("Teclados y pianos digitales", "Teclados", "Busca entre los teclados: modelo, marca…"),
              "micro": ("Micrófonos", "Micrófonos", "Busca entre los micrófonos: modelo, marca, tipo…"),
              "estuche": ("Estuches y fundas", "Estuches", "Busca entre los estuches y fundas: modelo, marca…"),
              "varios": ("Accesorios para guitarra", "Accesorios", "Busca entre los accesorios: cuerdas, púas, correas, cables…")},
    # Qué se cuenta en cada categoría (portada y listado), en plural.
    "nouns": {"bajo": "bajos", "ampli": "amplificadores", "pedal": "efectos", "teclado": "teclados", "micro": "micrófonos",
              "estuche": "estuches", "varios": "productos"},
    "allWord": "productos",
    "anyPrice": "Cualquier precio", "upTo": "Hasta {v}", "over": "Más de {v}", "brandLabel": "Marca", "priceLabel": "Precio",
    "showLabel": "Mostrar", "showAll": "Todas", "showMulti": "En varias tiendas", "showStock": "Disponibles",
    "showLow": "En su precio mínimo", "showLh": "Solo para zurdos", "loading": "Cargando el catálogo…", "sortLabel": "Ordenar",
    "sorts": ["Más tiendas", "Precio más bajo", "Precio más alto", "Mayor ahorro entre tiendas", "Nombre"],
    "moreBtn": "Ver más", "sections": "Secciones", "searchAria": "Buscar",
    "bestPrice": "mejor precio", "inStock": "disponible", "noStock": "agotado", "goLong": "Ver en la tienda", "goShort": "Ver",
    "store": "tienda", "stores": "tiendas", "lh": "zurdo", "storesH3": "Tiendas", "historyH3": "Historial de precios",
    "amazon": "", "titleFrom": "{name}: desde {price} {where}", "inN": "en {n} tiendas", "inS": "en {s}",
    "whereMany": "en {s} · {n} tiendas", "whereDiff": ", hasta {d} de diferencia",
    "desc": "{name} desde {price} en {s}. Compara su precio en {n} {stores} ({list}) y revisa el historial para saber "
            "si es buen momento para comprar.",
    "alertTitle": "Aviso de precio", "alertWait": "Un momento…", "alertSaving": "Estamos guardando tu respuesta.",
    "alertGo": "Ir a guitle", "alertBad": ["Enlace no válido", "Copia el enlace completo del correo e inténtalo de nuevo."],
    "alertDone": ["¡Aviso confirmado!", "Te escribiremos en cuanto baje el precio. Cada correo trae un enlace para darte de baja."],
    "alertGone": ["Aviso cancelado", "Ya no recibirás más correos de este aviso. Borramos tu dirección de nuestra lista."],
    "alertMissing": ["No encontramos el aviso", "Puede que ya estuviera confirmado o cancelado, o que hayan pasado más de 7 días "
                                                "sin confirmarlo. ¿Necesitas ayuda? Escríbenos a hola@guitle.com."],
    "js": {"loadErr": "No se pudo cargar el catálogo.", "allBrands": "Todas las marcas", "all": "Todas", "low": "Mínimo",
           "save": "Ahorra {v}", "lh": "zurdo", "store": "tienda", "stores": "tiendas",
           "empty": "No hay {many} con esos filtros.", "more": "Ver más ({n} restantes)",
           "meta": "{a} de {b} {many} · {m} comparables en varias tiendas · actualizado: {d}", "best": "mejor precio",
           "inStock": "disponible", "noStock": "agotado", "goLong": "Ver en la tienda", "goShort": "Ver", "close": "Cerrar",
           "inAt": "en {s}", "saveMax": " · hasta {v} menos que en la más cara", "atLow": "En su precio mínimo registrado",
           "lowTag": "Precio mínimo: {v}", "storesH": "Tiendas", "evolH": "Evolución del precio",
           "histErr": "No se pudo cargar el historial de precios.", "histSoon": "El historial de precios aparecerá en los próximos días.",
           "many": "guitarras",
           "types": {"ST": "Tipo ST", "T": "Tipo T", "Semihueca": "Semihueca", "Offset / Retro": "Offset / Retro", "Moderna / Metal": "Moderna / Metal",
                     "Otras": "Otras", "Auditorio / Concierto": "Auditorio / Concierto", "12 cuerdas": "12 cuerdas",
                     "Tamaño reducido": "Tamaño reducido", "Clásica": "Clásica", "Flamenca": "Flamenca",
                     "Electroclásica": "Electroclásica",
                     "4 cuerdas": "4 cuerdas", "5 cuerdas": "5 cuerdas", "6 cuerdas o más": "6 cuerdas o más",
                     "Acústico": "Bajos acústicos", "Fretless": "Fretless", "Escala corta": "Escala corta", "Combo": "Combos",
                     "Cabezal": "Cabezales", "Pantalla": "Gabinetes", "Para bajo": "Para bajo", "Para acústica": "Para acústica",
                     "De auriculares y portátil": "De audífonos y portátiles", "Para eléctrica": "Para eléctrica",
                     "Para clásica": "Para clásica", "Overdrive y distorsión": "Overdrive y distorsión",
                     "Modulación": "Modulación", "Compresor": "Compresor", "Wah y volumen": "Wah y volumen",
                     "Octavador y pitch": "Octavador y pitch", "Ecualizador": "Ecualizador", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintetizadores", "Afinador": "Afinador", "Multiefectos": "Multiefectos",
                     "Reverb": "Reverb", "Piano digital": "Pianos digitales", "Teclado portátil": "Teclados portátiles",
                     "Piano de escenario": "Pianos de escenario", "Controlador MIDI": "Controladores MIDI", "Piano acústico": "Pianos acústicos",
                     "Dinámico": "Dinámico", "Condensador": "Condensador", "Inalámbrico": "Inalámbrico",
                     "Para instrumento": "Para instrumento", "De cinta": "De listón", "Cuerdas": "Cuerdas",
                     "Púas": "Púas", "Correas": "Correas", "Cables": "Cables", "Afinadores": "Afinadores",
                     "Cejillas": "Capos", "Soportes": "Soportes", "Pastillas": "Pastillas", "Recambios": "Refacciones",
                     "Mantenimiento": "Mantenimiento"},
           "wait": "Llevamos {n} {days} siguiendo este modelo", "day": "día", "days": "días",
           "waitSub": "El veredicto será más confiable con unas semanas de historial.",
           "min": "Precio mínimo registrado", "minSub": "Nunca la hemos visto más barata.",
           "minBelow": " Un {p}% por debajo de su promedio de 30 días.",
           "good": "Buen momento: un {p}% por debajo de su precio promedio", "goodSub": "Promedio de los últimos 30 días: {avg}.",
           "bad": "Ahora está un {p}% más cara de lo normal",
           "badSub": "Si no tienes prisa, espera: su promedio de 30 días es {avg} y su mínimo, {min}.",
           "normal": "Precio normal", "normalSub": "En línea con su promedio de 30 días ({avg}). Mínimo registrado: {min}.",
           "today": "precio hoy", "lowest": "mínimo histórico ({d})", "highest": "máximo histórico", "avg": "promedio {n} días",
           "since": "Seguimos este modelo desde el {d}.", "noHist": "Aún no hay historial de precios.", "pvp": "Precio de lista", "bestLine": "Mejor precio",
           "alertOpen": "Avísame si baja de precio", "emailPh": "tu@correo.com", "emailLabel": "Tu correo",
           "targetPh": "Precio máx. (opcional)", "targetLabel": "Precio objetivo en pesos", "alertBtn": "Avisarme",
           "alertLegal": "Gratis y sin registro. Al dar clic en «Avisarme» aceptas el "
                         "<a href=\"/mx/legal.html#privacidad\">aviso de privacidad</a>: usaremos tu correo solo para este "
                         "aviso y puedes darte de baja con un clic.",
           "alertOk": "<b>¡Listo!</b> En unos minutos te llegará un correo a {email} para confirmar el aviso "
                      "(revisa también la carpeta de spam).",
           "alertErr": "No se pudo guardar el aviso. Revisa el correo e inténtalo de nuevo."},
    "mail": {"tagline": "guitarras al mejor precio",
             "footer": "guitle compara a diario los precios de las tiendas de instrumentos. Recibes este correo porque pediste un "
                       "aviso de precio en guitle.com. Responsable: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Privacidad", "confirmSubject": "Confirma tu aviso de precio de guitle",
             "confirmTitle": "Confirma tu aviso", "asked": "Pediste que te avisemos cuando el precio baje{target}:",
             "below": " de <b>{v}</b>", "confirmAsk": "Confirma que quieres recibir el aviso en esta dirección:",
             "confirmBtn": "Confirmar aviso",
             "notYou": "Si no fuiste tú, no hagas nada: los avisos sin confirmar se borran automáticamente a los 7 días.",
             "dropSubject": "Bajó de precio: {name} ahora en {price}", "dropTitle": "¡Bajó el precio!", "nowAt": "en {s} · antes {v}",
             "seeAll": "Ver precios en todas las tiendas",
             "check": "Los precios cambian a diario: revisa el precio en la tienda antes de comprar. ¿Ya no te interesa?",
             "stop": "Cancelar este aviso"},
}

# Autoridad en México: la Secretaría Anticorrupción y Buen Gobierno, que asumió en 2025 las funciones de protección de
# datos personales del extinto INAI (Ley Federal de Protección de Datos Personales en Posesión de los Particulares, 2025).
# Frase para un posible legal_replace: "o ante la autoridad mexicana de protección de datos personales (Secretaría
# Anticorrupción y Buen Gobierno)".
LEGAL_LANG = ("Aviso legal y privacidad", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Aviso legal y privacidad</h1>
<p class="muted">Última actualización: 28 de octubre de 2026. Esta es la versión para México; en caso de duda, prevalece la <a href="/legal.html">versión de España</a>.</p>

<h2 id="aviso">Aviso legal</h2>
<p>El titular de este sitio es <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), España
(número de identificación fiscal español, NIF: 17747339X), contacto:
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, sitio web: guitle.com. Actividad: comparador de precios de instrumentos musicales y publicidad de afiliación.
Alojamiento: GitHub Pages (GitHub, Inc.).</p>

<h2 id="condiciones">Condiciones de uso</h2>
<p>guitle es un comparador de precios y no vende nada. Mostramos los precios que las tiendas publican en sus sitios web y te enlazamos a ellas,
para que compres directamente en la tienda. La compra, el envío, la garantía y las devoluciones son responsabilidad de cada tienda.</p>
<ul>
<li><b>Precios orientativos.</b> Revisamos los precios con regularidad, pero pueden cambiar en cualquier momento. El precio válido es siempre el que muestra la tienda al hacer el pedido.</li>
<li><b>Sin garantía de exactitud.</b> Cuidamos que productos, precios y disponibilidad sean correctos, pero puede haber errores. Si encuentras uno, escríbenos.</li>
<li><b>Marcas e imágenes.</b> Las marcas, nombres de producto e imágenes pertenecen a sus respectivos titulares y se usan solo para identificar los productos.</li>
<li><b>Contenido de guitle.</b> El diseño, el logotipo, los textos y las recopilaciones de datos de guitle son de su titular. No se permite copiarlos de forma masiva ni usarlos con fines comerciales sin autorización.</li>
</ul>

<h2 id="afiliacion">Enlaces de afiliado</h2>
<p>Algunos enlaces a tiendas son de afiliado: si compras después de dar clic, la tienda puede pagarle a guitle una pequeña comisión. Para ti
el precio es el mismo. Las comisiones no influyen en el orden: las tiendas se ordenan siempre por precio, de menor a mayor.</p>

<h2 id="privacidad">Aviso de privacidad</h2>
<p>guitle no te pide datos personales para usar el sitio: no hay registro, ni boletín, ni herramientas de analítica o publicidad que te rastreen.
Solo contamos las visitas de forma anónima y, si pides un aviso de precio, guardamos tu correo para ese aviso. Este aviso de privacidad
se ofrece conforme a la Ley Federal de Protección de Datos Personales en Posesión de los Particulares.</p>
<ul>
<li><b>Avisos de precio.</b> Si pides que te avisemos cuando baje el precio de un producto, guardamos tu dirección de correo, el producto, su precio ese día
y, si lo indicas, tu precio objetivo. Los usamos solo para enviarte el correo de confirmación y los avisos de ese producto, nunca con fines
publicitarios, y no los compartimos con nadie. Base: tu consentimiento expreso, que das al pedir el aviso y confirmar tu correo. Los datos se guardan
en Google Cloud Firestore (Google Ireland Ltd., servidor en Madrid, España), y los correos salen de nuestro buzón hola@guitle.com (DonDominio, España),
por lo que tus datos se transfieren a España para este único fin. Si no confirmas el aviso, se borra a los 7 días; si lo confirmas, lo conservamos
hasta que te des de baja con el enlace que trae cada correo (el aviso se borra al momento) o nos pidas borrarlo.</li>
<li><b>Preferencias en tu navegador.</b> Los filtros y la vista elegida se guardan en el almacenamiento local de tu navegador (localStorage) y no se envían a ningún servidor.</li>
<li><b>Alojamiento.</b> El sitio se sirve desde GitHub Pages (GitHub, Inc.). Como cualquier servidor web, GitHub puede registrar la dirección IP de cada visita
por motivos técnicos y de seguridad.</li>
<li><b>Contador de visitas.</b> Cada página suma 1 a un contador anónimo: el día, la página vista, el sitio desde el que llegas (por ejemplo, google.com),
lo que escribes en el buscador del catálogo y, si das clic en una tienda, su nombre. Sin cookies, sin dirección IP, sin nada que te identifique. Los contadores
se guardan en Google Cloud Firestore (Google Ireland Ltd.), en un servidor de la Unión Europea (Madrid).</li>
<li><b>Sin otras peticiones a terceros.</b> Las tipografías, las gráficas y las fotos de los productos se sirven desde guitle.com.</li>
<li><b>Al ir a una tienda.</b> Cuando das clic en una tienda, sales de guitle y a partir de ahí se aplica el aviso de privacidad de esa tienda.</li>
</ul>
<p><b>Tus derechos (ARCO).</b> Puedes ejercer tus derechos de acceso, rectificación, cancelación y oposición, así como revocar tu consentimiento,
escribiendo a <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Si consideras que no se atendió tu solicitud, puedes acudir a la autoridad mexicana
de protección de datos personales (Secretaría Anticorrupción y Buen Gobierno) o a la Agencia Española de Protección de Datos. Responsable del tratamiento: el titular indicado en el aviso legal.</p>

<h2 id="cookies">Cookies</h2>
<p>guitle no usa cookies, ni propias ni de terceros; por eso no ves ningún aviso de cookies. Solo usamos el almacenamiento local del navegador
para recordar tus preferencias. Las tiendas a las que enlazamos pueden usar sus propias cookies en sus sitios.</p>
""")
