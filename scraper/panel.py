"""Datos del panel de marketing (artifact "guitle Marketing"): cuentas por país, indicadores diarios de Instagram,
publicaciones, Reels de hoy, embajadores y calendario de Black Friday. Escribe social/panel/*.json, que se suben como
archivos del panel cada día.

Las cuentas de cada país están en social/cuentas.json; las que tienen token (variable de entorno) se leen por la API.
La de España usa el token que inyecta el proxy (sin variable).

Uso: python -m scraper.panel
"""
import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

from .catalog import load

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "social" / "panel"
API = "https://graph.instagram.com/v23.0"
RAW = "https://raw.githubusercontent.com/logistips01-rgb/guitle/claude/exciting-cerf-q48nxa"
PAISES = {"es": "España", "pt": "Portugal", "fr": "Francia", "it": "Italia", "de": "Alemania", "br": "Brasil",
          "ie": "Irlanda", "at": "Austria", "nl": "Países Bajos", "pl": "Polonia", "bg": "Bulgaria", "se": "Suecia",
          "no": "Noruega", "dk": "Dinamarca", "ch": "Suiza", "be": "Bélgica", "uk": "Reino Unido"}
DAY_METRICS = ["reach", "views", "profile_views", "accounts_engaged", "total_interactions", "website_clicks"]
TIPOS = {"FEED": "Post", "REELS": "Reel", "STORY": "Story"}


def api(path, token=None, **params):
    if token:
        params["access_token"] = token
    r = requests.get(f"{API}/{path}", params=params, timeout=60)
    j = r.json()
    if "error" in j:
        raise RuntimeError(j["error"].get("message"))
    return j


def day_insights(user, token, day):
    """Indicadores de la cuenta en un día (UTC); un indicador que la API no da se queda en None."""
    since = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
    out = {}
    for m in DAY_METRICS:
        try:
            data = api(f"{user}/insights", token, metric=m, period="day", metric_type="total_value",
                       since=since, until=since + 86400)["data"]
            out[m] = data[0]["total_value"]["value"] if data else 0
        except RuntimeError:
            out[m] = None
    return out


def media_rows(user, token, cuenta):
    rows = []
    media = api(f"{user}/media", token, fields="id,caption,media_type,media_product_type,timestamp,permalink,"
                                                "like_count,comments_count", limit=100)["data"]
    for m in media:
        ins = {}
        try:
            for i in api(m["id"] + "/insights", token, metric="reach,saved,shares,views")["data"]:
                ins[i["name"]] = i["values"][0]["value"]
        except RuntimeError:
            pass
        first = (m.get("caption") or "").strip().split("\n")[0]
        tipo = "Carrusel" if m.get("media_type") == "CAROUSEL_ALBUM" else TIPOS.get(m.get("media_product_type"), "Post")
        rows.append({"id": m["id"], "fecha": m["timestamp"][:10], "hora": m["timestamp"][11:16], "cuenta": cuenta,
                     "tipo": tipo, "titulo": first[:90], "enlace": m.get("permalink"),
                     "alcance": ins.get("reach"), "visualizaciones": ins.get("views"),
                     "me_gusta": m.get("like_count"), "comentarios": m.get("comments_count"),
                     "guardados": ins.get("saved"), "compartidos": ins.get("shares")})
    return rows


def stories_rows(cuenta):
    """Stories publicadas por los scripts (la API solo las lista 24 h): fecha y enlace, sin indicadores."""
    rows = []
    for f in sorted((ROOT / "social").glob("*/published.json")) + sorted((ROOT / "social").glob("*/tarde/published.json")):
        day = f.parent.name if f.parent.name != "tarde" else f.parent.parent.name
        for i, link in enumerate(load(f, {}).get("stories", []), 1):
            rows.append({"id": link.rsplit("/", 1)[-1], "fecha": day, "hora": "20:13" if "tarde" in str(f) else "12:47",
                         "cuenta": cuenta, "tipo": "Story", "titulo": f"Story de chollo {i}" + (" (tarde)" if "tarde" in str(f) else ""),
                         "enlace": link, "alcance": None, "visualizaciones": None, "me_gusta": None,
                         "comentarios": None, "guardados": None, "compartidos": None})
    return rows


def reels_hoy(today, posted):
    """Los 3 Reels del día para subir a mano, con su texto, el enlace al vídeo y si ya se ve publicado."""
    rows = []
    horas = {"reel-1-chollos": "13:00", "reel-3-guitle": "18:00", "reel-2-black-friday": "21:00"}
    nombres = {"reel-1-chollos": "Chollos", "reel-3-guitle": "guitle", "reel-2-black-friday": "Black Friday"}
    # Los del día; antes de la publicación de mediodía, los del último día que tiene
    days = sorted(f.parent.parent.name for f in (ROOT / "social").glob("*/reel-1-chollos/reel.mp4"))
    if not days:
        return rows
    day = today.isoformat() if today.isoformat() in days else days[-1]
    folder = ROOT / "social" / day
    for name in ("reel-1-chollos", "reel-3-guitle", "reel-2-black-friday"):
        sub = folder / name
        if not (sub / "reel.mp4").exists():
            continue
        texto = (sub / "texto.txt").read_text(encoding="utf-8").strip()
        key = re.sub(r"\W", "", texto.split("\n")[0])[:24].lower()
        subido = any(p["tipo"] == "Reel" and p["fecha"] >= day
                     and re.sub(r"\W", "", p["titulo"])[:24].lower() == key for p in posted)
        rows.append({"dia": day, "cuenta": "@guitle.es", "reel": nombres[name], "hora": horas[name], "estado": "Subido" if subido else "Pendiente",
                     "titulo": texto.split("\n")[0], "texto": texto,
                     "video": f"{RAW}/social/{day}/{name}/reel.mp4"})
    # Material suelto para subir a mano (p. ej. la presentación de una cuenta nueva), hasta que aparece publicado
    for r in load(ROOT / "social" / "pendientes.json", []):
        subido = any(p["cuenta"] == r["cuenta"] and p["titulo"].startswith(r["match"]) for p in posted)
        rows.append({"dia": today.isoformat(), "cuenta": r["cuenta"], "reel": r["reel"], "hora": r["hora"],
                     "estado": "Subido" if subido else "Pendiente", "titulo": r["texto"].split("\n")[0],
                     "texto": r["texto"], "video": r["video"]})
    return rows


def embajadores():
    rows, pais = [], None
    estados = {"⬜": "Sin contactar", "📨": "Enviado", "💬": "Contestó", "✅": "Embajador"}
    for line in (ROOT / "marketing" / "embajadores.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            pais = line[3:].split(" (")[0].strip()
            continue
        if not line.startswith("| ") or line.startswith("| |") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or not pais:
            continue
        marca, nombre, ig, seg, contenido, fuente = cells[:6]
        estado = next((v for k, v in estados.items() if k in marca), "Sin contactar")
        rows.append({"id": f"{pais}-{nombre}"[:80], "pais": pais, "nombre": nombre, "instagram": ig, "seguidores": seg,
                     "contenido": contenido, "prioridad": "Sí" if "⭐" in marca else "", "estado": estado,
                     "perfil": f"https://www.instagram.com/{ig.lstrip('@')}/" if ig.startswith("@") else ""})
    return rows


CALENDARIO = [
    ("2026-10-30", "2026-11-01", "Arranque", "3 Reels diarios (chollos, guitle, cuenta atrás) + post y 6 stories al día", "Instagram"),
    ("2026-11-01", "2026-11-14", "Embajadores", "Contactar a los guitarristas ⭐ de cada país", "DM y correo"),
    ("2026-11-02", "2026-11-02", "Presentación", "Presentación y carrusel con las cifras actuales (programado 18:13)", "Instagram"),
    ("2026-11-02", "2026-11-15", "Calentamiento", "Cuenta atrás diaria «Apunta este precio» y Reels sobre descuentos inflados", "Instagram, TikTok"),
    ("2026-11-16", "2026-11-22", "Detector de descuentos falsos", "Carrusel educativo, ejemplos reales de precios inflados, primeras colaboraciones", "Instagram, TikTok"),
    ("2026-11-23", "2026-11-26", "Black Week", "2 posts al día, stories cada 3 h, Reels de chollos reales con su histórico", "Instagram, TikTok"),
    ("2026-11-27", "2026-11-27", "Black Friday", "Resultado de la cuenta atrás (¿bajó de verdad?), stories cada 2 h, Reel resumen", "Instagram, TikTok"),
    ("2026-11-28", "2026-11-29", "Fin de semana", "Chollos que siguen vigentes", "Instagram"),
    ("2026-11-30", "2026-11-30", "Cyber Monday", "Top final de chollos reales", "Instagram, TikTok"),
    ("2026-12-01", "2026-12-01", "Balance", "«Lo que de verdad bajó»: resumen de la campaña", "Instagram"),
]


def calendario(today):
    rows = []
    for ini, fin, fase, accion, canal in CALENDARIO:
        a, b = date.fromisoformat(ini), date.fromisoformat(fin)
        estado = "Hecho" if b < today else "En curso" if a <= today else "Pendiente"
        rows.append({"id": f"{ini}-{fase}", "inicio": ini, "fin": fin, "fase": fase, "accion": accion, "canal": canal,
                     "estado": estado})
    return rows


def avisos(now, cuentas_cfg, cuentas, posts):
    """Lo que necesita atención: cuentas sin acceso, datos sin actualizar, tokens a punto de caducar, días sin publicar."""
    out = []
    add = lambda cuenta, nivel, texto: out.append({"id": f"{cuenta}-{len(out)}", "cuenta": cuenta, "nivel": nivel, "aviso": texto})
    by_handle = {r["cuenta"]: r for r in cuentas}
    for cc, cfg in cuentas_cfg.items():
        h = cfg.get("handle")
        if not h:
            continue
        r = by_handle.get(h, {})
        if cfg.get("creada") is False:
            continue
        if r.get("estado") != "Activa":
            add(h, "Alta", f"Sin acceso a la cuenta ({r.get('estado', 'desconocido')}). Revisa su token.")
            continue
        if r.get("actualizado") and now - datetime.fromisoformat(r["actualizado"]) > timedelta(hours=30):
            add(h, "Media", f"Datos sin actualizar desde el {r['actualizado'][:10]}.")
        if cfg.get("token_desde"):
            caduca = date.fromisoformat(cfg["token_desde"]) + timedelta(days=60)
            dias = (caduca - now.date()).days
            if dias <= 10:
                add(h, "Alta" if dias <= 3 else "Media", f"El token caduca el {caduca.isoformat()} ({max(dias, 0)} días): hay que renovarlo.")
        if cfg.get("publica") and now.hour >= 12:
            hoy = [p for p in posts if p["cuenta"] == h and p["fecha"] == now.date().isoformat()]
            if not hoy:
                add(h, "Alta", "Hoy no se ha publicado nada todavía.")
        elif not cfg.get("publica"):
            add(h, "Baja", "Publicación diaria aún sin programar.")
    return out


def main():
    today = datetime.now(timezone.utc).date()
    OUT.mkdir(parents=True, exist_ok=True)
    cuentas_cfg = load(ROOT / "social" / "cuentas.json", {})
    paises = load(ROOT / "data" / "catalog" / "paises.json", {})
    cuentas, diario, posts = [], [], []
    history = load(OUT / "diario.json", [])
    for cc, cfg in cuentas_cfg.items():
        handle, env = cfg.get("handle"), cfg.get("token_env")
        token = os.environ.get(env) if env else None
        row = {"pais": PAISES.get(cc, cc), "cuenta": handle or "Por crear", "web": "guitle.com" + paises.get(cc, {}).get("path", "/"),
               "guitarras": paises.get(cc, {}).get("guitars"), "tiendas": paises.get(cc, {}).get("stores"),
               "estado": "Por crear", "seguidores": None, "publicaciones": None, "alcance_7d": None,
               "visualizaciones_7d": None, "visitas_7d": None}
        if cfg.get("creada") is False:  # cuenta prevista, aún sin crear en Instagram
            row["estado"] = "Por crear"
        elif handle and (token or not env):
            try:
                me = api("me", token, fields="user_id,followers_count,media_count")
                user = me["user_id"]
                row.update(estado="Activa", seguidores=me["followers_count"], publicaciones=me["media_count"],
                           actualizado=datetime.now(timezone.utc).isoformat(timespec="minutes"))
                known = {(h["dia"], h["cuenta"]) for h in history}
                start = date.fromisoformat(cfg.get("desde", today.isoformat()))
                for n in range((today - start).days + 1):
                    d = start + timedelta(days=n)
                    if (d.isoformat(), handle) in known and d < today - timedelta(days=2):
                        continue  # los últimos días se recalculan: Instagram los completa con retraso
                    ins = day_insights(user, token, d)
                    history = [h for h in history if not (h["dia"] == d.isoformat() and h["cuenta"] == handle)]
                    history.append({"dia": d.isoformat(), "cuenta": handle, "alcance": ins["reach"],
                                    "visualizaciones": ins["views"], "visitas_perfil": ins["profile_views"],
                                    "cuentas_interactuaron": ins["accounts_engaged"], "interacciones": ins["total_interactions"],
                                    "clics_web": ins["website_clicks"], "seguidores": me["followers_count"] if d == today else None})
                # Seguidores: la API solo da el total actual; se guarda el de cada día al pasar
                for h in history:
                    if h["cuenta"] == handle and h["dia"] == today.isoformat():
                        h["seguidores"] = me["followers_count"]
                week = [h for h in history if h["cuenta"] == handle and h["dia"] > (today - timedelta(days=7)).isoformat()]
                row.update(alcance_7d=sum(h["alcance"] or 0 for h in week),
                           visualizaciones_7d=sum(h["visualizaciones"] or 0 for h in week),
                           visitas_7d=sum(h["visitas_perfil"] or 0 for h in week))
                posts += media_rows(user, token, handle) + (stories_rows(handle) if cc == "es" else [])
            except RuntimeError as exc:
                row["estado"] = f"Error: {exc}"[:80]
        elif handle:
            # El token solo se ve en sesiones abiertas después de guardarlo: se conservan los últimos datos de esa cuenta
            prev = next((r for r in load(OUT / "cuentas.json", []) if r.get("cuenta") == handle and r.get("estado") == "Activa"), None)
            if prev:
                row = {**prev, "guitarras": row["guitarras"], "tiendas": row["tiendas"]}
                posts += [p for p in load(OUT / "publicaciones.json", []) if p.get("cuenta") == handle]
            else:
                row["estado"] = "Falta el token"
        cuentas.append(row)
    history.sort(key=lambda h: (h["dia"], h["cuenta"]))
    posts.sort(key=lambda p: (p["fecha"], p["hora"]), reverse=True)
    files = {"cuentas.json": cuentas, "diario.json": history, "publicaciones.json": posts,
             "reels_hoy.json": reels_hoy(today, posts), "embajadores.json": embajadores(), "calendario.json": calendario(today),
             "avisos.json": avisos(datetime.now(timezone.utc), cuentas_cfg, cuentas, posts)}
    for name, rows in files.items():
        (OUT / name).write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{name}: {len(rows)} filas")


if __name__ == "__main__":
    main()
