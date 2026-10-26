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
import re
import unicodedata

import requests

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
SCOPE = "https://api.ebay.com/oauth/api_scope"  # token de aplicación (client credentials)
TIMEOUT = 25  # segundos por petición a la API
NEW_CONDITION = "1000"

_token = None


def has_credentials():
    return bool(os.environ.get("EBAY_CLIENT_ID") and os.environ.get("EBAY_CLIENT_SECRET"))


class TokenError(requests.RequestException):
    pass


_token_error = None


def _get_token():
    global _token, _token_error
    if _token_error:  # no repetir la misma petición fallida para cada producto
        raise TokenError(_token_error)
    if _token is None:
        # strip(): al pegar las claves en GitHub es fácil que se cuele un espacio o salto de línea.
        client_id = os.environ["EBAY_CLIENT_ID"].strip()
        secret = os.environ["EBAY_CLIENT_SECRET"].strip()
        auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
        resp = requests.post(TOKEN_URL, timeout=TIMEOUT,
                             headers={"Authorization": f"Basic {auth}",
                                      "Content-Type": "application/x-www-form-urlencoded"},
                             data={"grant_type": "client_credentials", "scope": SCOPE})
        if resp.status_code != 200:
            # El cuerpo de error de eBay (p. ej. invalid_client) no contiene las claves.
            _token_error = f"token HTTP {resp.status_code}: {resp.text[:200]}"
            print(f"ebay: {_token_error} (client_id termina en ...{client_id[-4:]}, "
                  f"lleva PRD: {'-PRD-' in client_id}, secret empieza por PRD-: {secret.startswith('PRD-')})")
            raise TokenError(_token_error)
        _token = resp.json()["access_token"]
    return _token


# Abreviaturas que las tiendas omiten o escriben distinto en los títulos de eBay.
OPTIONAL_TOKENS = {"mn", "rw", "lrl", "bpg", "wpg", "sss", "hh", "inspired", "by", "gibson", "artcore", "genesis",
                   "estuche", "case"}
SYNONYMS = {"tele": "telecaster", "strat": "stratocaster", "blk": "black", "bk": "black", "pwt": "polar",
            "aqb": "aquatone"}


def _tokens(text):
    text = unicodedata.normalize("NFKD", (text or "").lower()).encode("ascii", "ignore").decode()
    words = re.sub(r"[^0-9a-z]+", " ", text).split()
    return {SYNONYMS.get(w, w) for w in words}


# Variantes que no son el mismo producto (zurdas, B-stock, packs, usadas…) salvo que el nombre las incluya.
EXCLUDED_TOKENS = {"lefthand", "lh", "left", "linkshander", "linkshaender", "zurdo", "zurda", "bstock", "b", "stock",
                   "gebraucht", "used", "set", "bundle", "pack", "versandrucklaufer", "versandruecklaeufer"}


def title_matches(product_name, title):
    """Todas las palabras importantes del producto (modelo y color) deben estar en el título del anuncio,
    y el título no puede ser de otra variante (zurda, B-stock, pack…)."""
    name, found = _tokens(product_name), _tokens(title)
    return (name - OPTIONAL_TOKENS) <= found and not ((found & EXCLUDED_TOKENS) - name)


def search(store, product):
    """Devuelve (status, datos). status: ok | not_found | no_credentials. Lanza RequestException en errores HTTP.

    Busca por EAN si lo hay y, si no, por nombre. Solo acepta anuncios nuevos, a precio fijo, del vendedor
    configurado y, en búsquedas por nombre, cuyo título contenga el modelo y el color.
    """
    if not has_credentials():
        return "no_credentials", None
    cfg = store["ebay"]
    seller = cfg["seller"].lower()
    headers = {"Authorization": f"Bearer {_get_token()}",
               "X-EBAY-C-MARKETPLACE-ID": cfg.get("marketplace", "EBAY_DE")}
    base = {"filter": f"sellers:{{{cfg['seller']}}},conditionIds:{{{NEW_CONDITION}}},buyingOptions:{{FIXED_PRICE}}",
            "limit": "50"}
    attempts = ([("gtin", {"gtin": product["ean"]})] if product.get("ean") else []) + [("q", {"q": product["name"]})]
    for kind, extra in attempts:
        resp = requests.get(SEARCH_URL, params={**base, **extra}, timeout=TIMEOUT, headers=headers)
        resp.raise_for_status()
        items = [i for i in resp.json().get("itemSummaries", [])
                 if i.get("price", {}).get("value")
                 and (i.get("seller", {}).get("username") or "").lower() == seller
                 and (kind == "gtin" or title_matches(product["name"], i.get("title")))]
        if items:
            best = min(items, key=lambda i: float(i["price"]["value"]))
            return "ok", {
                "price": float(best["price"]["value"]),
                "currency": best["price"].get("currency"),
                "url": best.get("itemWebUrl"),
                "image": (best.get("image") or {}).get("imageUrl"),
                "title": best.get("title"),
            }
    return "not_found", None


def discover(queries=("Fender Player II Telecaster", "Fender Player II Stratocaster", "Epiphone ES-335")):
    """Diagnóstico (temporal): lista los vendedores de eBay.de que venden estos productos nuevos (para encontrar el usuario
    exacto de cada tienda). Se ejecuta con: python -m scraper.ebay"""
    if not has_credentials():
        print("ebay: faltan EBAY_CLIENT_ID / EBAY_CLIENT_SECRET")
        return
    sellers = {}
    for q in queries:
        resp = requests.get(SEARCH_URL, timeout=TIMEOUT,
                            params={"q": q, "limit": "200",
                                    "filter": f"conditionIds:{{{NEW_CONDITION}}},buyingOptions:{{FIXED_PRICE}}"},
                            headers={"Authorization": f"Bearer {_get_token()}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE"})
        print(f"ebay: '{q}' -> HTTP {resp.status_code}")
        resp.raise_for_status()
        for item in resp.json().get("itemSummaries", []):
            s = item.get("seller", {})
            name = s.get("username")
            if name:
                sellers.setdefault(name, [s.get("feedbackScore"), 0])[1] += 1
    for name, (feedback, n) in sorted(sellers.items(), key=lambda x: -(x[1][0] or 0)):
        print(f"ebay vendedor: {name:<40} valoraciones={feedback} anuncios={n}")


if __name__ == "__main__":
    discover()
