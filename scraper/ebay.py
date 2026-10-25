"""Precios vía la Browse API oficial de eBay (tiendas que bloquean su web pero venden en eBay).

Necesita las claves de Production en las variables EBAY_CLIENT_ID y EBAY_CLIENT_SECRET
(secrets del repositorio en GitHub Actions). Sin ellas, cada producto queda como "no_credentials".

stores.json:
    {"id": "musicstore_ebay", "method": "ebay",
     "ebay": {"marketplace": "EBAY_DE", "seller": "<usuario eBay de la tienda>"},
     "items": [{"sku": "0140552506", "url": null}]}

Busca por EAN (gtin) si el producto lo tiene; si no, por nombre. Solo anuncios nuevos a precio fijo del vendedor.
"""
import base64
import os

import requests

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
SCOPE = "https://api.ebay.com/oauth/api_scope"
TIMEOUT = 25
NEW_CONDITION = "1000"

_token = None


def has_credentials():
    return bool(os.environ.get("EBAY_CLIENT_ID") and os.environ.get("EBAY_CLIENT_SECRET"))


def _get_token():
    global _token
    if _token is None:
        auth = base64.b64encode(
            f"{os.environ['EBAY_CLIENT_ID']}:{os.environ['EBAY_CLIENT_SECRET']}".encode()).decode()
        resp = requests.post(TOKEN_URL, timeout=TIMEOUT,
                             headers={"Authorization": f"Basic {auth}",
                                      "Content-Type": "application/x-www-form-urlencoded"},
                             data={"grant_type": "client_credentials", "scope": SCOPE})
        resp.raise_for_status()
        _token = resp.json()["access_token"]
    return _token


def search(store, product):
    """Devuelve (status, datos). status: ok | not_found | no_credentials. Lanza RequestException en errores HTTP."""
    if not has_credentials():
        return "no_credentials", None
    cfg = store["ebay"]
    params = {
        "filter": f"sellers:{{{cfg['seller']}}},conditionIds:{{{NEW_CONDITION}}},buyingOptions:{{FIXED_PRICE}}",
        "limit": "20",
    }
    if product.get("ean"):
        params["gtin"] = product["ean"]
    else:
        params["q"] = product["name"]
    resp = requests.get(SEARCH_URL, params=params, timeout=TIMEOUT,
                        headers={"Authorization": f"Bearer {_get_token()}",
                                 "X-EBAY-C-MARKETPLACE-ID": cfg.get("marketplace", "EBAY_DE")})
    resp.raise_for_status()
    items = [i for i in resp.json().get("itemSummaries", []) if i.get("price", {}).get("value")]
    if not items:
        return "not_found", None
    best = min(items, key=lambda i: float(i["price"]["value"]))
    return "ok", {
        "price": float(best["price"]["value"]),
        "currency": best["price"].get("currency"),
        "url": best.get("itemWebUrl"),
        "image": (best.get("image") or {}).get("imageUrl"),
        "title": best.get("title"),
    }
