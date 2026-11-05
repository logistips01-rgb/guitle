"""Chollos publicados hoy en Instagram, para la página «Chollos de hoy» de la web (guitle.com/hoy/ y
guitle.com/<país>/hoy/), que es el enlace de la bio de cada cuenta: Instagram no deja enlaces en posts, Reels ni stories.

Escribe data/hoy/<país>.json en la rama de la web (claude/friendly-fermat-yycain), solo esa carpeta, desde una copia
aparte (git worktree con sparse-checkout en data/hoy) para no tocar nada más de la web ni la rama de redes. La página la
mantiene la sesión de la web; el formato acordado con ella:
    {"fecha": "AAAA-MM-DD", "pais": "es", "items": [{"slug", "name", "brand", "price", "store", "kind", "img", "why"}]}
en el orden de publicación (post, Reel de chollos, stories), con el precio ya formateado y la miniatura de la web.

Uso:
    python -m scraper.hoy es fr it de uk br            # escribe y sube los del día
    python -m scraper.hoy es --dry                     # solo muestra lo que escribiría
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import instagram as ig
from . import paises
from .catalog import load

ROOT = ig.ROOT
WEB = "claude/friendly-fermat-yycain"
COPIA = ROOT.parent / "guitle-hoy"  # copia aparte de la rama de la web, solo con data/hoy


def _thumbs(catalogs):
    """slug → miniatura de la web (campo th del catálogo, servida en /img/p/<th>)."""
    out = {}
    for path in catalogs.values():
        for p in load(path, {}).get("products", []):
            if p.get("th"):
                out[p["slug"]] = p["th"]
    return out


def items(cc, day):
    """Guitarras publicadas hoy en la cuenta del país, sin repetir, en el orden de publicación."""
    if cc == "es":
        folder, money, catalogs = ig.OUT / day.isoformat(), ig.eur, ig.CATALOGS
    else:
        cfg = paises.PAISES[cc]
        folder, money = ig.OUT / day.isoformat() / cc, paises.dinero(cfg)
        catalogs = {k: ROOT / v for k, v in cfg["catalogs"].items()}
    plan = load(folder / "plan.json", {})
    if not plan or not (folder / "published.json").exists():
        return []
    post = plan.get("post") or {}
    reel = (load(folder / "reel-1-chollos" / "plan.json", {}).get("post") or {}).get("picks") or []
    orden = ([post["deal"]] if post.get("deal") else []) + (post.get("picks") or []) + reel + plan.get("stories", [])
    th = _thumbs(catalogs)
    out, vistos = [], set()
    for p in orden:
        if not p.get("slug") or p["slug"] in vistos:
            continue
        vistos.add(p["slug"])
        out.append({"slug": p["slug"], "name": p["name"], "brand": p.get("brand", ""), "price": money(p["price"]),
                    "store": p.get("store", ""), "kind": p.get("kind", ""), "img": th.get(p["slug"]) or p.get("img", ""),
                    "why": p.get("why", "")})
    return out


def _git(*args, check=True):
    return subprocess.run(["git", "-C", str(COPIA), *args], check=check, capture_output=True, text=True).stdout.strip()


def _copia():
    """Copia aparte de la rama de la web con solo data/hoy, puesta al día con el servidor."""
    subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin", WEB], check=True)
    if not (COPIA / ".git").exists():
        subprocess.run(["git", "-C", str(ROOT), "worktree", "prune"], check=True)
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-q", "--no-checkout", "--detach", str(COPIA),
                        f"origin/{WEB}"], check=True)
        _git("sparse-checkout", "set", "--no-cone", "/data/hoy/")
    _git("checkout", "-q", "--detach", f"origin/{WEB}")


def subir(datos):
    """Escribe data/hoy/<país>.json en la rama de la web, con reintentos si alguien sube a la vez."""
    for intento in range(5):
        _copia()
        carpeta = COPIA / "data" / "hoy"
        carpeta.mkdir(parents=True, exist_ok=True)
        for cc, d in datos.items():
            (carpeta / f"{cc}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        _git("add", "data/hoy")
        if not _git("diff", "--cached", "--name-only"):
            return "sin cambios"
        _git("commit", "-q", "-m", f"hoy: chollos publicados en Instagram ({', '.join(datos)})")
        if subprocess.run(["git", "-C", str(COPIA), "push", "-q", "origin", f"HEAD:{WEB}"],
                          capture_output=True).returncode == 0:
            return _git("rev-parse", "--short", "HEAD")
        time.sleep(2 ** intento)
    raise RuntimeError("no se pudo subir data/hoy a la rama de la web")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+", choices=["es", *sorted(paises.PAISES)])
    ap.add_argument("--date")
    ap.add_argument("--dry", action="store_true", help="solo muestra lo que escribiría")
    args = ap.parse_args(argv)
    day = datetime.fromisoformat(args.date).date() if args.date else datetime.now(timezone.utc).date()
    datos = {}
    for cc in args.paises:
        lista = items(cc, day)
        if lista:
            datos[cc] = {"fecha": day.isoformat(), "pais": cc, "items": lista}
        print(f"{cc}: {len(lista)} chollos" + ("" if lista else " (aún no se ha publicado hoy)"))
    if args.dry:
        print(json.dumps(datos, ensure_ascii=False, indent=1)[:3000])
        return
    if datos:
        print("data/hoy:", subir(datos))


if __name__ == "__main__":
    sys.exit(main())
