"""Afiliaciones de todas las webs (guitle y mootle) en un sitio: lo ganado cada día en Awin (Cultura y los que lleguen) y
en eBay Partner Network (por campaña/etiqueta: guitle, mootle), guardado en Firestore (colección "c", documentos
"afil_AAAA-MM-DD", solo los lee el titular, como el resto de estadísticas) y enseñado en stats.html. Los lunes manda a
hola@guitle.com el resumen de la semana y del mes, con el gasto de Cloudflare al lado.

Amazon no tiene API de ganancias para afiliados: su informe se carga a mano (data de Manuel → "amazon_eur" del día),
separando por ID de seguimiento: guitle-21, guitle00-21, guitle08-21, guitle0e-21 → guitle; mootle-21 → mootle (ya en
producción en las fichas de motos de mootle).

Claves (secretos de GitHub): AWIN_API_TOKEN (Awin → perfil → API credentials), EPN_ACCOUNT_SID y EPN_AUTH_TOKEN (eBay
Partner Network → Tools → API), FIREBASE_SA y SMTP_* (ya están). Sin una clave, ese programa se salta.

Uso: python -m scraper.afiliados [--dias 35] [--correo]   (lo lanza .github/workflows/afiliados.yml cada mañana)
"""
import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone

import requests

AWIN_PUBLISHER = 3136285
TO = "hola@guitle.com"


def _num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def awin(start, end):
    """{día: {"eur": comisión, "n": ventas, "por": {anunciante: comisión}}} de Awin (comisiones pendientes y aprobadas)."""
    tok = os.environ.get("AWIN_API_TOKEN")
    if not tok:
        print("[awin] sin AWIN_API_TOKEN: se salta", flush=True)
        return {}
    h = {"Authorization": f"Bearer {tok.strip()}"}
    names = {}
    try:
        r = requests.get(f"https://api.awin.com/publishers/{AWIN_PUBLISHER}/programmes?relationship=joined", headers=h, timeout=60)
        names = {str(p.get("id")): p.get("name") for p in (r.json() if r.ok else [])}
    except Exception:  # noqa: BLE001
        pass
    out, d = {}, start
    while d <= end:  # la API da como mucho 31 días por consulta
        e = min(end, d + timedelta(days=30))
        r = requests.get(f"https://api.awin.com/publishers/{AWIN_PUBLISHER}/transactions/", headers=h, timeout=120,
                         params={"startDate": f"{d}T00:00:00", "endDate": f"{e}T23:59:59", "timezone": "Europe/Paris",
                                 "dateType": "transaction"})
        if not r.ok:
            print(f"[awin] HTTP {r.status_code}: {r.text[:200]}", flush=True)
            return out
        for t in r.json():
            if (t.get("commissionStatus") or "").lower() in ("declined", "deleted"):
                continue
            day = (t.get("transactionDate") or "")[:10]
            com = _num((t.get("commissionAmount") or {}).get("amount"))
            adv = names.get(str(t.get("advertiserId")), str(t.get("advertiserId")))
            o = out.setdefault(day, {"eur": 0.0, "n": 0, "por": {}})
            o["eur"] += com
            o["n"] += 1
            o["por"][adv] = round(o["por"].get(adv, 0) + com, 2)
        d = e + timedelta(days=1)
    print(f"[awin] {sum(v['n'] for v in out.values())} ventas, {sum(v['eur'] for v in out.values()):.2f} €", flush=True)
    return out


def _pick(rec, *words):
    """Valor del primer campo cuyo nombre contiene alguna de las palabras (los nombres del informe de eBay varían)."""
    for k, v in rec.items():
        if any(w in k.lower() for w in words):
            return v
    return None


def ebay(start, end):
    """{día: {"eur": ganancia, "n": ventas, "por": {etiqueta: ganancia}}} de eBay Partner Network; la etiqueta separa
    guitle (guitle, guitle-es…) de mootle."""
    sid, tok = os.environ.get("EPN_ACCOUNT_SID"), os.environ.get("EPN_AUTH_TOKEN")
    if not (sid and tok):
        print("[ebay] sin EPN_ACCOUNT_SID / EPN_AUTH_TOKEN: se salta", flush=True)
        return {}
    r = requests.get(f"https://api.partner.ebay.com/Mediapartners/{sid.strip()}/Reports/ebay_partner_transaction_detail.json",
                     # Tokens de acceso nuevos: usuario = su propio SID (EPN_TOKEN_SID); los antiguos: el Account SID
                     auth=((os.environ.get("EPN_TOKEN_SID") or sid).strip(), tok.strip()), timeout=120,
                     headers={"Accept": "application/json"},
                     params={"STATUS": "ALL", "START_DATE": str(start), "END_DATE": str(end)})
    if not r.ok:
        print(f"[ebay] HTTP {r.status_code}: {r.text[:200]}", flush=True)
        return {}
    recs = r.json().get("Records") or r.json().get("records") or []
    if recs:
        print(f"[ebay] campos del informe: {sorted(recs[0])[:40]}", flush=True)
    out = {}
    for rec in recs:
        day = str(_pick(rec, "event_date", "eventdate", "transaction_date", "date") or "")[:10]
        com = _num(_pick(rec, "earning", "commission"))
        tag = str(_pick(rec, "custom_id", "customid", "subid", "reference") or "")
        site = "mootle" if "mootle" in tag.lower() else "guitle"
        o = out.setdefault(day, {"eur": 0.0, "n": 0, "por": {}})
        o["eur"] += com
        o["n"] += 1
        o["por"][site] = round(o["por"].get(site, 0) + com, 2)
    print(f"[ebay] {sum(v['n'] for v in out.values())} ventas, {sum(v['eur'] for v in out.values()):.2f} €", flush=True)
    return out


def save(days):
    """Un documento por día en Firestore (c/afil_AAAA-MM-DD); lo puesto a mano (amazon_eur) se conserva."""
    from .alerts import DOCS, session
    s = session()
    for day, v in sorted(days.items()):
        fields = {"fecha": {"stringValue": day}, "detalle": {"stringValue": json.dumps(v, ensure_ascii=False)}}
        for prog in ("awin", "ebay"):
            p = v.get(prog) or {}
            fields[f"{prog}_eur"] = {"doubleValue": round(p.get("eur", 0.0), 2)}
            fields[f"{prog}_n"] = {"integerValue": str(p.get("n", 0))}
        mask = "&".join(f"updateMask.fieldPaths={k}" for k in fields)
        s.patch(f"{DOCS}/c/afil_{day}?{mask}", json={"fields": fields}, timeout=60).raise_for_status()
    print(f"[afiliados] {len(days)} días guardados", flush=True)


def _load(start, end):
    from .alerts import DOCS, session
    s = session()
    base = DOCS.split("/v1/", 1)[1]
    q = {"structuredQuery": {"from": [{"collectionId": "c"}], "where": {"compositeFilter": {"op": "AND", "filters": [
        {"fieldFilter": {"field": {"fieldPath": "__name__"}, "op": "GREATER_THAN_OR_EQUAL",
                         "value": {"referenceValue": f"{base}/c/afil_{start}"}}},
        {"fieldFilter": {"field": {"fieldPath": "__name__"}, "op": "LESS_THAN_OR_EQUAL",
                         "value": {"referenceValue": f"{base}/c/afil_{end}"}}}]}}}}
    r = s.post(f"{DOCS}:runQuery", json=q, timeout=60)
    r.raise_for_status()
    out = []
    for x in r.json():
        f = (x.get("document") or {}).get("fields")
        if f:
            out.append({k: v["stringValue"] if "stringValue" in v else _num(v.get("doubleValue", v.get("integerValue")))
                        for k, v in f.items()})
    return out


def _manual():
    """Informes de Amazon y eBay subidos a mano en stats.html (colección "afilm": {fecha, prog, eur, por})."""
    from .alerts import DOCS, session
    s, out, tok = session(), [], ""
    while True:
        r = s.get(f"{DOCS}/afilm", params={"pageSize": 300, **({"pageToken": tok} if tok else {})}, timeout=60)
        if not r.ok:
            return out
        j = r.json()
        for d in j.get("documents", []):
            f = d.get("fields", {})
            out.append({"fecha": f.get("fecha", {}).get("stringValue", ""), "prog": f.get("prog", {}).get("stringValue", ""),
                        "eur": _num(f.get("eur", {}).get("doubleValue", f.get("eur", {}).get("integerValue")))})
        tok = j.get("nextPageToken")
        if not tok:
            return out


def email(today):
    """Resumen de la semana pasada y del mes, con el gasto de Cloudflare."""
    week0, month0 = today - timedelta(days=7), today.replace(day=1)
    rows = _load(min(week0, month0), today)
    for m in _manual():  # Amazon y eBay subidos a mano
        if m["fecha"] >= str(min(week0, month0)) and m["prog"] in ("amazon", "ebay"):
            rows.append({"fecha": m["fecha"], f"{m['prog']}_eur": m["eur"]})
    tot = lambda rs, k: sum(r.get(k) or 0 for r in rs)
    wk = [r for r in rows if r["fecha"] >= str(week0)]
    mo = [r for r in rows if r["fecha"] >= str(month0)]
    progs = [("Amazon", "amazon_eur"), ("Awin", "awin_eur"), ("eBay", "ebay_eur")]
    cf = ""
    try:
        from . import gasto
        start, _ = gasto.cycle(today)
        a, b, gb, w, _ = gasto.usage(os.environ["ACCOUNT"].lower(), start, today)
        cf = f"{sum(gasto.cost_usd(a, b, gb, w).values()) * gasto.USD_EUR:.2f} €"
    except Exception:  # noqa: BLE001
        cf = "—"
    tr = "".join(f"<tr><td>{n}</td><td style='text-align:right'>{tot(wk, k):.2f} €</td><td style='text-align:right'>{tot(mo, k):.2f} €</td></tr>"
                 for n, k in progs)
    week_eur, month_eur = sum(tot(wk, k) for _, k in progs), sum(tot(mo, k) for _, k in progs)
    subject = f"guitle: afiliados — {week_eur:.2f} € esta semana, {month_eur:.2f} € en el mes"
    html = (f"<p>Comisiones de guitle y mootle (pendientes y aprobadas).</p><table cellpadding='6'>"
            f"<tr><th></th><th>Últimos 7 días</th><th>Este mes</th></tr>{tr}"
            f"<tr><th>Total</th><th style='text-align:right'>{week_eur:.2f} €</th><th style='text-align:right'>{month_eur:.2f} €</th></tr></table>"
            f"<p>Gasto de Cloudflare en el ciclo: {cf}. Detalle por día en guitle.com/stats.html.</p>"
            "<p>Amazon y eBay no dan sus ganancias por API: sube su informe (CSV) en stats.html, en el panel de afiliados.</p>")
    from .alerts import Mailer
    m = Mailer(dry_run=not os.environ.get("SMTP_PASS"))
    m.send(TO, subject, html, subject)
    m.close()
    print(f"[afiliados] correo: {subject}", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=35)
    ap.add_argument("--correo", action="store_true", help="manda el resumen aunque no sea lunes")
    a = ap.parse_args(argv)
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=a.dias)
    days = {}
    for prog, data in (("awin", awin(start, today)), ("ebay", ebay(start, today))):
        for day, v in data.items():
            if day:
                days.setdefault(day, {})[prog] = v
    if days and os.environ.get("FIREBASE_SA"):
        save(days)
    if (a.correo or today.weekday() == 0) and os.environ.get("FIREBASE_SA"):
        email(today)


if __name__ == "__main__":
    main()
