"""Música para los Reels publicados por la API (que no permite usar la biblioteca de música de Instagram).

Temas de Kevin MacLeod (incompetech.com) con licencia Creative Commons BY 4.0: uso comercial permitido citando al
autor, por eso cada Reel lleva la línea de crédito en su texto. Se descargan una vez en social/musica/ (no se suben al
repo) y se mezclan en el vídeo con ffmpeg: entrada y salida con fundido, volumen moderado.
"""
import subprocess
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "social" / "musica"
BASE = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
# (título, segundo en que empieza el fragmento): temas con ritmo, sin voz
TEMAS = [("Funky Chunk", 6), ("Hep Cats", 4), ("Life of Riley", 2), ("Werq", 8), ("Pamgaea", 10),
         ("Movement Proposition", 4), ("Rollin at 5", 2), ("Hard Boiled", 6), ("Feelin Good", 12)]
TEMAS_BR = [("Bossa Antigua", 4), ("Samba Isobel", 6)] + TEMAS


def credito(titulo):
    return f"🎵 \"{titulo}\" Kevin MacLeod (incompetech.com) · CC BY 4.0"


def archivo(titulo):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (titulo.replace(" ", "_") + ".mp3")
    if not f.exists():
        r = requests.get(BASE + urllib.parse.quote(titulo) + ".mp3", timeout=120)
        r.raise_for_status()
        f.write_bytes(r.content)
    return f


def duracion(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def poner(video, n, temas=TEMAS):
    """Mezcla el tema número n (rota por la lista) en el vídeo, en su sitio. Devuelve la línea de crédito."""
    titulo, inicio = temas[n % len(temas)]
    mp3 = archivo(titulo)
    dur = duracion(video)
    tmp = video.with_suffix(".musica.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ss", str(inicio), "-i", str(mp3),
                    "-filter_complex", f"[1:a]atrim=0:{dur:.2f},afade=t=in:d=0.4,afade=t=out:st={max(0, dur - 1.5):.2f}:d=1.5,volume=0.85[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(video)
    return credito(titulo)
