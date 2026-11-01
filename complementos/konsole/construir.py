"""Esquemas de color de Konsole (`.colorscheme`), uno por variante, sobre el esquema «Nothing» (decisiones 4.29).

Formato INI: `[Background]`, `[BackgroundFaint]`, `[BackgroundIntense]`, `[Foreground*]`, `[Color0..7]` con
`Faint` e `Intense`, y `[General]` (`Description`, `Opacity`, `Blur`, `Wallpaper`, `ColorRandomization`).

La base es `fuentes/base/Nothing-konsole/Nothing.colorscheme` (jomada, GPL-3.0-or-later), como WhiteSur lo es del
esquema de Plasma (decisiones 4.4): el autor la prefirió a la paleta ANSI de los tokens, que no combinaba con el tema.

- Oscuro: Nothing tal cual, con el rojo en el azul (`Color4`: las carpetas, las claves de fastfetch, el prompt). Ese
  rojo, `#eb3131`, es el de que sale el acento (decisiones 4.25) y como texto se lee mejor que `#e22529` (4,0:1
  frente a 3,7:1 sobre su fondo). Solo cambian el nombre, la opacidad (`efectos.opacidad-konsole`, la de Nothing) y
  `ColorRandomization`, que se apaga para que cada pestaña tenga el mismo fondo.
- Claro: el espejo. El fondo y el texto son neutros del claro. Nothing pone rojos en el rojo (`Color1`, el de fastfetch
  y su logotipo) y en el azul (`Color4`), y su azul en el negro (`Color0`); el claro cambia rojo por azul: el `Color4`
  es el acento azul (`acento`, tenue `acento-suave`, intenso `acento-texto`), el `Color1` es el azul de Nothing y el
  `Color0`, su rojo. Así lo que en el oscuro es rojo, en el claro es azul (también lo que se pinte de rojo). Cada color
  de Nothing conserva matiz y croma y toma la luz más alta que da ≥ 4,5:1 sobre el fondo (en OKLCH); el tenue es 0,06
  más claro y el intenso 0,06 más oscuro. El texto intenso es el texto teñido del acento, como el de Nothing."""
from __future__ import annotations

import math
from pathlib import Path

from nucleo import CABECERA_INI, escribir, rgb

BASE = Path(__file__).resolve().parents[2] / "fuentes" / "base" / "Nothing-konsole" / "Nothing.colorscheme"
SUFIJOS = ("", "Faint", "Intense")


def leer_base() -> dict[str, tuple[int, int, int]]:
    """Grupo → color de la base ([Background], [Color4Faint]…)."""
    salida, grupo = {}, None
    for linea in BASE.read_text(encoding="utf-8").splitlines():
        if linea.startswith("["):
            grupo = linea.strip("[]")
        elif linea.startswith("Color=") and grupo:
            salida[grupo] = tuple(int(x) for x in linea[6:].split(","))
    return salida


# --- OKLab / OKLCH (Björn Ottosson, 2020), solo para el claro ---------------------------------------------------------

def _lineal(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gamma(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def a_oklch(c: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_lineal(x / 255) for x in c)
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _desde_oklch(L: float, C: float, h: float) -> tuple[float, float, float]:
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_, m_, s_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, \
        (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def de_oklch(L: float, C: float, h: float) -> tuple[int, int, int]:
    """sRGB de un OKLCH; si no cabe, baja el croma (mismo matiz y luz)."""
    while C > 0 and not all(-1e-4 <= x <= 1 + 1e-4 for x in _desde_oklch(L, C, h)):
        C = max(0.0, C - 0.002)
    return tuple(round(min(1.0, max(0.0, _gamma(max(0.0, x)))) * 255) for x in _desde_oklch(L, C, h))


def luminancia(c: tuple[int, int, int]) -> float:
    r, g, b = (_lineal(x / 255) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def legible(c: tuple[int, int, int], fondo: tuple[int, int, int], minimo: float = 4.5) -> float:
    """La luz OKLCH más alta con la que `c` (su matiz y croma) da ≥ `minimo`:1 sobre un fondo claro."""
    L, C, h = a_oklch(c)
    while L > 0 and contraste(de_oklch(L, C, h), fondo) < minimo:
        L -= 0.002
    return L


# --- las dos variantes ------------------------------------------------------------------------------------------------

def tupla(token: dict) -> tuple[int, int, int]:
    return tuple(int(x) for x in rgb(token).split(","))


def colores(tokens: dict, variante: str) -> dict[str, tuple[int, int, int]]:
    """Grupo del `.colorscheme` → color, para una variante."""
    base, p = leer_base(), tokens["primitivas"][variante]
    if variante == "oscuro":
        return dict(base)          # su rojo (#eb3131) es el de que sale el acento (4.25) y se lee mejor como texto
    fondo, texto = tupla(p["neutro-1"]), tupla(p["neutro-7"])
    c = {"Background": fondo, "BackgroundFaint": tupla(p["neutro-0"]), "BackgroundIntense": tupla(p["neutro-2"]),
         "Foreground": texto, "ForegroundFaint": texto}
    tinte = tupla(p["acento-texto"])
    c["ForegroundIntense"] = tuple(round(texto[i] + (tinte[i] - texto[i]) * 0.25) for i in range(3))
    origen = {0: 4, 1: 0, 2: 2, 3: 3, 5: 5, 6: 6, 7: 7}       # espejo: los rojos de Nothing pasan a azul y al revés
    for i, j in origen.items():
        _L, C, h = a_oklch(base[f"Color{j}"])
        L = legible(base[f"Color{j}"], fondo)
        c[f"Color{i}"], c[f"Color{i}Faint"], c[f"Color{i}Intense"] = (de_oklch(L + d, C, h) for d in (0, 0.06, -0.06))
    c["Color4"], c["Color4Faint"], c["Color4Intense"] = (tupla(p[k]) for k in ("acento", "acento-suave", "acento-texto"))
    return c


def texto_konsole(tokens: dict, marca: dict, variante: str) -> str:
    c = colores(tokens, variante)
    grupos = ["Background", "BackgroundFaint", "BackgroundIntense",
              *[f"Color{i}{s}" for i in range(8) for s in SUFIJOS], "Foreground", "ForegroundFaint", "ForegroundIntense"]
    lineas = [CABECERA_INI]
    for g in grupos:
        lineas += [f"[{g}]", "Color=" + ",".join(str(x) for x in c[g]), ""]
    opacidad = tokens.get("efectos", {}).get("opacidad-konsole", {}).get("$value", 0.8)
    lineas += ["[General]", "Anchor=0.5,0.5", "Blur=true", "ColorRandomization=false",
               f"Description={marca['nombre_esquema'][variante]}", "FillStyle=Tile", f"Opacity={opacidad}", "Wallpaper=",
               "WallpaperFlipType=NoFlip", "WallpaperOpacity=1", ""]
    return "\n".join(lineas)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        escribir(destino / f"{marca['nombre_esquema'][variante]}.colorscheme",
                 texto_konsole(tokens, marca, variante), hechos)
    return hechos
