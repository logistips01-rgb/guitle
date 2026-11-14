"""Vigilancia del buzón hola@guitle.com (pedido por Manuel el 14/11/2026, tras pedir la marca «guitle» en la OEPM).

Una vez al día lee, sin marcar nada como leído (BODY.PEEK) ni borrar nada, los correos de los últimos días y busca:
  - correos de la OEPM (oepm.es / oepm.gob.es): notificaciones oficiales de la marca;
  - cartas de cobro que imitan a un registro oficial ("registro de marcas", "publicación", "WIPO/OMPI", facturas por
    la marca) y que NO vienen de la OEPM, la EUIPO ni la OMPI: posibles cobros falsos.
Si encuentra algo nuevo, manda a hola@guitle.com un aviso con el remitente y el asunto de cada uno. En el registro
de GitHub (público) solo salen cuántos hay de cada tipo, nunca remitentes ni asuntos.

Usa los secretos de los avisos de precio: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS (el mismo buzón); el servidor
IMAP es IMAP_HOST o el de SMTP con "imap" delante (DonDominio: imap.dondominio.com).
"""
import email
import email.header
import email.utils
import imaplib
import os
import re
import smtplib
import ssl
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage

OFICIAL = re.compile(r"(?i)@(?:[\w.-]+\.)?(?:oepm\.es|oepm\.gob\.es|euipo\.europa\.eu|wipo\.int)>?$")
OEPM = re.compile(r"(?i)@(?:[\w.-]+\.)?(?:oepm\.es|oepm\.gob\.es)>?$")
SOSPECHA = re.compile(r"(?i)registro (?:de|internacional de) marcas?|trademark (?:register|registration|publication)|"
                      r"publicaci[oó]n (?:de|en el registro)|register of (?:trade ?marks|brands)|marca .{0,30}(?:factura|pago|tasa)|"
                      r"(?:factura|invoice|pago|payment).{0,40}(?:marca|trademark|guitle)|wipo|ompi|world intellectual|"
                      r"european (?:trade ?mark|patent) (?:register|office)|\bguitle\b.{0,40}(?:registr|publica)")
DIAS = 2  # IMAP busca por días; de esos, solo cuentan los llegados en las últimas HORAS (sin avisos repetidos)
HORAS = 24


def _dec(v):
    return str(email.header.make_header(email.header.decode_header(v or "")))


def main():
    host = os.environ.get("IMAP_HOST") or re.sub(r"^smtp\.", "imap.", os.environ["SMTP_HOST"])
    user, pw = os.environ["SMTP_USER"], os.environ["SMTP_PASS"]
    m = imaplib.IMAP4_SSL(host, 993, ssl_context=ssl.create_default_context(), timeout=60)
    m.login(user, pw)
    m.select("INBOX", readonly=True)
    since = (date.today() - timedelta(days=DIAS)).strftime("%d-%b-%Y")
    _, data = m.search(None, "SINCE", since)
    oepm, falsos, otros_ofic = [], [], []
    for num in (data[0] or b"").split():
        _, msg = m.fetch(num, "(BODY.PEEK[HEADER] BODY.PEEK[TEXT]<0.4000>)")
        raw = b"".join(p[1] for p in msg if isinstance(p, tuple))
        e = email.message_from_bytes(raw)
        frm, subj = _dec(e.get("From")), _dec(e.get("Subject"))
        addr = email.utils.parseaddr(frm)[1]
        text = subj + " " + raw.decode("utf-8", "replace")[-4000:]
        if subj.startswith("guitle: aviso del buzón"):  # los avisos de esta misma tarea
            continue
        try:
            when = email.utils.parsedate_to_datetime(e.get("Date"))
            if (datetime.now(timezone.utc) - when).total_seconds() > HORAS * 3600:
                continue
        except (TypeError, ValueError):
            pass
        row = f"{e.get('Date', '')} · {frm} · {subj}"
        if OEPM.search(addr):
            oepm.append(row)
        elif OFICIAL.search(addr):
            otros_ofic.append(row)
        elif SOSPECHA.search(text):
            falsos.append(row)
    m.logout()
    print(f"[buzon] últimas {HORAS} h: OEPM {len(oepm)}, EUIPO/OMPI {len(otros_ofic)}, posibles cobros falsos {len(falsos)}")
    if not (oepm or otros_ofic or falsos):
        return
    body = ["Aviso automático de guitle (vigilancia de hola@guitle.com).", ""]
    if oepm:
        body += ["CORREOS DE LA OEPM (oficiales, léelos):"] + [f"  - {r}" for r in oepm] + [""]
    if otros_ofic:
        body += ["Correos de la EUIPO u OMPI (oficiales):"] + [f"  - {r}" for r in otros_ofic] + [""]
    if falsos:
        body += ["POSIBLES COBROS FALSOS (no vienen de la OEPM): NO PAGUES sin comprobarlo.",
                 "La OEPM solo cobra en su sede electrónica; las cartas de 'registros' privados no son obligatorias."] \
                + [f"  - {r}" for r in falsos] + [""]
    msg = EmailMessage()
    msg["From"] = msg["To"] = user
    msg["Subject"] = "guitle: aviso del buzón (marca)"
    msg.set_content("\n".join(body))
    port = int(os.environ.get("SMTP_PORT") or 465)
    ctx = ssl.create_default_context()
    s = (smtplib.SMTP_SSL(os.environ["SMTP_HOST"], port, context=ctx, timeout=30) if port == 465
         else smtplib.SMTP(os.environ["SMTP_HOST"], port, timeout=30))
    if port != 465:
        s.starttls(context=ctx)
    s.login(user, pw)
    s.send_message(msg)
    s.quit()
    print("[buzon] aviso enviado a hola@guitle.com")


if __name__ == "__main__":
    main()
