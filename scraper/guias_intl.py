"""Guías de compra en la web de cada país (/<país>/guias/…), en su idioma, con sus guitarras, tiendas y moneda.

Los textos están en scraper/guias_i18n/<idioma>.py (GUIDES, INDEX); aquí se monta cada página con la cabecera y el pie
del país (intl) y las fichas más vendidas de su catálogo. Las cantidades del texto van como {p150}, {p300}… y salen en
la moneda del país (en Brasil, en reales redondos). Una guía sin fichas en ese país (p. ej. sin catálogo de bajos) no se
escribe.
"""
import html
import importlib
import json
from datetime import date

from . import pages

esc = lambda v: html.escape(str(v or ""), quote=True)

# Cantidades redondas en cada moneda (el euro, la libra y el franco suizo van a la par para esto).
NICE = {"BRL": {30: 200, 50: 300, 100: 600, 150: 1000, 200: 1200, 300: 2000, 400: 2500, 500: 3000, 1000: 6000},
        "PLN": {30: 150, 50: 200, 100: 400, 150: 600, 200: 800, 300: 1200, 400: 1700, 500: 2000, 1000: 4000},
        "CZK": {30: 750, 50: 1200, 100: 2500, 150: 3500, 200: 5000, 300: 7500, 400: 10000, 500: 12000, 1000: 25000},
        "HUF": {30: 12000, 50: 20000, 100: 40000, 150: 60000, 200: 80000, 300: 120000, 400: 160000, 500: 200000, 1000: 400000},
        "RON": {30: 150, 50: 250, 100: 500, 150: 750, 200: 1000, 300: 1500, 400: 2000, 500: 2500, 1000: 5000},
        "SEK": {30: 300, 50: 500, 100: 1000, 150: 1500, 200: 2000, 300: 3000, 400: 4500, 500: 5500, 1000: 11000},
        "NOK": {30: 300, 50: 500, 100: 1000, 150: 1500, 200: 2000, 300: 3000, 400: 4500, 500: 6000, 1000: 12000},
        "DKK": {30: 200, 50: 400, 100: 750, 150: 1100, 200: 1500, 300: 2200, 400: 3000, 500: 3700, 1000: 7500}}


def _lang_module(lang):
    try:
        return importlib.import_module(f".guias_i18n.{lang}", __package__)
    except ModuleNotFoundError:
        return None


def _amount(v, code, intl):
    cur = intl.SITES[code]["cur"]
    v = NICE.get(cur, {}).get(v, v)
    txt = intl.money(v, code)
    return txt.replace(",00", "") if cur == "BRL" else txt


def _tile(code, p, names, intl, t):
    best = p["items"][0]
    n = len({i["s"] for i in p["items"]})
    img = f'<img loading="lazy" src="/img/p/{esc(p["th"])}" alt="">' if p.get("th") else ""
    return (f'<a class="tile" href="/{code}/g/{esc(p["slug"])}.html"><div class="img">{img}</div><div class="body">'
            f'<span class="brand">{esc(p.get("brand"))}</span><span class="name">{esc(html.unescape(p["name"]))}</span>'
            f'<span class="price"><strong>{intl.money(best["p"], code)}</strong></span><span class="foot">'
            f'<span>{esc(names.get(best["s"], best["s"]))}</span><span class="stores-n">{n}</span></span></div></a>')


def _pick(products, max_price, n, min_stores, guitar):
    from .guias import _pick as pick_es
    return pick_es(products, max_price, n, min_stores, guitar)


def write(code, cats, intl):
    """Escribe las guías del país; devuelve sus URL (para su sitemap)."""
    s = intl.SITES[code]
    mod = _lang_module(s["t"])
    if not mod:
        return []
    t = intl.strings(code)
    names = {k: v for d in cats.values() for k, v in d["stores"].items()}
    shops = len(names)
    fmt = {f"p{v}": _amount(v, code, intl) for v in (30, 50, 100, 150, 200, 300, 400, 500, 1000)} | {"shops": shops}
    out = pages.ROOT / code / "guias"
    urls, done = [], []
    for g in mod.GUIDES:
        grids, any_tiles = [], False
        for kind, maxp, n, min_stores, guitar, title in g["grids"]:
            prods = cats.get(kind, {}).get("products", [])
            if kind == "pack":
                prods = prods + cats.get("packac", {}).get("products", [])
            limit = NICE.get(s["cur"], {}).get(maxp, maxp)
            # En países con pocas tiendas, una guitarra rara vez está en tres: se baja el mínimo.
            ms = 1 if shops < 4 else (min(min_stores, 2) if shops < 15 else min_stores)
            picked = _pick(prods, limit, n, ms, guitar)
            if not picked:
                continue
            any_tiles = True
            page = s["kinds"].get(kind) or (intl.PACK_PAGE.get(s["t"]) if kind == "pack" and hasattr(intl, "PACK_PAGE") else None)
            more = f' <a class="navlink" href="/{code}/{page}.html">{esc(mod.MORE)} →</a>' if isinstance(page, str) else ""
            tiles = "".join(_tile(code, p, names, intl, t) for p in picked)
            grids.append(f'<section class="hub-sec"><h2>{esc(title.format_map(fmt))}{more}</h2><div class="grid">{tiles}</div></section>')
        if not any_tiles:
            continue
        url = f"/{code}/guias/{g['slug']}.html"
        body = g["body"].format_map(fmt)
        faqs = [(q.format_map(fmt), a.format_map(fmt)) for q, a in g["faqs"]]
        pages._write(out / f"{g['slug']}.html", _page(code, url, g["title"], g["desc"].format_map(fmt), body, grids, faqs, mod, intl, t))
        urls.append(url)
        done.append((url, g["title"], g["desc"].format_map(fmt)))
    if urls:
        if mod.COURSE_URL and (pages.ROOT / code / mod.COURSE_URL / "index.html").exists():
            done.append((f"/{code}/{mod.COURSE_URL}", mod.COURSE_TITLE, mod.COURSE_DESC))
        lis = "".join(f'<li><a href="{u}"><strong>{esc(ti)}</strong></a><br>{esc(d)}</li>' for u, ti, d in done)
        pages._write(out / "index.html", _page(code, f"/{code}/guias/", mod.INDEX_TITLE, mod.INDEX_DESC,
                                                f'<section class="hub-sec guia"><ul>{lis}</ul></section>', [], [], mod, intl, t))
        urls.insert(0, f"/{code}/guias/")
    return urls


def _page(code, url, title, desc, body, grids, faqs, mod, intl, t):
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
           "dateModified": date.today().isoformat(), "inLanguage": intl.SITES[code]["lang"],
           "publisher": {"@type": "Organization", "name": "guitle", "url": "https://guitle.com"}}]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage",
                   "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
    style = ("<link rel=\"stylesheet\" href=\"/catalogo.css\">\n<style>.hub-sec{margin-top:26px}.hub-sec h2{font-size:1.15rem;margin:0 0 10px}"
             ".guia{max-width:780px;line-height:1.65}.guia h2{font-size:1.2rem;margin:26px 0 6px}.guia p,.guia li{color:var(--text-secondary)}"
             ".guia strong{color:var(--text-primary)}.faq details{border-bottom:1px solid var(--border);padding:10px 0}"
             ".faq summary{cursor:pointer;font-weight:600}.faq p{color:var(--text-secondary);margin:8px 0 0}</style>\n"
             + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))
    faq_html = (f'<section class="hub-sec faq guia"><h2>{esc(mod.FAQ)}</h2>'
                + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs) + "</section>") if faqs else ""
    return (intl._head(code, f"{title} · guitle", desc, url, style) + "</head>\n<body>\n<main>\n"
            f'  <div class="topbar"><div class="row">{intl._logo(code, t)}<a class="navlink" href="/{code}/guias/">{esc(mod.GUIDES_WORD)}</a></div></div>\n'
            f'  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{esc(title)}</h2>\n'
            f'  <p class="hub-intro" style="color:var(--text-secondary);max-width:780px">{esc(desc)}</p>\n'
            f'  {body}\n  {"".join(grids)}\n  {faq_html}\n  {intl._foot(code, t)}\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n')


# --- Curso "Tu primera guitarra" en el idioma del país (/<país>/<curso>/) ---------------------------------------
# scraper/curso/plantilla.html lleva los textos como {{n}}; scraper/curso/<idioma>.json, sus traducciones (180, en el
# mismo orden que es.json). Un portugués para Portugal y Brasil.
COURSE_LANG = {"pt": "pt", "br": "pt", "fr": "fr", "it": "it", "en": "en", "de": "de", "nl": "nl",
               **{x: x for x in ("pl", "cs", "sk", "hu", "ro", "bg", "el", "fi", "sv", "nb", "da")}}


def write_course(code, intl):
    """Escribe el curso del país; devuelve su URL o None."""
    import re
    s = intl.SITES[code]
    mod, lang = _lang_module(s["t"]), COURSE_LANG.get(s["t"])
    folder = pages.ROOT / "scraper" / "curso"
    if not mod or not lang or not (folder / f"{lang}.json").exists():
        return None
    texts = json.loads((folder / f"{lang}.json").read_text(encoding="utf-8"))
    tpl = (folder / "plantilla.html").read_text(encoding="utf-8")
    page = re.sub(r"\{\{(\d+)\}\}", lambda m: texts[int(m.group(1))], tpl)
    url = f"/{code}/{mod.COURSE_URL}"
    ld = {"@context": "https://schema.org", "@type": "Course", "name": mod.COURSE_TITLE, "description": mod.COURSE_DESC,
          "inLanguage": s["lang"], "isAccessibleForFree": True, "provider": {"@type": "Organization", "name": "guitle", "url": "https://guitle.com"}}
    page = page.replace('<html lang="es">', f'<html lang="{s["lang"]}">', 1)
    page = re.sub(r"<title>[^<]*</title>", f"<title>{esc(mod.COURSE_TITLE)} · guitle</title>", page, count=1)
    page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(mod.COURSE_DESC)}">', page, count=1)
    page = page.replace('href="https://guitle.com/curso/"', f'href="https://guitle.com{url}"', 1)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>', page, count=1)
    page = page.replace('href="/guias/primera-guitarra-electrica.html"', f'href="/{code}/guias/{mod.GUIDES[0]["slug"]}.html"')
    page = page.replace('href="/guias/guitarra-clasica-o-acustica.html"', f'href="/{code}/guias/{mod.GUIDES[1]["slug"]}.html"')
    page = page.replace('href="/"', f'href="/{code}/"')
    pages._write(pages.ROOT / code / mod.COURSE_URL / "index.html", page)
    return url
