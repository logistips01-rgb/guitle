"""Extracción vía JSON-LD (schema.org Product / Offer / AggregateOffer)."""
import json

from .common import matches_sku, normalize_currency, parse_availability, parse_price


def _iter_nodes(data):
    if isinstance(data, list):
        for item in data:
            yield from _iter_nodes(item)
    elif isinstance(data, dict):
        yield data
        for key in ("@graph", "hasVariant", "mainEntity", "itemListElement", "item"):
            if key in data:
                yield from _iter_nodes(data[key])


def _types(node):
    t = node.get("@type", [])
    return {x.lower() for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)}


def _ids(node):
    return [node.get(k) for k in ("sku", "mpn", "gtin", "gtin12", "gtin13", "gtin14", "productID")]


def _offers(product):
    offers = product.get("offers")
    if offers is None:
        return []
    offers = offers if isinstance(offers, list) else [offers]
    out = []
    for offer in offers:
        if not isinstance(offer, dict):
            continue
        if "aggregateoffer" in _types(offer) and "offers" in offer:
            out.extend(_offers(offer))
            if offer.get("lowPrice") and not out:
                out.append({**offer, "price": offer["lowPrice"]})
            continue
        if offer.get("price") is None and offer.get("lowPrice") is not None:
            offer = {**offer, "price": offer["lowPrice"]}
        spec = offer.get("priceSpecification")
        if offer.get("price") is None and spec:
            spec = spec[0] if isinstance(spec, list) else spec
            offer = {**offer, "price": spec.get("price"),
                     "priceCurrency": offer.get("priceCurrency") or spec.get("priceCurrency")}
        out.append(offer)
    return out


def _image(value):
    """schema.org image puede ser URL, lista de URLs u ImageObject."""
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        value = value.get("url") or value.get("contentUrl")
    return value if isinstance(value, str) and value.startswith("http") else None


def load_blocks(soup):
    blocks = []
    for tag in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
        raw = (tag.string or tag.get_text() or "").strip()
        if not raw:
            continue
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            try:  # Algunos sitios meten saltos de línea/controles dentro de strings.
                blocks.append(json.loads(raw, strict=False))
            except json.JSONDecodeError:
                continue
    return blocks


def extract(soup, product_ids, store):
    """Devuelve dict con price/currency/in_stock/identifiers/note, o None si no hay Product con precio."""
    candidates = []  # (product_node, offer)
    for block in load_blocks(soup):
        for node in _iter_nodes(block):
            types = _types(node)
            if "product" in types or "productgroup" in types:
                for offer in _offers(node):
                    candidates.append((node, offer))
            elif "offer" in types and node.get("price") is not None:
                candidates.append(({}, node))
    candidates = [(p, o) for p, o in candidates if parse_price(o.get("price")) is not None]
    if not candidates:
        return None

    note = None
    matched = [(p, o) for p, o in candidates if matches_sku(_ids(o) + _ids(p), product_ids)]
    if matched:
        product, offer = matched[0]
        note = "variant_matched"
    else:
        product, offer = candidates[0]
        prices = {parse_price(o.get("price")) for _, o in candidates}
        if len(prices) > 1:
            note = f"ambiguous: {len(candidates)} offers, prices {sorted(prices)}"

    return {
        "price": parse_price(offer.get("price")),
        "currency": normalize_currency(offer.get("priceCurrency")),
        "in_stock": parse_availability(offer.get("availability")),
        "identifiers": sorted({str(i) for i in _ids(offer) + _ids(product) if i}),
        "image": _image(product.get("image") or offer.get("image")),
        "note": note,
    }
