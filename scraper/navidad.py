"""Regalos de Navidad para músicos (guitle.com/navidad/, /fr/noel/, /it/natale/, /pt/natal/, /uk/christmas/): una página
por país con ideas de regalo por presupuesto, sacadas cada día del catálogo (productos con foto, en stock y comparados
en dos o más tiendas, primero los que más se ahorran) y, si el país tiene sección de discos, vinilos para regalar.

Se genera con la web de cada país (intl.write_site) y, la de España, con la de España (pages.py); sus enlaces llevan a
las fichas de guitle, donde se comparan las tiendas.
"""
import html
import json

from . import pages

# Presupuestos y qué categorías entran en cada uno (por orden de preferencia)
BUCKETS = [(0, 25, ("varios", "pedal", "micro")),
           (25, 75, ("pedal", "micro", "varios", "ampli", "clasica")),
           (75, 200, ("ampli", "pedal", "clasica", "acustica", "micro", "teclado", "electrica")),
           (200, 600, ("electrica", "acustica", "ampli", "bajo", "teclado", "pack"))]
PER_BUCKET = 8
# Lo que da comisión va primero: tiendas afiliadas (Cultura, en Awin) y marcas que seguro están en Amazon (cada regalo
# lleva su botón de Amazon con el código del país).
AFFILIATE_STORES = {"cultura"}
AMAZON_BRANDS = {"fender", "squier", "boss", "yamaha", "ibanez", "epiphone", "gibson", "d'addario", "daddario", "elixir",
                 "ernie ball", "dunlop", "jim dunlop", "shure", "audio technica", "audio-technica", "rode", "korg",
                 "marshall", "orange", "vox", "blackstar", "line 6", "zoom", "tc electronic", "electro-harmonix",
                 "mxr", "behringer", "harley benton", "snark", "planet waves", "martinez", "cort", "takamine",
                 "ortega", "alhambra", "admira", "kyser", "g7th", "fishman", "nux", "mooer", "joyo", "donner", "roland",
                 "casio", "m-audio", "akg", "sennheiser", "samson", "positive grid", "valeton", "hotone", "jbl"}
AMAZON = {"es": "https://www.amazon.es/s?k={q}&tag=guitle-21", "pt": "https://www.amazon.es/s?k={q}&tag=guitle-21",
          "fr": "https://www.amazon.fr/s?k={q}&tag=guitle00-21", "it": "https://www.amazon.it/s?k={q}&tag=guitle0e-21",
          "uk": "https://www.amazon.co.uk/s?k={q}&tag=guitle08-21", "ie": "https://www.amazon.co.uk/s?k={q}&tag=guitle08-21"}

TXT = {
    "es": {"sel": "Nuestra selección en Amazon", "amz": "Ver en Amazon", "dir": "navidad", "title": "Regalos de Navidad para músicos",
           "desc": "Ideas de regalo para guitarristas y músicos por presupuesto, con el precio más bajo de hoy en cada tienda: accesorios, pedales, amplis, guitarras y vinilos.",
           "intro": "¿No sabes qué regalar a un guitarrista? Aquí tienes ideas por presupuesto, con el mejor precio de hoy comparado entre tiendas. Los precios se actualizan cada día.",
           "b": ["Menos de 25 €", "De 25 a 75 €", "De 75 a 200 €", "Más de 200 €"],
           "bd": ["Detalles que todo músico usa: correas, afinadores, cuerdas, cejillas…", "Pedales, micros y accesorios que se notan.",
                  "Amplis, pedales de calidad y guitarras para empezar.", "Para el regalo gordo: guitarras, amplis y bajos."],
           "discs": "Vinilos y discos para regalar", "discs_more": "Todos los discos", "tips_h": "Consejos para acertar",
           "tips": ["Si no sabes qué guitarra toca, los accesorios (afinador, correa, cejilla, púas) siempre se usan.",
                    "Mira la fecha de entrega de cada tienda: en diciembre los envíos tardan más.",
                    "Antes de comprar, compara: la misma guitarra puede costar bastante menos en otra tienda.",
                    "Para los que empiezan, un pack (guitarra + ampli + accesorios) suele salir más barato que por separado."]},
    "fr": {"sel": "Notre sélection sur Amazon", "amz": "Voir sur Amazon", "dir": "noel", "title": "Cadeaux de Noël pour musiciens",
           "desc": "Idées cadeaux pour guitaristes et musiciens par budget, au prix le plus bas du jour : accessoires, pédales, amplis, guitares et vinyles.",
           "intro": "Vous ne savez pas quoi offrir à un guitariste ? Voici des idées par budget, au meilleur prix du jour comparé entre magasins. Les prix sont mis à jour chaque jour.",
           "b": ["Moins de 25 €", "De 25 à 75 €", "De 75 à 200 €", "Plus de 200 €"],
           "bd": ["Les petits cadeaux qui servent toujours : sangles, accordeurs, cordes, capodastres…", "Pédales, micros et accessoires qui changent tout.",
                  "Amplis, belles pédales et guitares pour débuter.", "Pour le gros cadeau : guitares, amplis et basses."],
           "discs": "Vinyles et disques à offrir", "discs_more": "Tous les disques", "tips_h": "Nos conseils",
           "tips": ["Si vous ne savez pas quelle guitare il joue, les accessoires (accordeur, sangle, capodastre, médiators) servent toujours.",
                    "Vérifiez le délai de livraison de chaque magasin : en décembre, les envois sont plus longs.",
                    "Comparez avant d'acheter : la même guitare peut coûter bien moins cher ailleurs.",
                    "Pour un débutant, un pack (guitare + ampli + accessoires) revient souvent moins cher."]},
    "it": {"sel": "La nostra selezione su Amazon", "amz": "Vedi su Amazon", "dir": "natale", "title": "Regali di Natale per musicisti",
           "desc": "Idee regalo per chitarristi e musicisti per budget, al prezzo più basso di oggi: accessori, pedali, amplificatori, chitarre e vinili.",
           "intro": "Non sai cosa regalare a un chitarrista? Ecco idee per budget, al miglior prezzo di oggi confrontato tra negozi. I prezzi si aggiornano ogni giorno.",
           "b": ["Meno di 25 €", "Da 25 a 75 €", "Da 75 a 200 €", "Più di 200 €"],
           "bd": ["Piccoli regali sempre utili: tracolle, accordatori, corde, capotasti…", "Pedali, microfoni e accessori che fanno la differenza.",
                  "Amplificatori, pedali di qualità e chitarre per iniziare.", "Per il regalo importante: chitarre, amplificatori e bassi."],
           "discs": "Vinili e dischi da regalare", "discs_more": "Tutti i dischi", "tips_h": "I nostri consigli",
           "tips": ["Se non sai che chitarra suona, gli accessori (accordatore, tracolla, capotasto, plettri) servono sempre.",
                    "Controlla i tempi di consegna di ogni negozio: a dicembre le spedizioni sono più lente.",
                    "Confronta prima di comprare: la stessa chitarra può costare molto meno in un altro negozio.",
                    "Per chi inizia, un pack (chitarra + ampli + accessori) di solito costa meno."]},
    "pt": {"sel": "A nossa seleção na Amazon", "amz": "Ver na Amazon", "dir": "natal", "title": "Prendas de Natal para músicos",
           "desc": "Ideias de prendas para guitarristas e músicos por orçamento, ao preço mais baixo de hoje: acessórios, pedais, amplificadores, guitarras e vinis.",
           "intro": "Não sabe o que oferecer a um guitarrista? Aqui tem ideias por orçamento, ao melhor preço de hoje comparado entre lojas. Os preços são atualizados todos os dias.",
           "b": ["Menos de 25 €", "De 25 a 75 €", "De 75 a 200 €", "Mais de 200 €"],
           "bd": ["Pequenas prendas que se usam sempre: correias, afinadores, cordas, capotrastes…", "Pedais, microfones e acessórios que fazem a diferença.",
                  "Amplificadores, bons pedais e guitarras para começar.", "Para a grande prenda: guitarras, amplificadores e baixos."],
           "discs": "Vinis e discos para oferecer", "discs_more": "Todos os discos", "tips_h": "Os nossos conselhos",
           "tips": ["Se não sabe que guitarra toca, os acessórios (afinador, correia, capotraste, palhetas) usam-se sempre.",
                    "Veja o prazo de entrega de cada loja: em dezembro os envios demoram mais.",
                    "Compare antes de comprar: a mesma guitarra pode custar bastante menos noutra loja.",
                    "Para quem começa, um pack (guitarra + amplificador + acessórios) costuma sair mais barato."]},
    "en": {"sel": "Our Amazon picks", "amz": "View on Amazon", "dir": "christmas", "title": "Christmas gifts for musicians",
           "desc": "Gift ideas for guitarists and musicians by budget, at today's lowest price: accessories, pedals, amps, guitars and vinyl.",
           "intro": "Not sure what to get a guitarist? Here are ideas by budget, at today's best price compared across shops. Prices update every day.",
           "b": ["Under £25", "£25 to £75", "£75 to £200", "Over £200"],
           "bd": ["Stocking fillers every player uses: straps, tuners, strings, capos…", "Pedals, mics and accessories that make a difference.",
                  "Amps, great pedals and starter guitars.", "The big present: guitars, amps and basses."],
           "discs": "Vinyl and records to give", "discs_more": "All records", "tips_h": "Gift tips",
           "tips": ["If you don't know what guitar they play, accessories (tuner, strap, capo, picks) always get used.",
                    "Check each shop's delivery times: deliveries take longer in December.",
                    "Compare before you buy: the same guitar can cost a lot less elsewhere.",
                    "For beginners, a bundle (guitar + amp + accessories) usually works out cheaper."]},
}
# Países con página (y su idioma)
COUNTRIES = {"fr": "fr", "it": "it", "pt": "pt", "uk": "en", "ie": "en"}


def _pick(cats, lo, hi, kinds, used):
    """Hasta PER_BUCKET productos de ese presupuesto: con foto, mejor precio en stock, en 2+ tiendas; primero los que más
    se ahorran frente a la tienda más cara; alternando categorías y como mucho 2 por marca."""
    pools = []
    for kind in kinds:
        cands = []
        for p in (cats.get(kind) or {}).get("products", []):
            items = [i for i in p.get("items", []) if i.get("p")]
            if not p.get("th") or not p.get("slug") or len({i["s"] for i in items}) < 2 or p["slug"] in used:
                continue
            best = min((i for i in items if i.get("st") is not False), key=lambda i: i["p"], default=None)
            if not best or not lo <= best["p"] < hi:
                continue
            top = max(i["p"] for i in items)
            # primero lo que da comisión (tienda afiliada; marca que está en Amazon), luego el ahorro
            paid = 0 if any(i["s"] in AFFILIATE_STORES for i in items) else 1 if (p.get("brand") or "").lower() in AMAZON_BRANDS else 2
            cands.append(((paid, -(top - best["p"]) / top), p))
        cands.sort(key=lambda x: x[0])
        pools.append([p for _, p in cands])
    out, brands = [], {}
    while len(out) < PER_BUCKET and any(pools):
        for pool in pools:
            while pool:
                p = pool.pop(0)
                b = (p.get("brand") or "").lower()
                if brands.get(b, 0) < 2 and p["slug"] not in used:
                    brands[b] = brands.get(b, 0) + 1
                    used.add(p["slug"])
                    out.append(p)
                    break
            if len(out) >= PER_BUCKET:
                break
    return out


def _tile(code, p, names, money, amazon_txt):
    from urllib.parse import quote_plus
    items = sorted((i for i in p["items"] if i.get("p")), key=lambda i: (i.get("st") is False, i["p"]))
    best, n = items[0], len({i["s"] for i in items})
    pre = "" if code == "es" else f"/{code}"
    e = lambda v: html.escape(str(v or ""), quote=True)
    return (f'<a class="tile" href="{pre}/g/{e(p["slug"])}.html"><div class="img"><img loading="lazy" src="/img/p/{e(p["th"])}" alt="">'
            f'</div><div class="body"><span class="brand">{e(p.get("brand"))}</span><span class="name">{e(html.unescape(p["name"]))}</span>'
            f'<span class="price"><strong>{money(best["p"])}</strong></span><span class="foot"><span>{e(names.get(best["s"], best["s"]))}</span>'
            f'<span class="stores-n">{n}</span></span></div></a>'
            + (f'<a class="amz" href="{e(AMAZON[code].format(q=quote_plus(html.unescape(p["name"]))))}" target="_blank" '
               f'rel="sponsored noopener">{e(amazon_txt)} →</a>' if code in AMAZON else ""))


def page(code, lang, cats, intl):
    """HTML de la página del país (code "es": España, en la raíz)."""
    from . import musica
    T, t = TXT[lang], intl.strings(code)
    names = {k: v for d in cats.values() for k, v in (d.get("stores") or {}).items()}
    money = lambda v: intl.money(v, code)
    pre = "" if code == "es" else f"/{code}"
    url = f"{pre}/{T['dir']}/"
    e = intl.esc
    used, secs = set(), []
    labels = T["b"] if code in ("uk",) else [b.replace("£", "€") for b in T["b"]]
    for (lo, hi, kinds), label, sub in zip(BUCKETS, labels, T["bd"]):
        ps = _pick(cats, lo, hi, kinds, used)
        if ps:
            secs.append(f'  <section class="hub-sec"><h2>{e(label)}</h2><p class="hub-intro" style="color:var(--text-secondary)">{e(sub)}</p>'
                        f'<div class="grid">{"".join(f'<div class="gift">{_tile(code, p, names, money, T["amz"])}</div>' for p in ps)}</div></section>')
    # Discos, si el país tiene sección
    M = musica.TXT.get(code)
    if M:
        deals = musica.home_deals(code, 8)
        if deals:
            cards = "".join(musica._disc_tile(code, d, M, {sid: n for sid, (n, _) in musica.STORES[code].items()}) for d, _, _ in deals)
            secs.append(f'  <section class="hub-sec"><h2>{e(T["discs"])} <a class="navlink" href="{musica._pre(code)}/{M["dir"]}/">'
                        f'{e(T["discs_more"])} →</a></h2><div class="grid">{cards}</div></section>')
    tips = "".join(f"<li>{e(x)}</li>" for x in T["tips"])
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": T["title"], "description": T["desc"],
          "url": f"https://guitle.com{url}"}
    head = intl._head(code, f"{T['title']} · guitle", T["desc"], url,
                      f'<meta property="og:title" content="{e(T["title"])}">\n<meta property="og:description" content="{e(T["desc"])}">\n'
                      '<link rel="stylesheet" href="/catalogo.css">\n<style>.hub-sec{margin-top:22px}.hub-sec h2{font-size:1.25rem}'
                      '.xmas{background:linear-gradient(135deg,#b3261e,#7a1a14);color:#fff;border-radius:16px;padding:22px 20px;margin-top:14px}'
                      '.xmas h2{color:#fff;margin:0 0 6px;font-size:1.7rem;letter-spacing:-.03em}.xmas p{margin:0;opacity:.92}'
                      '.gift{display:flex;flex-direction:column;gap:6px}.gift .tile{flex:1}.amz{display:block;text-align:center;padding:7px 10px;'
                      'border-radius:999px;border:1.5px solid var(--accent);color:var(--accent);font-weight:600;font-size:.88rem;'
                      'text-decoration:none}.amz:hover{background:var(--accent);color:#fff}</style>\n'
                      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    return (head + "</head>\n<body>\n<main>\n"
            f'  <div class="topbar"><div class="row">{intl._logo(code, t)}<a class="navlink" href="{pre}/">{e(t["home"])}</a></div></div>\n'
            f'  <div class="xmas"><h2>🎄 {e(T["title"])}</h2><p>{e(T["intro"])}</p></div>\n'
            # Selección a mano en Amazon (data/navidad/<país>.json, la edita Manuel): la lee navidad.js al abrir la página
            f'  <section class="hub-sec" id="amzsel" data-pais="{code}" data-h="{e(T["sel"])}" data-b="{e(T["amz"])}" hidden></section>\n'
            '  <script src="/navidad.js" defer></script>\n'
            + "\n".join(secs)
            + f'\n  <section class="hub-sec" style="max-width:780px"><h2>{e(T["tips_h"])}</h2><ul style="line-height:1.7">{tips}</ul></section>\n'
            f'  {intl._foot(code, t)}\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n'), url


def write_country(code, intl):
    """La página del país (si tiene textos); devuelve su URL o None."""
    lang = COUNTRIES.get(code)
    if not lang:
        return None
    html_, url = page(code, lang, intl.catalogs(code), intl)
    pages._write(pages.ROOT / code / TXT[lang]["dir"] / "index.html", html_)
    return url


def write_spain():
    """España (guitle.com/navidad/), con sus catálogos (pages.KINDS)."""
    from . import intl
    cats = {}
    for kind, k in pages.KINDS.items():
        try:
            d = json.loads((pages.ROOT / k["src"]).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        if kind == "packac":  # packs de acústica, con los demás packs
            cats.setdefault("pack", {"products": [], "stores": {}})
            cats["pack"]["products"] += d.get("products", [])
            cats["pack"]["stores"].update(d.get("stores", {}))
            continue
        if kind in cats:
            cats[kind]["products"] += d.get("products", [])
            cats[kind]["stores"].update(d.get("stores", {}))
        else:
            cats[kind] = {"products": list(d.get("products", [])), "stores": dict(d.get("stores", {}))}
    html_, url = page("es", "es", cats, intl)
    pages._write(pages.ROOT / "navidad" / "index.html", html_)
    return url


if __name__ == "__main__":
    print(write_spain())
