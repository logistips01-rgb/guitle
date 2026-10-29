"""Prueba, desde GitHub, las tiendas que no podemos leer (_interno/tiendas-bloqueadas.md) y algunas candidatas.

Desde el entorno de pruebas algunas tiendas responden distinto que desde GitHub (que es desde donde lee guitle cada
noche). Para cada dominio mira: si responde, si robots.txt nos deja, si sale una página antibots, si publica sitemap
(y cuántas URLs), si es una tienda Shopify (products.json) y si una ficha trae precio y EAN en JSON-LD.

    python -m scraper.probe [--out informe.md]
"""
import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from .catalog import _parse_jsonld, sitemap_urls
from .fetch import Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "_interno" / "tiendas-bloqueadas.md"
# Dominios de las filas agrupadas ("varias") de la lista.
EXTRA = ["fanfara.it", "rockshop.it", "strumentimusicali.it", "chitarre-online.it", "lafavoritamusica.it", "aiellomusicshop.it",
         "casadellamusica.it", "bandaroma.it", "mondomusicastore.it", "musikhaus-doblinger.at", "musikhaus-hammer.at",
         "gitarrenzentrum.at", "musikhaus.at", "keymusic.com", "musicmatters.nl", "guitarshop-online.nl", "max-music.nl",
         "gitaarshop.nl", "musicstore.nl", "musicalexpress.com.br", "playtech.com.br", "contemporanea.com.br",
         "izzomusical.com.br", "davyandersonmusic.ie", "kytary.fr", "musikia.fr", "planetemusique.fr", "hollywoodmusic.fr",
         "musicmatter.co.uk", "veerkamponline.com", "audiomusica.com", "long-mcquade.com", "musiciansfriend.com"]
PRODUCT_HINT = re.compile(r"/products?/|/p/|/pd/|-p\d+|\.htm|/produ|/artikel|/item")


def domains():
    found = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        for d in re.findall(r"\|\s*([a-z0-9-]+(?:\.[a-z0-9-]+)+)(?:/[^\s|]*)?\s*\|", line):
            if d not in found:
                found.append(d)
    return found + [d for d in EXTRA if d not in found]


def probe(fetcher, domain):
    base = f"https://www.{domain}" if domain.count(".") == 1 else f"https://{domain}"
    row = {"domain": domain}
    try:
        robots = fetcher.get(base + "/robots.txt")
        row["robots"] = robots.status_code
        home = fetcher.get(base + "/")
        row["home"] = home.status_code
        row["final"] = home.url.split("/")[2]
        row["antibots"] = is_challenge(home)
        row["allowed"] = fetcher.allowed(base + "/")[0] if robots.status_code == 200 else None
        sitemaps = re.findall(r"(?im)^sitemap:\s*(\S+)", robots.text) if robots.status_code == 200 else []
        shop = fetcher.get(base + "/products.json?limit=1")
        row["shopify"] = shop.status_code == 200 and shop.headers.get("content-type", "").startswith("application/json")
        urls = []
        for sm in sitemaps[:2]:
            # Solo el primer nivel (y, si es un índice, sus dos primeros sitemaps): basta para saber si hay fichas.
            urls += sitemap_urls(fetcher, sm, sub=lambda u, seen=[]: seen.append(u) or len(seen) <= 2)
        row["sitemap"] = len(urls) if sitemaps else 0
        sample = next((u for u in urls if PRODUCT_HINT.search(u)), None)
        if sample:
            page = fetcher.get(sample)
            data = _parse_jsonld(BeautifulSoup(page.text, "html.parser"), "probe")
            row["ficha"] = f"{page.status_code}, precio {'sí' if data.get('price') else 'no'}, EAN {'sí' if data.get('ean') else 'no'}"
    except Exception as exc:  # noqa: BLE001
        row["error"] = type(exc).__name__
    return row


def report(rows):
    # "Va a": a dónde lleva la portada (GAK y PMT, por ejemplo, redirigen a gear4music.com).
    head = "| Dominio | robots | Portada | Va a | Antibots | Nos deja | Shopify | URLs sitemap | Ficha de muestra | Error |\n"
    head += "|---|---|---|---|---|---|---|---|---|---|\n"
    yes = lambda v: "sí" if v else ("no" if v is not None else "")
    return head + "\n".join(
        f"| {r['domain']} | {r.get('robots', '')} | {r.get('home', '')} | {r.get('final', '')} | {yes(r.get('antibots'))} | "
        f"{yes(r.get('allowed'))} | {yes(r.get('shopify'))} | {r.get('sitemap', '')} | {r.get('ficha', '')} | {r.get('error', '')} |"
        for r in rows) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="informe-tiendas.md")
    args = parser.parse_args(argv)
    fetcher = Fetcher(delay=(1.0, 2.0))
    rows = []
    for d in domains():
        rows.append(probe(fetcher, d))
        print(rows[-1], flush=True)
    Path(args.out).write_text("# Prueba de tiendas desde GitHub\n\n" + report(rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
