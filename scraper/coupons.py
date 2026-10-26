"""Detector diario de cupones: busca códigos promocionales en la portada de cada tienda accesible.

No aplica nada por su cuenta: guarda los candidatos en data/coupon_candidates.json y, si hay alguno
nuevo, escribe un resumen en el fichero indicado con --new-out (el workflow lo publica como aviso).
Los cupones confirmados se añaden a mano en data/coupons.json.

Uso:
    python -m scraper.coupons [--new-out FICHERO]
    python -m scraper.coupons --records-out F / --merge F --new-out MD   # en CI
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from .fetch import Fetcher, is_challenge

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "data" / "coupon_candidates.json"
KEEP_DAYS = 30

# "código OTONO10", "cupón: GUITAR15", "code SUMMER", "Gutschein XMAS24"…
CODE_RE = re.compile(
    r"\b(?:c[oó]digo|cup[oó]n|coupon|code|gutschein(?:code)?|codice)\b(?:\s+(?:promocional|de descuento|promo))?"
    r"(?:\s*[:\-–]\s*|\s+)[\"'“”«»]?([A-Za-z0-9][A-Za-z0-9_-]{3,19})\b", re.IGNORECASE)
# Palabras que el regex podría tomar por código y no lo son.
NOT_CODES = {"POSTAL", "DESCUENTO", "PROMOCIONAL", "PROMO", "HERE", "AQUI", "AQUÍ", "CODE", "CODIGO", "CUPON", "GRATIS",
             "ENVIO", "CLIENTE", "PRODUCTO", "ARTICULO", "SECRETO", "QR", "EAN", "SKU", "PEDIDO", "REGALO"}
DISCOUNT_RE = re.compile(r"(-?\d{1,2}\s?%|\d{1,3}\s?€|€\s?\d{1,3})")


def stores_to_check():
    """Tiendas con web accesible (las de guitarras y las de Jordan), sin repetir dominio."""
    seen, out = set(), []
    for s in json.loads((ROOT / "stores.json").read_text(encoding="utf-8")):
        if s.get("method") == "ebay" or not s.get("domain") or not any(i.get("url") for i in s.get("items", [])):
            continue
        if s["domain"] not in seen:
            seen.add(s["domain"])
            out.append({"id": s["id"], "name": s["name"], "url": f"https://{s['domain']}/"})
    for s in json.loads((ROOT / "sneakers_stores.json").read_text(encoding="utf-8")):
        domain = re.sub(r"^https?://", "", s["base"]).rstrip("/")
        if domain not in seen:
            seen.add(domain)
            out.append({"id": s["id"], "name": s["name"], "url": s["base"] + "/"})
    return out


def find_codes(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" "))
    found = {}
    for m in CODE_RE.finditer(text):
        raw = m.group(1)
        code = raw.upper()
        # Un código real va en mayúsculas en el texto, tiene letras y no es una palabra genérica.
        if raw != code or code in NOT_CODES or code.isdigit() or not re.search(r"[A-Z]", code):
            continue
        context = text[max(0, m.start() - 90): m.end() + 90].strip()
        discount = DISCOUNT_RE.search(context)
        found.setdefault(code, {"code": code, "context": context, "discount": discount.group(0) if discount else None})
    return list(found.values())


def scan():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    fetcher = Fetcher()
    current = []
    for store in stores_to_check():
        try:
            allowed, _ = fetcher.allowed(store["url"])
            if not allowed:
                continue
            resp = fetcher.get(store["url"])
            if resp.status_code != 200 or is_challenge(resp):
                continue
            found = find_codes(resp.text)
            for c in found:
                current.append({"store": store["id"], "store_name": store["name"], "url": store["url"],
                                "first_seen": now, "last_seen": now, **c})
            print(f"[ok] {store['id']}: {len(found)} candidatos", flush=True)
        except Exception as exc:  # noqa: BLE001 - una tienda no rompe el resto
            print(f"[error] {store['id']}: {type(exc).__name__}", flush=True)
    return current


def merge(current, new_out=None):
    """Fusiona con data/coupon_candidates.json (conserva first_seen, olvida lo no visto en 30 días)."""
    previous = json.loads(CANDIDATES.read_text(encoding="utf-8")) if CANDIDATES.exists() else []
    by_key = {(c["store"], c["code"]): c for c in previous}
    new = []
    for c in current:
        key = (c["store"], c["code"])
        if key in by_key:
            by_key[key].update(last_seen=c["last_seen"], context=c["context"], discount=c["discount"])
        else:
            by_key[key] = c
            new.append(c)
    cutoff = datetime.now(timezone.utc).timestamp() - KEEP_DAYS * 86400
    merged = [c for c in by_key.values() if datetime.fromisoformat(c["last_seen"]).timestamp() >= cutoff]
    CANDIDATES.parent.mkdir(exist_ok=True)
    CANDIDATES.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if new_out:
        out = Path(new_out)
        if new:
            lines = ["Se han detectado posibles cupones nuevos en la portada de estas tiendas:", ""]
            for c in new:
                lines.append(f"- **{c['store_name']}**: código `{c['code']}`" + (f" ({c['discount']})" if c["discount"] else "")
                             + f" — [{c['url']}]({c['url']})")
                lines.append(f"  > {c['context']}")
            lines += ["", "Revisa las condiciones y, si vale, añádelo a `data/coupons.json` para que se aplique en los precios."]
            out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif out.exists():
            out.unlink()
    print(f"{len(current)} candidatos hoy, {len(new)} nuevos", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--records-out", help="guarda los candidatos de hoy en este fichero (CI)")
    parser.add_argument("--merge", help="fusiona en data/ los candidatos de un --records-out previo")
    parser.add_argument("--new-out", help="fichero Markdown con los cupones nuevos (si los hay)")
    args = parser.parse_args(argv)
    if args.merge:
        merge(json.loads(Path(args.merge).read_text(encoding="utf-8")), args.new_out)
        return 0
    current = scan()
    if args.records_out:
        Path(args.records_out).write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
        return 0
    merge(current, args.new_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
