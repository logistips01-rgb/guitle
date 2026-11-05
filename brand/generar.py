"""Kit de marca de guitle: genera los SVG del logo (letras convertidas a trazos, tipografía Inter Display
ExtraBold) y, con Playwright, los PNG para redes.

Uso (necesita fonttools, Playwright y la fuente Inter, https://rsms.me/inter/):
    python brand/generar.py --font ruta/InterDisplay-ExtraBold.ttf --font-text ruta/Inter-SemiBold.ttf
"""
import argparse
import os
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
BLUE = "#2a78d6"
INK = "#0b0b0b"
# Púa de guitarra (punta abajo), unidades propias: ancho 76, alto 78, origen en la punta.
PICK = "M0 0C-12-10-38-30-38-52C-38-70-20-78 0-78C20-78 38-70 38-52C38-30 12-10 0 0Z"


class Font:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm

    def glyph(self, ch):
        return self.cmap[ord(ch)]

    def path(self, text, x, y, size, tracking=0.0):
        """Trazo SVG del texto con la línea base en y. Devuelve (d, x_final, posiciones por letra)."""
        scale = size / self.upm
        pen = SVGPathPen(self.gs)
        pos = []
        for ch in text:
            name = self.glyph(ch)
            g = self.gs[name]
            g.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
            pos.append((ch, x, g.width * scale))
            x += g.width * scale + tracking * size
        return pen.getCommands(), x - tracking * size, pos

    def bounds(self, ch, x, y, size):
        scale = size / self.upm
        bp = BoundsPen(self.gs)
        self.gs[self.glyph(ch)].draw(bp)
        x0, y0, x1, y1 = bp.bounds
        return x + x0 * scale, y - y1 * scale, x + x1 * scale, y - y0 * scale


def icon_svg(font, bg=BLUE, fg="#fff", rounded=True, size=512):
    """Monograma: "g" con una púa como apóstrofo, centrado ópticamente en un cuadrado."""
    gsize = 380
    d, _, _ = font.path("g", 0, 0, gsize)
    x0, y0, x1, y1 = font.bounds("g", 0, 0, gsize)
    pick_w, pick_h = 76 * 0.95, 78 * 0.95
    gap = 14
    group_w = (x1 - x0) + gap + pick_w
    group_h = y1 - y0
    tx = (512 - group_w) / 2 - x0
    ty = (512 - group_h) / 2 - y0 + 6  # ligera bajada óptica
    px = tx + x1 + gap + pick_w / 2
    py = ty + y0 + pick_h + 4
    rx = 112 if rounded else 0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="{size}" height="{size}">'
            f'<rect width="512" height="512" rx="{rx}" fill="{bg}"/>'
            f'<path transform="translate({tx:.1f} {ty:.1f})" fill="{fg}" d="{d}"/>'
            f'<path transform="translate({px:.1f} {py:.1f}) scale(0.95)" fill="{fg}" d="{PICK}"/></svg>')


def wordmark(font, x, y, size, color, pick_color):
    """"guitle" con la i sin punto y una púa encima. Devuelve (svg, ancho)."""
    tracking = -0.035
    d, end, pos = font.path("guıtle", x, y, size, tracking)
    _, ix, iw = pos[2]
    bx0, by0, bx1, _ = font.bounds("ı", ix, y, size)
    s = size / 230 * 0.82
    cx = (bx0 + bx1) / 2
    top = by0 - size * 0.075
    svg = (f'<path fill="{color}" d="{d}"/>'
           f'<path transform="translate({cx:.1f} {top:.1f}) scale({s:.3f})" fill="{pick_color}" d="{PICK}"/>')
    return svg, end - x


def logo_svg(font, color=INK, accent=BLUE, icon=True, tagline=True, icon_bg=BLUE, icon_fg="#fff"):
    size = 230
    x = 20
    parts = []
    if icon:
        parts.append(f'<g transform="translate(20 {30 if tagline else 20}) scale(0.625)">'
                     f'{icon_svg(font, icon_bg, icon_fg).split(">", 1)[1].rsplit("</svg>", 1)[0]}</g>')
        x = 380
    base = 236
    wm, width = wordmark(font, x, base, size, color, accent)
    parts.append(wm)
    right = x + width
    if tagline:
        # Bajo la cola de la "g" (descendente de Inter ≈ 0,24 em)
        td, tend, _ = font.path("guitarras al mejor precio", x + 6, base + 104, 50, -0.01)
        parts.append(f'<path fill="{accent}" d="{td}"/>')
        right = max(right, tend)
    w = round(right + 24)
    h = 380 if tagline else 360 if icon else 290
    vb_y = 0 if (icon or tagline) else 40
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {vb_y} {w} {h - vb_y}" role="img" aria-label="guitle">'
            + "".join(parts) + "</svg>")


def hires(root):
    """Fotos de guitarra en alta resolución para las plantillas (brand/.cache/, no se sube al repo)."""
    import json
    import sys
    sys.path.insert(0, str(root))
    from scraper.fetch import Fetcher
    from scraper.thumbs import name_for, normalize
    cache = OUT / ".cache"
    cache.mkdir(exist_ok=True)
    latest = json.loads((root / "data" / "latest.json").read_text(encoding="utf-8"))
    fetcher = Fetcher(delay=(1.0, 2.0))
    for p in latest["products"]:
        target = cache / (p.get("thumb") or "")
        if p.get("category") != "guitarra" or not p.get("thumb") or target.exists():
            continue
        # Misma foto que la miniatura de la web, a 1400 px de alto
        src = next((i["image"] for i in latest["items"] if i["sku"] == p["sku"] and i.get("image")
                    and name_for(i["image"]) == p["thumb"]), None)
        if not src:
            continue
        url = src if fetcher.allowed(src)[0] else src.split("?")[0]
        resp = fetcher.get(url)
        if resp.status_code == 200:
            data = normalize(resp.content, True, 1400)
            if data:
                target.write_bytes(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True, help="InterDisplay-ExtraBold.ttf (logo y titulares)")
    ap.add_argument("--font-text", help="Inter-SemiBold.ttf (textos de las plantillas)")
    args = ap.parse_args()
    font = Font(args.font)
    files = {
        "logo.svg": logo_svg(font),
        "logo-sin-lema.svg": logo_svg(font, tagline=False),
        "logo-blanco.svg": logo_svg(font, color="#fff", accent="#fff", icon_bg="#fff", icon_fg=BLUE),
        "logo-negro.svg": logo_svg(font, color=INK, accent=INK, icon_bg=INK, icon_fg="#fff"),
        "nombre.svg": logo_svg(font, icon=False, tagline=False),
        "icono.svg": icon_svg(font),
        "icono-blanco.svg": icon_svg(font, bg="#fff", fg=BLUE),
        "icono-cuadrado.svg": icon_svg(font, rounded=False),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg + "\n", encoding="utf-8")
    # La web usa el mismo icono.
    (ROOT / "icons" / "icon.svg").write_text(files["icono.svg"] + "\n", encoding="utf-8")
    (ROOT / "icons" / "logo.svg").write_text(files["logo.svg"] + "\n", encoding="utf-8")
    hires(ROOT)
    env = {**os.environ, "FONT": args.font, "FONT_TEXT": args.font_text or args.font}
    subprocess.run(["node", str(OUT / "png.js")], check=True, cwd=ROOT, env=env)


if __name__ == "__main__":
    main()
