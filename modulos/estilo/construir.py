"""Estilo de Plasma de Lliphi, DERIVADO de WhiteSur-kde (Vince Liuice, GPL-3.0; `fuentes/base/WhiteSur-kde`).

Decisión del autor (2026-10-18, docs/decisiones.md 3.11): no dibujar desde cero; tomar el estilo de Plasma de WhiteSur
(vidrio, radios, sombras, 38 SVG pulidos), quitarle lo que imita a Apple y recolorearlo con los tokens de Lliphi.
Qué se hace con la base:

- `colors` se retira: el estilo sigue el esquema de color del sistema (y el acento del usuario) en vez de la paleta
  fija de WhiteSur; los SVG de WhiteSur ya usan el `current-color-scheme` de Plasma para texto y fondos.
- Los hex fijos que quedan en los SVG (el negro translúcido del panel, los grises de los botones, el azul de Google
  de los indicadores) se sustituyen por los tokens de la variante.
- `metadata.json` y `plasmarc` son de Lliphi (desenfoque y contraste activos; fondo de Lliphi).
- Dos variantes porque la base las tiene: `lliphi-oscuro` ← WhiteSur-dark, `lliphi-claro` ← WhiteSur.
- Dock de Lliphi (mejora 11, `ajustes.json`): el fondo de paneles del oscuro más opaco, en el gris de la ventana y sin la
  sombra de WhiteSur (el negro al 45 % se veía gris lavado con el desenfoque; la sombra, como manchas en las puntas del
  dock); los mosaicos del gestor de tareas
  (`widgets/tasks.svg`) y el marco de los escritorios del paginador (`widgets/pager.svg`) los dibuja Lliphi: un fondito
  claro tras cada aplicación abierta, la activa con un mosaico teñido del acento y su marca, y el paginador con una línea
  fina arriba (en el acento, el escritorio activo). Usan las clases `ColorScheme-*` de Plasma: siguen el acento.
Lo derivado es GPL-3.0-or-later (REUSE.toml).
"""
from __future__ import annotations

import gzip
import json
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

from nucleo import RAIZ, VERSION, aplanar, autores, escribir, registro, rgb, semanticos

con_acento = registro.codigo("esquema").con_acento   # dependencia de construcción declarada en modulo.json

BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "plasma" / "desktoptheme"
ORIGEN = {"oscuro": "WhiteSur-dark", "claro": "WhiteSur"}

# hex fijo de WhiteSur → token semántico de Lliphi (los colores de marcador de Plasma —magenta, cian, verde, naranja—
# y los del stylesheet de Breeze no se tocan: Plasma los sustituye o los ignora)
MAPA = {"oscuro": {}, "claro": {}}   # línea base del autor: WhiteSur tal cual, sin recolorear (salvo el acento de `colors`)


AJUSTES = Path(__file__).resolve().parent / "ajustes.json"
SVG = "http://www.w3.org/2000/svg"
ESTILO_COLORES = """
.ColorScheme-Text { color:#232629; }
.ColorScheme-Highlight { color:#3daee9; }
.ColorScheme-ViewFocus { color:#3daee9; }
.ColorScheme-NeutralText { color:#f67400; }
.ColorScheme-PositiveText { color:#27ae60; }
"""


def ajustes() -> dict:
    return json.loads(AJUSTES.read_text(encoding="utf-8"))


def _pieza(id_: str, x: float, y: float, w: float, h: float, cuerpo: str) -> str:
    """Un elemento de marco: un rectángulo invisible que fija sus límites y lo que se ve dentro."""
    return (f'<g id="{id_}"><rect x="{x}" y="{y}" width="{w}" height="{h}" style="fill:none"/>{cuerpo}</g>')


def _forma(clase: str, opacidad: float, d: str) -> str:
    return f'<path class="ColorScheme-{clase}" fill="currentColor" style="opacity:{opacidad}" d="{d}"/>'


def tareas_svg(base: str, aj: dict) -> str:
    """`widgets/tasks.svg` de Lliphi: conserva de la base de WhiteSur lo que no es un estado (las flechas de grupo y las
    pistas de márgenes) y dibuja cada estado en tres piezas (arriba, centro, abajo; 64 px de ancho, como WhiteSur):
    un mosaico redondeado opcional y una marca centrada abajo."""
    ET.register_namespace("", SVG)
    raiz = ET.fromstring(base)
    estados = aj["estados"]
    quitar = {f"{e}-{p}" for e in list(estados) + ["normal", "focus", "hover", "minimized", "progress", "attention"]
              for p in ("top", "center", "bottom")}
    for padre in list(raiz.iter()):
        for hijo in list(padre):
            if hijo.get("id") in quitar:
                padre.remove(hijo)
    texto = ET.tostring(raiz, encoding="unicode")
    r = aj["radio"]
    piezas = []
    for i, (estado, d) in enumerate(estados.items()):
        x = 1000 + i * 90
        top, cen, bot = "", "", ""
        if d.get("fondo"):
            clase, op = d["fondo"]
            top = _forma(clase, op, f"M {x + 1},{12} V {r} A {r},{r} 0 0 1 {x + 1 + r},0 H {x + 63 - r} A {r},{r} 0 0 1 {x + 63},{r} V 12 Z")
            cen = _forma(clase, op, f"M {x + 1},20 H {x + 63} V 52 H {x + 1} Z")
            bot = _forma(clase, op, f"M {x + 1},60 V {72 - r} A {r},{r} 0 0 0 {x + 1 + r},72 H {x + 63 - r} A {r},{r} 0 0 0 {x + 63},{72 - r} V 60 Z")
        if d.get("marca"):
            clase, ancho, op = d["marca"]
            bot += (f'<rect class="ColorScheme-{clase}" fill="currentColor" style="opacity:{op}" x="{x + 32 - ancho / 2}" '
                    f'y="{60 + 7}" width="{ancho}" height="3" rx="1.5" ry="1.5"/>')
        piezas += [_pieza(f"{estado}-top", x, 0, 64, 12, top), _pieza(f"{estado}-center", x, 20, 64, 32, cen),
                   _pieza(f"{estado}-bottom", x, 60, 64, 12, bot)]
    return texto.replace("</svg>", "".join(piezas) + "</svg>")


def paginador_svg(aj: dict) -> str:
    """`widgets/pager.svg` de Lliphi: cada estado es un marco de nueve piezas (esquinas de 3 px) con una línea de 2 px
    arriba, a lo ancho, y un fondo opcional; el número del escritorio lo pone el paginador encima."""
    piezas = []
    for i, (estado, d) in enumerate(aj["estados"].items()):
        x0, y0 = 10 + i * 45, 10
        linea_c, linea_o = d["linea"]
        fondo = d.get("fondo")
        def caja(nombre, x, y, w, h, con_linea):
            cuerpo = ""
            if fondo:
                cuerpo += f'<rect class="ColorScheme-{fondo[0]}" fill="currentColor" style="opacity:{fondo[1]}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
            if con_linea:
                cuerpo += (f'<rect class="ColorScheme-{linea_c}" fill="currentColor" style="opacity:{linea_o}" x="{x}" '
                           f'y="{y + aj.get("separacion", 0)}" width="{w}" height="2"/>')
            return _pieza(f"{estado}-{nombre}", x, y, w, h, cuerpo)
        c, m = aj.get("separacion", 0) + 3, 24   # la línea baja «separacion» px: queda cerca del número
        # la línea va solo en la pieza de arriba, no en las esquinas: entre dos escritorios queda un hueco de 6 px
        piezas += [caja("topleft", x0, y0, c, c, False), caja("top", x0 + c, y0, m, c, True), caja("topright", x0 + c + m, y0, c, c, False),
                   caja("left", x0, y0 + c, c, m, False), caja("center", x0 + c, y0 + c, m, m, False),
                   caja("right", x0 + c + m, y0 + c, c, m, False), caja("bottomleft", x0, y0 + c + m, c, c, False),
                   caja("bottom", x0 + c, y0 + c + m, m, c, False), caja("bottomright", x0 + c + m, y0 + c + m, c, c, False)]
    return (f'<svg xmlns="{SVG}" width="140" height="70" viewBox="0 0 140 70">'
            f'<style id="current-color-scheme" type="text/css">{ESTILO_COLORES}</style>{"".join(piezas)}</svg>\n')


def panel(texto: str, t: dict[str, str], aj: dict | None) -> str:
    """El fondo de paneles: el negro al 45 % de WhiteSur pasa al relleno y la opacidad de los ajustes."""
    if not aj:
        return texto
    texto = texto.replace("opacity:0.45;fill:#000000", f"opacity:{aj['opacidad']};fill:{t[aj['relleno']]}")
    if aj.get("sombra", True):
        return texto
    # sin sombra: fuera los elementos `shadow-*` (Plasma no dibuja la que falta); en las puntas del dock flotante la
    # sombra de WhiteSur se veía como dos manchas oscuras (pedido del autor, 2026-11-01)
    ET.register_namespace("", SVG)
    for prefijo, uri in (("inkscape", "http://www.inkscape.org/namespaces/inkscape"),
                         ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"),
                         ("xlink", "http://www.w3.org/1999/xlink")):
        ET.register_namespace(prefijo, uri)
    raiz = ET.fromstring(texto)
    for padre in list(raiz.iter()):
        for hijo in list(padre):
            if (hijo.get("id") or "").startswith("shadow-"):
                padre.remove(hijo)
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + ET.tostring(raiz, encoding="unicode") + "\n"


def propio(rel: str, texto: str, t: dict[str, str], aj: dict, variante: str, tokens: dict | None = None) -> str:
    """Lo que Lliphi cambia de un SVG de la base: el fondo de paneles, los mosaicos de tareas y el paginador."""
    if rel == "widgets/panel-background.svg":
        ajp = aj["panel"].get(variante)
        if ajp and ajp.get("de") and tokens is not None:   # el claro conserva el panel oscuro (decisiones 4.16)
            t = semanticos(tokens, ajp["de"])
        return panel(texto, t, ajp)
    if rel == "widgets/tasks.svg":
        return tareas_svg(texto, aj["tareas"])
    if rel == "widgets/pager.svg":
        return paginador_svg(aj["paginador"])
    return texto


def recolorear(texto: str, mapa: dict[str, str]) -> str:
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), texto)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    aj = ajustes()
    ef = {k: v["$value"] for k, v in tokens.get("efectos", {}).items() if isinstance(v, dict) and "$value" in v}
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        mapa = {h: t[tok] for h, tok in MAPA[variante].items()}
        id_ = f"{marca['id']}-{variante}"
        base = destino / id_
        origen = BASE / ORIGEN[variante]
        for f in sorted(origen.rglob("*")):
            if not f.is_file() or f.name in ("plasmarc", "metadata.json", "metadata.desktop"):
                continue
            rel = f.relative_to(origen)
            if f.suffix == ".svgz":
                texto = gzip.open(f).read().decode("utf-8", errors="ignore")
                rel = rel.with_suffix(".svg")   # sin comprimir: diff legible
                escribir(base / rel, propio(str(rel), recolorear(texto, mapa), t, aj, variante, tokens), hechos)
            elif f.name == "colors":
                # mejora 8 (decisiones 4.13): el `colors` de WhiteSur con solo el acento de la variante (rojo en el
                # oscuro, azul de WhiteSur en el claro), igual que el esquema de la mejora 1; lo demás, byte a byte
                trgb = {k: rgb(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}
                escribir(base / rel, con_acento(f.read_text(encoding="utf-8"), trgb), hechos)
            elif f.suffix == ".svg":
                texto = recolorear(f.read_text(encoding="utf-8", errors="ignore"), mapa)
                escribir(base / rel, propio(str(rel), texto, t, aj, variante, tokens), hechos)
            else:
                (base / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, base / rel); hechos.append(base / rel)
        escribir(base / "metadata.json", json.dumps({
            "KPlugin": {"Authors": autores(marca) + [{"Name": "Vince Liuice (WhiteSur-kde, base GPL-3.0)", "Email": ""}],
                        "Category": "", "Description": f"{marca['descripcion']} Derivado del estilo de Plasma WhiteSur-kde.",
                        "EnabledByDefault": True, "Id": id_, "License": "GPL-3.0-or-later",
                        "Name": marca["nombre_esquema"][variante], "Version": VERSION, "Website": marca["sitio"]},
            "X-Plasma-API": "5.0"}, ensure_ascii=False, indent=4) + "\n", hechos)
        escribir(base / "plasmarc", "\n".join([
            "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/WhiteSur-kde; no editar", "",
            "[Settings]", "FallbackTheme=default", "",
            "[Wallpaper]", f"defaultWallpaperTheme={marca['id_fondo']}", "defaultFileSuffix=.png", "defaultWidth=1920", "defaultHeight=1080", "",
            "[ContrastEffect]", "enabled=true", f"contrast={ef.get('contraste', 0.35)}", f"intensity={ef.get('intensidad', 1.0)}", f"saturation={ef.get('saturacion', 1.15)}", "",
            "[BlurBehindEffect]", "enabled=true", "",
            "[AdaptiveTransparency]", "enabled=true", ""]), hechos)
    return hechos


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: el estilo de Plasma de la variante."""
    return {"plasmarc][Theme": {"name": f"{marca['id']}-{variante}"}}
