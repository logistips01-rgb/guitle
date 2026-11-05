"""Guías en español de México/Latinoamérica (guitle.com/mx/guias/)."""
MORE, FAQ, GUIDES_WORD = "Ver todo", "Preguntas frecuentes", "Guías"
INDEX_TITLE = "Guías para comprar guitarra"
INDEX_DESC = "Guías para elegir guitarra eléctrica, clásica o acústica, bajo y amplificador, con modelos y precios reales de hoy."
COURSE_URL, COURSE_TITLE = "curso/", "Curso gratis: tu primera guitarra"
COURSE_DESC = "Cinco lecciones desde cero: postura, acordes, ritmo, escalas y dos canciones, con metrónomo."

GUIDES = [
    {"slug": "primera-guitarra-electrica", "title": "Cómo elegir tu primera guitarra eléctrica",
     "desc": "Qué forma, qué pastillas y cuánto gastar en tu primera guitarra eléctrica, con las más vendidas por menos de {p300} y su precio de hoy.",
     "body": """<section class="hub-sec guia">
<h2>Qué forma elegir</h2>
<ul>
<li><strong>Tipo Stratocaster (ST):</strong> la más versátil y cómoda, para pop, rock, blues y funk. Si tienes dudas, empieza por aquí.</li>
<li><strong>Tipo Telecaster (T):</strong> más sencilla, con un sonido brillante y directo, muy usada en rock y country.</li>
<li><strong>Single cut (tipo Les Paul):</strong> sonido más grueso y con más sustain, ideal para rock y blues. Suele pesar más.</li>
<li><strong>Superstrat:</strong> mástil delgado y pastillas potentes, pensada para rock pesado y metal.</li>
</ul>
<h2>Pastillas: sencillas o dobles</h2>
<p>Las <strong>pastillas sencillas</strong> (single coil) suenan claras y brillantes; las <strong>dobles</strong> (humbucker) suenan más gruesas y hacen menos ruido con distorsión. Una configuración <strong>HSS</strong> combina las dos y es la más versátil para quien empieza.</p>
<h2>Cuánto gastar</h2>
<p>Entre <strong>{p150} y {p300}</strong> hay guitarras que suenan bien y duran años: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone o Harley Benton, entre otras. Una eléctrica necesita <strong>amplificador</strong> (o un pequeño ampli de audífonos); si empiezas desde cero, un paquete suele salir más barato.</p>
<p>El mismo modelo puede variar bastante de precio entre tiendas. guitle compara el precio todos los días en {shops} tiendas y guarda el historial de precios.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Eléctricas de menos de {p300} que más tiendas venden (precios de hoy)")],
     "faqs": [("¿Qué guitarra eléctrica comprar para empezar?", "Una tipo Stratocaster con pastillas HSS entre {p150} y {p300}: Yamaha Pacifica, Squier e Ibanez GIO son primeras guitarras muy comunes."),
              ("¿Necesito un amplificador para tocar la guitarra eléctrica?", "Sí: sin amplificador casi no se escucha. Para empezar basta un ampli pequeño de práctica o un ampli de audífonos."),
              ("¿Conviene comprar un paquete de guitarra para principiantes?", "Si empiezas desde cero, sí: guitarra, ampli y accesorios juntos salen más baratos que por separado.")]},
    {"slug": "guitarra-clasica-o-acustica", "title": "Guitarra clásica o acústica: cuál elegir",
     "desc": "Diferencias entre guitarra clásica y acústica, cuál elegir para empezar, tamaños para niños y modelos con su precio de hoy.",
     "body": """<section class="hub-sec guia">
<h2>La diferencia está en las cuerdas</h2>
<p>La <strong>guitarra clásica</strong> lleva cuerdas de <strong>nylon</strong>: son suaves para los dedos, tienen un sonido cálido y el mástil es más ancho. La <strong>acústica</strong> lleva cuerdas de <strong>acero</strong>: suena más brillante y fuerte, pero al principio cuesta más pisar las cuerdas.</p>
<ul>
<li><strong>Clásica:</strong> música clásica, flamenco, bossa nova, boleros y, en general, para niños o para aprender con un maestro.</li>
<li><strong>Acústica:</strong> pop, rock, folk y acompañar canciones cantando.</li>
</ul>
<h2>Tamaños</h2>
<p>Las clásicas vienen en <strong>4/4</strong> para adultos, <strong>3/4</strong> para niños de unos 8 a 11 años y <strong>1/2</strong> para los más pequeños. Una guitarra <strong>electroacústica</strong> lleva un preamplificador para conectarla a un amplificador.</p>
<h2>Cuánto gastar</h2>
<p>Hay buenas clásicas desde unos <strong>{p100}–{p200}</strong> y acústicas desde unos <strong>{p150}–{p300}</strong>. Con tapa sólida suenan mejor y mejoran con los años. guitle compara su precio todos los días en {shops} tiendas.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Clásicas de menos de {p200} que más tiendas venden (precios de hoy)"),
               ("acustica", 300, 8, 3, True, "Acústicas de menos de {p300} que más tiendas venden (precios de hoy)")],
     "faqs": [("¿Qué es mejor para empezar, guitarra clásica o acústica?", "La clásica es más cómoda por sus cuerdas de nylon; la acústica es mejor si quieres tocar pop, rock o folk."),
              ("¿Qué tamaño de guitarra necesita un niño?", "Como referencia, 1/2 hasta unos 7-8 años, 3/4 de 8 a 11 años y 4/4 a partir de los 12."),
              ("¿Se le pueden poner cuerdas de acero a una guitarra clásica?", "No: la clásica no está hecha para esa tensión y se pueden dañar el mástil o el puente.")]},
    {"slug": "primer-bajo", "title": "Cómo elegir tu primer bajo eléctrico",
     "desc": "4 o 5 cuerdas, Precision o Jazz Bass y cuánto gastar en tu primer bajo, con los más vendidos por menos de {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 o 5 cuerdas</h2>
<p>Empieza con un bajo de <strong>4 cuerdas</strong>: es el estándar en casi todos los estilos. El de <strong>5 cuerdas</strong> añade una cuerda grave, muy usada en metal y funk moderno, pero tiene el mástil más ancho.</p>
<ul>
<li><strong>Tipo Precision (P):</strong> sonido redondo y grueso, sencillo y efectivo.</li>
<li><strong>Tipo Jazz Bass (J):</strong> dos pastillas y mástil más delgado, con un sonido más definido.</li>
<li><strong>Escala corta:</strong> mástil más corto, más cómodo para manos pequeñas.</li>
</ul>
<p>Entre <strong>{p200} y {p400}</strong> hay bajos muy buenos para empezar. El bajo necesita un amplificador de bajo: las notas graves pueden dañar un ampli de guitarra.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Bajos de menos de {p400} que más tiendas venden (precios de hoy)")],
     "faqs": [("¿Qué bajo comprar para empezar?", "Un bajo de 4 cuerdas tipo Precision, Jazz Bass o PJ entre {p200} y {p400}."),
              ("¿Puedo conectar un bajo a un amplificador de guitarra?", "No es recomendable: las notas graves pueden dañar la bocina. Necesitas un ampli de bajo.")]},
    {"slug": "primer-amplificador", "title": "Qué amplificador de guitarra comprar para empezar",
     "desc": "Cuántos watts, modelador o bulbos y cuánto gastar en tu primer amplificador, con los más vendidos por menos de {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Para la casa basta con poco</h2>
<p>Para practicar en casa, un ampli de <strong>10 a 30 watts</strong> es más que suficiente; lo importante es que suene bien a volumen bajo y tenga <strong>salida para audífonos</strong>.</p>
<ul>
<li><strong>Modelador (digital):</strong> imita muchos amplis y trae efectos integrados: lo más práctico para empezar (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>De bulbos:</strong> el sonido clásico del rock y el blues, más caro y pensado para tocar a volumen alto.</li>
</ul>
<p>Entre <strong>{p100} y {p300}</strong> hay amplis de práctica muy completos.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplis de menos de {p300} que más tiendas venden (precios de hoy)")],
     "faqs": [("¿Qué amplificador de guitarra comprar para la casa?", "Uno de 10 a 30 watts con salida para audífonos; un modelador digital es lo más práctico para empezar.")]},
    {"slug": "paquetes-de-guitarra", "title": "Paquetes de guitarra: cuándo conviene comprarlos",
     "desc": "Qué trae un paquete de guitarra, cuándo conviene frente a comprar por separado y los paquetes más vendidos con su precio de hoy.",
     "body": """<section class="hub-sec guia">
<h2>Qué trae un paquete</h2>
<p>Un paquete de guitarra eléctrica suele traer <strong>guitarra, amplificador pequeño, funda, cable, correa, púas y afinador</strong>. <strong>Conviene</strong> si empiezas desde cero; <strong>no tanto</strong> si ya tienes ampli o quieres una guitarra en particular. Fíjate sobre todo en la guitarra: es lo que más dura.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Paquetes de menos de {p400} que más tiendas venden (precios de hoy)")],
     "faqs": [("¿Conviene un paquete de guitarra para empezar?", "Sí si empiezas desde cero: sale más barato que comprar todo por separado.")]},
]
