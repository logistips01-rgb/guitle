"""Monta la copia de emergencia de la web española para guitle.es (.github/workflows/copia-es.yml).

    python3 scraper/copia_es.py WEB CAJAS SALIDA FOTOS

WEB es lo bajado de R2 sin los países ni las fotos; CAJAS, las cajas de la sección de discos (_r/<nnnn>.json.gz,
{"discos/x.html": html}), que aquí se abren en ficheros porque GitHub Pages no tiene Worker. En SALIDA queda la copia:
cada página con noindex (la buena es la de guitle.com, que es su canonical), los enlaces a otros países apuntando a
guitle.com y robots.txt cerrado. En FOTOS, la lista de miniaturas (img/p/…) que usan las páginas, para bajar solo esas.
Solo usa la biblioteca estándar: el trabajo no instala nada.
"""
import gzip
import json
import os
import re
import shutil
import sys
from pathlib import Path

COUNTRIES = "pt|fr|it|uk|de|br|ie|at|nl|be|ch|pl|se|no|dk|cz|sk|hu|ro|bg|gr|fi|lu|mx|ar"
NOINDEX = '<meta name="robots" content="noindex">'
# En la copia no hay otros países: fuera el botón del mapa ("N países", paises.html) y los enlaces a sus webs, que
# durante un corte tampoco cargarían. Con CSS porque el botón lo pinta el JavaScript de la portada.
SOLO_ES = ('<style>a[href$="paises.html"],a[href^="https://guitle.com/"]{display:none!important}</style>')
# Enlaces a otro país: en guitle.es no están, se van a guitle.com.
TO_COUNTRY = re.compile(rf'(<a\b[^>]*?\bhref=")/(?=(?:{COUNTRIES})/)')
# Enlaces absolutos a la propia web española: se quedan en la copia (canonical, og:url y hreflang no son <a>).
TO_SELF = re.compile(rf'(<a\b[^>]*?\bhref=")https://guitle\.com/(?!(?:{COUNTRIES})/)')
IMG = re.compile(r'(?<![\w.-])/?(img/p/[\w./-]+\.(?:webp|jpg|jpeg|png|avif))')


def fix_html(text, fotos):
    for m in IMG.finditer(text):
        fotos.add(m.group(1))
    if "noindex" not in text[:4000]:
        text = re.sub(r"(<head[^>]*>)", r"\1" + NOINDEX + SOLO_ES, text, count=1, flags=re.I)
    text = TO_COUNTRY.sub(r"\1https://guitle.com/", text)
    return TO_SELF.sub(r"\1/", text)


def main(web, cajas, out, fotos_file):
    web, cajas, out = Path(web), Path(cajas), Path(out)
    if out.exists():
        shutil.rmtree(out)
    fotos, n_html, n_other = set(), 0, 0
    # Fichas de hoy (g/_indice.txt.gz, scraper/cajas.py): las retiradas se quedan en R2 con su último precio y aquí no van
    hoy = None
    idx = web / "g" / "_indice.txt.gz"
    if idx.exists():
        hoy = set(gzip.decompress(idx.read_bytes()).decode("utf-8").split("\n")[1:]) - {""}
        hoy = hoy if len(hoy) >= 20000 else None
    for src in web.rglob("*"):
        if not src.is_file():
            continue
        if hoy is not None and src.parent == web / "g" and src.suffix == ".html" and src.stem not in hoy:
            continue
        dst = out / src.relative_to(web)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".html":
            dst.write_text(fix_html(src.read_text(encoding="utf-8", errors="replace"), fotos), encoding="utf-8")
            n_html += 1
        else:
            os.link(src, dst)  # sin copiar: lo bajado se queda en la caché tal cual
            n_other += 1
    n_box = 0
    for box in sorted(cajas.glob("*.json.gz")):
        for rel, html in json.loads(gzip.decompress(box.read_bytes())).items():
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(fix_html(html, fotos), encoding="utf-8")
            n_box += 1
    (out / "robots.txt").write_text("# Copia de emergencia de guitle.com: la web es https://guitle.com/\n"
                                    "User-agent: *\nDisallow: /\n", encoding="utf-8")
    for f in out.glob("sitemap*.xml"):
        f.unlink()
    if (out / "sw.js").exists():  # el service worker es de guitle.com
        (out / "sw.js").unlink()
    (out / ".nojekyll").write_text("", encoding="utf-8")
    Path(fotos_file).write_text("".join(f"{p}\n" for p in sorted(fotos)), encoding="utf-8")
    print(f"copia: {n_html} páginas, {n_box} de discos (cajas), {n_other} ficheros más, {len(fotos)} fotos")
    if n_html < 1000:
        sys.exit(f"copia a medias: solo {n_html} páginas")


if __name__ == "__main__":
    main(*sys.argv[1:5])
