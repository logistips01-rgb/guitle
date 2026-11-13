"""Sección de discos de los países que aún no tienen tiendas de discos leídas, solo con Amazon (y eBay).

Manuel (13/11/2026): "arranca con el botón de Amazon y luego ves llenando país a país con más tiendas". Cada país tiene
una página (/<país>/<carpeta>/index.html) con un buscador de discos en Amazon (con el código de afiliado del país, la
categoría de música) y en eBay, y los discos más comparados de guitle con su botón de Amazon. Sin precios: no se
inventa ninguno; cuando un país tenga tiendas leídas (scraper/musica.py) su sección pasa a ser la de musica.py y
sale de STARTER.

  python -m scraper.discos_amazon            # escribe las páginas de todos los países de STARTER
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

from . import intl, mercados

ROOT = Path(__file__).resolve().parent.parent
esc = lambda s: html.escape(str(s or ""), quote=True)

# Carpeta de la sección y textos por idioma (intl.SITES[país]["t"])
TXT = {
    "de": {"dir": "schallplatten", "home": "Schallplatten", "title": "Schallplatten, CDs und Kassetten",
           "intro": "Finde jede Schallplatte, CD oder Kassette. Bald vergleichen wir hier auch die Preise der Plattenläden; bis dahin suchst du direkt bei Amazon oder eBay.",
           "ph": "Künstler oder Album", "go": "Bei Amazon suchen", "popular": "Beliebte Alben auf Vinyl"},
    "cs": {"dir": "desky", "home": "Desky", "title": "Vinylové desky, CD a kazety",
           "intro": "Najděte jakoukoli desku, CD nebo kazetu. Brzy tu budeme porovnávat i ceny obchodů s deskami; zatím hledejte přímo na Amazonu nebo eBay.",
           "ph": "Interpret nebo album", "go": "Hledat na Amazonu", "popular": "Oblíbená alba na vinylu"},
    "sk": {"dir": "platne", "home": "Platne", "title": "Vinylové platne, CD a kazety",
           "intro": "Nájdite akúkoľvek platňu, CD alebo kazetu. Čoskoro tu budeme porovnávať aj ceny obchodov s platňami; zatiaľ hľadajte priamo na Amazone alebo eBay.",
           "ph": "Interpret alebo album", "go": "Hľadať na Amazone", "popular": "Obľúbené albumy na vinyle"},
    "hu": {"dir": "lemezek", "home": "Lemezek", "title": "Bakelitlemezek, CD-k és kazetták",
           "intro": "Találj meg bármilyen lemezt, CD-t vagy kazettát. Hamarosan itt a lemezboltok árait is összehasonlítjuk; addig keress közvetlenül az Amazonon vagy az eBay-en.",
           "ph": "Előadó vagy album", "go": "Keresés az Amazonon", "popular": "Népszerű albumok bakeliten"},
    "ro": {"dir": "viniluri", "home": "Viniluri", "title": "Viniluri, CD-uri și casete",
           "intro": "Găsește orice vinil, CD sau casetă. În curând vom compara aici și prețurile magazinelor de discuri; până atunci, caută direct pe Amazon sau eBay.",
           "ph": "Artist sau album", "go": "Caută pe Amazon", "popular": "Albume populare pe vinil"},
    "bg": {"dir": "plochi", "home": "Плочи", "title": "Грамофонни плочи, CD и касети",
           "intro": "Намерете всяка плоча, CD или касета. Скоро тук ще сравняваме и цените на магазините за плочи; дотогава търсете директно в Amazon или eBay.",
           "ph": "Изпълнител или албум", "go": "Търси в Amazon", "popular": "Популярни албуми на винил"},
    "el": {"dir": "diskoi", "home": "Δίσκοι", "title": "Δίσκοι βινυλίου, CD και κασέτες",
           "intro": "Βρείτε οποιονδήποτε δίσκο, CD ή κασέτα. Σύντομα θα συγκρίνουμε εδώ και τις τιμές των δισκοπωλείων· μέχρι τότε, αναζητήστε απευθείας στο Amazon ή στο eBay.",
           "ph": "Καλλιτέχνης ή άλμπουμ", "go": "Αναζήτηση στο Amazon", "popular": "Δημοφιλή άλμπουμ σε βινύλιο"},
    "fi": {"dir": "levyt", "home": "Levyt", "title": "Vinyylilevyt, CD:t ja kasetit",
           "intro": "Löydä mikä tahansa levy, CD tai kasetti. Pian vertailemme täällä myös levykauppojen hintoja; siihen asti hae suoraan Amazonista tai eBaysta.",
           "ph": "Artisti tai albumi", "go": "Hae Amazonista", "popular": "Suosittuja albumeja vinyylinä"},
    "da": {"dir": "plader", "home": "Plader", "title": "Vinylplader, cd'er og kassettebånd",
           "intro": "Find enhver plade, cd eller kassette. Snart sammenligner vi også pladebutikkernes priser her; indtil da kan du søge direkte på Amazon eller eBay.",
           "ph": "Kunstner eller album", "go": "Søg på Amazon", "popular": "Populære album på vinyl"},
    "nb": {"dir": "plater", "home": "Plater", "title": "Vinylplater, CD-er og kassetter",
           "intro": "Finn enhver plate, CD eller kassett. Snart sammenligner vi også prisene i platebutikkene her; inntil da kan du søke direkte på Amazon eller eBay.",
           "ph": "Artist eller album", "go": "Søk på Amazon", "popular": "Populære album på vinyl"},
}
# Países con sección solo de Amazon: los de Amazon.de (código guitle0f-21) sin tiendas de discos leídas todavía
# (Alemania ya tiene las suyas desde el 13/11/2026: scraper/musica.py)
STARTER = ["at", "ch", "cz", "sk", "hu", "ro", "bg", "gr", "fi", "dk", "no"]
N_POPULAR = 48


def section(code):
    """(carpeta, nombre) de la sección de un país de STARTER, o None."""
    if code not in STARTER or not intl.SITES[code].get("amazon"):
        return None
    T = TXT[intl.SITES[code]["t"]]
    return T["dir"], T["home"]


def _popular():
    """Los discos de vinilo más conocidos: los que están en más países y tiendas de guitle (mismo código de barras)."""
    from . import musica
    seen, best = {}, {}
    for c in ("uk", "es", "fr", "it", "pt"):
        for d in musica._load(ROOT / "data" / "musica" / c / "discos.json", []):
            if (d["fmt"] != "vinilo" or not d.get("img") or " - " not in d["name"]
                    or re.search(r"(?i)reissues|\bneuf\b|- -|translucent|pearly", d["name"])):  # nombres de serie o de anuncio
                continue
            e = d["ean"].zfill(13)
            n = seen.setdefault(e, [0, 0])
            n[0] += 1
            n[1] += len(d["items"])
            if c == "uk" or e not in best:  # el nombre en inglés si está en Reino Unido
                best[e] = d
    order = sorted(seen, key=lambda e: (-seen[e][0], -seen[e][1], best[e]["name"]))
    out, artists = [], set()
    for e in order:  # un disco por artista, para que haya variedad
        a = re.sub(r"^the |\s*\(the\)", "", best[e]["name"].split(" - ")[0].strip().lower())
        if a not in artists:
            artists.add(a)
            out.append(best[e])
        if len(out) == N_POPULAR:
            break
    return out


def page(code, popular):
    from . import musica
    s, t = intl.SITES[code], intl.strings(code)
    T = TXT[s["t"]]
    amz = s["amazon"]  # https://www.amazon.de/s?k={q}&tag=…
    base, tag = amz.split("?")[0], amz.split("tag=")[1]
    label = mercados.TXT.get(s["t"], mercados.TXT["en"])[0]
    url = f"/{code}/{T['dir']}/"
    btn = ('display:block;text-align:center;margin-top:8px;padding:9px 10px;border-radius:10px;background:#FF9900;'
           'color:#111;font-weight:700;font-size:.9rem;text-decoration:none')
    cards = "".join(
        f'<div class="card" style="display:flex;flex-direction:column"><div class="img"><img src="{esc(musica._img(d["img"], 300))}" '
        f'alt="{esc(d["name"])}" loading="lazy"></div><div class="body" style="flex:1"><span class="name">{esc(d["name"])}</span></div>'
        f'<a href="{esc(amz.format(q=quote_plus(d["name"].replace(" - ", " ") + " vinyl")))}&i=popular" target="_blank" '
        f'rel="sponsored noopener" style="{btn}">{esc(label)} →</a></div>'
        for d in popular)
    ebay = mercados.ebay_url(code, "vinyl")
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": T["title"], "url": intl.SITE + url}
    head = intl._head(code, f"{T['title']} · guitle", T["intro"], url,
                      '<link rel="stylesheet" href="/catalogo.css">\n'
                      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>')
    return f"""{head}
<body>
<main>
  <div class="topbar"><div class="row">{intl._logo(code, t)}</div></div>
  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{esc(T['title'])}</h2>
  <p class="muted">{esc(T['intro'])}</p>
  <form action="{esc(base)}" method="get" target="_blank" style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 6px">
    <input class="search" name="k" type="search" required placeholder="{esc(T['ph'])}" aria-label="{esc(T['ph'])}" style="flex:1 1 240px;margin:0">
    <input type="hidden" name="i" value="popular"><input type="hidden" name="tag" value="{esc(tag)}">
    <button type="submit" style="flex:0 0 auto;padding:12px 18px;border:0;border-radius:12px;background:#FF9900;color:#111;font-weight:700;font-size:1rem;cursor:pointer">{esc(T['go'])} →</button>
  </form>
  <p class="small"><a href="{esc(ebay)}" target="_blank" rel="sponsored noopener">{esc(mercados.TXT.get(s['t'], mercados.TXT['en'])[1])} →</a></p>
  <section><h3>{esc(T['popular'])}</h3><div class="grid">{cards}</div></section>
  {intl._foot(code, t)}
</main>
<script src="/c.js" defer></script>
</body>
</html>
"""


def write():
    popular = _popular()
    out = []
    for code in STARTER:
        if not section(code):
            continue
        d = ROOT / code / TXT[intl.SITES[code]["t"]]["dir"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(code, popular), encoding="utf-8")
        out.append(f"{code}/{d.name}")
    print("discos (solo Amazon):", " ".join(out), f"· {len(popular)} discos populares", flush=True)
    return out


if __name__ == "__main__":
    write()
