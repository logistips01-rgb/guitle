"""Vigilancia del gasto de Cloudflare (tope de infraestructura de guitle: 10 € al mes, de un presupuesto total de 50 €:
verificación de Instagram 16 €, el resto publicidad).

Cada mañana consulta el consumo real del ciclo de facturación (empieza el día 30) con la API de analítica: operaciones
de R2 de clase A (escrituras y listados) y B (lecturas), espacio de R2 y peticiones del Worker. Calcula lo que va
gastado y la previsión a fin de ciclo (al ritmo de los últimos 3 días) y, si la previsión pasa del tope, manda un correo
a hola@guitle.com. El día 1 manda siempre el informe del ciclo anterior.

Uso: CLOUDFLARE_API_TOKEN=… ACCOUNT=… SMTP_*=… python -m scraper.gasto   (lo lanza .github/workflows/gasto.yml)
"""
import json
import math
import os
from datetime import date, datetime, timedelta, timezone

import requests

TOPE_EUR = 10.0       # infraestructura al mes
USD_EUR = 0.93        # aproximado
FIJO_USD = 5.0        # Workers Paid
A_TYPES = {"PutObject", "CopyObject", "CreateMultipartUpload", "UploadPart", "UploadPartCopy", "CompleteMultipartUpload",
           "ListObjects", "ListObjectsV2", "ListMultipartUploads", "ListParts", "ListBuckets", "PutBucket",
           "PutBucketCors", "PutBucketLifecycleConfiguration"}
B_TYPES = {"GetObject", "HeadObject", "HeadBucket", "GetBucketLocation", "GetBucketCors", "GetBucketLifecycleConfiguration"}
TO = "hola@guitle.com"


def q(query):
    r = requests.post("https://api.cloudflare.com/client/v4/graphql", timeout=60,
                      headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"}, json={"query": query})
    r.raise_for_status()
    d = r.json()
    if d.get("errors"):
        raise RuntimeError(d["errors"])
    return d["data"]["viewer"]["accounts"][0]


def _thirtieth(y, m):
    """El día 30 del mes (o el último, en febrero): ahí empieza cada ciclo de facturación de Cloudflare."""
    last = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).day
    return date(y, m, min(30, last))


def cycle(today):
    """Inicio y último día del ciclo de facturación que contiene hoy (del 30 al 29)."""
    start = _thirtieth(today.year, today.month)
    if today < start:
        prev = today.replace(day=1) - timedelta(days=1)
        start = _thirtieth(prev.year, prev.month)
    nxt = start.replace(day=1) + timedelta(days=32)
    return start, _thirtieth(nxt.year, nxt.month) - timedelta(days=1)


def usage(acc, start, end):
    s, e = f"{start.isoformat()}T00:00:00Z", f"{(end + timedelta(days=1)).isoformat()}T00:00:00Z"
    d = q(f'{{viewer{{accounts(filter:{{accountTag:"{acc}"}}){{'
          f'r2OperationsAdaptiveGroups(limit:1000,filter:{{datetime_geq:"{s}",datetime_lt:"{e}"}}){{sum{{requests}} dimensions{{actionType date}}}}'
          f' r2StorageAdaptiveGroups(limit:1,filter:{{datetime_geq:"{s}",datetime_lt:"{e}"}},orderBy:[datetime_DESC]){{max{{payloadSize}}}}'
          f' workersInvocationsAdaptive(limit:100,filter:{{datetime_geq:"{s}",datetime_lt:"{e}"}}){{sum{{requests}}}}}}}}}}')
    a, b, by_day = 0, 0, {}
    for g in d["r2OperationsAdaptiveGroups"]:
        t, n, day = g["dimensions"]["actionType"], g["sum"]["requests"], g["dimensions"]["date"]
        if t in A_TYPES:
            a += n
            by_day[day] = by_day.get(day, 0) + n
        elif t in B_TYPES:
            b += n
    gb = (d["r2StorageAdaptiveGroups"][0]["max"]["payloadSize"] / 1e9) if d["r2StorageAdaptiveGroups"] else 0
    workers = sum(g["sum"]["requests"] for g in d["workersInvocationsAdaptive"])
    return a, b, gb, workers, by_day


def cost_usd(a, b, gb, workers):
    """Precios de Cloudflare: clase A 4,50 $ por millón (se cobra por millones enteros) por encima de 1 M; clase B 0,36 $
    por millón por encima de 10 M; espacio 0,015 $/GB por encima de 10 GB; Worker 0,30 $ por millón por encima de 10 M."""
    return {"fijo": FIJO_USD,
            "escrituras R2 (clase A)": 4.5 * max(0, math.ceil((a - 1e6) / 1e6)),
            "lecturas R2 (clase B)": 0.36 * max(0, (b - 10e6) / 1e6),
            "espacio R2": 0.015 * max(0, gb - 10),
            "peticiones Worker": 0.30 * max(0, (workers - 10e6) / 1e6)}


def main():
    acc = os.environ["ACCOUNT"].lower()
    today = datetime.now(timezone.utc).date()
    start, end = cycle(today)
    a, b, gb, workers, by_day = usage(acc, start, today)
    days_done = (today - start).days + 1
    days_total = (end - start).days + 1
    recent = [by_day.get((today - timedelta(days=i)).isoformat(), 0) for i in range(1, 4)]
    a_proj = a + (sum(recent) / 3) * (days_total - days_done)
    k = days_total / max(1, days_done)
    now = cost_usd(a, b, gb, workers)
    proj = cost_usd(a_proj, b * k, gb, workers * k)
    eur_now, eur_proj = sum(now.values()) * USD_EUR, sum(proj.values()) * USD_EUR
    resumen = {"ciclo": f"{start} → {end}", "dia": f"{days_done}/{days_total}", "escrituras_A": a, "lecturas_B": b,
               "GB": round(gb, 2), "peticiones_worker": workers, "gastado_eur": round(eur_now, 2),
               "prevision_eur": round(eur_proj, 2), "tope_eur": TOPE_EUR, "desglose_prevision_usd": proj}
    print(json.dumps(resumen, ensure_ascii=False, indent=1), flush=True)
    # Aviso si lo que queda de ciclo, al ritmo de los últimos 3 días, va a sumar más de 3 € (algo se ha disparado), o si
    # la previsión pasa del tope sin que lo expliquen gastos ya hechos; y siempre el día 1, el informe.
    informe = today.day == 1
    if not informe and (eur_proj - eur_now) <= 3 and (eur_proj <= TOPE_EUR or eur_now >= TOPE_EUR):
        return
    asunto = (f"guitle: el gasto de Cloudflare va camino de {eur_proj:.2f} € (tope {TOPE_EUR:.0f} €)" if not informe
              else f"guitle: informe de gasto de Cloudflare ({eur_now:.2f} € en el ciclo)")
    filas = "".join(f"<tr><td>{k}</td><td style='text-align:right'>{v * USD_EUR:.2f} €</td></tr>" for k, v in proj.items())
    html = (f"<p>Ciclo {start} → {end} (día {days_done} de {days_total}).</p>"
            f"<p><b>Gastado:</b> {eur_now:.2f} € · <b>Previsión a fin de ciclo:</b> {eur_proj:.2f} € · <b>Tope:</b> {TOPE_EUR:.0f} €</p>"
            f"<table>{filas}</table><p>Escrituras R2: {a:,} · lecturas: {b:,} · espacio: {gb:.1f} GB · peticiones a la web: {workers:,}</p>"
            "<p>Este aviso lo manda la vigilancia diaria de guitle (scraper/gasto.py).</p>")
    from .alerts import Mailer
    m = Mailer(dry_run=not os.environ.get("SMTP_PASS"))
    m.send(TO, asunto, html, f"{asunto}\nGastado {eur_now:.2f} €, previsión {eur_proj:.2f} €, tope {TOPE_EUR:.0f} €.")
    m.close()


if __name__ == "__main__":
    main()
