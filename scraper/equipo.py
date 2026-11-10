"""Ciclo de categorías en el Reel de las 17:37 (los días sin cuenta atrás del Black Friday): cada día una rama distinta
(guitarras, amplis, bajos, teclados, pedales, micrófonos) con sus mejores ofertas del día. Mismas normas que las
guitarras: en stock y leídas en los 2 últimos días, diferencias creíbles, foto revisada y portada con el producto.
Las guitarras siguen con su top de siempre (scraper.instagram.reel_top y scraper.paises.reels_tarde)."""
from datetime import date

from . import instagram as ig

RAMAS = ["guitarras", "amplis", "bajos", "teclados", "baterias", "pedales", "micros"]
# Forma de la foto (ig.with_photos): los bajos, en vertical como las guitarras; amplis y teclados, apaisados
FORMA = {"amplis": "ancho", "bajos": "vertical", "teclados": "ancho", "pedales": "libre", "micros": "libre", "baterias": "libre"}

# Catálogo de cada rama por país (España, en data/catalog/mas y data/catalog/equipo; los demás, en <país>mas)
ARCHIVOS = {
    "es": {"amplis": "mas/amplis", "bajos": "mas/bajos", "teclados": "equipo/teclados", "pedales": "equipo/pedales",
           "micros": "mas/micros", "baterias": "mas/baterias"},
    "fr": {"amplis": "frmas/amplis", "bajos": "frmas/basses", "teclados": "frmas/claviers", "pedales": "frmas/pedales-effets",
           "micros": "frmas/micros", "baterias": "frmas/batteries"},
    "it": {"amplis": "itmas/amplificatori", "bajos": "itmas/bassi", "teclados": "itmas/tastiere",
           "pedales": "itmas/pedali-effetto", "micros": "itmas/microfoni", "baterias": "itmas/batterie"},
    "de": {"amplis": "demas/verstaerker", "bajos": "demas/baesse", "teclados": "demas/keyboards",
           "pedales": "demas/effektpedale", "micros": "demas/mikrofone", "baterias": "demas/schlagzeuge"},
    "uk": {"amplis": "ukmas/amps", "bajos": "ukmas/basses", "teclados": "ukmas/keyboards", "pedales": "ukmas/effects-pedals",
           "micros": "ukmas/microphones", "baterias": "ukmas/drum-kits"},
    "br": {"amplis": "brmas/amplificadores", "bajos": "brmas/baixos", "teclados": "brmas/teclados", "pedales": "brmas/pedais",
           "micros": "brmas/microfones", "baterias": "brmas/baterias"},
    "pt": {"amplis": "ptmas/amplificadores", "bajos": "ptmas/baixos", "teclados": "ptmas/teclados", "pedales": "ptmas/pedais",
           "micros": "ptmas/microfones", "baterias": "ptmas/baterias"},
}

# Textos: nombre de la rama (título del Reel), etiqueta de la portada, plantilla del texto y etiquetas
TXT = {
    "es": {"nombre": {"amplis": "amplis", "bajos": "bajos", "teclados": "teclados", "pedales": "pedales",
                      "micros": "micrófonos", "baterias": "baterías"},
           "hook": "Chollos de hoy", "titulo": "{n} chollos en {rama}",
           "linea": "{i}️⃣ {name}: {price} en {store} ({why})",
           "cap": "🔥 {titulo}: los más baratos hoy frente al resto de tiendas 👇\n\n{lines}\n\n¿Con cuál te quedas? 💬\n"
                  "👉 Todos los chollos de hoy, a un toque: enlace en la bio. Precios del {fecha}; pueden cambiar.",
           "menos": "{x} menos que en cualquier otra tienda",
           "tags": {"amplis": "#amplificador #amplificadorguitarra", "bajos": "#bajo #bajoelectrico #bajistas",
                    "teclados": "#teclado #sintetizador #pianodigital", "pedales": "#pedales #pedalesdeguitarra #pedalboard",
                    "micros": "#microfono #homestudio", "baterias": "#bateria #bateriaelectronica #bateristas"}, "base": "#chollos #ofertas #musica #musicos"},
    "fr": {"nombre": {"amplis": "amplis", "bajos": "basses", "teclados": "claviers", "pedales": "pédales d'effet",
                      "micros": "micros", "baterias": "batteries"},
           "hook": "Bons plans du jour", "titulo": "{n} bons plans {rama}",
           "linea": "{i}️⃣ {name} : {price} chez {store} ({why})",
           "cap": "🔥 {titulo} : les moins chers aujourd'hui par rapport aux autres magasins 👇\n\n{lines}\n\nTu prendrais lequel ? 💬\n"
                  "🔎 Compare les prix sur guitle.com/fr (tous les bons plans du jour via le lien en bio 👆). Prix du {fecha} ; ils peuvent changer.",
           "tags": {"amplis": "#ampli #ampliguitare", "bajos": "#basse #bassiste", "teclados": "#clavier #synthe #pianonumerique",
                    "pedales": "#pedale #pedaleguitare #pedalboard", "micros": "#micro #homestudio", "baterias": "#batterie #batteur #batterieelectronique"},
           "base": "#bonplan #promo #musique #musicien"},
    "it": {"nombre": {"amplis": "amplificatori", "bajos": "bassi", "teclados": "tastiere", "pedales": "pedali",
                      "micros": "microfoni", "baterias": "batterie"},
           "hook": "Offerte di oggi", "titulo": "{n} offerte: {rama}",
           "linea": "{i}️⃣ {name}: {price} da {store} ({why})",
           "cap": "🔥 {titulo}, i più convenienti oggi rispetto agli altri negozi 👇\n\n{lines}\n\nQuale prenderesti? 💬\n"
                  "🔎 Confronta i prezzi su guitle.com/it (tutte le offerte di oggi nel link in bio 👆). Prezzi del {fecha}; possono cambiare.",
           "tags": {"amplis": "#amplificatore #ampli", "bajos": "#basso #bassista", "teclados": "#tastiera #synth #pianodigitale",
                    "pedales": "#pedali #pedaliera #pedalboard", "micros": "#microfono #homestudio", "baterias": "#batteria #batterista #batteriaelettronica"},
           "base": "#offerte #sconti #musica #musicisti"},
    "de": {"nombre": {"amplis": "Verstärker", "bajos": "Bässe", "teclados": "Keyboards", "pedales": "Effektpedale",
                      "micros": "Mikrofone", "baterias": "Schlagzeuge"},
           "hook": "Deals von heute", "titulo": "{n} Deals: {rama}",
           "linea": "{i}️⃣ {name}: {price} bei {store} ({why})",
           "cap": "🔥 {titulo}, heute am günstigsten im Vergleich zu den anderen Shops 👇\n\n{lines}\n\nWelches würdest du nehmen? 💬\n"
                  "🔎 Preise vergleichen auf guitle.com/de (alle Deals von heute über den Link in der Bio 👆). Preise vom {fecha}; können sich ändern.",
           "tags": {"amplis": "#verstärker #gitarrenverstärker", "bajos": "#bass #bassist", "teclados": "#keyboard #synthesizer #digitalpiano",
                    "pedales": "#effektpedal #pedalboard", "micros": "#mikrofon #homestudio", "baterias": "#schlagzeug #schlagzeuger #edrums"},
           "base": "#angebote #deals #musik #musiker"},
    "uk": {"nombre": {"amplis": "amps", "bajos": "basses", "teclados": "keyboards", "pedales": "pedals",
                      "micros": "microphones", "baterias": "drum kits"},
           "hook": "Today’s deals", "titulo": "{n} deals on {rama}",
           "linea": "{i}️⃣ {name}: {price} at {store} ({why})",
           "cap": "🔥 {titulo}: cheapest today compared with every other UK shop 👇\n\n{lines}\n\nWhich one would you pick? 💬\n"
                  "🔎 Compare prices on guitle.com/uk (all today’s deals via the link in bio 👆). Prices on {fecha}; they may change.",
           "tags": {"amplis": "#guitaramp #amp", "bajos": "#bassguitar #bassist", "teclados": "#keyboard #synth #digitalpiano",
                    "pedales": "#guitarpedals #pedalboard", "micros": "#microphone #homestudio", "baterias": "#drums #drumkit #edrums"},
           "base": "#deals #ukdeals #music #musician"},
    "br": {"nombre": {"amplis": "amplificadores", "bajos": "baixos", "teclados": "teclados", "pedales": "pedais",
                      "micros": "microfones", "baterias": "baterias"},
           "hook": "Promoções de hoje", "titulo": "{n} promoções em {rama}",
           "linea": "{i}️⃣ {name}: {price} em {store} ({why})",
           "cap": "🔥 {titulo}: os mais baratos hoje em comparação com as outras lojas 👇\n\n{lines}\n\nQual você levaria? 💬\n"
                  "🔎 Compare preços em guitle.com/br (todas as promoções de hoje no link da bio 👆). Preços de {fecha}; podem mudar.",
           "tags": {"amplis": "#amplificador #amplificadordeguitarra", "bajos": "#baixo #baixista", "teclados": "#teclado #sintetizador",
                    "pedales": "#pedais #pedalboard", "micros": "#microfone #homestudio", "baterias": "#bateria #baterista #bateriaeletronica"},
           "base": "#promoção #ofertas #musica #musicos"},
    "pt": {"nombre": {"amplis": "amplificadores", "bajos": "baixos", "teclados": "teclados", "pedales": "pedais",
                      "micros": "microfones", "baterias": "baterias"},
           "hook": "Promoções de hoje", "titulo": "{n} promoções em {rama}",
           "linea": "{i}️⃣ {name}: {price} na {store} ({why})",
           "cap": "🔥 {titulo}: os mais baratos hoje face às outras lojas 👇\n\n{lines}\n\nQual escolhias? 💬\n"
                  "🔎 Compara preços em guitle.com/pt (todas as promoções de hoje no link da bio 👆). Preços de {fecha}; podem mudar.",
           "tags": {"amplis": "#amplificador #amplificadordeguitarra", "bajos": "#baixo #baixista", "teclados": "#teclado #sintetizador",
                    "pedales": "#pedais #pedalboard", "micros": "#microfone #homestudio", "baterias": "#bateria #baterista #bateriaeletronica"},
           "base": "#promoções #ofertas #musica #musicos"},
}


def rama_del_dia(day: date):
    return RAMAS[day.toordinal() % len(RAMAS)]


def plan(cc, rama, day, recent, fetcher, sub, money, rango, fecha):
    """Plan del Reel de ofertas de la rama (post tipo «top» de brand/reel.js) y su texto; None si no hay 3 buenas.
    rango: (mínimo, máximo) del país para guitarras; los pedales bajan el mínimo a algo más de la mitad."""
    lo, hi = rango
    if rama == "pedales":
        lo = round(lo * 80 / 150)
    t = TXT[cc]
    path = ig.ROOT / "data" / "catalog" / f"{ARCHIVOS[cc][rama]}.json"
    if not path.exists():
        return None
    prods = ig.products(lo, hi, catalogs={rama: path})
    # Ofertas: la más barata frente a todas las demás tiendas, con diferencia creíble (≤ 1,45 × la más cara)
    cands = sorted((p for p in prods if p["next"] > p["price"] and p["max"] <= 1.45 * p["price"]
                    and p["name"] not in recent and ig.foto_revisada(p)),
                   key=lambda p: (not ig.monetiza(p["store"]), -(p["next"] - p["price"]) / p["price"]))  # eBay/Amazon primero
    elegidos, marcas = [], set()
    for p in cands:
        if p["brand"] in marcas or (p["next"] - p["price"]) / p["price"] < 0.03:  # sin marcas repetidas ni rebajas de calderilla
            continue
        got = ig.with_photos([p], 1, fetcher, sub, f"g{len(elegidos) + 1}-", forma=FORMA[rama])
        if got:
            why = t.get("menos", TXT_MENOS.get(cc, "{x}")).format(x=money(p["next"] - p["price"]))
            elegidos.append({**got[0], "why": why})
            marcas.add(p["brand"])
        if len(elegidos) == 5:
            break
    if len(elegidos) < 3:
        return None
    elegidos.sort(key=lambda p: p["price"])
    titulo = t["titulo"].format(n=len(elegidos), rama=t["nombre"][rama])
    lines = "\n".join(t["linea"].format(i=i, name=p["name"], price=money(p["price"]), store=p["store"], why=p["why"])
                      for i, p in enumerate(elegidos, 1))
    caption = (t["cap"].format(titulo=titulo, lines=lines, fecha=fecha) + f"\n\n{t['base']} {t['tags'][rama]} "
               + " ".join(dict.fromkeys(ig.tag(p["brand"]) for p in elegidos if p["brand"])))
    post = {"type": "top", "title": titulo, "hook": t["hook"], "picks": elegidos, "rama": rama}
    return post, caption


# Texto «X menos que en cualquier otra tienda» de cada país (el de España está en TXT)
TXT_MENOS = {"fr": "{x} de moins qu'ailleurs", "it": "{x} in meno che altrove", "de": "{x} günstiger als anderswo",
             "uk": "{x} less than anywhere else", "br": "{x} a menos que nas outras lojas", "pt": "{x} a menos que nas outras lojas"}
