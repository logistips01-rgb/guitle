"""Comprueba en guitle.com que las fichas de un país salen idénticas desde las cajas (?caja=1) y desde el fichero de
siempre, antes de activar el país en el Worker (scraper/cajas.py). Uso: python -m scraper.verificar_cajas lu [400]"""
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

UA = {"User-Agent": "guitle-verificacion/1.0 (+https://guitle.com)"}


def check(code, n=400):
    sm = requests.get(f"https://guitle.com/sitemap-{code}.xml", headers=UA, timeout=60).text
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if f"/{code}/g/" in u]
    random.seed(7)
    sample = urls if len(urls) <= n else random.sample(urls, n)

    def get(url):
        for attempt in range(4):  # cortes de red puntuales: se reintenta
            try:
                return requests.get(url, headers=UA, timeout=60)
            except requests.RequestException:
                if attempt == 3:
                    raise

    def one(u):
        r = random.randint(0, 10**9)
        a, b = get(f"{u}?x={r}"), get(f"{u}?caja=1&x={r}")
        if b.headers.get("x-guitle-caja") != "1":
            return u, "sin caja"
        return u, "ok" if a.status_code == 200 and a.content == b.content else "distinta"

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, sample))
    bad = [(u, s) for u, s in res if s != "ok"]
    print(f"{code}: {len(urls)} fichas en el sitemap, {len(sample)} comprobadas, {len(sample) - len(bad)} iguales, "
          f"{len(bad)} mal", flush=True)
    for u, s in bad[:5]:
        print("   ", s, u)
    return not bad


if __name__ == "__main__":
    code, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 400
    sys.exit(0 if check(code, n) else 1)
