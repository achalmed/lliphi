"""Estilo de Plasma (desktoptheme): un solo paquete que sigue el esquema de color del sistema.

Como Breeze `default`, no trae `colors`: cada SVG lleva `<style id="current-color-scheme">` con las clases
`ColorScheme-*` y rellena con `currentColor`, de modo que Plasma lo tiñe con el esquema activo y con el
acento del usuario (Calibre 10530). Los SVG se construyen aquí, con el contrato de `background-svg`
(Calibre 10524): nueve losas `[posición]`, `hint-*-margin`, `hint-*-inset`, `mask-*`, `shadow-*` con
`shadow-hint-*-margin`, `hint-tile-center`, y el juego `thick-*` del panel. Lo que no se dibuja aquí
(botones, barras, iconos…) lo hereda de Breeze.

Geometría desde los tokens: radios (`radio.*`), espacios (`espaciado.*`); opacidad del panel 1 (decisión 2.5)."""
from __future__ import annotations

import json
from pathlib import Path

from . import VERSION, autores, escribir

ESTILO = """  <defs>
    <style id="current-color-scheme" type="text/css">
      .ColorScheme-Text {{ color:{texto}; }}
      .ColorScheme-Background {{ color:{fondo}; }}
      .ColorScheme-Highlight {{ color:{acento}; }}
      .ColorScheme-ViewText {{ color:{texto}; }}
      .ColorScheme-ViewBackground {{ color:{vista}; }}
      .ColorScheme-ViewHover {{ color:{acento}; }}
      .ColorScheme-ViewFocus {{ color:{acento}; }}
      .ColorScheme-ButtonText {{ color:{texto}; }}
      .ColorScheme-ButtonBackground {{ color:{boton}; }}
      .ColorScheme-ButtonHover {{ color:{acento}; }}
      .ColorScheme-ButtonFocus {{ color:{acento}; }}
    </style>
{gradientes}  </defs>
"""


def _arco_esquina(x: float, y: float, t: float, r: float, cual: str, inset: float = 0.0) -> str:
    """Trayectoria de una losa de esquina (t×t) con radio r en la esquina `cual`, encogida `inset` px hacia dentro."""
    i = inset
    r = max(r - i, 0)
    x0, y0, x1, y1 = x + i, y + i, x + t, y + t
    if cual == "topleft":
        return f"M{x0 + r},{y0} H{x1} V{y1} H{x0} V{y0 + r} A{r},{r} 0 0 1 {x0 + r},{y0} Z"
    if cual == "topright":
        x0, x1 = x, x + t - i
        return f"M{x0},{y0} H{x1 - r} A{r},{r} 0 0 1 {x1},{y0 + r} V{y1} H{x0} Z"
    if cual == "bottomleft":
        y0, y1 = y, y + t - i
        return f"M{x0},{y0} H{x1} V{y1} H{x0 + r} A{r},{r} 0 0 1 {x0},{y1 - r} Z"
    x0, y0, x1, y1 = x, y, x + t - i, y + t - i
    return f"M{x0},{y0} H{x1} V{y1 - r} A{r},{r} 0 0 1 {x1 - r},{y1} H{x0} Z"


def _rect(id_: str, x: float, y: float, w: float, h: float, extra: str = "") -> str:
    return f'  <rect id="{id_}" x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>\n'


def marco(prefijo: str, ox: float, oy: float, t: float, radio: float, margen: float, borde: bool,
          fondo_clase: str = "ColorScheme-Background", opacidad: float = 1.0, hx: float | None = None) -> str:
    """Nueve losas + hints de margen e inset de un marco, con origen (ox, oy); borde de 1 px en el color del texto."""
    c = 32  # tamaño del centro
    px = prefijo + "-" if prefijo else ""
    s = ""
    rel = f'class="{fondo_clase}" fill="currentColor" fill-opacity="{opacidad}"'
    bor = 'class="ColorScheme-Text" fill="currentColor" fill-opacity="0.14"'
    # esquinas
    for cual, (x, y) in {"topleft": (ox, oy), "topright": (ox + t + c, oy), "bottomleft": (ox, oy + t + c),
                         "bottomright": (ox + t + c, oy + t + c)}.items():
        s += f'  <g id="{px}{cual}">\n'
        if borde:
            s += f'    <path d="{_arco_esquina(x, y, t, radio, cual)}" {bor}/>\n'
            s += f'    <path d="{_arco_esquina(x, y, t, radio, cual, 1)}" {rel}/>\n'
        else:
            s += f'    <path d="{_arco_esquina(x, y, t, radio, cual)}" {rel}/>\n'
        s += "  </g>\n"
    # lados
    lados = {"top": (ox + t, oy, c, t), "bottom": (ox + t, oy + t + c, c, t), "left": (ox, oy + t, t, c), "right": (ox + t + c, oy + t, t, c)}
    for cual, (x, y, w, h) in lados.items():
        s += f'  <g id="{px}{cual}">\n'
        if borde:
            s += f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" {bor}/>\n'
            ix, iy, iw, ih = {"top": (x, y + 1, w, h - 1), "bottom": (x, y, w, h - 1), "left": (x + 1, y, w - 1, h), "right": (x, y, w - 1, h)}[cual]
            s += f'    <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" {rel}/>\n'
        else:
            s += f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" {rel}/>\n'
        s += "  </g>\n"
    s += _rect(f"{px}center", ox + t, oy + t, c, c, rel)
    # márgenes e insets, en una columna aparte para que no se solapen con las losas
    hx = ox + 2 * t + c + 8 if hx is None else hx
    for i, lado in enumerate(("top", "bottom", "left", "right")):
        w, h = (4, margen) if lado in ("top", "bottom") else (margen, 4)
        s += _rect(f"{px}hint-{lado}-margin", hx, oy + i * (margen + 6), w, h, 'fill="#000" fill-opacity="0"')
        s += _rect(f"{px}hint-{lado}-inset", hx + margen + 8, oy + i * (margen + 6), 4 if lado in ("top", "bottom") else 0.01, 0.01 if lado in ("top", "bottom") else 4, 'fill="#000" fill-opacity="0"')
    return s


def mascara(ox: float, oy: float, t: float, radio: float) -> str:
    """mask-*: la misma geometría del marco, en negro."""
    c = 32
    s = ""
    for cual, (x, y) in {"topleft": (ox, oy), "topright": (ox + t + c, oy), "bottomleft": (ox, oy + t + c), "bottomright": (ox + t + c, oy + t + c)}.items():
        s += f'  <path id="mask-{cual}" d="{_arco_esquina(x, y, t, radio, cual)}" fill="#000"/>\n'
    for cual, (x, y, w, h) in {"top": (ox + t, oy, c, t), "bottom": (ox + t, oy + t + c, c, t), "left": (ox, oy + t, t, c), "right": (ox + t + c, oy + t, t, c)}.items():
        s += _rect(f"mask-{cual}", x, y, w, h, 'fill="#000"')
    s += _rect("mask-center", ox + t, oy + t, c, c, 'fill="#000"')
    return s


def sombra(ox: float, oy: float, t: float, tam: float, opacidad: float, hx: float, hy: float) -> tuple[str, str]:
    """shadow-*: degradados negros alrededor del marco (que mide (2t+32)² con origen ox, oy); los hints de
    la sombra van en la columna (hx, hy). Devuelve (defs, cuerpo). Sin transformaciones: un degradado por lado."""
    c = 32
    W = 2 * t + c
    op = opacidad
    paro = f'<stop offset="0" stop-color="#000" stop-opacity="{op}"/><stop offset="1" stop-color="#000" stop-opacity="0"/>'
    g = (f'    <linearGradient id="s-arriba" x1="0" y1="1" x2="0" y2="0">{paro}</linearGradient>\n'
         f'    <linearGradient id="s-abajo" x1="0" y1="0" x2="0" y2="1">{paro}</linearGradient>\n'
         f'    <linearGradient id="s-izq" x1="1" y1="0" x2="0" y2="0">{paro}</linearGradient>\n'
         f'    <linearGradient id="s-der" x1="0" y1="0" x2="1" y2="0">{paro}</linearGradient>\n')
    esquinas = {"topleft": (ox - tam, oy - tam, ox, oy), "topright": (ox + W, oy - tam, ox + W, oy),
                "bottomleft": (ox - tam, oy + W, ox, oy + W), "bottomright": (ox + W, oy + W, ox + W, oy + W)}
    for cual, (x, y, cx, cy) in esquinas.items():
        g += f'    <radialGradient id="s-{cual}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{tam}">{paro}</radialGradient>\n'
    s = _rect("shadow-center", ox, oy, W, W, f'fill="#000" fill-opacity="{op}"')
    s += _rect("shadow-top", ox, oy - tam, W, tam, 'fill="url(#s-arriba)"')
    s += _rect("shadow-bottom", ox, oy + W, W, tam, 'fill="url(#s-abajo)"')
    s += _rect("shadow-left", ox - tam, oy, tam, W, 'fill="url(#s-izq)"')
    s += _rect("shadow-right", ox + W, oy, tam, W, 'fill="url(#s-der)"')
    for cual, (x, y, cx, cy) in esquinas.items():
        s += _rect(f"shadow-{cual}", x, y, tam, tam, f'fill="url(#s-{cual})"')
    for i, lado in enumerate(("top", "bottom", "left", "right")):
        w, h = (4, tam) if lado in ("top", "bottom") else (tam, 4)
        s += _rect(f"shadow-hint-{lado}-margin", hx, hy + i * (tam + 6), w, h, 'fill="#000" fill-opacity="0"')
        s += _rect(f"shadow-hint-{lado}-inset", hx + tam + 8, hy + i * (tam + 6), 4 if lado in ("top", "bottom") else 0.01, 0.01 if lado in ("top", "bottom") else 4, 'fill="#000" fill-opacity="0"')
    return g, s


def svg_fondo(colores: dict, radio: float, margen: float, borde: bool, sombra_tam: float, sombra_op: float,
              con_thick: bool = False, thick_margen: float = 8, opacidad: float = 1.0, tile_center: bool = True) -> str:
    """Un SVG de fondo completo: sombra + marco + máscara (+ juego thick), cada juego en su columna."""
    t = max(radio, 4) + 2
    W = 2 * t + 32
    S = sombra_tam
    col_marco, col_hints, col_mask, col_sh = S, S + W + 8, S + W + 60, S + 2 * W + 72
    ancho = col_sh + S + 40
    fila2 = S + W + 24
    alto = (fila2 + W + S if con_thick else S + W + S) + 12
    defs_sombra, cuerpo_sombra = sombra(col_marco, S, t, S, sombra_op, col_sh, S)
    s = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERADO por herramientas/generar.py desde tokens/; no editar -->\n'
    s += f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">\n'
    s += ESTILO.format(gradientes=defs_sombra, **colores)
    s += cuerpo_sombra
    s += marco("", col_marco, S, t, radio, margen, borde, opacidad=opacidad, hx=col_hints)
    s += mascara(col_mask, S, t, radio)
    if tile_center:
        s += _rect("hint-tile-center", 2, alto - 8, 5, 5, 'fill="#000" fill-opacity="0"')
    if con_thick:
        s += marco("thick", col_marco, fila2, t, radio, thick_margen, borde, opacidad=opacidad, hx=col_hints)
    s += "</svg>\n"
    return s


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    base = destino / "desktoptheme" / marca["id"]
    r = {k: v["$value"]["value"] for k, v in tokens["radio"].items() if isinstance(v, dict) and "$value" in v}
    # colores de referencia del stylesheet: los del oscuro; Plasma los sustituye por los del esquema activo
    from . import semanticos
    t = semanticos(tokens, "oscuro")
    colores = {"texto": t["texto.normal"], "fondo": t["fondo.ventana"], "acento": t["acento.base"], "vista": t["fondo.vista"], "boton": t["fondo.boton"]}
    escribir(base / "metadata.json", json.dumps({
        "KPlugin": {"Authors": autores(marca), "Category": "", "Description": marca["descripcion"],
                    "EnabledByDefault": True, "Id": marca["id"], "License": marca["licencia_activos"],
                    "Name": marca["nombre"], "Version": VERSION, "Website": marca["sitio"]},
        "X-Plasma-API": "5.0"}, ensure_ascii=False, indent=4) + "\n", hechos)
    escribir(base / "plasmarc", "\n".join([
        "# GENERADO por herramientas/generar.py desde tokens/; no editar", "",
        "[Settings]", "FallbackTheme=default", "",
        "[Wallpaper]", f"defaultWallpaperTheme={marca['id_fondo']}", "defaultFileSuffix=.png", "defaultWidth=1920", "defaultHeight=1080", "",
        "[ContrastEffect]", "enabled=true", "contrast=0.3", "saturation=1.2", "",
        "[BlurBehindEffect]", "enabled=true", "",
        "[AdaptiveTransparency]", "enabled=true", ""]), hechos)
    # panel: radio del panel flotante, margen 8 (juego normal) y 8 (thick), opaco, sin borde cuando es de borde a borde
    escribir(base / "widgets" / "panel-background.svg",
             svg_fondo(colores, r["panel-flotante"], 8, True, 12, 0.35, con_thick=True, thick_margen=8), hechos)
    escribir(base / "dialogs" / "background.svg", svg_fondo(colores, r["ventana"], 12, True, 24, 0.40), hechos)
    escribir(base / "widgets" / "tooltip.svg", svg_fondo(colores, r["menu"], 8, True, 12, 0.35), hechos)
    escribir(base / "widgets" / "background.svg", svg_fondo(colores, r["ventana"], 12, True, 12, 0.30), hechos)
    escribir(base / "widgets" / "translucentbackground.svg", svg_fondo(colores, r["ventana"], 12, True, 12, 0.30, opacidad=0.92), hechos)
    return hechos
