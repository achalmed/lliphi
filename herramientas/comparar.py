#!/usr/bin/env python3
"""Hoja de comparación antes/después: pone lado a lado pares de capturas con rótulos.

Uso:  .venv/bin/python herramientas/comparar.py muestras/comparacion-0.1-0.2.png "antes 0.1.0=muestras/capturas-0.1/oscuro-02-lanzador.png" "después 0.2.0=muestras/capturas/oscuro-14-lanzador-cristal.png" ...
Cada argumento «rótulo=ruta» es una celda; se disponen en filas de dos (antes | después). Requiere Pillow.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANCHO = 900


def celda(ruta: Path, rotulo: str) -> Image.Image:
    im = Image.open(ruta).convert("RGB")
    im = im.resize((ANCHO, round(im.height * ANCHO / im.width)), Image.LANCZOS)
    lienzo = Image.new("RGB", (ANCHO, im.height + 40), "#101012")
    lienzo.paste(im, (0, 40))
    d = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Medium.ttf", 20)
    except OSError:
        fuente = ImageFont.load_default()
    d.text((12, 10), rotulo, fill="#eaebed", font=fuente)
    return lienzo


def main() -> int:
    salida = Path(sys.argv[1])
    pares = [a.split("=", 1) for a in sys.argv[2:]]
    celdas = [celda(Path(r), t) for t, r in pares]
    filas = [celdas[i:i + 2] for i in range(0, len(celdas), 2)]
    alto = sum(max(c.height for c in f) for f in filas) + 16 * (len(filas) + 1)
    hoja = Image.new("RGB", (2 * ANCHO + 48, alto), "#101012")
    y = 16
    for f in filas:
        for j, c in enumerate(f):
            hoja.paste(c, (16 + j * (ANCHO + 16), y))
        y += max(c.height for c in f) + 16
    salida.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(salida, optimize=True)
    print(f"escrito {salida} ({hoja.width}×{hoja.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
