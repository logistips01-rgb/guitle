"""Correo comercial desde hola@guitle.com (DonDominio), lanzado por .github/workflows/correo.yml.

- _interno/comercial/correo/borradores/*.md → se guardan como BORRADOR en el buzón (IMAP APPEND en Borradores), para
  que Manuel los lea en el webmail o en su programa de correo. No se envía nada.
- _interno/comercial/correo/enviar/*.md → se ENVÍAN por SMTP y se guarda copia en Enviados. Un fichero solo pasa a
  enviar/ cuando Manuel dice «envía» para ese correo.

Formato de cada fichero (texto plano, sin Markdown):
    Para: tienda@ejemplo.com
    Cc: (opcional)
    Asunto: ...
    <línea en blanco>
    Cuerpo del correo…

Cada fichero lleva un Message-ID fijo (sale de su nombre): si ya está en Borradores o en Enviados, no se repite. Así
la tarea se puede lanzar las veces que haga falta sin duplicar ni reenviar.

En los registros solo sale el nombre del fichero y el resultado: ni direcciones, ni textos, ni claves.

Secretos (los mismos que ya usan los avisos y el resumen de afiliados): SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.
Opcional: IMAP_HOST si el servidor IMAP no es el mismo que el SMTP.
"""
import hashlib
import imaplib
import os
import re
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "_interno" / "comercial" / "correo"
NAME = "Manuel Lorente · guitle"


def parse(path):
    head, _, body = path.read_text(encoding="utf-8").partition("\n\n")
    h = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        h[k.strip().lower()] = v.strip()
    if not h.get("para") or not h.get("asunto") or not body.strip():
        raise ValueError("faltan Para, Asunto o cuerpo")
    user = os.environ["SMTP_USER"]
    msg = EmailMessage()
    msg["From"] = formataddr((NAME, user))
    msg["To"] = h["para"]
    if h.get("cc"):
        msg["Cc"] = h["cc"]
    msg["Subject"] = h["asunto"]
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = f"<comercial-{hashlib.sha1(path.stem.encode()).hexdigest()[:16]}@guitle.com>"
    msg.set_content(body.strip() + "\n")
    return msg


def imap():
    host = os.environ.get("IMAP_HOST") or os.environ["SMTP_HOST"]
    hosts = [host] + ([re.sub(r"^smtp\.", "imap.", host)] if host.startswith("smtp.") else [])
    last = None
    for h in hosts:
        try:
            m = imaplib.IMAP4_SSL(h, 993, ssl_context=ssl.create_default_context(), timeout=30)
            m.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            return m
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"no se pudo entrar por IMAP: {type(last).__name__}")


def folder(m, flag, names):
    """Carpeta de Borradores/Enviados: la marcada como \\Drafts o \\Sent, o la primera que exista con su nombre."""
    _, rows = m.list()
    found, delim = [], "/"
    for r in rows or []:
        s = r.decode(errors="replace")
        mm = re.match(r'\((?P<f>[^)]*)\) "(?P<d>[^"]*)" (?P<n>.+)$', s)
        if not mm:
            continue
        n, delim = mm["n"].strip().strip('"'), mm["d"] or delim
        if flag.lower() in mm["f"].lower():
            return n
        found.append(n)
    for want in names:
        for n in found:
            if n.split(delim)[-1].lower() == want.lower():
                return n
    return names[0]


def present(m, box, msgid):
    typ, _ = m.select(f'"{box}"', readonly=True)
    if typ != "OK":
        return False
    typ, data = m.search(None, "HEADER", "Message-ID", msgid)
    return typ == "OK" and bool(data and data[0].split())


def append(m, box, msg, flags):
    typ, _ = m.append(f'"{box}"', flags, imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    if typ != "OK":
        raise RuntimeError(f"APPEND en {box} falló")


def send(msg):
    host, port = os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT") or 465)
    ctx = ssl.create_default_context()
    if port == 465:
        s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
    else:
        s = smtplib.SMTP(host, port, timeout=30)
        s.starttls(context=ctx)
    s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
    s.send_message(msg)
    s.quit()


def main():
    drafts = sorted((ROOT / "borradores").glob("*.md"))
    outbox = sorted((ROOT / "enviar").glob("*.md"))
    if not drafts and not outbox:
        print("[correo] nada que hacer", flush=True)
        return 0
    m = imap()
    box_d = folder(m, "\\Drafts", ["Drafts", "Borradores", "INBOX.Drafts", "INBOX.Borradores"])
    box_s = folder(m, "\\Sent", ["Sent", "Enviados", "INBOX.Sent", "INBOX.Enviados", "Sent Items"])
    print(f"[correo] carpetas: borradores={box_d!r}, enviados={box_s!r}", flush=True)
    errors = 0
    for p in drafts:
        try:
            msg = parse(p)
            if present(m, box_d, msg["Message-ID"]) or present(m, box_s, msg["Message-ID"]):
                print(f"[correo] {p.name}: ya estaba", flush=True)
                continue
            append(m, box_d, msg, "(\\Draft \\Seen)")
            print(f"[correo] {p.name}: borrador guardado", flush=True)
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"[correo] {p.name}: ERROR {type(e).__name__}", flush=True)
    for p in outbox:
        try:
            msg = parse(p)
            if present(m, box_s, msg["Message-ID"]):
                print(f"[correo] {p.name}: ya enviado, no se repite", flush=True)
                continue
            send(msg)
            append(m, box_s, msg, "(\\Seen)")
            print(f"[correo] {p.name}: ENVIADO y copiado en enviados", flush=True)
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"[correo] {p.name}: ERROR {type(e).__name__}", flush=True)
    m.logout()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
