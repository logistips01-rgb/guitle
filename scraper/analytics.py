"""Extracción vía el bloque de analítica de comercio electrónico de la ficha (Egitana).

Egitana no publica JSON-LD ni meta de precio; su ficha envía a la analítica nombre, id, precio, marca y
categoría:  EventSender.send('detail', {products: [{'name': …, 'id': …, 'price': '791', 'brand': …,
'category': 'guitarras formato ST'}]}).  Si el producto no está disponible, la ficha no trae el bloque.
"""
import re

from .common import parse_price

DETAIL = re.compile(
    r"EventSender\.send\('detail'.*?'name':\s*'(?P<name>(?:\\'|[^'])*)'.*?'price':\s*'(?P<price>[\d.,]+)'"
    r".*?'brand':\s*'(?P<brand>(?:\\'|[^'])*)'.*?'category':\s*'(?P<cat>(?:\\'|[^'])*)'", re.S)
# Breadcrumb de las fichas: <li><a title="Guitarras Eléctricas" href="/guitarras-electricas/c/187">
CRUMB = re.compile(r'<li>\s*<a title="([^"]+)" href="/[^"]+/c/\d+"')


def detail(text):
    """{name, price, brand, category} del bloque de analítica, o None."""
    m = DETAIL.search(text)
    if not m:
        return None
    unq = lambda v: v.replace("\\'", "'")
    return {"name": unq(m["name"]), "price": parse_price(m["price"]), "brand": unq(m["brand"]), "category": unq(m["cat"])}


def crumbs(text):
    return CRUMB.findall(text)


def extract(soup, product_ids, store):
    d = detail(str(soup))
    if not d or d["price"] is None:
        return None
    return {"price": d["price"], "currency": "EUR", "in_stock": None, "identifiers": [], "note": None}
