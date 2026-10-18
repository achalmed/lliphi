#!/usr/bin/env python3
"""Hoja de contacto de los iconos: todos los iconos del tema, a 22 y 48 px (y cada uno al doble, para ver el
escalado) con su nombre, renderizados con Inkscape sobre el fondo de ventana de cada variante. Es una muestra
(`muestras/iconos-contacto-<variante>.png`), no un archivo generado: sirve para mirar el conjunto entero de un
vistazo y detectar trazos rotos o iconos ilegibles.

Uso:  python3 herramientas/contacto.py [--tamanos 22,48] [--solo oscuro|claro]
Cada SVG se exporta a PNG al tamaño exacto en una sola sesión `inkscape --shell` (nítido, sin reescalar) y la hoja
se compone con Pillow (`.venv`)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from destinos import RAIZ, cargar, semanticos  # noqa: E402
from destinos.iconos import ARCHIVO, CONTEXTOS, ICONOS, id_tema  # noqa: E402

MUESTRAS = RAIZ / "muestras"


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _fuente(tam: int, negrita: bool = False):
    from PIL import ImageFont
    for ruta in ("/usr/share/fonts/opentype/inter/Inter-Bold.otf" if negrita else "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
                 "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if negrita else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"):
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default()


def exportar(trabajos: list[tuple[Path, Path, int]]) -> None:
    """[(svg, png, lado)] → PNG con Inkscape en una sola sesión."""
    ordenes = []
    for svg, png, lado in trabajos:
        ordenes += [f"file-open:{svg}", f"export-filename:{png}", f"export-width:{lado}", f"export-height:{lado}",
                    "export-background-opacity:0", "export-do", "file-close"]
    subprocess.run(["inkscape", "--shell"], input="\n".join(ordenes) + "\nquit\n", check=True, capture_output=True, text=True)


def hoja(variante: str, tamanos: tuple[int, ...], tokens: dict, marca: dict) -> Path:
    from PIL import Image, ImageDraw
    s = semanticos(tokens, variante)
    base = RAIZ / "generado" / "icons" / id_tema(marca, variante)
    columnas, margen, hueco = 7, 24, 12
    ancho_celda = max(S * 3 + hueco for S in tamanos) + 20          # el icono y su doble, lado a lado
    alto_celda = sum(S * 2 + 8 for S in tamanos) + 22
    fuente, titulo_f, seccion_f = _fuente(11), _fuente(16, True), _fuente(13, True)
    grupos = [(c, [n for n, (cc, _f, _a) in ICONOS.items() if cc == c]) for c in CONTEXTOS]
    alto = margen + 34 + sum(14 + ((len(n) + columnas - 1) // columnas) * alto_celda + 16 for _c, n in grupos)
    ancho = margen * 2 + columnas * ancho_celda
    im = Image.new("RGB", (ancho, alto), _hex(s["fondo.ventana"]))
    d = ImageDraw.Draw(im)
    d.text((margen, margen), f'{marca["nombre"]} · iconografía de línea · variante {variante} · '
           + ", ".join(f"{S} px y ×2" for S in tamanos), fill=_hex(s["texto.normal"]), font=titulo_f)
    with tempfile.TemporaryDirectory(prefix="lliphi-contacto-") as tmp:
        trabajos: list[tuple[Path, Path, int]] = []
        posiciones: list[tuple[Path, int, int]] = []
        y = margen + 34
        for contexto, nombres in grupos:
            d.text((margen, y), f"{contexto} · {len(nombres)}", fill=_hex(s["texto.normal"]), font=seccion_f)
            y += 14 + 8
            for i, nombre in enumerate(nombres):
                x0 = margen + (i % columnas) * ancho_celda
                y0 = y + (i // columnas) * alto_celda
                svg = base / contexto / "22" / f"{ARCHIVO.get(nombre, nombre)}.svg"
                yy = y0
                for S in tamanos:
                    svg = base / contexto / str(S) / f"{ARCHIVO.get(nombre, nombre)}.svg"
                    for lado, dx in ((S, 0), (S * 2, S + hueco)):
                        png = Path(tmp) / f"{variante}-{contexto}-{nombre}-{S}-{lado}.png"
                        trabajos.append((svg, png, lado))
                        posiciones.append((png, x0 + dx, yy + (S * 2 - lado)))
                    yy += S * 2 + 8
                etiqueta = nombre if len(nombre) <= 22 else nombre[:21] + "…"
                d.text((x0, yy + 2), etiqueta, fill=_hex(s["texto.secundario"]), font=fuente)
            y += ((len(nombres) + columnas - 1) // columnas) * alto_celda + 8
        exportar(trabajos)
        for png, x, yy in posiciones:
            icono = Image.open(png).convert("RGBA")
            im.paste(icono, (x, yy), icono)
    salida = MUESTRAS / f"iconos-contacto-{variante}.png"
    im.save(salida, optimize=True)
    return salida


def main() -> int:
    args = sys.argv[1:]
    tamanos = (22, 48)
    if "--tamanos" in args:
        tamanos = tuple(int(x) for x in args[args.index("--tamanos") + 1].split(","))
    variantes = ("oscuro", "claro")
    if "--solo" in args:
        variantes = (args[args.index("--solo") + 1],)
    tokens, marca = cargar()
    for v in variantes:
        print(" ", hoja(v, tamanos, tokens, marca).relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
