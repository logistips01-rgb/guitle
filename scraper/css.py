"""Extracción vía selector CSS declarado en stores.json."""
from .common import normalize_currency, parse_availability, parse_price


def extract(soup, product_ids, store):
    selector = store.get("selector")
    if not selector:
        return None
    tag = soup.select_one(selector)
    if not tag:
        return None
    text = tag.get("content") or tag.get_text(" ", strip=True)
    price = parse_price(text)
    if price is None:
        return None
    currency = "EUR" if "€" in text else None
    in_stock = None
    if store.get("stock_selector"):
        stock = soup.select_one(store["stock_selector"])
        in_stock = parse_availability(stock.get_text(" ", strip=True)) if stock else None
    return {"price": price, "currency": normalize_currency(currency), "in_stock": in_stock,
            "identifiers": [], "note": None}
