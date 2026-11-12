"""Discos en Instagram de guitle Reino Unido (@guitle.uk): «Same record, £X cheaper» y «Vinyl deal of the week».

Sale de lo mismo que guitle.com/uk/records/deals.html: discos (por código de barras) en stock en 2 o más tiendas de
discos inglesas, con la mayor diferencia de precio de hoy. Solo artistas conocidos (FAMOSOS), con diferencias
creíbles. Post 4:5 y story 9:16 con la portada, el precio más barato y su tienda frente al más caro (sin nombrar esa
tienda: nunca se dice «caro en Y», solo «más barato en X»).

Calendario (lo decide el día): martes y jueves, «Same record»; viernes, «Vinyl deal of the week» (el de más ahorro de
un artista conocido). Los demás días no hace nada.

  python -m scraper.discos_ig                 # genera el de hoy en social/<fecha>/uk/discos/ (sin publicar)
  python -m scraper.discos_ig --publish       # y lo publica en @guitle.uk (INSTAGRAM_TOKEN_UK)
  python -m scraper.discos_ig --tipo semana   # fuerza un tipo (same / semana), para probar
"""
import argparse
import json
import os
import subprocess
import unicodedata
from datetime import date

import requests

from . import instagram as ig
from .paises import MESES

ROOT = ig.ROOT
DISCOS = ROOT / "data" / "musica" / "uk" / "discos.json"
HECHOS = ROOT / "social" / "discos-publicados.json"
WEB = "https://guitle.com/uk/records"
TIENDAS = {"recordstore": "Recordstore", "assai": "Assai Records", "sisterray": "Sister Ray", "drift": "Drift Records",
           "crash": "Crash Records"}
FORMATO = {"vinilo": "vinyl", "cd": "CD", "casete": "cassette"}
TAGS = "#vinyl #vinylrecords #vinylcollection #recordcollector #vinyldeals #ukvinyl"
DIAS = {1: "same", 3: "same", 4: "semana"}  # martes, jueves, viernes
# Cuentas cuyos discos aún no se publican (Italia: Manuel quiere probar antes guitle.com/it/dischi/)
EN_ESPERA = {"it"}

# Artistas conocidos (grandes, clásicos y actuales con público amplio en Reino Unido). Se compara sin acentos ni
# mayúsculas con lo que va antes de " - " en el nombre del disco.
FAMOSOS = """
ABBA; AC/DC; Adele; Aerosmith; a-ha; Alanis Morissette; Amy Winehouse; Arctic Monkeys; Ariana Grande; Atomic Kitten;
Bad Bunny; Beastie Boys; Beck; Bee Gees; Beyonce; Billie Eilish; Billy Bragg; Billy Joel; Black Sabbath; Blondie;
Blur; Bob Dylan; Bob Marley; Bob Marley & The Wailers; Bon Jovi; Bonnie Tyler; Bruce Springsteen; Bryan Adams;
Buzzcocks; Calvin Harris; Chappell Roan; Charli XCX; Cher; Coldplay; Creedence Clearwater Revival; Crowded House;
Daft Punk; David Bowie; De La Soul; Deep Purple; Def Leppard; Depeche Mode; Dire Straits; Dolly Parton; Doves;
Dua Lipa; Duran Duran; Ed Sheeran; Elbow; Elton John; Elvis Costello; Elvis Presley; Eminem; Erasure; Eric Clapton;
Eurythmics; Fleetwood Mac; Florence + The Machine; Foo Fighters; Frank Ocean; Frank Sinatra; Franz Ferdinand;
Gary Numan; Genesis; George Harrison; George Michael; Gorillaz; Green Day; Guns N' Roses; Happy Mondays; Harry Styles;
Iron Maiden; Jamiroquai; Jimi Hendrix; John Lennon; Johnny Cash; Joni Mitchell; Joy Division; Kate Bush; Keane;
Kendrick Lamar; Kings Of Leon; Kiss; Kylie Minogue; Lady Gaga; Lana Del Rey; Led Zeppelin; Lewis Capaldi;
Lily Allen; Linkin Park; Lorde; Madness; Madonna; Manic Street Preachers; Marillion; Massive Attack; Metallica;
Michael Jackson; Miles Davis; Morrissey; Motley Crue; Motorhead; Muse; Neil Young; New Order; Nick Cave & The Bad Seeds;
Nine Inch Nails; Nirvana; Noel Gallagher's High Flying Birds; Oasis; Olivia Rodrigo; Ozzy Osbourne; Paul McCartney;
Paul Weller; Pearl Jam; Pet Shop Boys; Peter Gabriel; Pink Floyd; PJ Harvey; Portishead; Primal Scream; Prince;
Pulp; Queen; Radiohead; Rage Against The Machine; Rammstein; Red Hot Chili Peppers; R.E.M.; Robbie Williams;
Rod Stewart; Roxy Music; Sabrina Carpenter; Sade; Siouxsie And The Banshees; Simple Minds; Slipknot; Spice Girls;
Stereophonics; Stevie Nicks; Stevie Wonder; Sting; Suede; Supergrass; Take That; Talking Heads; Taylor Swift;
Tears For Fears; The Beatles; The Black Keys; The Charlatans; The Chemical Brothers; The Clash; The Cure;
The Doors; The Jam; The Killers; The Kinks; The Libertines; The Prodigy; The Rolling Stones; The Smiths;
The Specials; The Stone Roses; The Strokes; The Verve; The Who; The Weeknd; Tom Petty; Tom Petty and the Heartbreakers;
Tracy Chapman; Travis; U2; UB40; Ultravox; Van Morrison; Weezer; Wham!; Wet Leg; Whitney Houston; Wolf Alice; Yes;
ZZ Top; Fontaines D.C.; IDLES; Sam Fender; The 1975; Arlo Parks; Fatboy Slim; Underworld; Orbital; Leftfield;
The Beach Boys; Steely Dan; Fleetwood Mac; Simon & Garfunkel; Paul Simon; Carole King; Bjork; Kraftwerk; Iggy Pop;
Lou Reed; The Velvet Underground; Ramones; Sex Pistols; The Stranglers; Echo & The Bunnymen; The Housemartins;
The Beautiful South; Ocean Colour Scene; Kasabian; Snow Patrol; The Script; Biffy Clyro; Bring Me The Horizon;
Ghost; Judas Priest; Megadeth; Slayer; Thin Lizzy; Status Quo; Electric Light Orchestra; ELO; Supertramp; Toto;
Journey; Heart; Pretenders; The Pretenders; Cyndi Lauper; Prince & The Revolution; Wu-Tang Clan; Nas; Jay-Z;
Kanye West; Dr. Dre; Snoop Dogg; Public Enemy; A Tribe Called Quest; The Streets; Dizzee Rascal; Stormzy;
""".replace("\n", " ")
FAMOSOS = {unicodedata.normalize("NFKD", a).encode("ascii", "ignore").decode().lower().strip()
           for a in FAMOSOS.split(";") if a.strip()}


# Artistas conocidos de cada país (además de los internacionales de arriba)
LOCALES = {
    "es": """Rosalia; Estopa; Heroes del Silencio; Extremoduro; Fito y Fitipaldis; Vetusta Morla; Love of Lesbian; Joaquin Sabina;
Joan Manuel Serrat; Mecano; Alejandro Sanz; Bunbury; Enrique Bunbury; Los Planetas; Leiva; Quevedo; C. Tangana; Aitana;
Melendi; La Oreja de Van Gogh; Hombres G; Radio Futura; Loquillo; Los Secretos; Nacha Pop; Duncan Dhu; Camilo Sesto;
Raphael; Rocio Jurado; Camaron de la Isla; Paco de Lucia; Lola Flores; Manolo Garcia; El Ultimo de la Fila; Ska-P;
Platero y Tu; Marea; Barricada; Rosendo; Miguel Rios; Ana Belen; Victor Manuel; Mikel Erentxun; Amaral; Dani Martin;
El Canto del Loco; Pereza; Supersubmarina; Izal; Sidonie; Lori Meyers; Dorian; Russian Red; Rocio Marquez; Silvia Perez Cruz;
Bad Gyal; Lola Indigo; Nathy Peluso; Rels B; Morat; Sabina; Antonio Vega; Mclan; Triana; Medina Azahara; Mago de Oz;
Baron Rojo; Obus; Siniestro Total; Los Suaves; Sopa de Cabra; Els Pets; Manel; Txarango; Estrella Morente; Enrique Morente""",
    "it": """Vasco Rossi; Ligabue; Maneskin; Lucio Battisti; Fabrizio De Andre; Mina; Adriano Celentano; Zucchero; Pino Daniele;
Franco Battiato; Lucio Dalla; Eros Ramazzotti; Laura Pausini; Jovanotti; Ultimo; Tiziano Ferro; Cesare Cremonini;
Marco Mengoni; Elodie; Annalisa; Sfera Ebbasta; Lazza; Geolier; Negramaro; Subsonica; Afterhours; CCCP Fedeli Alla Linea;
Litfiba; Pooh; Renato Zero; Claudio Baglioni; Francesco De Gregori; Antonello Venditti; Fiorella Mannoia; Gianna Nannini;
Edoardo Bennato; Rino Gaetano; Paolo Conte; Ennio Morricone; Ludovico Einaudi; Andrea Bocelli; Il Volo; Mahmood; Blanco;
Tananai; Angelina Mango; Salmo; Marracash; Guè; Fabri Fibra; Articolo 31; 883; Max Pezzali; Gemelli DiVersi; Elisa;
Carmen Consoli; Caparezza; Baustelle; Verdena; Marlene Kuntz; I Cani; Calcutta; Coez; Thegiornalisti; Brunori Sas;
Vinicio Capossela; Lucio Corsi; Loredana Berte; Mia Martini; Ornella Vanoni; Patty Pravo; Raffaella Carra; Gianni Morandi;
Al Bano; Toto Cutugno; Umberto Tozzi; Nek; Biagio Antonacci; Modà; Pinguini Tattici Nucleari; Lo Stato Sociale; Gazzelle""",
}

# Textos, moneda y web de cada país (Reino Unido igual que siempre)
PAIS = {
    "uk": {"token": "INSTAGRAM_TOKEN_UK", "cuenta": "@guitle.uk", "web": "https://guitle.com/uk/records", "lang": "en",
           "fmt": {"vinilo": "vinyl", "cd": "CD", "casete": "cassette"}, "tags": TAGS, "tope": (60, 150)},
    "es": {"token": "INSTAGRAM_TOKEN_ES", "cuenta": "@guitle.es", "web": "https://guitle.com/discos", "lang": "es",
           "fmt": {"vinilo": "vinilo", "cd": "CD", "casete": "casete"}, "tope": (60, 150),
           "tags": "#vinilo #vinilos #discos #coleccionismo #coleccionvinilos #musica #ofertas",
           "t": {"cab_same": "Mismo disco, {x} más barato", "cab_semana": "El chollo de vinilo de la semana",
                 "pill_post": "💿 Chollo de disco", "pill_post_semana": "🏆 Chollo de la semana",
                 "pill_story": "💿 Mismo disco, más barato", "pill_story_semana": "🏆 Vinilo de la semana",
                 "cheapest": "Lo más barato hoy", "at": "en", "others": "Otras tiendas de discos", "upto": "hasta",
                 "footer": "Comparamos precios de tiendas de discos de España · guitle.com/discos",
                 "elsewhere": "Hasta {hi} en otras tiendas · ahorras {x}",
                 "story_footer": "Precios y stock: enlace en la bio · guitle.com/discos"},
           "cap": ("{head}\n\n{artist} – {title} ({fmt})\n✅ {lo} en {tienda}\n🔁 Hasta {hi} en otras tiendas de discos: "
                   "ahorras {x}\n\nComparamos los precios de las tiendas de discos de España para que no tengas que hacerlo tú.\n"
                   "🔎 Precios y stock de este disco: enlace en la bio → guitle.com/discos\nPrecios del {fecha}; pueden cambiar."
                   "\n\n{tags}"),
           "head": ("💿 Mismo disco, {x} más barato", "🏆 El chollo de vinilo de la semana")},
    "it": {"token": "INSTAGRAM_TOKEN_IT", "cuenta": "@guitle.it", "web": "https://guitle.com/it/dischi", "lang": "it",
           "fmt": {"vinilo": "vinile", "cd": "CD", "casete": "cassetta"}, "tope": (60, 150),
           "tags": "#vinile #vinili #dischi #collezionismo #vinilecollection #musica #offerte",
           "t": {"cab_same": "Stesso disco, {x} in meno", "cab_semana": "L’affare vinile della settimana",
                 "pill_post": "💿 Offerta disco", "pill_post_semana": "🏆 Affare della settimana",
                 "pill_story": "💿 Stesso disco, meno caro", "pill_story_semana": "🏆 Vinile della settimana",
                 "cheapest": "Il più economico oggi", "at": "da", "others": "Altri negozi", "upto": "fino a",
                 "footer": "Confrontiamo i prezzi dei negozi di musica in Italia · guitle.com/it/dischi",
                 "elsewhere": "Fino a {hi} altrove · risparmi {x}",
                 "story_footer": "Prezzi e disponibilità: link in bio · guitle.com/it/dischi"},
           "cap": ("{head}\n\n{artist} – {title} ({fmt})\n✅ {lo} da {tienda}\n🔁 Fino a {hi} negli altri negozi: "
                   "risparmi {x}\n\nConfrontiamo i prezzi dei negozi di musica in Italia, così non devi farlo tu.\n"
                   "🔎 Prezzi e disponibilità di questo disco: link in bio → guitle.com/it/dischi\nPrezzi del {fecha}; "
                   "possono cambiare.\n\n{tags}"),
           "head": ("💿 Stesso disco, {x} in meno", "🏆 L’affare vinile della settimana")},
}


def eur(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return (s[:-3] if s.endswith(",00") else s) + " €"


def dinero(cc):
    return gbp if cc == "uk" else eur


def _norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().strip()


def artista(name):
    return name.split(" - ", 1)[0].strip() if " - " in name else ""


def gbp(v):
    return f"£{v:,.2f}".replace(".00", "")


def candidatos(recent, cc="uk"):
    """Discos de artistas conocidos con 2+ tiendas en stock y una diferencia creíble, de más a menos ahorro."""
    from .musica import STORES
    tiendas = {k: v[0] for k, v in STORES.get(cc, {}).items()} or TIENDAS
    famosos = FAMOSOS | {_norm(a) for a in LOCALES.get(cc, "").replace("\n", " ").split(";") if a.strip()}
    web = PAIS[cc]["web"]
    out = []
    for d in json.loads((ROOT / "data" / "musica" / cc / "discos.json").read_text(encoding="utf-8")):
        # eBay sí cuenta (Manuel monetiza con eBay y Amazon: si están más baratos, mejor)
        live = sorted((i for i in d["items"] if i.get("st") and i.get("p")
                       # tiendas de otro país (p. ej. «CDGO (Portugal)»): el post dice «tiendas de discos de <país>»
                       and "(" not in tiendas.get(i["s"], "")), key=lambda i: i["p"])
        if len({i["s"] for i in live}) < 2 or not d.get("img"):
            continue
        lo, hi = live[0], live[-1]
        ahorro = round(hi["p"] - lo["p"], 2)
        # Diferencias absurdas suelen ser ediciones distintas con el mismo código: fuera
        if ahorro < 3 or hi["p"] > 1.45 * lo["p"] or _norm(artista(d["name"])) not in famosos or d["ean"] in recent:
            continue
        out.append({**d, "artist": artista(d["name"]), "title": d["name"].split(" - ", 1)[1].strip(),
                    "lo": lo["p"], "hi": hi["p"], "ahorro": ahorro, "tienda": tiendas.get(lo["s"], lo["s"]),
                    "tiendas": len({i["s"] for i in live}), "url": f"{web}/{d['slug']}.html"})
    # Primero los de eBay y Amazon (Manuel cobra comisión por sus ventas), luego los vinilos con más ahorro
    return sorted(out, key=lambda d: ("ebay" not in d["tienda"].lower() and "amazon" not in d["tienda"].lower(),
                                      d["fmt"] != "vinilo", -d["ahorro"]))


def portada(url, dest):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (guitle)"})
    if r.status_code != 200 or len(r.content) < 2000:
        return False
    dest.write_bytes(r.content)
    return True


def _hechos_path(cc):
    return HECHOS if cc == "uk" else ROOT / "social" / f"discos-publicados-{cc}.json"


def generar(day, tipo=None, cc="uk"):
    tipo = tipo or DIAS.get(day.weekday())
    if not tipo:
        print("hoy no toca disco")
        return None, None
    hp = _hechos_path(cc)
    hechos = json.loads(hp.read_text(encoding="utf-8")) if hp.exists() else {}
    recent = {v["ean"] for v in hechos.values()}
    folder = ig.OUT / day.isoformat() / cc / "discos"
    folder.mkdir(parents=True, exist_ok=True)
    tope = PAIS[cc]["tope"][tipo == "semana"]  # «same»: discos a precio normal; la del semana puede ser una edición especial
    money = dinero(cc)
    for d in [c for c in candidatos(recent, cc) if c["lo"] <= tope][:15]:
        img = folder / f"portada{'.png' if '.png' in d['img'].split('?')[0].lower() else '.jpg'}"
        try:
            ok = portada(d["img"], img)
        except Exception:
            ok = False
        if not ok:
            continue
        d["photo"] = img.name
        if cc != "uk":
            cfg = PAIS[cc]
            fmt = cfg["fmt"].get(d["fmt"], d["fmt"])
            t = {k: v.replace("{x}", money(d["ahorro"])).replace("{hi}", money(d["hi"])) for k, v in cfg["t"].items()}
            cab = t["cab_semana"] if tipo == "semana" else t["cab_same"]
            caption = cfg["cap"].format(head=cfg["head"][tipo == "semana"].format(x=money(d["ahorro"])), artist=d["artist"],
                                        title=d["title"], fmt=fmt, lo=money(d["lo"]), hi=money(d["hi"]), x=money(d["ahorro"]),
                                        tienda=d["tienda"], fecha=f"{day.day} de {MESES['it' if cc == 'it' else 'pt'][day.month - 1]}"
                                        if cc == "it" else f"{day.day} de {['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'][day.month - 1]}",
                                        tags=cfg["tags"])
            if cc == "it":
                caption = caption.replace(f"Prezzi del {day.day} de ", f"Prezzi del {day.day} ")
            plan = {"tipo": tipo, "cab": cab, "fmt": fmt, "disco": d, "fecha": day.isoformat(), "cc": cc, "t": t}
            (folder / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            (folder / "texto.txt").write_text(caption + "\n", encoding="utf-8")
            subprocess.run(["node", str(ROOT / "brand" / "discos.js"), str(folder)], check=True, cwd=ROOT)
            reel(folder, day, cc)
            return folder, plan
        fmt = FORMATO.get(d["fmt"], d["fmt"])
        cab = "Vinyl deal of the week" if tipo == "semana" else f"Same record, {gbp(d['ahorro'])} cheaper"
        caption = (f"{'🏆 Vinyl deal of the week' if tipo == 'semana' else '💿 Same record, ' + gbp(d['ahorro']) + ' cheaper'}\n\n"
                   f"{d['artist']} – {d['title']} ({fmt})\n"
                   f"✅ {gbp(d['lo'])} at {d['tienda']}\n"
                   f"🔁 Up to {gbp(d['hi'])} at other UK record shops: save {gbp(d['ahorro'])}\n\n"
                   f"We compare prices across UK record shops, so you don’t have to.\n"
                   f"🔎 Prices and stock for this record: link in bio → guitle.com/uk/records\n"
                   f"Prices on {day.day} {MESES['en'][day.month - 1]}; "
                   f"they may change.\n\n{TAGS}")
        plan = {"tipo": tipo, "cab": cab, "fmt": fmt, "disco": d, "fecha": day.isoformat()}
        (folder / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        (folder / "texto.txt").write_text(caption + "\n", encoding="utf-8")
        subprocess.run(["node", str(ROOT / "brand" / "discos.js"), str(folder)], check=True, cwd=ROOT)
        reel(folder, day, cc)
        return folder, plan
    print("no hay disco que publicar hoy")
    return None, None


def reel(folder, day, cc):
    """Reel del disco (Manuel, 12-11: «en reel con música»): la imagen de la story (1080×1920) empieza con zoom sobre la
    portada y se abre hasta verse entera; ~9 s con música libre de derechos (scraper/musica_libre.py) y su crédito al
    final del texto."""
    from . import musica_libre
    video = folder / "reel.mp4"
    zoom = "if(lte(on,90),1.3-0.3*on/90,1)"  # 3 s de zoom sobre la portada y luego quieto
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", "9", "-i", str(folder / "story.jpg"),
                    "-vf", f"scale=2160:3840,zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='max(0,min(ih-ih/zoom,ih*0.27-ih/zoom/2))'"
                    ":d=1:s=1080x1920:fps=30,fade=t=in:st=0:d=0.3,format=yuv420p",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", str(video)], check=True)
    credito = musica_libre.poner(video, day.toordinal() + sorted(PAIS).index(cc))
    texto = (folder / "texto.txt").read_text(encoding="utf-8").strip()
    (folder / "texto.txt").write_text(f"{texto}\n\n{credito}\n", encoding="utf-8")


def publicar(day, folder, plan, cc="uk"):
    cfg = PAIS[cc]
    token = os.environ.get(cfg["token"])
    if not token:
        raise SystemExit(f"falta {cfg['token']}")
    ig.TOKEN = token
    hp = _hechos_path(cc)
    try:
        user = ig.api("GET", "me", fields="user_id")["user_id"]
        hechos = json.loads(hp.read_text(encoding="utf-8")) if hp.exists() else {}
        if day.isoformat() in hechos:
            print("ya publicado hoy:", hechos[day.isoformat()].get("post"))
            return
        rel = folder.relative_to(ROOT).as_posix()
        branch = ig.git("rev-parse", "--abbrev-ref", "HEAD")
        ig.git("add", rel)
        if ig.git("diff", "--cached", "--name-only"):
            ig.git("commit", "-q", "-m", f"social: disco de {cfg['cuenta']} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        base = f"{ig.REPO_RAW}/{ig.git('rev-parse', 'HEAD')}/{rel}/"
        for name in ("reel.mp4", "story.jpg"):
            for _ in range(20):
                if requests.head(base + name, timeout=30).status_code == 200:
                    break
        caption = (folder / "texto.txt").read_text(encoding="utf-8").strip()
        if (folder / "reel.mp4").exists():  # Reel con música (desde el 13-11); si no hay vídeo, la imagen de siempre
            post = ig.publish(user, ig.container(user, tries=100, media_type="REELS", video_url=base + "reel.mp4",
                                                 caption=caption, share_to_feed="true"))
        else:
            post = ig.publish(user, ig.container(user, image_url=base + "post.jpg", caption=caption))
        story = ig.publish(user, ig.container(user, image_url=base + "story.jpg", media_type="STORIES"))
        d = plan["disco"]
        hechos[day.isoformat()] = {"ean": d["ean"], "disco": d["name"], "tipo": plan["tipo"], "ahorro": d["ahorro"],
                                   "url": d["url"], "post": post, "story": story}
        hp.write_text(json.dumps(hechos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        ig.git("add", rel, hp.relative_to(ROOT).as_posix())
        ig.git("commit", "-q", "-m", f"social: publicado el disco de {cfg['cuenta']} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        print("post:", post, "| story:", story, "| página:", d["url"])
    finally:
        ig.TOKEN = None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--tipo", choices=["same", "semana"])
    ap.add_argument("--date")
    ap.add_argument("--pais", default="uk", choices=sorted(PAIS), help="cuenta (uk, es, it); por defecto uk")
    a = ap.parse_args(argv)
    if a.pais in EN_ESPERA:
        print(f"{a.pais}: discos en espera hasta que Manuel lo diga (EN_ESPERA en scraper/discos_ig.py); no se genera nada")
        return
    day = date.fromisoformat(a.date) if a.date else date.today()
    folder, plan = generar(day, a.tipo, a.pais)
    if folder:
        d, money = plan["disco"], dinero(a.pais)
        print(f"{plan['cab']}: {d['name']} ({plan['fmt']}) {money(d['lo'])} en {d['tienda']} frente a {money(d['hi'])} → {folder}")
        if a.publish:
            publicar(day, folder, plan, a.pais)


if __name__ == "__main__":
    main()
