"""Enlaces de afiliado: convierte la URL de una ficha en el enlace de afiliado de su tienda (data/affiliates.json).

Se aplica al construir la web (catálogo, páginas de guitarra y seguimiento); los datos guardan siempre la URL
original de la tienda.
"""
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

CONFIG = Path(__file__).resolve().parent.parent / "data" / "affiliates.json"


@lru_cache(maxsize=1)
def _config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def wrap(store, url):
    """URL de afiliado de la tienda o, si no tiene programa configurado, la URL tal cual."""
    if not url:
        return url
    cfg = _config()
    template = (cfg.get("stores", {}).get(store) or {}).get("template")
    awin = cfg.get("awin_publisher_id")
    if not template or ("{awin}" in template and not awin):
        return url
    return template.replace("{awin}", str(awin or "")).replace("{url}", quote(url, safe=""))
