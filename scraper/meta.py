"""Extracción vía meta tags (og:/product:price:amount) y microdatos itemprop."""
from .common import normalize_currency, parse_availability, parse_price


def _meta(soup, *names):
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"]
    return None


def _itemprop(soup, prop):
    tag = soup.find(attrs={"itemprop": prop})
    if not tag:
        return None
    return tag.get("content") or tag.get("href") or tag.get_text(strip=True)


def extract(soup, product_ids, store):
    price = parse_price(_meta(soup, "og:price:amount", "product:price:amount"))
    currency = _meta(soup, "og:price:currency", "product:price:currency")
    availability = _meta(soup, "og:availability", "product:availability")
    if price is None:
        price = parse_price(_itemprop(soup, "price"))
        currency = currency or _itemprop(soup, "priceCurrency")
        availability = availability or _itemprop(soup, "availability")
    if price is None:
        return None
    return {
        "price": price,
        "currency": normalize_currency(currency),
        "in_stock": parse_availability(availability),
        "identifiers": [i for i in (_itemprop(soup, k) for k in ("sku", "mpn", "gtin13", "gtin")) if i],
        "note": None,
    }
