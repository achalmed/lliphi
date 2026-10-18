"""Esquemas de color de Konsole (`.colorscheme`), uno por variante, desde el grupo `terminal` de los tokens.

Formato INI: `[Background]`, `[BackgroundFaint]`, `[BackgroundIntense]`, `[Foreground*]`, `[Color0..7]` con
`Faint` e `Intense`, y `[General]` (`Description`, `Opacity`, `Blur`, `Wallpaper`, `ColorRandomization`)."""
from __future__ import annotations

from pathlib import Path

from . import CABECERA_INI, escribir, rgb


def texto_konsole(tokens: dict, marca: dict, variante: str) -> str:
    t = {k: rgb(v) for k, v in tokens["terminal"][variante].items()}
    lineas = [CABECERA_INI, "[Background]", f"Color={t['fondo']}", "", "[BackgroundFaint]", f"Color={t['fondo']}", "",
              "[BackgroundIntense]", f"Color={t['fondo']}", ""]
    for i in range(8):
        lineas += [f"[Color{i}]", f"Color={t[f'color{i}']}", "", f"[Color{i}Faint]", f"Color={t[f'color{i}']}", "",
                   f"[Color{i}Intense]", f"Color={t[f'color{i + 8}']}", ""]
    lineas += ["[Foreground]", f"Color={t['texto']}", "", "[ForegroundFaint]", f"Color={t['texto-tenue']}", "",
               "[ForegroundIntense]", f"Color={t['texto-intenso']}", "",
               "[General]", "Anchor=0.5,0.5", "Blur=false", "ColorRandomization=false",
               f"Description={marca['nombre_esquema'][variante]}", "FillStyle=Tile", "Opacity=1", "Wallpaper=",
               "WallpaperFlipType=NoFlip", "WallpaperOpacity=1", ""]
    return "\n".join(lineas)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        escribir(destino / "konsole" / f"{marca['nombre_esquema'][variante]}.colorscheme",
                 texto_konsole(tokens, marca, variante), hechos)
    return hechos
