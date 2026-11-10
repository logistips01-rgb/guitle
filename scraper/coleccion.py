"""Guitarras de coleccionista (guitle.com/coleccionista/): piezas únicas de Custom Shop, series numeradas,
colaboraciones, aniversarios, ediciones limitadas y modelos signature que se pueden comprar hoy (en stock), sacadas cada
día del catálogo por el nombre del producto. Cada guitarra va a su ficha de guitle, donde se comparan las tiendas.

Reglas para no equivocarse (la información tiene que ser correcta):
  - "LTD" solo cuenta como edición limitada si no es la marca ESP LTD (LTD EC-1000 es un modelo de serie);
  - "Anniversary Green" (Gretsch) es un color: un aniversario necesita su número (75th, 70.º…);
  - una serie numerada necesita "1 of 100", "#R123456", "numbered"…; "3/4" (tamaño) no cuenta.
Cada guitarra va en un solo apartado, el primero que le toque por este orden.

    python -m scraper.coleccion            (España: coleccionista/index.html)
"""
import html
import json
import re

from . import pages

KINDS = ("electrica", "acustica", "clasica", "bajo")  # solo instrumentos
PER_SEC = 48
LTD_BRANDS = {"fender", "squier", "gretsch", "prs", "gibson", "epiphone", "charvel"}
SIGNATURE_MIN = 600  # los signature baratos (de serie, de iniciación) no son de coleccionista

# (clave, regla). El orden decide el apartado de cada guitarra.
RULES = [
    ("unica", re.compile(r"custom\s?shop|master\s?built|murphy\s?lab|\bone[- ]off\b|#\s?[A-Z]{0,3}\d{5,}", re.I)),
    # "1 of 100", "1 de 50" (no "62/63", que son años, ni "3/4", que es el tamaño)
    ("numerada", re.compile(r"\b\d{1,4}\s(?:of|de)\s\d{2,4}\b|\bnumbered\b|\bnumerad[ao]s?\b|\bnummeriert\b|\bnumerot", re.I)),
    ("colab", re.compile(r"pok[eé]mon|pikachu|marvel|star\s?wars|disney|hello\s?kitty|sanrio|minecraft|fortnite|"
                         r"\bnintendo\b|\bsega\b|street\s?fighter|\bnaruto\b|dragon\s?ball|one\s?piece", re.I)),
    ("aniversario", re.compile(r"\b\d{1,3}\s?(?:th|st|nd|rd|\.?º|°)?\s+anniv|\banniversary\s+\d|"
                               r"\b\d{1,3}\.?\s?º?\s+aniversario|\baniversario\s+\d", re.I)),
    ("limitada", re.compile(r"limited|edici[oó]n\s+limitada|\bFSR\b|\bLTD\b", re.I)),
    ("signature", re.compile(r"\bsignature\b|\bsig\.?\s(?:model|series)", re.I)),
]

TXT = {
    "es": {"dir": "coleccionista", "title": "Guitarras de coleccionista",
           "desc": "Piezas únicas de Custom Shop, series numeradas, ediciones limitadas, aniversarios y modelos signature que puedes comprar hoy, con el mejor precio comparado entre tiendas.",
           "intro": "Guitarras que no se ven todos los días: piezas únicas, series numeradas, ediciones limitadas y modelos de artista. Solo las que se pueden comprar hoy, con el mejor precio comparado entre tiendas. Se actualiza cada día.",
           "secs": {"unica": ("Piezas únicas y Custom Shop", "Hechas a mano, con su número de serie: no hay dos iguales."),
                    "numerada": ("Series numeradas", "Tiradas cortas con cada guitarra numerada."),
                    "colab": ("Colaboraciones", "Guitarras de marcas con personajes, juegos y sagas."),
                    "aniversario": ("Ediciones de aniversario", "Modelos que celebran los años de una marca o de un modelo mítico."),
                    "limitada": ("Ediciones limitadas", "Acabados y versiones que se fabrican solo durante un tiempo."),
                    "signature": ("Modelos signature", "Las guitarras de los grandes guitarristas.")},
           "more": "Ver las {n}", "n": "{n} guitarras", "tips_h": "Antes de comprar una guitarra de coleccionista",
           "tips": ["Pide el certificado y el estuche original: en una pieza de colección forman parte de su valor.",
                    "En las piezas únicas, mira que el número de serie de la foto coincide con el de la guitarra que te envían.",
                    "Una edición limitada se agota y no vuelve: si es la que buscas, no esperes mucho a una rebaja.",
                    "Compara: la misma edición limitada puede costar bastante menos en otra tienda."]},
}


def kind_of(p):
    """Apartado de coleccionista de un producto, o None."""
    name = html.unescape(p.get("name") or "")
    brand = (p.get("brand") or "").lower()
    for key, rx in RULES:
        m = rx.search(name)
        if not m:
            continue
        if key == "limitada" and not any(x.group(0).upper() != "LTD" for x in rx.finditer(name)):
            # Solo "LTD": es edición limitada en estas marcas; en las demás es parte del nombre (ESP LTD es una marca;
            # Yamaha Attitude Limited, Jackson LTD Legend…)
            if brand not in LTD_BRANDS:
                continue
        if key == "signature" and _best(p)["p"] < SIGNATURE_MIN:
            continue
        return key
    return None


def _best(p):
    items = [i for i in p.get("items", []) if i.get("p") and i.get("st") is not False]
    return min(items, key=lambda i: i["p"], default=None)


def _bad_thumbs():
    """Miniaturas que no se enseñan: las cortadas (data/fotos-malas.txt, hasta rehacerlas) y las que no son la guitarra
    (data/coleccion-fuera.txt)."""
    bad = set()
    for f in ("fotos-malas.txt", "coleccion-fuera.txt"):
        try:
            bad |= {x for x in (pages.ROOT / "data" / f).read_text(encoding="utf-8").split() if x.endswith(".webp")}
        except FileNotFoundError:
            pass
    return bad


def pick(cats):
    """{apartado: [productos]} con lo que se puede comprar hoy y tiene una buena foto; cada guitarra una vez (la misma
    guitarra con dos fichas, por la foto o por el nombre)."""
    out = {k: [] for k, _ in RULES}
    seen, bad = set(), _bad_thumbs()
    for kind in KINDS:
        for p in (cats.get(kind) or {}).get("products", []):
            if not p.get("slug") or not p.get("th") or p["th"] in bad or not _best(p):
                continue
            ids = {p["slug"], p["th"], re.sub(r"\W+", " ", html.unescape(p.get("name") or "").lower()).strip()}
            if ids & seen:
                continue
            k = kind_of(p)
            if k:
                seen |= ids
                out[k].append(p)
    for k, ps in out.items():
        # Las más especiales primero: las piezas únicas y numeradas por precio; el resto, primero las que más se ahorran
        if k in ("unica", "numerada"):
            ps.sort(key=lambda p: -_best(p)["p"])
        else:
            def save(p):
                prices = [i["p"] for i in p["items"] if i.get("p")]
                return -(max(prices) - _best(p)["p"]) / max(prices), -_best(p)["p"]
            ps.sort(key=save)
    return out


def page(code, cats, intl):
    from . import navidad
    T, t = TXT[code], intl.strings(code)
    names = {k: v for d in cats.values() for k, v in (d.get("stores") or {}).items()}
    money = lambda v: intl.money(v, code)
    pre = "" if code == "es" else f"/{code}"
    url = f"{pre}/{T['dir']}/"
    e = intl.esc
    picked = pick(cats)
    tabs, secs = [], []
    for key, _ in RULES:
        ps = picked[key]
        if not ps:
            continue
        h, sub = T["secs"][key]
        tabs.append(f'<a class="chip" href="#{key}">{e(h)} <span>{len(ps)}</span></a>')
        tiles = "".join(f'<div class="gift">{navidad._tile(code, p, names, money, "").split('<a class="amz"')[0]}</div>' for p in ps[:PER_SEC])
        secs.append(f'  <section class="hub-sec" id="{key}"><h2>{e(h)} <small>{e(T["n"].format(n=len(ps)))}</small></h2>'
                    f'<p class="hub-intro" style="color:var(--text-secondary)">{e(sub)}</p><div class="grid">{tiles}</div></section>')
    tips = "".join(f"<li>{e(x)}</li>" for x in T["tips"])
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": T["title"], "description": T["desc"],
          "url": f"https://guitle.com{url}"}
    head = intl._head(code, f"{T['title']} · guitle", T["desc"], url,
                      f'<meta property="og:title" content="{e(T["title"])}">\n<meta property="og:description" content="{e(T["desc"])}">\n'
                      '<link rel="stylesheet" href="/catalogo.css">\n<style>.hub-sec{margin-top:26px;scroll-margin-top:12px}'
                      '.hub-sec h2{font-size:1.25rem}.hub-sec h2 small{font-size:.8rem;font-weight:500;color:var(--text-secondary)}'
                      '.coll{background:linear-gradient(135deg,#1d1d1f,#3a3226);color:#f5e6c8;border-radius:16px;padding:22px 20px;margin-top:14px}'
                      '.coll h2{color:#f5e6c8;margin:0 0 6px;font-size:1.7rem;letter-spacing:-.03em}.coll p{margin:0;opacity:.9}'
                      '.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.chip{padding:6px 12px;border-radius:999px;'
                      'border:1.5px solid var(--border,#ddd);text-decoration:none;color:inherit;font-weight:600;font-size:.9rem}'
                      '.chip span{color:var(--text-secondary);font-weight:500}.gift{min-width:0;display:flex}.gift .tile{flex:1;min-width:0}'
                      '.gift .name{overflow-wrap:anywhere}</style>\n'
                      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    return (head + "</head>\n<body>\n<main>\n"
            f'  <div class="topbar"><div class="row">{intl._logo(code, t)}<a class="navlink" href="{pre}/">{e(t["home"])}</a></div></div>\n'
            f'  <div class="coll"><h2>{e(T["title"])}</h2><p>{e(T["intro"])}</p></div>\n'
            f'  <nav class="chips">{"".join(tabs)}</nav>\n'
            + "\n".join(secs)
            + f'\n  <section class="hub-sec" style="max-width:780px"><h2>{e(T["tips_h"])}</h2><ul style="line-height:1.7">{tips}</ul></section>\n'
            f'  {intl._foot(code, t)}\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n'), url, picked


def spain_cats():
    cats = {}
    for kind in KINDS:
        k = pages.KINDS[kind]
        try:
            d = json.loads((pages.ROOT / k["src"]).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        cats[kind] = {"products": list(d.get("products", [])), "stores": dict(d.get("stores", {}))}
    return cats


def write_spain():
    from . import intl
    html_, url, picked = page("es", spain_cats(), intl)
    pages._write(pages.ROOT / TXT["es"]["dir"] / "index.html", html_)
    return url, {k: len(v) for k, v in picked.items()}


if __name__ == "__main__":
    print(write_spain())
