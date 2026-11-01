"""Esquemas de color de Konsole (`.colorscheme`), uno por variante, desde el grupo `terminal` de los tokens.

Formato INI: `[Background]`, `[BackgroundFaint]`, `[BackgroundIntense]`, `[Foreground*]`, `[Color0..7]` con
`Faint` e `Intense`, y `[General]` (`Description`, `Opacity`, `Blur`, `Wallpaper`, `ColorRandomization`).

Konsole no tiene color de acento: el magenta (`Color5`) lleva el de la variante (decisiones 4.28), el rojo en el oscuro
y el azul en el claro, para que el prompt y lo que se pinte en magenta combinen con el tema. Es el primer acento que
da ≥ 4.5:1 sobre el fondo (`acento`, si no `acento-suave`); el intenso es `acento-texto`. El magenta de los tokens no
cambia: lo usan con su nombre LibreOffice, Obsidian y los editores."""
from __future__ import annotations

from pathlib import Path

from nucleo import CABECERA_INI, escribir, rgb


def contraste(a: dict, b: dict) -> float:
    def lum(token: dict) -> float:
        c = [int(token["$value"]["hex"].lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def acento_terminal(tokens: dict, variante: str) -> tuple[dict, dict]:
    """El acento de la variante para el magenta: (normal, intenso)."""
    p, fondo = tokens["primitivas"][variante], tokens["terminal"][variante]["fondo"]
    normal = next((p[k] for k in ("acento", "acento-suave") if contraste(p[k], fondo) >= 4.5), p["acento-texto"])
    return normal, p["acento-texto"]


def texto_konsole(tokens: dict, marca: dict, variante: str) -> str:
    t = {k: rgb(v) for k, v in tokens["terminal"][variante].items()}
    t["color5"], t["color13"] = (rgb(x) for x in acento_terminal(tokens, variante))
    lineas = [CABECERA_INI, "[Background]", f"Color={t['fondo']}", "", "[BackgroundFaint]", f"Color={t['fondo']}", "",
              "[BackgroundIntense]", f"Color={t['fondo']}", ""]
    for i in range(8):
        lineas += [f"[Color{i}]", f"Color={t[f'color{i}']}", "", f"[Color{i}Faint]", f"Color={t[f'color{i}']}", "",
                   f"[Color{i}Intense]", f"Color={t[f'color{i + 8}']}", ""]
    lineas += ["[Foreground]", f"Color={t['texto']}", "", "[ForegroundFaint]", f"Color={t['texto-tenue']}", "",
               "[ForegroundIntense]", f"Color={t['texto-intenso']}", "",
               "[General]", "Anchor=0.5,0.5", "Blur=true", "ColorRandomization=false",
               f"Description={marca['nombre_esquema'][variante]}", "FillStyle=Tile", f"Opacity={tokens.get('efectos', {}).get('opacidad-konsole', {}).get('$value', 0.86)}", "Wallpaper=",
               "WallpaperFlipType=NoFlip", "WallpaperOpacity=1", ""]
    return "\n".join(lineas)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        escribir(destino / f"{marca['nombre_esquema'][variante]}.colorscheme",
                 texto_konsole(tokens, marca, variante), hechos)
    return hechos
