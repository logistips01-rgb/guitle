"""Idiomas de las webs de los países nuevos, uno por fichero (pl.py, cs.py…): T_LANG (textos, como intl.T["de"]),
LEGAL_LANG (aviso legal), PACK_LANG (sección de packs), KINDS_LANG (nombre de cada página) y MONEY_NOTE (cómo se
escribe un precio). scraper.intl y scraper.intl_legal los cargan todos."""
import importlib
import pkgutil

LANGS = {m.name: importlib.import_module(f"{__name__}.{m.name}") for m in pkgutil.iter_modules(__path__)}
