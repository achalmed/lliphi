"""Tema de interfaz de GIMP 3 y paletas de Lliphi (decisiones 5.21).

El tema, `themes/<nombre>/`, DERIVA del tema «Default» de GIMP 3.2 (GPL-3.0-or-later, `fuentes/base/GIMP-Default/`).
Ese tema ya es paramétrico: `gimp-light.css`, `gimp-gray.css` y `gimp-dark.css` definen diecisiete colores con nombre
(`@define-color bg-color …`) e importan `common-<luz>.css`, y todo lo demás (`common.css`) usa esos nombres. Aquí se
escriben los tres archivos de color desde los tokens (el claro con los de Lliphi Claro; el oscuro y el gris con los
de Lliphi Oscuro: Lliphi no tiene gris) y se copian los comunes tal cual, salvo dos cosas: la importación
`../System/gimp.css`, que fuera de la carpeta del sistema no existe y pasa a `system.css` (copia de la hoja del tema
«System» de GIMP), y los puntos de los separadores (`ui/*.svg`), que toman el gris de los tokens. Al final de cada
archivo de color va una capa de Lliphi: la fila elegida de listas y vistas (capas, canales, pinceles), el elemento del
menú bajo el ratón, las casillas, el progreso y los interruptores, en el acento de la variante, como en Kvantum. El
lienzo, las barras de valor de las opciones de herramienta (`GimpSpinScale`: en rojo entero, cada opacidad y cada tamaño
gritaban) y lo demás siguen neutros: GIMP los quiere grises para no sesgar la percepción del color.

Un solo tema con dos variantes, como hace GIMP 3 y como Kvantum (decisiones 4.19): con `(theme-color-scheme system)`
en `gimprc`, GIMP elige el claro o el oscuro según el escritorio y lo cambia en vivo.

Las paletas, `palettes/<nombre> Claro.gpl` y `<nombre> Oscuro.gpl` (formato «GIMP Palette», el mismo que leen
Inkscape, Krita y Xournal++), llevan los mismos colores que las de LibreOffice (`libreoffice.paleta`): neutros,
acento, estados y los dieciséis ANSI, sin repetidos, en filas de dieciséis.
"""
from __future__ import annotations

import re
from pathlib import Path

from nucleo import RAIZ, escribir, registro, semanticos

BASE = RAIZ / "fuentes" / "base" / "GIMP-Default"
CABECERA = "/* GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/GIMP-Default (complementos/gimp); no editar */\n"
LUZ = {"light": "claro", "gray": "oscuro", "dark": "oscuro"}       # archivo de GIMP → variante de Lliphi

# color con nombre de GIMP → token; ("mix", a, b, f) como mix() de GTK; ("alpha", a, f) como alpha()
COLORES = {
    "fg-color": "texto.normal", "bg-color": "fondo.ventana",
    "border-color": {"claro": "borde.sutil", "oscuro": "fondo.vista"},
    "dimmed-fg-color": "texto.secundario", "disabled-fg-color": "texto.inactivo",
    "disabled-button-color": ("mix", "texto.inactivo", "fondo.ventana", 0.4),
    "hover-color": {"claro": "fondo.vista", "oscuro": "fondo.boton"},
    "widget-bg-color": {"claro": "fondo.ventana-alterno", "oscuro": "fondo.vista-alterno"},
    "selected-color": {"claro": "fondo.vista", "oscuro": "fondo.vista"},
    "extreme-bg-color": {"claro": "fondo.vista", "oscuro": "fondo.vista"},
    "extreme-selected-color": {"claro": "fondo.ventana-alterno", "oscuro": "fondo.boton"},
    "strong-border-color": {"claro": "borde.separador", "oscuro": "borde.sutil"},
    "stronger-border-color": {"claro": "borde.separador", "oscuro": "borde.separador"},
    "edge-border-color": {"claro": "borde.separador", "oscuro": "fondo.vista"},
    "scrollbar-slider-color": "texto.inactivo",
    "scrollbar-trough-color": {"claro": "fondo.vista", "oscuro": "fondo.ventana"},
    "ruler-color": ("alpha", "borde.separador", 0.3),
}

# la capa de Lliphi: selectores de common.css cuyo fondo pasa al acento (texto encima: seleccion.texto)
SELECCION = ("treeview.view:selected", ".view:selected", ".view row:selected", "list row:selected", "iconview:selected",
             ".sidebar-row:selected", ".sidebar-row:selected *", "menuitem:hover", "menuitem:selected", "popover list row:selected")


def _valor(s: dict[str, str], variante: str, v) -> str:
    if isinstance(v, dict):
        return s[v[variante]]
    if isinstance(v, tuple) and v[0] == "mix":
        return f"mix({s[v[1]]}, {s[v[2]]}, {v[3]})"
    if isinstance(v, tuple) and v[0] == "alpha":
        return f"alpha({s[v[1]]}, {v[2]})"
    return s[v]


def resueltos(tokens: dict, variante: str) -> dict[str, str]:
    """{color de GIMP: hex} sin las mezclas (para las pruebas de contraste)."""
    s = semanticos(tokens, variante)
    return {n: _valor(s, variante, v) for n, v in COLORES.items() if not isinstance(v, tuple)}


def texto_color(tokens: dict, marca: dict, archivo: str) -> str:
    """`gimp-<archivo>.css`: los colores con nombre, la importación de los comunes y la capa del acento."""
    variante = LUZ[archivo]
    s = semanticos(tokens, variante)
    comun = "common-light.css" if archivo == "light" else "common-dark.css"
    lineas = [CABECERA.rstrip("\n"),
              f"/* {marca['nombre']} para GIMP 3, variante «{archivo}» con los colores de {marca['nombre_esquema'][variante]}; deriva del tema",
              "   Default de GIMP 3.2 (GPL-3.0-or-later). Se elige en Preferencias → Interfaz → Tema. */", ""]
    ancho = max(map(len, COLORES))
    lineas += [f"@define-color {n.ljust(ancho)} {_valor(s, variante, v)};" for n, v in COLORES.items()]
    lineas += ["", f'@import url("{comun}");', "", f"/* {marca['nombre']}: lo elegido, en el acento de la variante */",
               ",\n".join(SELECCION) + " {",
               f"  background-color: {s['seleccion.fondo']};", f"  color: {s['seleccion.texto']};", "}",
               "progressbar trough progress, switch:checked, scale contents trough highlight {",
               f"  background-color: {s['acento.base']};", "}",
               "checkbutton check:checked, radiobutton radio:checked {",
               f"  background-color: {s['acento.base']};", f"  color: {s['seleccion.texto']};", f"  border-color: {s['acento.base']};", "}"]
    return "\n".join(lineas) + "\n"


def svg(texto: str, color: str) -> str:
    """Un separador de GIMP con el color de sus puntos de los tokens y sin los colores de la página de Inkscape."""
    texto = re.sub(r'\s(?:pagecolor|bordercolor|inkscape:deskcolor)="#[0-9a-fA-F]{6}"', "", texto)
    return re.sub(r"stop-color:#[0-9a-fA-F]{6}", f"stop-color:{color}", texto)


def texto_gpl(tokens: dict, nombre: str, variante: str) -> str:
    colores = registro.codigo("libreoffice").paleta(tokens, variante)
    lineas = ["GIMP Palette", f"Name: {nombre}", "Columns: 16", "# GENERADO por herramientas/generar.py desde tokens/; no editar"]
    for etiqueta, h in colores:
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
        lineas.append(f"{r:3d} {g:3d} {b:3d}\t{etiqueta}")
    return "\n".join(lineas) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    tema = destino / "themes" / marca["nombre"]
    for archivo in LUZ:
        escribir(tema / f"gimp-{archivo}.css", texto_color(tokens, marca, archivo), hechos)
    for comun in ("common.css", "common-dark.css", "common-light.css"):
        texto = (BASE / comun).read_text(encoding="utf-8").replace('@import url("../System/gimp.css");', '@import url("system.css");')
        escribir(tema / comun, texto, hechos)
    escribir(tema / "system.css", (BASE / "system.css").read_text(encoding="utf-8"), hechos)
    for f in sorted((BASE / "ui").glob("*.svg")):
        variante = "oscuro" if f.stem.endswith("-dark") else "claro"
        escribir(tema / "ui" / f.name, svg(f.read_text(encoding="utf-8"), semanticos(tokens, variante)["texto.inactivo"]), hechos)
    for variante in ("claro", "oscuro"):
        nombre = marca["nombre_esquema"][variante]
        escribir(destino / "palettes" / f"{nombre}.gpl", texto_gpl(tokens, nombre, variante), hechos)
    return hechos
