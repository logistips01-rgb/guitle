"""Helpers compartidos: parseo de precios, disponibilidad e identificadores."""
import re

AVAILABILITY_IN = ("instock", "limitedavailability", "onlineonly", "presale", "preorder", "backorder")
AVAILABILITY_OUT = ("outofstock", "soldout", "discontinued", "instoreonly")


def parse_price(value):
    """Convierte '1.234,56 €', '1234.56', 929 ... en float. None si no se puede."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else None
    text = str(value).strip().replace("\xa0", " ")
    match = re.search(r"\d[\d.,\s]*", text)
    if not match:
        return None
    num = match.group(0).strip().replace(" ", "")
    if "," in num and "." in num:
        # El último separador es el decimal.
        if num.rfind(",") > num.rfind("."):
            num = num.replace(".", "").replace(",", ".")
        else:
            num = num.replace(",", "")
    elif "," in num:
        head, _, tail = num.rpartition(",")
        num = num.replace(",", ".") if len(tail) != 3 else num.replace(",", "")
    elif num.count(".") > 1 or (num.count(".") == 1 and len(num.rpartition(".")[2]) == 3):
        num = num.replace(".", "")
    num = num.rstrip(".,")
    try:
        price = float(num)
    except ValueError:
        return None
    return price if price > 0 else None


def parse_availability(value):
    """True / False / None (desconocido) a partir de schema.org o texto libre."""
    if not value:
        return None
    key = re.sub(r"[^a-z]", "", str(value).lower().rsplit("/", 1)[-1])
    if any(k in key for k in AVAILABILITY_OUT):
        return False
    if any(k in key for k in AVAILABILITY_IN):
        return True
    return None


def normalize_currency(value):
    if not value:
        return None
    value = str(value).strip().upper()
    return "EUR" if value in ("€", "EURO", "EUROS") else value


def digits(value):
    return re.sub(r"\D", "", str(value or ""))


def normalize_id(value):
    return re.sub(r"[^0-9A-Z]", "", str(value or "").upper())


def matches_sku(identifiers, product_ids):
    """¿Algún identificador de la página (sku/mpn/gtin) contiene el SKU del fabricante o el EAN?

    Vale para SKUs numéricos (Fender 0140552506) y alfanuméricos (Gibson LPS5P00EBNH1).
    """
    targets = [normalize_id(t) for t in product_ids if len(normalize_id(t)) >= 6]
    page = [normalize_id(i) for i in identifiers if i]
    return any(t in p for t in targets for p in page)
