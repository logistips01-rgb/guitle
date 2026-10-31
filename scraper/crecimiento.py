"""Crecimiento de guitle: productos y tiendas de cada país a lo largo del tiempo (data/crecimiento.json), y el
resumen de ahora (data/resumen.json: productos, tiendas y países) para la página "Para tiendas".

Un punto cada 6 horas (hora de España): [momento, país, guitarras, equipo, tiendas]. Lo pinta stats.html, que también
avisa de anomalías; para la de "sin actualizar" se guarda la última lectura de cada catálogo ("actualizado").

    python -m scraper.crecimiento             # añade el punto de ahora, con el catálogo del disco
    python -m scraper.crecimiento --backfill  # rehace todo desde el historial de git (desde el primer día)

Lo lanza .github/workflows/crecimiento.yml al acabar cada lectura del catálogo.
"""
import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "data" / "catalog"
OUT = ROOT / "data" / "crecimiento.json"
COUNTRIES = ["es", "pt", "fr", "it", "uk", "de", "br", "ie", "at", "nl", "be"]
# España tiene sus propias carpetas; los demás países, <país>/ (guitarras) y <país>mas/ (equipo).
ES_GUITARS = {"products.json", "acusticas/acusticas.json", "acusticas/clasicas.json"}
ES_EQUIPO = ("equipo/", "mas/")
SKIP = ("history.json", "offers.json", "pvp.json", "paises.json")


def group(path):
    """'fr/electriques.json' → ('fr', 'g'); 'frmas/amplis.json' → ('fr', 'e'); None si no es un catálogo."""
    if path.endswith(SKIP) or not path.endswith(".json"):
        return None
    if path in ES_GUITARS:
        return "es", "g"
    if path.startswith(ES_EQUIPO):
        return "es", "e"
    top = path.split("/")[0]
    if "/" not in path:
        return None
    if top in COUNTRIES:
        return top, "g"
    if top.endswith("mas") and top[:-3] in COUNTRIES:
        return top[:-3], "e"
    return None


def count(files):
    """{ruta: (productos, {tiendas})} → {país: [guitarras, equipo, tiendas]}."""
    acc = {}
    for path, (n, stores) in files.items():
        g = group(path)
        if not g or not n:
            continue
        a = acc.setdefault(g[0], [0, 0, set()])
        a[0 if g[1] == "g" else 1] += n
        a[2] |= stores
    return {c: [g, e, len(s)] for c, (g, e, s) in acc.items()}


def parse(text):
    try:
        j = json.loads(text)
    except ValueError:
        return 0, set()
    s = j.get("stores", {}) if isinstance(j, dict) else {}
    return len(j.get("products", [])) if isinstance(j, dict) else 0, set(s if isinstance(s, list) else s.keys())


def bucket(dt):
    """Momento en tramos de 6 horas, hora de España (CET, UTC+1; basta para agrupar)."""
    dt = dt.astimezone(timezone(timedelta(hours=1)))
    return dt.replace(hour=dt.hour // 6 * 6, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")


def rows(moment, counts):
    return [[moment, c, *counts[c]] for c in COUNTRIES if c in counts]


def resumen():
    """data/resumen.json: productos, tiendas distintas y países con catálogo, para la página "Para tiendas"."""
    total, stores, countries = 0, set(), set()
    for p in CAT.rglob("*.json"):
        g = group(str(p.relative_to(CAT)))
        if not g:
            continue
        n, st = parse(p.read_text(encoding="utf-8"))
        if n:
            total += n
            stores |= st
            countries.add(g[0])
    out = {"productos": total, "tiendas": len(stores), "paises": [c for c in COUNTRIES if c in countries],
           "actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes")}
    (ROOT / "data" / "resumen.json").write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")


def now():
    files = {str(p.relative_to(CAT)): parse(p.read_text(encoding="utf-8")) for p in CAT.rglob("*.json")}
    return rows(bucket(datetime.now(timezone.utc)), count(files))


def updated():
    """{país: {"g": última lectura de sus guitarras, "e": de su equipo}} (ISO, UTC)."""
    out = {}
    for p in CAT.rglob("*.json"):
        g = group(str(p.relative_to(CAT)))
        if not g:
            continue
        try:
            u = json.loads(p.read_text(encoding="utf-8")).get("updated")
        except ValueError:
            continue
        if u and u > out.setdefault(g[0], {}).get(g[1], ""):
            out[g[0]][g[1]] = u
    return out


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def backfill():
    """Un punto por tramo de 6 horas: el último commit del catálogo de ese tramo."""
    last = {}
    for line in git("log", "--format=%H %cI", "--first-parent", "HEAD", "--", "data/catalog").splitlines()[::-1]:
        h, t = line.split()
        last[bucket(datetime.fromisoformat(t))] = h
    cache, out = {}, []
    for moment, h in sorted(last.items()):
        files = {}
        for line in git("ls-tree", "-r", h, "data/catalog").splitlines():
            meta, path = line.split("\t", 1)
            path, blob = path[len("data/catalog/"):], meta.split()[2]
            if not group(path):
                continue
            if blob not in cache:
                cache[blob] = parse(git("cat-file", "-p", blob))
            files[path] = cache[blob]
        out += rows(moment, count(files))
        print(moment, sum(r[2] + r[3] for r in out if r[0] == moment), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true")
    a = ap.parse_args()
    if a.backfill:
        data = backfill()
    else:
        data = json.loads(OUT.read_text(encoding="utf-8"))["rows"] if OUT.exists() else []
        new = now()
        data = [r for r in data if r[0] != new[0][0]] + new if new else data
    OUT.write_text(json.dumps({"cols": ["momento", "pais", "guitarras", "equipo", "tiendas"], "rows": data,
                               "actualizado": updated()},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"crecimiento: {len(data)} filas, {len({r[0] for r in data})} momentos", flush=True)
    resumen()


if __name__ == "__main__":
    main()
