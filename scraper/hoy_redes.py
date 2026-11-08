"""Chollos de hoy (guitle.com/hoy/, /<país>/hoy/) con lo que la sesión de redes ha PUBLICADO de verdad en Instagram.

La sesión de redes guarda en su rama (claude/exciting-cerf-q48nxa) cada día social/<fecha>/[<país>/]plan.json (lo que
prepara) y published.json (lo que llegó a publicarse). Esto coge, por país, el último día publicado y escribe
data/hoy/<país>.json para hoy.js: primero los chollos de las historias (con su motivo) y luego los de la publicación.
Las fotos: la miniatura de la ficha del catálogo (la buena, sin cortes ni espaldas) si la hay.

Uso: python -m scraper.hoy_redes   (lo lanza .github/workflows/hoy.yml cada pocas horas)
"""
import glob
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "origin/claude/exciting-cerf-q48nxa"
PAISES = ["es", "fr", "it", "de", "uk", "br", "pt", "ie", "nl"]


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def _show(path):
    try:
        return json.loads(_git("show", f"{BRANCH}:{path}") or "null")
    except json.JSONDecodeError:
        return None


def _money(v, pais):
    try:
        from . import intl
        return intl.money(float(v), pais)
    except Exception:  # noqa: BLE001
        return f"{float(v):.0f} €"


def main():
    _git("fetch", "-q", "origin", BRANCH.split("/", 1)[1])
    files = _git("ls-tree", "-r", "--name-only", BRANCH, "social/").split()
    days = sorted({m.group(1) for f in files if (m := re.match(r"social/(\d{4}-\d{2}-\d{2})/", f))}, reverse=True)
    try:
        bad = {k for k, v in json.loads((ROOT / "data" / "fotos-revisadas.json").read_text()).items() if v}
    except (FileNotFoundError, json.JSONDecodeError):
        bad = set()
    th = {}
    for cat in glob.glob(str(ROOT / "data" / "catalog" / "**" / "*.json"), recursive=True):
        try:
            for p in json.loads(open(cat, encoding="utf-8").read()).get("products", []):
                if p.get("slug") and p.get("th") and p["th"] not in bad:
                    th.setdefault(p["slug"], p["th"])
        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            continue
    n = 0
    for pais in PAISES:
        sub = "" if pais == "es" else f"{pais}/"
        for day in days:
            if f"social/{day}/{sub}published.json" not in files:
                continue
            plan = _show(f"social/{day}/{sub}plan.json") or {}
            picks = [dict(p, _why=p.get("why") or "") for p in plan.get("stories") or []]
            picks += [dict(p, _why="") for p in ((plan.get("post") or {}).get("picks") or [])]
            items, seen = [], set()
            for p in picks:
                if not p.get("slug") or p["slug"] in seen:
                    continue
                seen.add(p["slug"])
                items.append({"slug": p["slug"], "name": p.get("name") or "", "brand": p.get("brand") or "",
                              "price": _money(p.get("price") or 0, pais), "store": p.get("store") or "",
                              "kind": p.get("kind") or "", "img": th.get(p["slug"]) or p.get("img") or "", "why": p["_why"]})
            if items:
                out = ROOT / "data" / "hoy" / f"{pais}.json"
                new = {"fecha": day, "pais": pais, "items": items}
                old = json.loads(out.read_text()) if out.exists() else None
                if old != new:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                    n += 1
                print(f"hoy {pais}: {day}, {len(items)} chollos", flush=True)
            break
    print(f"hoy: {n} países actualizados", flush=True)


if __name__ == "__main__":
    main()
