"""Música grabada (vinilos, CD y casetes): tiendas de discos, el mismo disco por su código de barras (EAN) y una página
por disco con su precio en cada tienda. Objetivo: tráfico de búsqueda ("<disco> vinyl price").

De momento Reino Unido, con tiendas de discos en Shopify: el catálogo sale de /products.json (paginado) y el código
de barras de la ficha de cada producto (/products/<handle>.json), que se guarda para no volver a pedirlo. Siempre con
robots.txt y las pausas de siempre (scraper.fetch). Para España y el resto: los ficheros de producto de los programas
de afiliados (Awin), cuando los haya.

  python -m scraper.musica --pais uk --minutes 120   # lee (catálogos y códigos nuevos) y genera las páginas
  python -m scraper.musica --pais uk --build         # solo las páginas, con lo guardado
"""
import argparse
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "musica"

STORES = {
    "uk": {"recordstore": ("Recordstore", "https://www.recordstore.co.uk"),
           "assai": ("Assai Records", "https://www.assai.co.uk"),
           "sisterray": ("Sister Ray", "https://www.sisterray.co.uk"),
           "drift": ("Drift Records", "https://www.driftrecords.com"),
           "crash": ("Crash Records", "https://www.crashrecords.co.uk")},
}
# Formato por el título, el tipo o la variante; lo demás (camisetas, chapas, bolsas, tocadiscos…) no entra.
FORMATS = [("casete", r"\bcassette|\bcass\b|\btape\b|\bmc\b"), ("cd", r"\bcd\b|\bcds\b|compact disc"),
           ("vinilo", r"vinyl|\blp\b|\b2lp\b|\b3lp\b|\b12\"|\b7\"|\b10\"|\b12 inch|\b7 inch|\bep\b")]
NOT_MUSIC = re.compile(r"(?i)t-?shirt|\btee\b|hoodie|sweat|badge|tote|\bbag\b|slipmat|poster|turntable|record player|"
                       r"gift card|voucher|cleaning|sleeve[s]? pack|inner sleeves|outer sleeves|mug\b|\bhat\b|cap\b|book\b")
CLEAN = re.compile(r"(?i)\s*[\(\[]?(?:\*?pre-?order\*?|due out[^\)\]]*|signed|indie exclusive|limited edition|"
                   r"vinyl lp|vinyl|\blp\b|\b2lp\b|\bcd\b|cassette|\btape\b)[\)\]]?\s*")


def _fmt(*texts):
    t = " ".join(x or "" for x in texts).lower()
    for f, rx in FORMATS:
        if re.search(rx, t):
            return f
    return None


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:90]


def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def read(pais, minutes):
    """Catálogo de cada tienda y códigos de barras que faltan, hasta agotar el tiempo."""
    from .fetch import Fetcher
    folder = DATA / pais
    catalog = _load(folder / "tiendas.json", {})   # {tienda: {handle: {t, v, ty, f, p, st, img}}}
    codes = _load(folder / "codigos.json", {})     # {tienda: {handle: ean o ""}}
    end = time.time() + minutes * 60
    fetcher = Fetcher(delay=(1.0, 2.0))
    fresh = (folder / "tiendas.json").exists() and time.time() - (folder / "tiendas.json").stat().st_mtime < 20 * 3600
    for sid, (name, base) in ([] if fresh else STORES[pais].items()):  # catálogos: una vez al día
        if time.time() > end:
            break
        items, page = {}, 1
        while time.time() < end and page <= 400:
            url = f"{base}/products.json?limit=250&page={page}"
            if not fetcher.allowed(url)[0]:
                break
            try:
                r = fetcher.get(url)
                prods = r.json().get("products", []) if r.status_code == 200 else []
            except Exception:  # noqa: BLE001
                break
            if not prods:
                break
            for p in prods:
                v = (p.get("variants") or [{}])[0]
                f = _fmt(p.get("title"), p.get("product_type"), " ".join(p.get("tags") or []), v.get("title"))
                if not f or NOT_MUSIC.search(p.get("title", "")):
                    continue
                try:
                    price = float(v.get("price"))
                except (TypeError, ValueError):
                    continue
                img = ((p.get("images") or [{}])[0]).get("src")
                items[p["handle"]] = {"t": p.get("title", ""), "v": p.get("vendor", ""), "ty": p.get("product_type", ""),
                                      "f": f, "p": price, "st": bool(v.get("available")), "img": img}
            page += 1
        if items:
            catalog[sid] = items
            print(f"[{sid}] {len(items)} discos", flush=True)
    if not fresh:
        _save(folder / "tiendas.json", catalog)
    # Códigos de barras: de la ficha de cada disco, una vez
    # Una tienda por hilo, cada una con su Fetcher y sus pausas: avanzan a la vez sin apretar a ninguna.
    from concurrent.futures import ThreadPoolExecutor
    import threading
    lock, count = threading.Lock(), [0]

    def store_codes(sid):
        f = Fetcher(delay=(1.0, 2.0))
        base = STORES[pais][sid][1]
        todo = [h for h in catalog.get(sid, {}) if h not in codes.get(sid, {})]
        for h in todo:
            if time.time() > end:
                return
            url = f"{base}/products/{h}.json"
            if not f.allowed(url)[0]:
                return
            try:
                r = f.get(url)
                vs = r.json()["product"]["variants"] if r.status_code == 200 else []
                ean = re.sub(r"\D", "", str((vs[0] if vs else {}).get("barcode") or "")).lstrip("0")
            except Exception:  # noqa: BLE001
                continue
            with lock:
                codes.setdefault(sid, {})[h] = ean.zfill(13) if 11 <= len(ean) <= 13 else ""  # GTIN-14 con ceros: EAN
                count[0] += 1
                if count[0] % 500 == 0:
                    _save(folder / "codigos.json", codes)
    print(f"códigos por pedir: {sum(len([h for h in its if h not in codes.get(sid, {})]) for sid, its in catalog.items())}", flush=True)
    with ThreadPoolExecutor(len(catalog) or 1) as ex:
        list(ex.map(store_codes, list(catalog)))
    _save(folder / "codigos.json", codes)
    print(f"códigos nuevos: {count[0]}", flush=True)


def build_data(pais):
    """Discos agrupados por código de barras: [{ean, name, fmt, img, items: [{s, p, u, st}]}]."""
    folder = DATA / pais
    catalog, codes = _load(folder / "tiendas.json", {}), _load(folder / "codigos.json", {})
    by = {}
    for sid, its in catalog.items():
        base = STORES[pais][sid][1]
        for h, it in its.items():
            ean = codes.get(sid, {}).get(h)
            if not ean:
                continue
            ean = ean.zfill(13)
            d = by.setdefault(ean, {"ean": ean, "names": [], "fmt": it["f"], "img": None, "items": []})
            artist = {"recordstore": it["v"], "sisterray": it["ty"]}.get(sid, "")
            title = it["t"]
            if artist and " - " not in title and not title.lower().startswith(artist.lower()):
                title = f"{artist} - {re.sub(r':\s*(?:CD|Vinyl LP|Cassette)\s*$', '', title)}"
            d["names"].append(title)
            d["img"] = d["img"] or it.get("img")
            d["items"].append({"s": sid, "p": it["p"], "u": f"{base}/products/{h}", "st": it["st"]})
    out = []
    for d in by.values():
        # El nombre más limpio: con "Artista - Título" y sin coletillas de formato o reserva
        names = sorted(d.pop("names"), key=lambda n: (" - " not in n, len(n)))
        name = re.sub(r"\s{2,}", " ", CLEAN.sub(" ", names[0])).strip(" -–:*")
        items = {}
        for i in sorted(d["items"], key=lambda i: (not i["st"], i["p"])):
            items.setdefault(i["s"], i)  # una oferta por tienda
        d["items"] = sorted(items.values(), key=lambda i: (not i["st"], i["p"]))
        d["name"] = name
        d["slug"] = f"{slug(name)}-{ {'vinilo': 'vinyl', 'cd': 'cd', 'casete': 'cassette'}[d['fmt']] }-{d['ean']}"
        out.append(d)
    out.sort(key=lambda d: (-len(d["items"]), d["name"]))
    # En git solo los que se comparan (dos o más tiendas): son los que tienen página. El catálogo de cada tienda
    # (tiendas.json) no se guarda en git: se vuelve a leer cada día.
    out = [d for d in out if len(d["items"]) >= 2]
    _save(folder / "discos.json", out)
    return out


# --- Páginas ---------------------------------------------------------------------------------------------------
TXT = {"uk": {"dir": "records", "one": "record", "home": "Records", "promo": "New: compare vinyl, CD & cassette prices", "tile": "Vinyl, CDs & cassettes", "fmts": {"vinilo": ("Vinyl", "vinyl"), "cd": ("CDs", "cds"),
                                                                                 "casete": ("Cassettes", "cassettes")},
              "fmt1": {"vinilo": "vinyl", "cd": "CD", "casete": "cassette"},
              "title": "{n} {f}: price comparison", "desc": "Compare the price of {n} on {f} in {k} UK record shops: today's price, stock and the cheapest shop.",
              "h_index": "Records: compare vinyl, CD and cassette prices", "d_index": "Compare the price of vinyl records, CDs and cassettes in UK record shops, every day.",
              "in_stock": "In stock", "out": "Out of stock", "shops": "shops", "buy": "Go to shop", "cheapest": "Cheapest today",
              "more": "Most compared", "note": "Prices include VAT; delivery may vary by shop.",
              "amazon": "https://www.amazon.co.uk/s?k={ean}&tag=guitle08-21", "amazon_btn": "Search this record on Amazon",
              "amazon_txt": "Prefer to buy on Amazon?",
              "search_ph": "Search records: artist or album…", "search_res": "{n} records found", "search_none": "No records found",
              "f_artist": "Artist or band", "f_format": "Format", "f_all": "All formats", "f_sort": "Sort",
              "s_price": "Cheapest first", "s_shops": "Most compared", "s_az": "A–Z",
              "artist_t": "{a}: vinyl, CD and cassette prices", "artist_d": "Compare the price of {n} {a} records on vinyl, CD and cassette in UK record shops.",
              "artist_all": "All their records",
              "deals": "Vinyl & CD deals", "deals_file": "deals", "save": "save {m} vs the dearest shop",
              "deals_desc": "The records with the biggest price difference between UK shops today (in stock only).",
              "guitars": "Guitar deals today", "guitars_more": "All guitar deals",
              "guide_file": "where-to-buy-vinyl-uk", "guide": "Where to buy vinyl cheapest in the UK",
              "guide_desc": "How to find the cheapest price for a vinyl record, CD or cassette in the UK: compare record shops, watch editions and delivery, with today's biggest savings.",
              "guide_body": """<section class="hub-sec guia" style="max-width:780px;line-height:1.65">
<h2>The same record can cost very different prices</h2>
<p>UK record shops price the same pressing differently, and the gap is often <strong>£5 to £20</strong> on new vinyl. Before buying, compare the exact same edition (same barcode) across shops: guitle does that every day for {shops} UK record shops and shows the cheapest one with stock.</p>
<h2>Check the edition</h2>
<ul>
<li><strong>Standard black vinyl</strong> is usually the cheapest pressing.</li>
<li><strong>Coloured, indie-exclusive or signed editions</strong> cost more and sell out fast: compare like with like.</li>
<li><strong>Reissues and remasters</strong> have their own barcode: a 2023 reissue is a different record from the original pressing.</li>
</ul>
<h2>Don't forget delivery</h2>
<p>Most UK record shops offer free delivery above a minimum order (often around £40 to £60). If you're buying one record, a slightly higher price with free delivery can work out cheaper.</p>
<h2>Pre-orders</h2>
<p>New releases are often cheapest on pre-order, and prices tend to rise once the first pressing sells out.</p>
</section>""",
              "faqs": [("Where is the cheapest place to buy vinyl in the UK?", "It depends on the record: the same pressing can be several pounds cheaper in one shop than another. Compare the exact edition (by barcode) across UK record shops before buying."),
                       ("Why is the same vinyl record different prices in different shops?", "Each shop sets its own price and runs its own offers, and stock levels change daily, so the cheapest shop for a record changes over time."),
                       ("Are coloured vinyl editions worth the extra cost?", "They're collectable and often limited, but the music is the same: if you just want to listen, the standard black pressing is usually cheaper.")]}}


def _e(v):
    return html.escape(str(v or ""), quote=True)


def write_pages(pais, discs=None):
    """Página de cada disco que está en dos o más tiendas, listados por formato y el índice. Devuelve sus URL."""
    from . import intl, pages
    if pais not in TXT:
        return []
    discs = discs if discs is not None else _load(DATA / pais / "discos.json", [])
    if not discs:
        return []
    T, t = TXT[pais], intl.strings(pais)
    names = {sid: n for sid, (n, _) in STORES[pais].items()}
    out = ROOT / pais / T["dir"]
    css = ('<link rel="stylesheet" href="/catalogo.css">\n<style>.disc{display:grid;grid-template-columns:minmax(0,260px) 1fr;gap:24px;'
           'margin-top:16px}.disc img{width:100%;border-radius:12px;background:#fff}.offers{width:100%;border-collapse:collapse}'
           '.offers td{padding:10px 6px;border-bottom:1px solid var(--border)}.offers .p{font-weight:700;text-align:right;'
           'font-variant-numeric:tabular-nums}.offers .st{color:var(--text-muted);font-size:.85rem}@media(max-width:640px)'
           '{.disc{grid-template-columns:1fr}}.dl{display:grid;gap:8px}.dl a{display:flex;justify-content:space-between;gap:12px;'
           'padding:10px 12px;border:1px solid var(--border);border-radius:10px;color:var(--text-primary);text-decoration:none}'
           '.dl a:hover{border-color:var(--accent)}.dl small{color:var(--text-muted)}</style>\n')
    top = f'  <div class="topbar"><div class="row">{intl._logo(pais, t)}<a class="navlink" href="/{pais}/{T["dir"]}/">{_e(T["home"])}</a></div></div>\n'

    def page(url, title, desc, body, ld=None):
        extra = css + (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' if ld else "")
        return (intl._head(pais, f"{title} · guitle", desc, url, extra) + "</head>\n<body>\n<main>\n" + top
                + f'  <h2 style="font-size:1.6rem;margin:18px 0 6px;letter-spacing:-.03em">{_e(title)}</h2>\n{body}\n  '
                + intl._foot(pais, t) + '\n</main>\n<script src="/c.js" defer></script>\n</body>\n</html>\n')

    urls, keep = [], set()
    multi = [d for d in discs if len(d["items"]) >= 2]
    # Chollos de guitarras del día en cada disco (y discos en las fichas de guitarras): un público lleva al otro
    guitar_box = ""
    try:
        cats = intl.catalogs(pais)
        gs = [p for k in ("electrica", "acustica", "clasica") for p in cats.get(k, {}).get("products", [])
              if p.get("slug") and p.get("th") and len({i["s"] for i in p["items"]}) >= 2]
        gap_g = lambda p: (max(i["p"] for i in p["items"]) - p["items"][0]["p"]) / max(i["p"] for i in p["items"])
        gs = sorted((p for p in gs if 0.05 <= gap_g(p) <= 0.4), key=gap_g, reverse=True)[:4]
        gnames = {k: v for d in cats.values() for k, v in d["stores"].items()}
        if gs:
            from .guias_intl import _tile
            guitar_box = (f'  <section><h3>{_e(T["guitars"])} <a class="navlink" href="/{pais}/">{_e(T["guitars_more"])} →</a></h3>'
                          f'<div class="grid">' + "".join(_tile(pais, p, gnames, intl, t) for p in gs) + "</div></section>")
    except Exception:  # noqa: BLE001 - sin catálogo de guitarras, sin recuadro
        pass
    acount = {}
    for d in multi:
        if " - " in d["name"]:
            a = d["name"].split(" - ", 1)[0].strip()
            acount[a] = acount.get(a, 0) + 1
    for d in multi:
        f1 = T["fmt1"][d["fmt"]]
        url = f"/{pais}/{T['dir']}/{d['slug']}.html"
        path = out / f"{d['slug']}.html"
        a = d["name"].split(" - ", 1)[0].strip() if " - " in d["name"] else ""
        alink = (f' · <a href="/{pais}/{T["dir"]}/artist/{slug(a)}.html">{_e(T["artist_all"])} ({_e(a)})</a>'
                 if a and acount.get(a, 0) >= 2 and slug(a) else "")
        pages._write(path, _disc_page(pais, d, f1, url, names, T, t, guitar_box, alink))
        urls.append(url)
        keep.add(path)
    # Listados por formato e índice
    links = []
    for fk, (label, fname) in T["fmts"].items():
        ds = [d for d in multi if d["fmt"] == fk][:240]
        if not ds:
            continue
        items = "".join(_disc_tile(pais, d, T, names) for d in ds)
        url = f"/{pais}/{T['dir']}/{fname}.html"
        path = out / f"{fname}.html"
        pages._write(path, page(url, label, T["d_index"], f'  <div class="grid">{items}</div>'))
        urls.append(url)
        keep.add(path)
        links.append(f'<a class="chip" href="{url}">{_e(label)} <span class="muted">({len([d for d in multi if d["fmt"] == fk])})</span></a>')
    # Mayores diferencias entre tiendas (solo ofertas con stock): para la portada, Instagram y quien busca chollos
    def gap(d):
        live = [i["p"] for i in d["items"] if i["st"]]
        return (max(live) - min(live)) if len(live) >= 2 else 0
    deals = sorted((d for d in multi if gap(d) >= 2), key=gap, reverse=True)[:100]
    if deals:
        rows = "".join(_disc_tile(pais, d, T, names).replace('<div class="img">', f'<span class="badge">{_e(T["save"].format(m=intl.money(gap(d), pais)))}</span><div class="img">', 1)
                       for d in deals)
        url = f"/{pais}/{T['dir']}/{T['deals_file']}.html"
        path = out / f"{T['deals_file']}.html"
        pages._write(path, page(url, T["deals"], T["deals_desc"], f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["deals_desc"])}</p>\n  <div class="grid">{rows}</div>'))
        urls.append(url)
        keep.add(path)
        links.insert(0, f'<a class="chip" href="{url}">{_e(T["deals"])}</a>')
    best = "".join(_disc_tile(pais, d, T, names) for d in multi[:48])
    # Artistas: "Artista - Título" (lo de antes del guion); una página por artista con dos o más discos
    def artist(d):
        return d["name"].split(" - ", 1)[0].strip() if " - " in d["name"] else ""
    by_artist = {}
    for d in multi:
        if artist(d):
            by_artist.setdefault(artist(d), []).append(d)
    adir = out / "artist"
    akeep = set()
    for name_a, ds in by_artist.items():
        if len(ds) < 2:
            continue
        aslug = slug(name_a)
        if not aslug:
            continue
        url = f"/{pais}/{T['dir']}/artist/{aslug}.html"
        path = adir / f"{aslug}.html"
        tiles = "".join(_disc_tile(pais, d, T, names) for d in sorted(ds, key=lambda d: d["name"]))
        pages._write(path, page(url, T["artist_t"].format(a=name_a), T["artist_d"].format(a=name_a, n=len(ds)),
                                f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["artist_d"].format(a=name_a, n=len(ds)))}</p>\n'
                                f'  <div class="grid">{tiles}</div>'))
        urls.append(url)
        akeep.add(path)
    for f in adir.glob("*.html") if adir.exists() else []:
        if f not in akeep:
            f.unlink()
    artists_pages = {a for a, ds in by_artist.items() if len(ds) >= 2 and slug(a)}
    # Buscador con filtros: índice ligero [nombre, página, formato, precio, tiendas, foto, artista] y todo en el navegador
    idx = [[d["name"], d["slug"], T["fmt1"][d["fmt"]], min(i["p"] for i in d["items"]), len(d["items"]), d.get("img") or "", artist(d)]
           for d in multi]
    (out / "search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    top_artists = sorted(by_artist, key=lambda a: -len(by_artist[a]))[:400]
    datalist = "".join(f'<option value="{_e(a)}">' for a in sorted(top_artists, key=str.lower))
    fmts = "".join(f'<option value="{_e(T["fmt1"][k])}">{_e(v[0])}</option>' for k, v in T["fmts"].items())
    field = ('padding:10px 14px;border-radius:999px;border:1px solid var(--border);font:inherit;'
             'background:var(--surface-1);color:var(--text-primary)')
    search = (f'  <form class="search" role="search" onsubmit="return false" style="margin:14px 0 4px;display:flex;flex-wrap:wrap;gap:8px">'
              f'<input id="q" type="search" placeholder="{_e(T["search_ph"])}" autocomplete="off" aria-label="{_e(T["search_ph"])}" '
              f'style="flex:2 1 260px;{field}">'
              f'<input id="fa" list="artists" placeholder="{_e(T["f_artist"])}" aria-label="{_e(T["f_artist"])}" style="flex:1 1 180px;{field}">'
              f'<datalist id="artists">{datalist}</datalist>'
              f'<select id="ff" aria-label="{_e(T["f_format"])}" style="{field}"><option value="">{_e(T["f_all"])}</option>{fmts}</select>'
              f'<select id="fs" aria-label="{_e(T["f_sort"])}" style="{field}"><option value="p">{_e(T["s_price"])}</option>'
              f'<option value="n">{_e(T["s_shops"])}</option><option value="a">{_e(T["s_az"])}</option></select></form>\n'
              '  <section class="hub-sec" id="results" hidden><h2 id="rh"></h2><div class="grid" id="rg"></div></section>\n'
              + r"""  <script>(()=>{let idx=null;const $=i=>document.getElementById(i),q=$('q'),fa=$('fa'),ff=$('ff'),fs=$('fs'),sec=$('results'),g=$('rg'),h=$('rh');
const n=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();const e=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const money=v=>'£'+v.toFixed(2).replace(/\.00$/,'');const AP=__AP__;
async function run(){const t=n(q.value.trim()),a=n(fa.value.trim()),f=ff.value;if(t.length<2&&!a&&!f){sec.hidden=true;return}
if(!idx)idx=await (await fetch('search.json')).json();const w=t.length>=2?t.split(/\s+/):[];
let r=idx.filter(d=>{const x=' '+n(d[0]).replace(/[^a-z0-9]+/g,' ');return w.every(k=>x.includes(' '+k))&&(!a||(' '+n(d[6]).replace(/[^a-z0-9]+/g,' ')).includes(' '+a.replace(/[^a-z0-9]+/g,' ').trim()))&&(!f||d[2]===f)});
const s=fs.value;r.sort((x,y)=>s==='n'?y[4]-x[4]||x[3]-y[3]:s==='a'?x[0].localeCompare(y[0]):x[3]-y[3]);const tot=r.length;r=r.slice(0,120);
const ap=fa.value.trim()&&AP[fa.value.trim()];h.innerHTML=(tot?'__RES__'.replace('{n}',tot):'__NONE__')+(ap?` · <a href="artist/${ap}.html">__ALL__ →</a>`:'');
g.innerHTML=r.map(d=>`<a class="tile" href="${e(d[1])}.html"><div class="img">${d[5]?`<img loading="lazy" src="${e(d[5])}&width=300" alt="">`:''}</div><div class="body"><span class="brand">${e(d[2])}</span><span class="name">${e(d[0])}</span><span class="price"><strong>${money(d[3])}</strong></span><span class="foot"><span>${e(d[6])}</span><span class="stores-n">${d[4]}</span></span></div></a>`).join('');sec.hidden=false}
let tm;const go=()=>{clearTimeout(tm);tm=setTimeout(run,200)};[q,fa].forEach(x=>x.addEventListener('input',go));[ff,fs].forEach(x=>x.addEventListener('change',run));})();</script>
""".replace("__AP__", json.dumps({a: slug(a) for a in artists_pages}, ensure_ascii=False))
                 .replace("__RES__", _e(T["search_res"])).replace("__NONE__", _e(T["search_none"])).replace("__ALL__", _e(T["artist_all"])))
    body = (f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["d_index"])}</p>\n' + search + f'  <div class="links">{"".join(links)}</div>\n'
            f'  <section class="hub-sec"><h2>{_e(T["more"])}</h2><div class="grid">{best}</div></section>')
    path = out / "index.html"
    pages._write(path, page(f"/{pais}/{T['dir']}/", T["h_index"], T["d_index"], body))
    urls.insert(0, f"/{pais}/{T['dir']}/")
    keep.add(path)
    # Guía "dónde comprar vinilo más barato"
    if "guide_file" in T:
        gd = deals[:12] if deals else multi[:12]
        rows = "".join(f'<a href="/{pais}/{T["dir"]}/{d["slug"]}.html"><span>{_e(d["name"])} · {T["fmt1"][d["fmt"]]}</span><small>'
                       f'{_e(T["save"].format(m=intl.money(gap(d), pais)))}</small></a>' for d in gd if gap(d))
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in T["faqs"]]}
        faq = "".join(f"<details><summary>{_e(q)}</summary><p>{_e(a)}</p></details>" for q, a in T["faqs"])
        body = (f'  <p class="hub-intro" style="color:var(--text-secondary)">{_e(T["guide_desc"])}</p>\n'
                + T["guide_body"].format(shops=len(STORES[pais]) - 1)
                + (f'\n  <section class="hub-sec"><h2>{_e(T["deals"])}</h2><div class="dl">{rows}</div></section>' if rows else "")
                + f'\n  <section class="hub-sec" style="max-width:780px"><h2>FAQ</h2>{faq}</section>\n' + guitar_box)
        url = f"/{pais}/{T['dir']}/{T['guide_file']}.html"
        path = out / f"{T['guide_file']}.html"
        pages._write(path, page(url, T["guide"], T["guide_desc"], body, ld))
        urls.insert(1, url)
        keep.add(path)
    # Mapa propio de discos para Google (uk/records/sitemap.xml, en robots.txt)
    sm = "".join(f"  <url><loc>https://guitle.com{u}</loc></url>\n" for u in urls)
    (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n', encoding="utf-8")
    for f in out.glob("*.html"):
        if f not in keep:
            f.unlink()
    print(f"música {pais}: {len(discs)} discos con código, {len(multi)} en dos o más tiendas", flush=True)
    return urls


def _disc_tile(pais, d, T, names):
    from . import intl
    best = sorted(d["items"], key=lambda i: (not i["st"], i["p"]))[0]
    img = f'<img loading="lazy" src="{_e(d["img"])}&width=300" alt="">' if d.get("img") else ""
    return (f'<a class="tile" href="/{pais}/{T["dir"]}/{_e(d["slug"])}.html"><div class="img">{img}</div><div class="body">'
            f'<span class="brand">{_e(T["fmt1"][d["fmt"]])}</span><span class="name">{_e(d["name"])}</span>'
            f'<span class="price"><strong>{intl.money(best["p"], pais)}</strong></span><span class="foot">'
            f'<span>{_e(names.get(best["s"], best["s"]))}</span><span class="stores-n">{len(d["items"])}</span></span></div></a>')


def _disc_page(pais, d, f1, url, names, T, t, guitar_box, alink=""):
    """Página de un disco con las mismas piezas que la ficha de una guitarra (intl._product): cabecera, migas, foto y
    precio, tabla de tiendas con su botón y Amazon debajo. Sin gráfica de precios (aún no hay historial de discos)."""
    from . import intl, pages
    items = sorted(d["items"], key=lambda i: (not i["st"], i["p"]))  # la mejor: la más barata con stock
    best = items[0]
    colors = {st: pages.PALETTE[n % len(pages.PALETTE)] for n, st in enumerate(sorted({i["s"] for i in items}))}
    n, prices = len(items), [i["p"] for i in items]
    title = T["title"].format(n=d["name"], f=f1)
    desc = T["desc"].format(n=d["name"], f=f1, k=n)
    where = t["whereMany"].format(s=names.get(best["s"], best["s"]), n=n) + (
        t["whereDiff"].format(d=intl.money(round(max(prices) - min(prices)), pais)) if max(prices) - min(prices) >= 1 else "")
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f"{d['name']} ({f1})", "gtin13": d["ean"],
          "image": d.get("img"), "url": f"https://guitle.com{url}",
          "offers": {"@type": "AggregateOffer", "priceCurrency": intl.SITES[pais]["cur"], "lowPrice": min(prices),
                     "highPrice": max(prices), "offerCount": n}}
    amazon = (f'\n    <p class="muted small amazon">{_e(T["amazon_txt"])} <a href="{_e(T["amazon"].format(ean=d["ean"]))}" '
              f'target="_blank" rel="sponsored noopener">{_e(T["amazon_btn"])}</a></p>' if T.get("amazon") else "")
    img = f'<div class="pimg"><img src="{_e(d["img"])}&width=600" alt="{_e(d["name"])}"></div>' if d.get("img") else ""
    head = intl._head(pais, f"{title} · guitle", desc, url,
                      f'<meta property="og:title" content="{_e(title)}">\n<meta property="og:description" content="{_e(desc)}">\n'
                      + (f'<meta property="og:image" content="{_e(d["img"])}">\n' if d.get("img") else "")
                      + '<link rel="stylesheet" href="/catalogo.css">\n<link rel="stylesheet" href="/producto.css">\n'
                      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>')
    return f"""{head}
<body>
<main>
  <div class="topbar">
    <div class="row">
      {intl._logo(pais, t)}
      <a class="navlink" href="/{pais}/{T['dir']}/">{_e(T['home'])}</a>
    </div>
  </div>
  <nav class="crumbs"><a href="/{pais}/">{_e(t['home'])}</a> › <a href="/{pais}/{T['dir']}/">{_e(T['home'])}</a> › <a href="/{pais}/{T['dir']}/{T['fmts'][d['fmt']][1]}.html">{_e(T['fmts'][d['fmt']][0])}</a></nav>
  <article class="product">
    {img}
    <div class="pinfo">
      <div class="muted">{_e(f1.capitalize() if f1.islower() else f1)}{alink}</div>
      <h2 class="pname">{_e(d['name'])}</h2>
      <div id="price" class="big">{intl.money(best['p'], pais)}</div>
      <div id="where" class="muted">{_e(where)}</div>
      <div class="muted small">EAN {d['ean']} · {_e(T['note'])}</div>
    </div>
  </article>
  <section><h3>{_e(t['storesH3'])}</h3><div class="table-wrap"><table id="stores">{intl._rows({'items': items}, names, colors, pais, t)}</table></div>{amazon}</section>
{guitar_box}
  {intl._foot(pais, t)}
</main>
<script src="/c.js" defer></script>
</body>
</html>
"""


def home_deals(pais, n=4):
    """Los n discos con más diferencia entre tiendas (con stock), para la portada del país: [(disco, ahorro)]."""
    discs = _load(DATA / pais / "discos.json", [])
    out = []
    for d in discs:
        live = [i["p"] for i in d["items"] if i["st"]]
        if len(live) >= 2 and d.get("img") and max(live) - min(live) >= 2:
            out.append((d, max(live) - min(live), min(live)))
    return sorted(out, key=lambda x: -x[1])[:n]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pais", default="uk")
    ap.add_argument("--minutes", type=float, default=60)
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args(argv)
    if not a.build:
        read(a.pais, a.minutes)
    write_pages(a.pais, build_data(a.pais))
    return 0


if __name__ == "__main__":
    sys.exit(main())
