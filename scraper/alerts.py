"""Avisos por correo cuando baja el precio de una guitarra (o de un teclado o pedal).

La ficha (producto.js) guarda en Firestore (colección "alertas", proyecto guitle-d48d8) un documento por aviso:
email, slug, name, kind, price (precio al apuntarse), target (precio objetivo, opcional) y ok=false. El id del
documento es un código aleatorio largo que solo conoce quien se apunta: sirve para confirmar y para darse de baja
(alerta.html?c=… / ?baja=…). Las reglas de Firestore (firestore.rules) no dejan leer la colección desde la web.

Esta tarea (GitHub Actions, cada 15 minutos) lee los avisos con una cuenta de servicio y:
  - manda el correo de confirmación a los nuevos (uno por dirección y día, contra el abuso);
  - borra los no confirmados en 7 días;
  - a los confirmados, si el mejor precio de hoy baja del de referencia (o del objetivo), les avisa una vez.

Secretos (GitHub › Settings › Secrets › Actions): FIREBASE_SA (JSON de la cuenta de servicio), SMTP_HOST,
SMTP_PORT (465 o 587), SMTP_USER (hola@guitle.com) y SMTP_PASS. Sin ellos no hace nada.

    python -m scraper.alerts [--dry-run]
"""
import argparse
import html
import json
import os
import re
import smtplib
import ssl
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://guitle.com"
DOCS = "https://firestore.googleapis.com/v1/projects/guitle-d48d8/databases/(default)/documents"
CATALOGS = ["data/catalog/products.json", "data/catalog/acusticas/acusticas.json", "data/catalog/acusticas/clasicas.json",
            "data/catalog/equipo/teclados.json", "data/catalog/equipo/pedales.json"]
PENDING_DAYS = 7  # sin confirmar en este tiempo, se borra
MAX_CONFIRMS = 40  # correos de confirmación por pasada como mucho (contra el abuso del formulario)


def eur(v):
    whole, cents = int(round(v * 100)) // 100, int(round(v * 100)) % 100
    txt = f"{whole:,}".replace(",", ".")
    return f"{txt},{cents:02d} €" if cents else f"{txt} €"


def products():
    """slug → producto de hoy (nombre, mejor precio y tienda, foto) de todos los catálogos. Los de otros países van
    con su código delante ("pt/<slug>"), igual que los guarda su ficha (producto.js)."""
    from .intl import SITES, _json_path
    out = {}
    paths = [("", path) for path in CATALOGS] + [(code + "/", _json_path(code, kind)) for code in SITES for kind in SITES[code]["kinds"]]
    for prefix, path in paths:
        try:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        for p in data["products"]:
            if p.get("slug") and p.get("items"):
                out[prefix + p["slug"]] = {**p, "store_name": data["stores"].get(p["items"][0]["s"], p["items"][0]["s"]),
                                           "site": prefix.rstrip("/")}
    return out


# --- Firestore (REST con la cuenta de servicio) ------------------------------------------------------------

def session():
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account
    info = json.loads(os.environ["FIREBASE_SA"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/datastore"])
    return AuthorizedSession(creds)


def _value(v):
    for kind in ("stringValue", "booleanValue", "timestampValue"):
        if kind in v:
            return v[kind]
    if "integerValue" in v:
        return float(v["integerValue"])
    if "doubleValue" in v:
        return float(v["doubleValue"])
    return None


def _field(v):
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, (int, float)):
        return {"doubleValue": float(v)}
    return {"stringValue": str(v)}


def list_alerts(s):
    out, token = [], None
    while True:
        resp = s.get(f"{DOCS}/alertas", params={"pageSize": 300, **({"pageToken": token} if token else {})}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for d in data.get("documents", []):
            doc = {k: _value(v) for k, v in d.get("fields", {}).items()}
            doc.update(id=d["name"].rsplit("/", 1)[-1], created=d["createTime"])
            out.append(doc)
        token = data.get("nextPageToken")
        if not token:
            return out


def patch(s, doc_id, **fields):
    params = [("updateMask.fieldPaths", k) for k in fields] + [("currentDocument.exists", "true")]
    s.patch(f"{DOCS}/alertas/{doc_id}", params=params, json={"fields": {k: _field(v) for k, v in fields.items()}},
            timeout=30).raise_for_status()


def delete(s, doc_id):
    s.delete(f"{DOCS}/alertas/{doc_id}", timeout=30).raise_for_status()


# --- Correos -------------------------------------------------------------------------------------------------

# Textos de los correos: España aquí; los demás países, en scraper.intl (T[...]["mail"]).
ES = {"tagline": "guitarras al mejor precio",
      "footer": "guitle compara cada día los precios de las tiendas de música.\nRecibes este correo porque pediste un aviso "
                "en guitle.com. Responsable: Manuel Lorente Gálvez, hola@guitle.com.",
      "privacy": "Privacidad", "confirmSubject": "Confirma tu aviso de precio en guitle", "confirmTitle": "Confirma tu aviso de precio",
      "asked": "Has pedido que te avisemos cuando baje de precio{target}:", "below": " por debajo de <b>{v}</b>",
      "confirmAsk": "Confirma que quieres recibir el aviso en esta dirección:", "confirmBtn": "Confirmar el aviso",
      "notYou": "Si no lo has pedido tú, no hagas nada: sin confirmar, el aviso se borra solo en 7 días y no volverás a saber de nosotros.",
      "dropSubject": "Ha bajado: {name} a {price}", "dropTitle": "¡Ha bajado de precio!", "nowAt": "en {s} · antes {v}",
      "seeAll": "Ver precios en todas las tiendas",
      "check": "Los precios cambian a diario: compruébalo en la tienda antes de comprar. ¿Ya no te interesa?",
      "stop": "Dejar de recibir este aviso"}


def _money(code):
    """Formato del precio: el de España, o el del país del aviso."""
    if not code:
        return globals()["eur"]
    from .intl import money
    return lambda v: money(v, code)


def _site(alert):
    """(código del país o "", textos, prefijo de la ruta, página de privacidad) según el slug del aviso."""
    from .intl import SITES, _anchor, strings
    code = alert["slug"].split("/")[0] if "/" in alert["slug"] else ""
    if code in SITES:
        return code, strings(code)["mail"], f"/{code}", f"/{code}/legal.html#{_anchor(code)}", SITES[code]["lang"][:2]
    return "", ES, "", "/legal.html#privacidad", "es"


def _page(title, body_html, m=ES, privacy="/legal.html#privacidad", lang="es"):
    return f"""<!doctype html><html lang="{lang}"><body style="margin:0;background:#f4f4f2;font-family:Arial,Helvetica,sans-serif;color:#0b0b0b">
<div style="max-width:560px;margin:0 auto;padding:24px 16px">
<p style="margin:0 0 18px"><a href="{SITE}/" style="text-decoration:none"><img src="{SITE}/icons/logo-email.png" width="115" height="42"
alt="guitle" style="vertical-align:middle;border:0"></a>
<span style="color:#2a78d6;font-size:13px;font-weight:600;vertical-align:middle"> · {m["tagline"]}</span></p>
<div style="background:#fcfcfb;border:1px solid #e2e1dc;border-radius:14px;padding:20px">
<h1 style="font-size:20px;margin:0 0 12px">{html.escape(title)}</h1>{body_html}</div>
<p style="color:#7a7974;font-size:12px;line-height:1.5;margin:16px 4px 0">{m["footer"]}
<a href="{SITE}{privacy}" style="color:#7a7974">{m["privacy"]}</a>.</p></div></body></html>"""


def _button(url, label):
    return (f'<p style="margin:18px 0 6px"><a href="{html.escape(url)}" style="background:#2a78d6;color:#fff;text-decoration:none;'
            f'font-weight:700;padding:11px 18px;border-radius:999px;display:inline-block">{html.escape(label)}</a></p>')


def confirm_mail(alert):
    code, m, base, privacy, lang = _site(alert)
    eur = _money(code)
    link = f"{SITE}{base}/alerta.html?c={alert['id']}"
    target = m["below"].format(v=eur(alert["target"])) if alert.get("target") else ""
    body = (f'<p style="line-height:1.5">{m["asked"].format(target=target)}</p>'
            f'<p style="font-weight:700;line-height:1.4">{html.escape(alert["name"])}</p>'
            f'<p style="line-height:1.5">{m["confirmAsk"]}</p>'
            + _button(link, m["confirmBtn"])
            + f'<p style="color:#7a7974;font-size:13px;line-height:1.5">{m["notYou"]}</p>')
    text = (f"{html.unescape(re.sub('<[^>]+>', '', m['asked'].format(target=target)))} {alert['name']}\n\n"
            f"{m['confirmBtn']}: {link}\n\n{m['notYou']}")
    return m["confirmSubject"], _page(m["confirmTitle"], body, m, privacy, lang), text, None


def drop_mail(alert, p, before):
    code, m, base, privacy, lang = _site(alert)
    eur = _money(code)
    page = f"{SITE}{base}/g/{p['slug']}.html"
    off = f"{SITE}{base}/alerta.html?baja={alert['id']}"
    best = p["items"][0]
    img = (f'<p style="margin:0 0 12px;text-align:center"><img src="{SITE}/img/p/{html.escape(p["th"])}" alt="" '
           f'style="max-height:180px;max-width:100%"></p>' if p.get("th") else "")
    body = (img + f'<p style="font-weight:700;line-height:1.4;margin:0 0 6px">{html.escape(p["name"])}</p>'
            f'<p style="font-size:28px;font-weight:800;margin:6px 0">{eur(best["p"])}</p>'
            f'<p style="color:#52514e;margin:0">{m["nowAt"].format(s=html.escape(p["store_name"]), v=eur(before))}</p>'
            + _button(page, m["seeAll"])
            + f'<p style="color:#7a7974;font-size:13px;line-height:1.5;margin-top:14px">{m["check"]} <a href="{off}" style="color:#7a7974">'
              f'{m["stop"]}</a>.</p>')
    text = (f"{p['name']}\n{eur(best['p'])} · {m['nowAt'].format(s=p['store_name'], v=eur(before))}\n\n"
            f"{m['seeAll']}: {page}\n\n{m['stop']}: {off}")
    return (m["dropSubject"].format(name=p["name"], price=eur(best["p"])), _page(m["dropTitle"], body, m, privacy, lang),
            text, off)


class Mailer:
    def __init__(self, dry_run):
        self.dry_run, self.smtp = dry_run, None
        self.user = os.environ.get("SMTP_USER", "hola@guitle.com")

    def send(self, to, subject, html_body, text, unsubscribe=None):
        msg = EmailMessage()
        msg["From"] = formataddr(("guitle", self.user))
        msg["To"] = to
        msg["Subject"] = subject
        msg["Message-ID"] = make_msgid(domain="guitle.com")
        if unsubscribe:
            msg["List-Unsubscribe"] = f"<{unsubscribe}>"
        msg.set_content(text)
        msg.add_alternative(html_body, subtype="html")
        if self.dry_run:
            print(f"[alerts] (prueba) a {to}: {subject}", flush=True)
            return
        if self.smtp is None:
            host, port = os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT") or 465)
            ctx = ssl.create_default_context()
            if port == 465:
                self.smtp = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
            else:
                self.smtp = smtplib.SMTP(host, port, timeout=30)
                self.smtp.starttls(context=ctx)
            self.smtp.login(self.user, os.environ["SMTP_PASS"])
        self.smtp.send_message(msg)

    def close(self):
        if self.smtp is not None:
            self.smtp.quit()


# --- Tarea -----------------------------------------------------------------------------------------------------

def threshold(alert):
    """Precio al que se avisa. Sin objetivo: una bajada de al menos 1 € (y el 1 %) sobre el de referencia (el del
    último aviso o, si no hubo, el del día en que se apuntó). Con objetivo: llegar a él, y después, cada nueva bajada."""
    base = alert.get("last") or alert["price"]
    drop = base - max(1.0, base * 0.01)
    if not alert.get("target"):
        return drop
    return min(alert["target"], drop) if alert.get("last") else alert["target"]


def run(dry_run=False):
    if not os.environ.get("FIREBASE_SA") or (not dry_run and not os.environ.get("SMTP_PASS")):
        print("[alerts] faltan los secretos FIREBASE_SA o SMTP_*: no se hace nada", flush=True)
        return
    s = session()
    alerts = list_alerts(s)
    catalog = products()
    mail = Mailer(dry_run)
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    stats = {"confirmaciones": 0, "avisos": 0, "borrados": 0}
    # Una confirmación por dirección y día: alguien no puede llenar de correos el buzón de otro.
    confirmed_today = {a["email"].lower() for a in alerts if (a.get("sent_confirm") or "")[:10] == today}
    try:
        for a in alerts:
            if not all(a.get(k) for k in ("email", "slug", "price")):
                continue
            p = catalog.get(a["slug"])
            if p is None:
                # Ficha que no existe (o retirada): no se manda nada. El nombre del correo sale siempre del catálogo,
                # nunca del formulario, para que nadie pueda colar su propio texto en un correo de guitle.
                if not a.get("ok"):
                    if not dry_run:
                        delete(s, a["id"])
                    stats["borrados"] += 1
                continue
            a["name"] = p["name"]
            if not a.get("ok"):
                if datetime.fromisoformat(a["created"].replace("Z", "+00:00")) < now - timedelta(days=PENDING_DAYS):
                    if not dry_run:
                        delete(s, a["id"])
                    stats["borrados"] += 1
                elif (not a.get("sent_confirm") and a["email"].lower() not in confirmed_today
                      and stats["confirmaciones"] < MAX_CONFIRMS):
                    mail.send(a["email"], *confirm_mail(a))
                    if not dry_run:
                        patch(s, a["id"], sent_confirm=now.isoformat(timespec="seconds"))
                    confirmed_today.add(a["email"].lower())
                    stats["confirmaciones"] += 1
                continue
            if a.get("notified") == today:
                continue
            best = p["items"][0]["p"]
            if best <= threshold(a):
                mail.send(a["email"], *drop_mail(a, p, a.get("last") or a["price"]))
                if not dry_run:
                    patch(s, a["id"], last=best, notified=today)
                stats["avisos"] += 1
    finally:
        mail.close()
    print(f"[alerts] {len(alerts)} avisos guardados; enviados {stats}", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="no envía ni cambia nada: solo dice qué haría")
    run(parser.parse_args(argv).dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
