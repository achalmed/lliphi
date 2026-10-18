"""Estilo de Plasma (desktoptheme) «Lliphi cristal»: un paquete que sigue el esquema de color del sistema.

Como Breeze `default`, no trae `colors`: cada SVG lleva `<style id="current-color-scheme">` con las clases
`ColorScheme-*` y rellena con `currentColor`, de modo que Plasma lo tiñe con el esquema activo y con el acento
del usuario (Calibre 10530). Los SVG se construyen aquí con el contrato de `background-svg` (Calibre 10524):
nueve losas `[posición]`, `hint-*-margin`, `hint-*-inset`, `mask-*`, `shadow-*`, `hint-tile-center`, el juego
`thick-*` del panel y los marcos por estado de `tasks`, `button`, `lineedit`, `tabbar`, `viewitem`, `listitem`,
`frame`, `toolbar`, `glowbar` y `slider` (Calibre 10521). Lo que no se dibuja aquí lo hereda de Breeze.

Dirección (docs/autocritica.md §3): vidrio de WhiteSur sobre la noche de Nothing. Los fondos de `translucent/` son
los de cristal (Plasma los usa solo cuando el compositor aplica desenfoque); los normales son casi opacos, para que
el texto siga legible sin desenfoque. Capa tecnológica: retícula de puntos en el panel, hairline luminosa, foco en
acento de 2 px.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import VERSION, autores, escribir, semanticos

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
C = 32          # lado del centro de cada marco
HUECO = 'fill="#000" fill-opacity="0"'


# ---------------------------------------------------------------------------- primitivas de dibujo

def _arco(x: float, y: float, t: float, r: float, cual: str, inset: float = 0.0) -> str:
    """Trayectoria de una losa de esquina (t×t) con radio r en la esquina `cual`, encogida `inset` px hacia dentro."""
    i = inset
    r = max(r - i, 0)
    if cual == "topleft":
        x0, y0, x1, y1 = x + i, y + i, x + t, y + t
        return f"M{x0 + r},{y0} H{x1} V{y1} H{x0} V{y0 + r} A{r},{r} 0 0 1 {x0 + r},{y0} Z"
    if cual == "topright":
        x0, y0, x1, y1 = x, y + i, x + t - i, y + t
        return f"M{x0},{y0} H{x1 - r} A{r},{r} 0 0 1 {x1},{y0 + r} V{y1} H{x0} Z"
    if cual == "bottomleft":
        x0, y0, x1, y1 = x + i, y, x + t, y + t - i
        return f"M{x0},{y0} H{x1} V{y1} H{x0 + r} A{r},{r} 0 0 1 {x0},{y1 - r} Z"
    x0, y0, x1, y1 = x, y, x + t - i, y + t - i
    return f"M{x0},{y0} H{x1} V{y1 - r} A{r},{r} 0 0 1 {x1 - r},{y1} H{x0} Z"


def _rect(id_: str, x: float, y: float, w: float, h: float, extra: str = "") -> str:
    return f'  <rect id="{id_}" x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>\n'


def relleno(clase: str, opacidad: float = 1.0) -> str:
    return f'class="{clase}" fill="currentColor" fill-opacity="{opacidad}"'


def marco(prefijo: str, ox: float, oy: float, t: float, radio: float, margen: float | None,
          capas: list[tuple], hx: float | None = None, hairline: float = 0.0,
          sin_hints: bool = False, insets: bool = True) -> str:
    """Nueve losas de un marco con origen (ox, oy). `capas` = [(clase, opacidad, inset)] se pintan en orden; `hairline`
    > 0 añade una línea de 1 px en el borde superior (texto a esa opacidad). `margen` escribe los `hint-*-margin`."""
    px = prefijo + "-" if prefijo else ""
    s = ""
    esquinas = {"topleft": (ox, oy), "topright": (ox + t + C, oy), "bottomleft": (ox, oy + t + C), "bottomright": (ox + t + C, oy + t + C)}
    lados = {"top": (ox + t, oy, C, t), "bottom": (ox + t, oy + t + C, C, t), "left": (ox, oy + t, t, C), "right": (ox + t + C, oy + t, t, C)}
    def lado_rect(cual, x, y, w, h, inset):
        return {"top": (x, y + inset, w, h - inset), "bottom": (x, y, w, h - inset), "left": (x + inset, y, w - inset, h), "right": (x, y, w - inset, h)}[cual]

    for cual, (x, y) in esquinas.items():
        s += f'  <g id="{px}{cual}">\n'
        for capa in capas:
            clase, op, inset = capa[:3]
            grosor = capa[3] if len(capa) > 3 else 0
            if grosor:
                s += f'    <path fill-rule="evenodd" d="{_arco(x, y, t, radio, cual, inset)} {_arco(x, y, t, radio, cual, inset + grosor)}" {relleno(clase, op)}/>\n'
            else:
                s += f'    <path d="{_arco(x, y, t, radio, cual, inset)}" {relleno(clase, op)}/>\n'
        s += "  </g>\n"
    for cual, (x, y, w, h) in lados.items():
        s += f'  <g id="{px}{cual}">\n'
        for capa in capas:
            clase, op, inset = capa[:3]
            grosor = capa[3] if len(capa) > 3 else 0
            ix, iy, iw, ih = lado_rect(cual, x, y, w, h, inset)
            if grosor:
                jx, jy, jw, jh = lado_rect(cual, x, y, w, h, inset + grosor)
                s += f'    <path fill-rule="evenodd" d="M{ix},{iy} h{iw} v{ih} h{-iw} Z M{jx},{jy} h{jw} v{jh} h{-jw} Z" {relleno(clase, op)}/>\n'
            else:
                s += f'    <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" {relleno(clase, op)}/>\n'
        if hairline and cual == "top":
            s += f'    <rect x="{x}" y="{y}" width="{w}" height="1" {relleno("ColorScheme-Text", hairline)}/>\n'
        s += "  </g>\n"
    s += f'  <g id="{px}center">\n'
    for capa in capas:
        clase, op, inset = capa[:3]
        if len(capa) > 3 and capa[3]:
            continue                      # un anillo no tiene centro
        s += f'    <rect x="{ox + t}" y="{oy + t}" width="{C}" height="{C}" {relleno(clase, op)}/>\n'
    if all(len(c) > 3 and c[3] for c in capas):
        s += f'    <rect x="{ox + t}" y="{oy + t}" width="{C}" height="{C}" fill="#000" fill-opacity="0"/>\n'
    s += "  </g>\n"
    if margen is not None and not sin_hints:
        hx = ox + 2 * t + C + 8 if hx is None else hx
        for i, lado in enumerate(("top", "bottom", "left", "right")):
            w, h = (4, margen) if lado in ("top", "bottom") else (margen, 4)
            s += _rect(f"{px}hint-{lado}-margin", hx, oy + i * (margen + 6), w, h, HUECO)
            if insets:
                s += _rect(f"{px}hint-{lado}-inset", hx + margen + 8, oy + i * (margen + 6), 4 if lado in ("top", "bottom") else 0.01, 0.01 if lado in ("top", "bottom") else 4, HUECO)
    return s


def mascara(ox: float, oy: float, t: float, radio: float) -> str:
    s = ""
    for cual, (x, y) in {"topleft": (ox, oy), "topright": (ox + t + C, oy), "bottomleft": (ox, oy + t + C), "bottomright": (ox + t + C, oy + t + C)}.items():
        s += f'  <path id="mask-{cual}" d="{_arco(x, y, t, radio, cual)}" fill="#000"/>\n'
    for cual, (x, y, w, h) in {"top": (ox + t, oy, C, t), "bottom": (ox + t, oy + t + C, C, t), "left": (ox, oy + t, t, C), "right": (ox + t + C, oy + t, t, C)}.items():
        s += _rect(f"mask-{cual}", x, y, w, h, 'fill="#000"')
    s += _rect("mask-center", ox + t, oy + t, C, C, 'fill="#000"')
    return s


def sombra(ox: float, oy: float, t: float, tam: float, opacidad: float, hx: float, hy: float, prefijo: str = "shadow") -> tuple[str, str]:
    W = 2 * t + C
    paro = f'<stop offset="0" stop-color="#000" stop-opacity="{opacidad}"/><stop offset="1" stop-color="#000" stop-opacity="0"/>'
    g = (f'    <linearGradient id="{prefijo}-arriba" x1="0" y1="1" x2="0" y2="0">{paro}</linearGradient>\n'
         f'    <linearGradient id="{prefijo}-abajo" x1="0" y1="0" x2="0" y2="1">{paro}</linearGradient>\n'
         f'    <linearGradient id="{prefijo}-izq" x1="1" y1="0" x2="0" y2="0">{paro}</linearGradient>\n'
         f'    <linearGradient id="{prefijo}-der" x1="0" y1="0" x2="1" y2="0">{paro}</linearGradient>\n')
    esquinas = {"topleft": (ox - tam, oy - tam, ox, oy), "topright": (ox + W, oy - tam, ox + W, oy),
                "bottomleft": (ox - tam, oy + W, ox, oy + W), "bottomright": (ox + W, oy + W, ox + W, oy + W)}
    for cual, (x, y, cx, cy) in esquinas.items():
        g += f'    <radialGradient id="g-{prefijo}-{cual}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{tam}">{paro}</radialGradient>\n'
    s = _rect(f"{prefijo}-center", ox, oy, W, W, f'fill="#000" fill-opacity="{opacidad}"')
    s += _rect(f"{prefijo}-top", ox, oy - tam, W, tam, f'fill="url(#{prefijo}-arriba)"')
    s += _rect(f"{prefijo}-bottom", ox, oy + W, W, tam, f'fill="url(#{prefijo}-abajo)"')
    s += _rect(f"{prefijo}-left", ox - tam, oy, tam, W, f'fill="url(#{prefijo}-izq)"')
    s += _rect(f"{prefijo}-right", ox + W, oy, tam, W, f'fill="url(#{prefijo}-der)"')
    for cual, (x, y, cx, cy) in esquinas.items():
        s += _rect(f"{prefijo}-{cual}", x, y, tam, tam, f'fill="url(#g-{prefijo}-{cual})"')
    for i, lado in enumerate(("top", "bottom", "left", "right")):
        w, h = (4, tam) if lado in ("top", "bottom") else (tam, 4)
        s += _rect(f"{prefijo}-hint-{lado}-margin", hx, hy + i * (tam + 6), w, h, HUECO)
        s += _rect(f"{prefijo}-hint-{lado}-inset", hx + tam + 8, hy + i * (tam + 6), 4 if lado in ("top", "bottom") else 0.01, 0.01 if lado in ("top", "bottom") else 4, HUECO)
    return g, s


def cabecera(ancho: float, alto: float, colores: dict, gradientes: str = "") -> str:
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERADO por herramientas/generar.py desde tokens/; no editar -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">\n'
            + ESTILO.format(gradientes=gradientes, **colores))


def puntos(ox: float, oy: float, opacidad: float) -> str:
    """Retícula de puntos (4 por losa de 32 px) para el centro teselado del panel: la capa tecnológica."""
    s = ""
    for x, y in ((8, 8), (24, 8), (8, 24), (24, 24)):
        s += f'    <circle cx="{ox + x}" cy="{oy + y}" r="1" {relleno("ColorScheme-Text", opacidad)}/>\n'
    return s


# ---------------------------------------------------------------------------- fondos (panel, diálogos, tooltip, widgets)

def svg_fondo(colores: dict, radio: float, margen: float, opacidad: float, sombra_tam: float, sombra_op: float,
              hairline: float = 0.10, borde: float = 0.16, con_thick: bool = False, thick_margen: float = 8,
              textura: float = 0.0) -> str:
    t = max(radio, 4) + 2
    W = 2 * t + C
    S = sombra_tam
    col_marco, col_hints, col_mask, col_sh = S, S + W + 8, S + W + 60, S + 2 * W + 72
    ancho = col_sh + S + 40
    fila2 = S + W + 24
    alto = (fila2 + W + S if con_thick else S + W + S) + 12
    g, cuerpo_sombra = sombra(col_marco, S, t, S, sombra_op, col_sh, S)
    capas = [("ColorScheme-Background", opacidad, 0.0), ("ColorScheme-Text", borde, 0.0, 1)]   # vidrio + anillo hairline
    s = cabecera(ancho, alto, colores, g) + cuerpo_sombra
    s += marco("", col_marco, S, t, radio, margen, capas, hx=col_hints, hairline=hairline)
    if textura:
        s = s.replace('  <g id="center">\n', '  <g id="center">\n' + puntos(col_marco + t, S + t, textura), 1)
    s += mascara(col_mask, S, t, radio)
    s += _rect("hint-tile-center", 2, alto - 8, 5, 5, HUECO)
    if con_thick:
        s += marco("thick", col_marco, fila2, t, radio, thick_margen, capas, hx=col_hints, hairline=hairline)
        if textura:
            s = s.replace('  <g id="thick-center">\n', '  <g id="thick-center">\n' + puntos(col_marco + t, fila2 + t, textura), 1)
    return s + "</svg>\n"


# ---------------------------------------------------------------------------- widgets con estados

def svg_estados(colores: dict, estados: dict[str, list[tuple[str, float, float]]], radio: float, margen: float | None,
                hairlines: dict[str, float] | None = None, extras: str = "", con_mask_de: str | None = None, insets: bool = False) -> str:
    """Un marco por estado (prefijo = nombre del estado), apilados en columnas de 2 (sin solaparse)."""
    t = max(radio, 3) + 2
    W = 2 * t + C
    paso = W + 60
    n = len(estados)
    cols = 2
    filas = (n + cols - 1) // cols
    ancho = cols * paso + 16
    alto = filas * (W + 16) + 16
    s = cabecera(ancho, alto, colores)
    for i, (nombre, capas) in enumerate(estados.items()):
        ox = 8 + (i % cols) * paso
        oy = 8 + (i // cols) * (W + 16)
        s += marco(nombre, ox, oy, t, radio, margen, capas, hx=ox + W + 8, hairline=(hairlines or {}).get(nombre, 0.0), insets=insets)
        if con_mask_de == nombre:
            s += mascara(ox + paso // 2, oy, t, radio).replace('id="mask-', 'id="mask-')
    s += extras
    return s + "</svg>\n"


def svg_tasks(colores: dict, radio: float) -> str:
    acento = "ColorScheme-Highlight"
    texto = "ColorScheme-Text"
    estados = {
        "normal": [(texto, 0.0, 0.0)],
        "hover": [(texto, 0.08, 0.0)],
        "focus": [(acento, 0.16, 0.0)],
        "attention": [(acento, 0.32, 0.0)],
        "minimized": [(texto, 0.03, 0.0)],
        "progress": [(acento, 0.22, 0.0)],
    }
    s = svg_estados(colores, estados, radio, 2)
    # indicador de 2 px en el borde inferior del estado activo y del de atención (la firma del dock)
    s = s.replace('  <g id="focus-bottom">\n', '  <g id="focus-bottom">\n    <rect x="0" y="0" width="0" height="0" fill="none"/>\n', 1)
    t = max(radio, 3) + 2
    W = 2 * t + C
    paso = W + 60
    for i, nombre in enumerate(("focus", "attention")):
        idx = list(estados).index(nombre)
        ox = 8 + (idx % 2) * paso
        oy = 8 + (idx // 2) * (W + 16)
        marca = f'    <rect x="{ox + t}" y="{oy + t + C + t - 2}" width="{C}" height="2" {relleno(acento, 1.0)}/>\n'
        s = s.replace(f'  <g id="{nombre}-bottom">\n', f'  <g id="{nombre}-bottom">\n' + marca, 1)
    return s


def svg_button(colores: dict, radio: float) -> str:
    fondo, texto, hover, foco = "ColorScheme-ButtonBackground", "ColorScheme-ButtonText", "ColorScheme-ButtonHover", "ColorScheme-ButtonFocus"
    estados = {
        "normal": [(fondo, 0.92, 0.0), (texto, 0.14, 0.0, 1)],
        "hover": [(fondo, 0.92, 0.0), (hover, 0.12, 0.0), (hover, 1.0, 0.0, 1)],
        "pressed": [(fondo, 0.92, 0.0), (hover, 0.28, 0.0), (hover, 1.0, 0.0, 1)],
        "focus": [(foco, 1.0, 0.0, 2)],
        "toolbutton-hover": [(texto, 0.08, 0.0)],
        "toolbutton-pressed": [(texto, 0.16, 0.0)],
    }
    return svg_estados(colores, estados, radio, 6, hairlines={"normal": 0.0})


def svg_lineedit(colores: dict, radio: float) -> str:
    vista, texto, hover, foco = "ColorScheme-ViewBackground", "ColorScheme-ViewText", "ColorScheme-ViewHover", "ColorScheme-ViewFocus"
    estados = {
        "base": [(vista, 0.88, 0.0), (texto, 0.18, 0.0, 1)],
        "hover": [(hover, 0.7, 0.0, 1)],
        "focus": [(foco, 1.0, 0.0, 2)],
        "focusframe": [(foco, 0.55, 0.0, 1)],
    }
    return svg_estados(colores, estados, radio, 4)


def svg_tabbar(colores: dict, radio: float) -> str:
    acento, texto = "ColorScheme-Highlight", "ColorScheme-Text"
    estados = {f"{d}-active-tab": [(acento, 0.14, 0.0)] for d in ("north", "south", "east", "west")}
    s = svg_estados(colores, estados, radio, 4)
    t = max(radio, 3) + 2
    W = 2 * t + C
    paso = W + 60
    for i, d in enumerate(("north", "south", "east", "west")):
        ox = 8 + (i % 2) * paso
        oy = 8 + (i // 2) * (W + 16)
        lado = {"north": "bottom", "south": "top", "east": "left", "west": "right"}[d]
        if lado in ("bottom", "top"):
            y = oy + t + C + t - 2 if lado == "bottom" else oy
            marca = f'    <rect x="{ox + t}" y="{y}" width="{C}" height="2" {relleno(acento, 1.0)}/>\n'
        else:
            x = ox if lado == "left" else ox + t + C + t - 2
            marca = f'    <rect x="{x}" y="{oy + t}" width="2" height="{C}" {relleno(acento, 1.0)}/>\n'
        s = s.replace(f'  <g id="{d}-active-tab-{lado}">\n', f'  <g id="{d}-active-tab-{lado}">\n' + marca, 1)
    base = f'  <rect id="base" x="4" y="{2 * (W + 16) + 12}" width="48" height="2" {relleno(texto, 0.12)}/>\n'
    return s.replace("</svg>\n", base + "</svg>\n")


def svg_viewitem(colores: dict, radio: float) -> str:
    acento, texto = "ColorScheme-Highlight", "ColorScheme-Text"
    estados = {
        "normal": [(texto, 0.0, 0.0)],
        "hover": [(texto, 0.08, 0.0)],
        "selected": [(acento, 0.92, 0.0)],
        "selected+hover": [(acento, 1.0, 0.0)],
    }
    return svg_estados(colores, estados, radio, 2)


def svg_listitem(colores: dict, radio: float) -> str:
    acento, texto = "ColorScheme-Highlight", "ColorScheme-Text"
    estados = {
        "normal": [(texto, 0.0, 0.0)],
        "hover": [(texto, 0.08, 0.0)],
        "pressed": [(acento, 0.18, 0.0)],
        "section": [(texto, 0.04, 0.0)],
    }
    return svg_estados(colores, estados, radio, 4)


def svg_frame(colores: dict, radio: float) -> str:
    texto = "ColorScheme-Text"
    estados = {
        "plain": [(texto, 0.14, 0.0, 1)],
        "raised": [(texto, 0.04, 0.0), (texto, 0.14, 0.0, 1)],
        "sunken": [(texto, 0.18, 0.0, 1)],
    }
    return svg_estados(colores, estados, radio, 4)


def svg_toolbar(colores: dict) -> str:
    estados = {"": [("ColorScheme-Background", 0.0, 0.0)]}
    s = svg_estados(colores, {"toolbar": estados[""]}, 2, 4)
    return s.replace('id="toolbar-', 'id="')


def svg_glowbar(colores: dict) -> str:
    acento = "ColorScheme-Highlight"
    s = svg_estados(colores, {"glow": [(acento, 0.45, 0.0), (acento, 0.9, 2.0)]}, 6, None)
    return s.replace('id="glow-', 'id="')


def svg_slider(colores: dict) -> str:
    acento, texto = "ColorScheme-Highlight", "ColorScheme-Text"
    s = svg_estados(colores, {"groove": [(texto, 0.18, 0.0)], "groove-highlight": [(acento, 1.0, 0.0)]}, 3, None)
    extra = ""
    for i, orient in enumerate(("horizontal", "vertical")):
        y = 200 + i * 40
        extra += f'  <circle id="{orient}-slider-shadow" cx="24" cy="{y}" r="11" fill="#000" fill-opacity="0.18"/>\n'
        extra += f'  <g id="{orient}-slider-handle"><circle cx="64" cy="{y}" r="9" {relleno("ColorScheme-ButtonBackground", 1.0)}/><circle cx="64" cy="{y}" r="9" fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-width="1" class="{texto}"/></g>\n'
        extra += f'  <circle id="{orient}-slider-hover" cx="104" cy="{y}" r="9" {relleno(acento, 1.0)}/>\n'
        extra += f'  <circle id="{orient}-slider-focus" cx="144" cy="{y}" r="11" fill="none" stroke="currentColor" stroke-width="2" class="{acento}"/>\n'
    return s.replace("</svg>\n", extra + "</svg>\n").replace('height="', 'height="', 1)


# ---------------------------------------------------------------------------- paquete

def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    base = destino / "desktoptheme" / marca["id"]
    r = {k: v["$value"]["value"] for k, v in tokens["radio"].items() if isinstance(v, dict) and "$value" in v}
    ef = {k: v["$value"] for k, v in tokens.get("efectos", {}).items() if isinstance(v, dict) and "$value" in v}
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
        "[ContrastEffect]", "enabled=true", f"contrast={ef.get('contraste', 0.45)}", f"intensity={ef.get('intensidad', 1.0)}", f"saturation={ef.get('saturacion', 1.25)}", "",
        "[BlurBehindEffect]", "enabled=true", "",
        "[AdaptiveTransparency]", "enabled=true", ""]), hechos)
    op_panel, op_dialogo = ef.get("opacidad-panel", 0.58), ef.get("opacidad-dialogo", 0.72)
    textura = ef.get("textura", 0.07)
    # fondos de cristal (Plasma los usa cuando hay desenfoque) y fondos casi opacos (sin compositor)
    for carpeta, opacidad_p, opacidad_d in (("translucent", op_panel, op_dialogo), ("", 0.96, 0.97)):
        pref = base / carpeta if carpeta else base
        escribir(pref / "widgets" / "panel-background.svg", svg_fondo(colores, r["panel-flotante"], 8, opacidad_p, 16, 0.38, con_thick=True, textura=textura), hechos)
        escribir(pref / "dialogs" / "background.svg", svg_fondo(colores, r["ventana"], 12, opacidad_d, 32, 0.42), hechos)
        escribir(pref / "widgets" / "tooltip.svg", svg_fondo(colores, r["menu"], 8, opacidad_d, 14, 0.36), hechos)
        escribir(pref / "widgets" / "background.svg", svg_fondo(colores, r["ventana"], 12, opacidad_d, 14, 0.30), hechos)
        escribir(pref / "widgets" / "translucentbackground.svg", svg_fondo(colores, r["ventana"], 12, opacidad_d, 14, 0.30), hechos)
    # opaque/: sin compositor, lo mismo que los normales
    escribir(base / "opaque" / "widgets" / "panel-background.svg", svg_fondo(colores, r["panel-flotante"], 8, 1.0, 16, 0.38, con_thick=True, textura=textura), hechos)
    escribir(base / "opaque" / "dialogs" / "background.svg", svg_fondo(colores, r["ventana"], 12, 1.0, 32, 0.42), hechos)
    # widgets propios
    escribir(base / "widgets" / "tasks.svg", svg_tasks(colores, r["control"] + 2), hechos)
    escribir(base / "widgets" / "button.svg", svg_button(colores, r["control"]), hechos)
    escribir(base / "widgets" / "lineedit.svg", svg_lineedit(colores, r["control"]), hechos)
    escribir(base / "widgets" / "tabbar.svg", svg_tabbar(colores, r["control"]), hechos)
    escribir(base / "widgets" / "viewitem.svg", svg_viewitem(colores, r["control"]), hechos)
    escribir(base / "widgets" / "listitem.svg", svg_listitem(colores, r["control"]), hechos)
    escribir(base / "widgets" / "frame.svg", svg_frame(colores, r["control"]), hechos)
    escribir(base / "widgets" / "toolbar.svg", svg_toolbar(colores), hechos)
    escribir(base / "widgets" / "glowbar.svg", svg_glowbar(colores), hechos)
    escribir(base / "widgets" / "slider.svg", svg_slider(colores), hechos)
    return hechos
