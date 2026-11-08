"""Guías de compra (guias/*.html): texto que explica cómo elegir, con las guitarras y precios reales de hoy del catálogo.

Los buscadores y sus asistentes citan páginas que explican algo ("qué guitarra eléctrica comprar para empezar"); las
fichas y listados solo tienen precios. Cada guía enlaza a los listados y fichas de guitle y lleva sus preguntas
frecuentes como datos estructurados (FAQPage). Se regeneran en cada lectura de España (pages.write_hubs).
"""
import html
import json
from datetime import date

from . import pages

esc = lambda v: html.escape(str(v or ""), quote=True)


def _pick(products, max_price, n, min_stores=3, guitar=True):
    """Las más comparadas (más tiendas) por debajo del precio, con foto."""
    ok = [p for p in products if p.get("th") and p.get("slug") and p["items"]
          and p["items"][0]["p"] <= max_price and len({i["s"] for i in p["items"]}) >= min_stores]
    ok.sort(key=lambda p: (-len({i["s"] for i in p["items"]}), p["items"][0]["p"]))
    from .thumbs import thumbs_ok
    good = thumbs_ok([p["th"] for p in ok[:n * 15]], guitar)
    out, seen, per_brand = [], set(), {}
    for p in ok[:n * 15]:  # un modelo una vez (sin repetir colores), dos por marca como mucho y con foto buena
        key = " ".join([w for w in p["name"].lower().replace("pacífica", "pacifica").split()
                        if w not in {"fender", "squier", "by", "esp/ltd", "esp", "ltd"}][:2])
        if key in seen or per_brand.get(p.get("brand"), 0) >= 2 or not good.get(p["th"]):
            continue
        seen.add(key)
        per_brand[p.get("brand")] = per_brand.get(p.get("brand"), 0) + 1
        out.append(p)
        if len(out) == n:
            break
    return out


def _grid(title, prods, names, more=None):
    if not prods:
        return ""
    tiles = "".join(pages._tile(p, names) for p in prods)
    link = f' <a class="navlink" href="{more[1]}">{esc(more[0])} →</a>' if more else ""
    return f'<section class="hub-sec"><h2>{esc(title)}{link}</h2><div class="grid">{tiles}</div></section>'


def _page(url, title, h1, desc, body, faqs):
    today = date.today().isoformat()
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc,
           "dateModified": today, "inLanguage": "es", "publisher": {"@type": "Organization", "name": "guitle",
                                                                     "url": pages.SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)
    page = pages._hub(url, title, h1, desc, [], {}, url)
    extra = ("<style>.guia{max-width:780px;line-height:1.65}.guia h2{font-size:1.2rem;margin:26px 0 6px}"
             ".guia p,.guia li{color:var(--text-secondary)}.guia strong{color:var(--text-primary)}"
             ".faq details{border-bottom:1px solid var(--border);padding:10px 0}.faq summary{cursor:pointer;font-weight:600}"
             ".faq p{color:var(--text-secondary);margin:8px 0 0}</style>\n"
             + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))
    page = page.replace("</head>", extra + "</head>", 1)
    page = page.replace("  <footer", f'{body}\n  <section class="hub-sec faq guia"><h2>Preguntas frecuentes</h2>{faq_html}</section>\n  <footer', 1)
    page = page.replace('<a class="navlink" href="/marcas.html">Marcas</a>',
                        '<a class="navlink" href="/guias/">Guías</a> <a class="navlink" href="/marcas.html">Marcas</a>', 1)
    return page


def write(catalogs, names):
    """Escribe las guías; devuelve sus URL (para el sitemap)."""
    elec = catalogs.get("electrica", {}).get("products", [])
    acu = catalogs.get("acustica", {}).get("products", [])
    cla = catalogs.get("clasica", {}).get("products", [])
    pack = catalogs.get("pack", {}).get("products", [])
    n_shops = len(names)
    urls = []

    # 1. Primera guitarra eléctrica
    url = "guias/primera-guitarra-electrica.html"
    cheap = _pick(elec, 300, 12)
    body = f"""<section class="hub-sec guia">
<h2>Qué forma elegir</h2>
<p>La forma cambia la comodidad y el sonido más que la marca. Las cuatro más habituales para empezar:</p>
<ul>
<li><strong>Tipo Stratocaster (ST):</strong> la más versátil y cómoda, con el cuerpo contorneado. Sirve para pop, rock, blues y funk. Si dudas, empieza por aquí.</li>
<li><strong>Tipo Telecaster (T):</strong> más sencilla, con un sonido brillante y directo. Muy usada en rock, country e indie.</li>
<li><strong>Single cut (tipo Les Paul):</strong> sonido más grueso y con más sustain, ideal para rock y blues. Suele pesar más.</li>
<li><strong>Superstrat o moderna:</strong> mástil fino, más trastes accesibles y pastillas potentes, pensada para rock duro y metal.</li>
</ul>
<h2>Pastillas: simples o dobles</h2>
<p>Las <strong>pastillas simples</strong> (single coil) suenan claras y brillantes; las <strong>dobles</strong> (humbucker) suenan más gruesas y tienen menos ruido con distorsión. Una configuración <strong>HSS</strong> (dos simples y una doble) combina las dos y es la más versátil para quien aún no sabe qué estilo va a tocar.</p>
<h2>Cuánto gastar</h2>
<p>Entre <strong>150 y 300 €</strong> hay guitarras que suenan bien y aguantan años: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone o Harley Benton, entre otras. Por debajo de 150 € conviene mirar bien el acabado de los trastes; por encima de 500 €, la diferencia está en materiales, pastillas y acabados más que en lo fácil que sea tocarla.</p>
<p>Recuerda que una eléctrica necesita <strong>amplificador</strong> (o unos auriculares con un pequeño ampli o un multiefectos). Si empiezas de cero, un <a href="/packs.html">pack de guitarra con ampli</a> suele salir más barato que comprarlo por separado.</p>
<h2>Compara antes de comprar</h2>
<p>El mismo modelo puede variar decenas de euros entre tiendas. En guitle comparamos el precio en {n_shops} tiendas cada día y guardamos su historial, así que puedes ver si el precio de hoy es bueno o si suele estar más bajo.</p>
</section>
{_grid("Las eléctricas de menos de 300 € que más tiendas venden (precios de hoy)", cheap, names, ("Ver todas las eléctricas", "/catalogo.html"))}"""
    faqs = [("¿Qué guitarra eléctrica comprar para empezar?",
             "Una tipo Stratocaster con pastillas HSS entre 150 y 300 € es la opción más versátil: Yamaha Pacifica, Squier o "
             "Ibanez GIO son modelos muy habituales para empezar."),
            ("¿Cuánto cuesta una buena guitarra eléctrica para principiantes?",
             "Entre 150 y 300 € hay guitarras de calidad suficiente para aprender y seguir tocando años; el precio cambia según "
             "la tienda, por eso conviene compararlo."),
            ("¿Necesito un amplificador para tocar la guitarra eléctrica?",
             "Sí: sin amplificador apenas suena. Para empezar basta un ampli pequeño de práctica, un ampli de auriculares o un "
             "multiefectos con salida de auriculares."),
            ("¿Es mejor comprar un pack de guitarra eléctrica?",
             "Si empiezas de cero, un pack con guitarra, ampli, funda y cable suele salir más barato que comprarlo por separado; "
             "si ya tienes ampli, compensa más elegir solo la guitarra.")]
    pages._write(pages.ROOT / url, _page(url, "Cómo elegir tu primera guitarra eléctrica",
                                         "Cómo elegir tu primera guitarra eléctrica",
                                         "Qué forma, qué pastillas y cuánto gastar en tu primera guitarra eléctrica, con las más "
                                         "vendidas por menos de 300 € y su precio de hoy en cada tienda.", body, faqs))
    urls.append(url)

    # 2. Clásica o acústica
    url = "guias/guitarra-clasica-o-acustica.html"
    body = f"""<section class="hub-sec guia">
<h2>La diferencia está en las cuerdas</h2>
<p>La <strong>guitarra clásica</strong> lleva cuerdas de <strong>nylon</strong>: son blandas, no hacen daño en los dedos y tienen un sonido cálido. El mástil es más ancho. La <strong>acústica</strong> lleva cuerdas de <strong>acero</strong>: suena más brillante y potente, pero al principio cuesta más pisar las cuerdas.</p>
<h2>Cuál elegir según lo que quieras tocar</h2>
<ul>
<li><strong>Clásica:</strong> música clásica, flamenco, bossa nova, canción española y, en general, para niños y para aprender con un profesor de conservatorio.</li>
<li><strong>Acústica:</strong> pop, rock, folk, country y acompañar canciones cantando, con o sin púa.</li>
</ul>
<p>Si es para un niño o para alguien que nunca ha tocado, la clásica es la más cómoda para empezar. Si te gusta el pop o el rock, empieza directamente con una acústica: tus dedos se acostumbran en pocas semanas.</p>
<h2>Tamaño y electrificación</h2>
<p>Las clásicas tienen tallas: <strong>4/4</strong> para adultos y adolescentes, <strong>3/4</strong> para niños de unos 8 a 11 años y <strong>1/2</strong> para los más pequeños. Una guitarra <strong>electroacústica o electroclásica</strong> lleva un previo para conectarla a un amplificador: no cambia cómo suena sin enchufar, pero sube el precio.</p>
<h2>Cuánto gastar</h2>
<p>Para empezar hay buenas clásicas desde unos <strong>100–200 €</strong> (Alhambra, Admira, Yamaha…) y acústicas desde unos <strong>150–300 €</strong> (Yamaha, Fender, Cort, Sigma…). Con tapa maciza suenan mejor y mejoran con los años. En guitle comparamos su precio en {n_shops} tiendas cada día.</p>
</section>
{_grid("Clásicas de menos de 200 € que más tiendas venden (precios de hoy)", _pick(cla, 200, 8), names, ("Ver todas las clásicas", "/clasicas.html"))}
{_grid("Acústicas de menos de 300 € que más tiendas venden (precios de hoy)", _pick(acu, 300, 8), names, ("Ver todas las acústicas", "/acusticas.html"))}"""
    faqs = [("¿Qué es mejor para empezar, guitarra clásica o acústica?",
             "La clásica es más cómoda para empezar por sus cuerdas de nylon; la acústica es mejor si quieres tocar pop, rock o "
             "folk, aunque al principio cueste un poco más pisar las cuerdas de acero."),
            ("¿Qué diferencia hay entre guitarra clásica y española?",
             "Ninguna: en España se llama guitarra española a la clásica, con cuerdas de nylon."),
            ("¿Qué tamaño de guitarra necesita un niño?",
             "Como orientación, una 1/2 hasta unos 7-8 años, una 3/4 de unos 8 a 11 años y una 4/4 a partir de unos 12 años."),
            ("¿Se pueden poner cuerdas de acero en una guitarra clásica?",
             "No: la clásica no está hecha para la tensión de las cuerdas de acero y se puede dañar el mástil o el puente.")]
    pages._write(pages.ROOT / url, _page(url, "Guitarra clásica o acústica: cuál elegir",
                                         "Guitarra clásica o acústica: cuál elegir",
                                         "Diferencias entre guitarra clásica y acústica, cuál elegir para empezar, tallas para niños "
                                         "y modelos con su precio de hoy en cada tienda.", body, faqs))
    urls.append(url)

    bajo = catalogs.get("bajo", {}).get("products", [])
    ampli = catalogs.get("ampli", {}).get("products", [])

    # 3. Primer bajo
    url = "guias/primer-bajo-electrico.html"
    body = f"""<section class="hub-sec guia">
<h2>Cuatro o cinco cuerdas</h2>
<p>Para empezar, un bajo de <strong>4 cuerdas</strong>: es el estándar en casi todos los estilos y en él están casi todos los métodos y canciones. El de <strong>5 cuerdas</strong> añade una cuerda grave (Si) muy usada en metal, gospel o funk moderno, pero tiene el mástil más ancho.</p>
<h2>Precision o Jazz Bass</h2>
<ul>
<li><strong>Tipo Precision (P):</strong> una pastilla partida, sonido grueso y redondo. Sencillo y muy agradecido: suena bien en casi todo.</li>
<li><strong>Tipo Jazz Bass (J):</strong> dos pastillas y mástil más fino en la cejuela, más fácil para manos pequeñas, con un sonido más definido.</li>
<li><strong>PJ:</strong> mezcla las dos, muy versátil para quien aún no sabe qué va a tocar.</li>
</ul>
<h2>Escala corta</h2>
<p>Los bajos de <strong>escala corta</strong> (unos 30") tienen los trastes más juntos: son más cómodos para niños, para manos pequeñas o para guitarristas que se pasan al bajo.</p>
<h2>Cuánto gastar</h2>
<p>Entre <strong>200 y 400 €</strong> hay bajos muy buenos para empezar: Squier, Yamaha, Ibanez, Cort o Harley Benton, entre otros. Y como la eléctrica, el bajo necesita su amplificador de bajo: uno de guitarra no vale, porque las notas graves pueden dañar su altavoz. En guitle comparamos su precio en {n_shops} tiendas cada día.</p>
</section>
{_grid("Bajos de menos de 400 € que más tiendas venden (precios de hoy)", _pick(bajo, 400, 12), names, ("Ver todos los bajos", "/bajos.html"))}"""
    faqs = [("¿Qué bajo comprar para empezar?",
             "Un bajo de 4 cuerdas tipo Precision, Jazz Bass o PJ entre 200 y 400 €: Squier, Yamaha o Ibanez son marcas muy habituales para empezar."),
            ("¿Es mejor un bajo de 4 o de 5 cuerdas para empezar?",
             "De 4: es el estándar, tiene el mástil más estrecho y casi todos los métodos y canciones están escritos para él."),
            ("¿Puedo conectar un bajo a un amplificador de guitarra?",
             "No es recomendable: las notas graves del bajo pueden dañar el altavoz de un ampli de guitarra. Necesitas un ampli de bajo."),
            ("¿Qué es un bajo de escala corta?",
             "Un bajo con el mástil más corto (unos 30 pulgadas) y los trastes más juntos: más cómodo para niños y manos pequeñas.")]
    pages._write(pages.ROOT / url, _page(url, "Cómo elegir tu primer bajo eléctrico", "Cómo elegir tu primer bajo eléctrico",
                                         "4 o 5 cuerdas, Precision o Jazz Bass, escala corta y cuánto gastar en tu primer bajo, con los "
                                         "más vendidos por menos de 400 € y su precio de hoy.", body, faqs))
    urls.append(url)

    # 4. Primer amplificador
    url = "guias/primer-amplificador-guitarra.html"
    body = f"""<section class="hub-sec guia">
<h2>Para casa basta con poco</h2>
<p>Para practicar en casa, un ampli de <strong>10 a 30 vatios</strong> sobra: un ampli de 100 vatios a volumen bajo suena peor que uno pequeño bien ajustado. Lo importante es que suene bien a volumen de salón y tenga <strong>salida de auriculares</strong> para tocar sin molestar.</p>
<h2>Modelador o de válvulas</h2>
<ul>
<li><strong>Modelador (digital):</strong> imita muchos amplis y trae efectos (reverb, delay, chorus…) incluidos. Para empezar es lo más práctico: Boss Katana, Fender Mustang, Line 6, Positive Grid o Blackstar ID son muy habituales.</li>
<li><strong>De válvulas:</strong> el sonido clásico de rock y blues, más caro y pensado para tocar con volumen. Mejor cuando ya sabes qué sonido buscas.</li>
<li><strong>De auriculares o portátil:</strong> pequeños amplis que se enchufan a la guitarra y a los auriculares, ideales para practicar en cualquier sitio.</li>
</ul>
<h2>Cuánto gastar</h2>
<p>Entre <strong>100 y 300 €</strong> hay amplis de práctica muy completos. Si vas a tocar con batería o en un local, busca a partir de 30–50 vatios. En guitle comparamos el precio de cada ampli en {n_shops} tiendas cada día.</p>
</section>
{_grid("Amplis de menos de 300 € que más tiendas venden (precios de hoy)", _pick(ampli, 300, 12, guitar=False), names, ("Ver todos los amplis", "/amplificadores.html"))}"""
    faqs = [("¿Qué amplificador de guitarra comprar para casa?",
             "Un ampli de 10 a 30 vatios con salida de auriculares; un modelador digital (Boss Katana, Fender Mustang, Line 6…) es lo más práctico para empezar."),
            ("¿Cuántos vatios necesita un ampli de guitarra?",
             "Para casa, de 10 a 30 vatios. Para tocar con batería, a partir de 30–50 vatios en transistor o 15–20 en válvulas."),
            ("¿Es mejor un ampli de válvulas o digital para empezar?",
             "Digital (modelador): es más barato, trae efectos y suena bien a volumen bajo. El de válvulas compensa cuando ya sabes qué sonido buscas.")]
    pages._write(pages.ROOT / url, _page(url, "Qué amplificador de guitarra comprar para empezar",
                                         "Qué amplificador de guitarra comprar para empezar",
                                         "Cuántos vatios, modelador o válvulas y cuánto gastar en tu primer ampli de guitarra, con los más "
                                         "vendidos por menos de 300 € y su precio de hoy.", body, faqs))
    urls.append(url)

    # 5. Packs
    url = "guias/packs-de-guitarra.html"
    body = f"""<section class="hub-sec guia">
<h2>Qué trae un pack</h2>
<p>Un pack de guitarra eléctrica suele traer <strong>guitarra, amplificador pequeño, funda, cable, correa, púas y afinador</strong>; uno de acústica o clásica, la guitarra con funda y accesorios. Todo lo necesario para empezar el mismo día.</p>
<h2>Cuándo compensa</h2>
<ul>
<li><strong>Sí compensa</strong> si empiezas de cero: sale más barato que comprar cada cosa por separado y no hay que elegir nada más.</li>
<li><strong>No compensa</strong> si ya tienes ampli o si quieres una guitarra concreta: el ampli de los packs es básico y lo cambiarás pronto si sigues tocando.</li>
</ul>
<p>Fíjate sobre todo en la guitarra del pack: los de Yamaha, Squier, Ibanez o Epiphone llevan la misma guitarra que se vende suelta, y eso es lo que más dura. En guitle comparamos el precio de cada pack en {n_shops} tiendas cada día.</p>
</section>
{_grid("Packs de menos de 400 € que más tiendas venden (precios de hoy)", _pick(pack, 400, 12, 2, guitar=False), names, ("Ver todos los packs", "/packs.html"))}"""
    faqs = [("¿Merece la pena un pack de guitarra para empezar?",
             "Sí si empiezas de cero: guitarra, ampli y accesorios salen más baratos que por separado. Si ya tienes ampli, compensa más comprar solo la guitarra."),
            ("¿Qué trae un pack de guitarra eléctrica?",
             "Normalmente guitarra, amplificador pequeño, funda, cable, correa, púas y afinador.")]
    pages._write(pages.ROOT / url, _page(url, "Packs de guitarra: cuándo compensan", "Packs de guitarra: cuándo compensan",
                                         "Qué trae un pack de guitarra, cuándo compensa frente a comprar por separado y los packs más "
                                         "vendidos con su precio de hoy.", body, faqs))
    urls.append(url)

    # Índice de guías
    url = "guias/index.html"
    items = [("guias/primera-guitarra-electrica.html", "Cómo elegir tu primera guitarra eléctrica",
              "Forma, pastillas, presupuesto y ampli, con las eléctricas más vendidas por menos de 300 €."),
             ("guias/guitarra-clasica-o-acustica.html", "Guitarra clásica o acústica: cuál elegir",
              "Nylon o acero, qué tocar con cada una, tallas para niños y modelos para empezar."),
             ("guias/primer-bajo-electrico.html", "Cómo elegir tu primer bajo eléctrico",
              "4 o 5 cuerdas, Precision o Jazz Bass, escala corta y los más vendidos por menos de 400 €."),
             ("guias/primer-amplificador-guitarra.html", "Qué amplificador de guitarra comprar para empezar",
              "Vatios, modelador o válvulas y los amplis de práctica más vendidos."),
             ("guias/packs-de-guitarra.html", "Packs de guitarra: cuándo compensan",
              "Qué traen, cuándo salen a cuenta y los packs más vendidos."),
             ("curso/", "Curso gratis: tu primera guitarra",
              "Cinco lecciones desde cero: postura, acordes, ritmo, escalas y dos canciones, con metrónomo.")]
    lis = "".join(f'<li><a href="/{u}"><strong>{esc(t)}</strong></a><br>{esc(d)}</li>' for u, t, d in items)
    body = f'<section class="hub-sec guia"><ul>{lis}</ul></section>'
    page = _page("guias/", "Guías para comprar guitarra", "Guías para comprar guitarra",
                 "Guías para elegir guitarra eléctrica, clásica o acústica, con modelos y precios reales de hoy.", body, [])
    page = page.replace('\n  <section class="hub-sec faq guia"><h2>Preguntas frecuentes</h2></section>', "")
    pages._write(pages.ROOT / url, page)
    return ["guias/"] + urls
