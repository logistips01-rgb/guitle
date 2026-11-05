"""Fotos de guitarras de espaldas: un modelo de visión libre (CLIP, en la máquina de GitHub, sin coste) mira cada
miniatura de guitarra y la apunta en data/fotos-revisadas.json ({miniatura: 0 buena, 1 de espaldas o sin la guitarra
(funda, estuche…), 2 cortada}). El catálogo no las usa para la ficha si hay otra tienda con una buena, y la portada
no las saca nunca.

Uso: python -m scraper.espaldas --minutes 300   (lo lanza .github/workflows/espaldas.yml; necesita torch y open_clip)
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "fotos-revisadas.json"
GUITARS = {"electrica", "acustica", "clasica", "portuguesa"}
UMBRAL = 0.9  # probabilidad de "de espaldas" a partir de la cual no se usa (probado: las de espaldas dan 0,98-0,99)
TEXTS = ["a photo of the front of a guitar, showing the strings and the soundhole or pickups",
         "a photo of the back of a guitar, showing the wooden back of the body and the back of the neck"]
_cache = None


def _load():
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    return _cache


def espaldas():
    """Miniaturas malas: guitarra de espaldas, sin guitarra o cortada."""
    return {k for k, v in _load().items() if v}


def _save(d):
    FILE.write_text("{\n" + ",\n".join(f'"{k}":{v}' for k, v in sorted(d.items())) + "\n}\n", encoding="utf-8")


def candidates():
    """Miniaturas de guitarra por mirar: primero las que hoy salen en las fichas, luego las de las demás tiendas."""
    from . import thumbs
    shown, others = [], []
    for f in sorted((ROOT / "data" / "catalog").rglob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        if d.get("kind") in GUITARS and "products" in d:
            shown += [p["th"] for p in sorted(d["products"], key=lambda p: -len(p["items"])) if p.get("th")]
        elif f.name == "offers.json":
            others += [n for n in (thumbs.existing(o.get("image")) for o in d.values()
                                   if isinstance(o, dict) and o.get("kind") in GUITARS and o.get("status") == "ok") if n]
    return list(dict.fromkeys(shown + others))


def main(minutes):
    import requests
    import torch
    import open_clip
    from PIL import Image
    from .thumbs import cortada
    t0 = time.time()
    done = _load()
    todo = [n for n in candidates() if n not in done]
    print(f"[espaldas] {len(done)} ya miradas, {len(todo)} por mirar", flush=True)
    model, _, pre = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
    model.eval()
    tok = open_clip.get_tokenizer("ViT-B-32")
    with torch.no_grad():
        txt = model.encode_text(tok(TEXTS))
        txt /= txt.norm(dim=-1, keepdim=True)
    http = requests.Session()

    def fetch(name):
        local = ROOT / "img" / "p" / name
        try:
            data = local.read_bytes() if local.exists() else http.get(f"https://guitle.com/img/p/{name}", timeout=20).content
            if cortada(data):
                return name, 2
            im = Image.open(BytesIO(data)).convert("RGB")
        except Exception:  # noqa: BLE001
            return name, None
        side = max(im.size)
        bg = Image.new("RGB", (side, side), "white")
        bg.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        return name, pre(bg)

    n_back = 0
    with ThreadPoolExecutor(16) as ex:
        for i in range(0, len(todo), 64):
            if time.time() - t0 > minutes * 60:
                break
            got = list(ex.map(fetch, todo[i:i + 64]))
            for n, x in got:
                if isinstance(x, int) and x == 2:
                    done[n] = 2
            batch = [(n, x) for n, x in got if x is not None and not isinstance(x, int)]
            if not batch:
                continue
            with torch.no_grad():
                img = model.encode_image(torch.stack([x for _, x in batch]))
                img /= img.norm(dim=-1, keepdim=True)
                prob = (100 * img @ txt.T).softmax(-1)[:, 1].tolist()
            for (n, _), p in zip(batch, prob):
                done[n] = int(p >= UMBRAL)
                n_back += done[n]
            if i % 6400 == 0:
                _save(done)
                print(f"[espaldas] {i + len(batch)}/{len(todo)} · de espaldas: {n_back}", flush=True)
    _save(done)
    print(f"[espaldas] fin: {len(done)} miradas, {sum(v == 1 for v in done.values())} de espaldas, "
          f"{sum(v == 2 for v in done.values())} cortadas", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=300)
    main(ap.parse_args().minutes)
