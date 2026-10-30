"""Avisa a Bing (y al resto de buscadores de IndexNow) de las páginas nuevas o cambiadas.

    python -m scraper.indexnow            # páginas .html cambiadas en el último commit
    python -m scraper.indexnow --files L  # las de la lista L (rutas como pt/g/x.html): webs que van directas a R2
    python -m scraper.indexnow --all      # todas las del sitemap (primera vez)

La clave se publica en guitle.com/<clave>.txt, que es como el buscador comprueba que el aviso es nuestro.
"""
import re
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://guitle.com"
KEY = "1d6ef0a9dbc598edfc01c52eaff8b727"
SKIP = {"stats.html"}


def changed():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "*.html"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if f not in SKIP and (ROOT / f).exists()]


def submit(urls):
    for i in range(0, len(urls), 10000):
        batch = urls[i:i + 10000]
        r = requests.post("https://api.indexnow.org/indexnow", timeout=60, json={
            "host": "guitle.com", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": batch})
        print(f"[indexnow] {len(batch)} URL → HTTP {r.status_code}", flush=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--all" in argv:
        urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    elif "--files" in argv:
        files = Path(argv[argv.index("--files") + 1]).read_text(encoding="utf-8").split()
        urls = [f"{SITE}/{f[:-len('index.html')] if f.endswith('index.html') else f}" for f in files
                if f.endswith(".html") and f.split("/")[-1] not in SKIP]
    else:
        urls = [f"{SITE}/" if f == "index.html" else f"{SITE}/{f}" for f in changed()]
    if urls:
        submit(urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
