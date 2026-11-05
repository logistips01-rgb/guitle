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


def _norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().strip()


def artista(name):
    return name.split(" - ", 1)[0].strip() if " - " in name else ""


def gbp(v):
    return f"£{v:,.2f}".replace(".00", "")


def candidatos(recent):
    """Discos de artistas conocidos con 2+ tiendas en stock y una diferencia creíble, de más a menos ahorro."""
    out = []
    for d in json.loads(DISCOS.read_text(encoding="utf-8")):
        live = sorted((i for i in d["items"] if i.get("st") and i.get("p")), key=lambda i: i["p"])
        if len({i["s"] for i in live}) < 2 or not d.get("img"):
            continue
        lo, hi = live[0], live[-1]
        ahorro = round(hi["p"] - lo["p"], 2)
        # Diferencias absurdas suelen ser ediciones distintas con el mismo código: fuera
        if ahorro < 3 or hi["p"] > 1.45 * lo["p"] or _norm(artista(d["name"])) not in FAMOSOS or d["ean"] in recent:
            continue
        out.append({**d, "artist": artista(d["name"]), "title": d["name"].split(" - ", 1)[1].strip(),
                    "lo": lo["p"], "hi": hi["p"], "ahorro": ahorro, "tienda": TIENDAS.get(lo["s"], lo["s"]),
                    "tiendas": len({i["s"] for i in live}), "url": f"{WEB}/{d['slug']}.html"})
    return sorted(out, key=lambda d: (d["fmt"] != "vinilo", -d["ahorro"]))


def portada(url, dest):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (guitle)"})
    if r.status_code != 200 or len(r.content) < 2000:
        return False
    dest.write_bytes(r.content)
    return True


def generar(day, tipo=None):
    tipo = tipo or DIAS.get(day.weekday())
    if not tipo:
        print("hoy no toca disco")
        return None, None
    hechos = json.loads(HECHOS.read_text(encoding="utf-8")) if HECHOS.exists() else {}
    recent = {v["ean"] for v in hechos.values()}
    folder = ig.OUT / day.isoformat() / "uk" / "discos"
    folder.mkdir(parents=True, exist_ok=True)
    tope = 150 if tipo == "semana" else 60  # «same»: discos a precio normal; la del semana puede ser una edición especial
    for d in [c for c in candidatos(recent) if c["lo"] <= tope][:15]:
        img = folder / f"portada{'.png' if '.png' in d['img'].split('?')[0].lower() else '.jpg'}"
        try:
            ok = portada(d["img"], img)
        except Exception:
            ok = False
        if not ok:
            continue
        d["photo"] = img.name
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
        return folder, plan
    print("no hay disco que publicar hoy")
    return None, None


def publicar(day, folder, plan):
    token = os.environ.get("INSTAGRAM_TOKEN_UK")
    if not token:
        raise SystemExit("falta INSTAGRAM_TOKEN_UK")
    ig.TOKEN = token
    try:
        user = ig.api("GET", "me", fields="user_id")["user_id"]
        hechos = json.loads(HECHOS.read_text(encoding="utf-8")) if HECHOS.exists() else {}
        if day.isoformat() in hechos:
            print("ya publicado hoy:", hechos[day.isoformat()].get("post"))
            return
        rel = folder.relative_to(ROOT).as_posix()
        branch = ig.git("rev-parse", "--abbrev-ref", "HEAD")
        ig.git("add", rel)
        if ig.git("diff", "--cached", "--name-only"):
            ig.git("commit", "-q", "-m", f"social: disco de @guitle.uk {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        base = f"{ig.REPO_RAW}/{ig.git('rev-parse', 'HEAD')}/{rel}/"
        for name in ("post.jpg", "story.jpg"):
            for _ in range(20):
                if requests.head(base + name, timeout=30).status_code == 200:
                    break
        caption = (folder / "texto.txt").read_text(encoding="utf-8").strip()
        post = ig.publish(user, ig.container(user, image_url=base + "post.jpg", caption=caption))
        story = ig.publish(user, ig.container(user, image_url=base + "story.jpg", media_type="STORIES"))
        d = plan["disco"]
        hechos[day.isoformat()] = {"ean": d["ean"], "disco": d["name"], "tipo": plan["tipo"], "ahorro": d["ahorro"],
                                   "url": d["url"], "post": post, "story": story}
        HECHOS.write_text(json.dumps(hechos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        ig.git("add", rel, HECHOS.relative_to(ROOT).as_posix())
        ig.git("commit", "-q", "-m", f"social: publicado el disco de @guitle.uk {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        print("post:", post, "| story:", story, "| página:", d["url"])
    finally:
        ig.TOKEN = None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--tipo", choices=["same", "semana"])
    ap.add_argument("--date")
    a = ap.parse_args(argv)
    day = date.fromisoformat(a.date) if a.date else date.today()
    folder, plan = generar(day, a.tipo)
    if folder:
        d = plan["disco"]
        print(f"{plan['cab']}: {d['name']} ({plan['fmt']}) {gbp(d['lo'])} en {d['tienda']} frente a {gbp(d['hi'])} → {folder}")
        if a.publish:
            publicar(day, folder, plan)


if __name__ == "__main__":
    main()
