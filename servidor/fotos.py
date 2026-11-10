"""Baja al servidor las fotos (img/p/) que le faltan, desde https://prueba.guitle.com/img/p/ (el Worker de Cloudflare,
que las sirve de R2 con caché: rápido y casi sin operaciones de R2). Antes era guitle.com, pero desde el cambio de DNS
(10/11/2026) guitle.com es este mismo servidor: se pedía las fotos a sí mismo y la copia acababa con error. Con rclone, foto a foto desde R2, iban 13 por segundo: 676.000 fotos eran 14 horas.
Aquí, 48 a la vez con conexiones que se reutilizan.

    python3 fotos.py LISTA RAIZ        (LISTA: "img/p/<nombre>" por línea; RAIZ: /srv/guitle/r2)
"""
import http.client
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

lista, root = sys.argv[1], sys.argv[2]
names = [line.strip() for line in open(lista, encoding="utf-8") if line.strip()]
local = threading.local()
done = [0, 0]  # bajadas, fallos
lock = threading.Lock()


def conn():
    c = getattr(local, "c", None)
    if c is None:
        c = local.c = http.client.HTTPSConnection("prueba.guitle.com", timeout=30)
    return c


def one(rel):
    dst = os.path.join(root, rel)
    if os.path.exists(dst):
        return
    for attempt in range(3):
        try:
            c = conn()
            c.request("GET", "/" + rel, headers={"User-Agent": "guitle-servidor/1"})
            r = c.getresponse()
            body = r.read()
            if r.status == 200 and body:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                tmp = dst + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(body)
                os.replace(tmp, dst)
                with lock:
                    done[0] += 1
                return
            if r.status == 404:
                break
        except Exception:  # noqa: BLE001 - conexión cortada: otra nueva
            local.c = None
            time.sleep(1 + attempt)
    with lock:
        done[1] += 1


t0 = time.time()
with ThreadPoolExecutor(48) as ex:
    for i, _ in enumerate(ex.map(one, names), 1):
        if i % 20000 == 0:
            print(f"{time.strftime('%H:%M:%S')} {i}/{len(names)} ({done[0]} bajadas, {done[1]} fallos, "
                  f"{i / (time.time() - t0):.0f}/s)", flush=True)
print(f"fotos: {done[0]} bajadas, {done[1]} fallos de {len(names)}", flush=True)
sys.exit(0 if done[1] < max(100, len(names) // 100) else 1)
