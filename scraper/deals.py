"""Chollos a partir del histórico: mínimos históricos, bajadas reales, bajadas de hoy y descuentos inflados.

Un descuento "inflado" es el de una tienda que sube el precio y luego lo "rebaja" a un precio que no es menor
que el que ya tenía antes (típico antes de Black Friday). Salida: data/deals-<categoría>.json para chollos.html.
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_DAYS = 7          # días de histórico para hablar de "mínimo" o "bajada real"
REAL_DROP = -5.0      # % frente a la media de 30 días
TOP = 24              # guitarras por sección


def _curated_series(sku, records):
    """Histórico de seguimiento (un registro por tienda y día) → {tienda: [[día, precio], ...]} con solo cambios."""
    out = {}
    for r in sorted((r for r in records if r.get("sku") == sku and r.get("status") == "ok" and r.get("price") is not None),
                    key=lambda r: r["date"]):
        pts = out.setdefault(r["store"], [])
        if not pts or pts[-1][1] != r["price"]:
            pts.append([r["date"][:10], r["price"]])
    return out


def _daily_best(series, stores, today):
    """Mejor precio de cada día (entre las tiendas que hoy venden la guitarra), del primer dato a hoy."""
    series = {s: pts for s, pts in series.items() if s in stores and pts}
    if not series:
        return []
    first = min(pts[0][0] for pts in series.values())
    out, d = [], date.fromisoformat(first)
    while d.isoformat() <= today:
        day = d.isoformat()
        prices = [next((p for pd, p in reversed(pts) if pd <= day), None) for pts in series.values()]
        prices = [p for p in prices if p is not None]
        out.append((day, min(prices) if prices else None))
        d += timedelta(days=1)
    return [(d, p) for d, p in out if p is not None]


def _inflated(series, stores, today):
    """Tienda que acaba de bajar el precio, pero no por debajo de lo que costaba antes de subirlo."""
    since = (date.fromisoformat(today) - timedelta(days=45)).isoformat()
    for store, pts in series.items():
        if store not in stores or len(pts) < 3:
            continue
        (d_prev, p_prev), (d_now, p_now) = pts[-2], pts[-1]
        before = [p for d, p in pts[:-2] if d >= since] or [pts[-3][1]]
        base = min(before)
        if p_now < p_prev and p_prev >= base * 1.05 and p_now >= base and d_now >= (date.fromisoformat(today) - timedelta(days=14)).isoformat():
            return {"store": store, "before": base, "raised": p_prev, "now": p_now, "since": d_now}
    return None


def build(kind, products, history, curated_records=(), names=None, today=None):
    today = today or date.today().isoformat()
    rows = []
    for p in products:
        if not p.get("slug") or not p.get("items"):
            continue
        series = {}
        for k in p.get("hk") or [p.get("ean")]:
            for store, pts in history.get(k, {}).items() if k else ():
                series.setdefault(store, pts)
        if p.get("sku"):
            for store, pts in _curated_series(p["sku"], curated_records).items():
                series.setdefault(store, pts)
        stores = {i["s"] for i in p["items"]}
        best = p["items"][0]
        # Solo tiendas con histórico propio: una tienda que entra hoy más barata no es una "bajada".
        cutoff = (date.fromisoformat(today) - timedelta(days=MIN_DAYS)).isoformat()
        known = {s for s in stores if series.get(s) and series[s][0][0] <= cutoff}
        daily = _daily_best(series, known, today)
        prev = [v for d, v in daily if d < today]
        card = {"slug": p["slug"], "name": p["name"], "brand": p.get("brand"), "th": p.get("th"), "price": best["p"],
                "store": best["s"], "stores": len(stores), "days": len(daily)}
        now_known = min((i["p"] for i in p["items"] if i["s"] in known), default=None)
        if prev and now_known is not None:
            last30 = prev[-30:]
            card["avg"] = round(sum(last30) / len(last30), 2)
            card["min"] = min(prev)
            card["vs_avg"] = round((now_known - card["avg"]) / card["avg"] * 100, 1)
        # Bajada de hoy: la propia tienda más barata ha rebajado su precio desde ayer.
        pts = series.get(best["s"], [])
        yesterday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
        if len(pts) >= 2 and pts[-1][0] >= yesterday and pts[-1][1] < pts[-2][1] and pts[-1][1] == best["p"]:
            card["vs_yesterday"] = round(pts[-1][1] - pts[-2][1], 2)
        fake = _inflated(series, stores, today)
        if fake:
            card["inflated"] = fake
        rows.append(card)
    # Un descuento inflado nunca cuenta como chollo, aunque su media (subida a propósito) lo haga parecer.
    honest = [r for r in rows if not r.get("inflated")]
    enough = [r for r in honest if r["days"] >= MIN_DAYS and "avg" in r]
    out = {
        "updated": today, "kind": kind,
        "records": sorted([r for r in enough if r["avg"] * (1 + r["vs_avg"] / 100) < r["min"]], key=lambda r: r["vs_avg"])[:TOP],
        "real_drops": sorted([r for r in enough if r["vs_avg"] <= REAL_DROP], key=lambda r: r["vs_avg"])[:TOP],
        "today": sorted([r for r in honest if r.get("vs_yesterday", 0) <= -1], key=lambda r: r["vs_yesterday"])[:TOP],
        "inflated": [r for r in rows if r.get("inflated")][:TOP],
        # Días desde el primer precio guardado (de cualquier guitarra de la categoría).
        "history_days": (date.fromisoformat(today) - date.fromisoformat(first)).days + 1 if (first := min(
            [pts[0][0] for s in history.values() for pts in s.values() if pts]
            + [r["date"][:10] for r in curated_records], default=None)) else 0,
    }
    used = {r["store"] for key in ("records", "real_drops", "today", "inflated") for r in out[key]}
    used |= {r["inflated"]["store"] for r in out["inflated"]}
    out["stores"] = {s: (names or {}).get(s, s) for s in sorted(used)}
    path = ROOT / "data" / f"deals-{kind}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"chollos {kind}: {len(out['records'])} mínimos, {len(out['real_drops'])} bajadas reales, "
          f"{len(out['today'])} bajadas de hoy, {len(out['inflated'])} inflados", flush=True)
    return out
