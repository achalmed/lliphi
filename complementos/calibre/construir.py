"""Calibre con Lliphi (decisiones 5.22): la biblioteca y el visor de libros, en las dos variantes.

Calibre no usa Kvantum: en Linux pinta con su propio estilo (`ui_style` «calibre», sobre Fusion) y su propia paleta,
salvo con `CALIBRE_USE_SYSTEM_THEME=1`. Con `color_palette` en «system» (lo que trae por omisión) sigue al esquema
claro u oscuro del escritorio, en vivo; y desde la 7 admite paletas con nombre para cada modo, que se guardan en
`gui.json` (`light_palette_name`, `light_palettes`, `dark_palette_name`, `dark_palettes`; cada paleta, un diccionario
rol de `QPalette` → color, con `<rol>-disabled` para el grupo inactivo: `calibre.gui2.palette.palette_from_dict` de
Calibre 9.17). Aquí se escriben las dos paletas de Lliphi con la misma lógica que Kvantum y el esquema.

El visor (`ebook-viewer`) tiene esquemas de color propios (`viewer-webengine.json` → `session_data`): su «Sistema»
toma el fondo, el texto y los enlaces de la paleta de Calibre (`system_colors()`: `Base`, `Text`, `Link`), así que con
las paletas de Lliphi ya sigue a la variante. Además se añaden dos esquemas fijos, «Lliphi Claro» y «Lliphi Oscuro»
(`user_color_schemes`, clave `*<nombre>`, con `foreground`, `background` y `link`), para leer en una variante distinta
de la del escritorio.

Lo generado son dos fragmentos JSON (`gui-<id>.json`, `visor-<id>.json`) que `aplicar.py` funde, con Calibre cerrado,
en los archivos de preferencias de la interfaz. La base de datos de la biblioteca (`metadata.db`) no se toca nunca.
"""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import escribir, semanticos

# rol de QPalette → token; por variante donde el claro y el oscuro difieren (las etiquetas, como Kvantum: decisiones 4.34)
ROLES = {
    "Window": "fondo.ventana", "WindowText": "texto.normal", "Base": "fondo.vista", "AlternateBase": "fondo.vista-alterno",
    "ToolTipBase": {"claro": "fondo.ventana", "oscuro": "fondo.tooltip"},
    "ToolTipText": {"claro": "texto.normal", "oscuro": "texto.tooltip"},
    "PlaceholderText": "texto.inactivo", "Text": "texto.normal", "Button": "fondo.boton", "ButtonText": "texto.normal",
    "BrightText": "texto.sobre-acento", "Highlight": "seleccion.fondo", "HighlightedText": "seleccion.texto",
    "Accent": "acento.base", "Link": "enlace", "LinkVisited": "visitado",
    # grupo inactivo (Calibre lo lee como <rol>-disabled)
    "WindowText-disabled": "texto.inactivo", "Text-disabled": "texto.inactivo", "ButtonText-disabled": "texto.inactivo",
    "Highlight-disabled": "fondo.ventana-alterno", "HighlightedText-disabled": "texto.inactivo",
}
PARES = (("WindowText", "Window"), ("Text", "Base"), ("Text", "AlternateBase"), ("ButtonText", "Button"),
         ("HighlightedText", "Highlight"), ("ToolTipText", "ToolTipBase"), ("Link", "Base"))


def paleta(tokens: dict, variante: str) -> dict[str, str]:
    s = semanticos(tokens, variante)
    return {rol: s[t[variante] if isinstance(t, dict) else t] for rol, t in ROLES.items()}


def preferencias_gui(tokens: dict, marca: dict) -> dict:
    """Las claves de `gui.json` que pone Lliphi (lo demás del archivo no se toca)."""
    claro, oscuro = marca["nombre_esquema"]["claro"], marca["nombre_esquema"]["oscuro"]
    return {"color_palette": "system",
            "light_palette_name": claro, "light_palettes": {claro: paleta(tokens, "claro")},
            "dark_palette_name": oscuro, "dark_palettes": {oscuro: paleta(tokens, "oscuro")}}


def esquemas_visor(tokens: dict, marca: dict) -> dict:
    """`user_color_schemes` del visor: los dos esquemas fijos de Lliphi."""
    salida = {}
    for v in ("claro", "oscuro"):
        s, nombre = semanticos(tokens, v), marca["nombre_esquema"][v]
        salida[f"*{nombre}"] = {"name": nombre, "foreground": s["texto.normal"], "background": s["fondo.vista"], "link": s["enlace"]}
    return salida


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    nota = "GENERADO por herramientas/generar.py desde tokens/ (complementos/calibre); no editar"
    escribir(destino / f"gui-{marca['id']}.json",
             json.dumps({"_nota": nota, **preferencias_gui(tokens, marca)}, ensure_ascii=False, indent=2) + "\n", hechos)
    escribir(destino / f"visor-{marca['id']}.json",
             json.dumps({"_nota": nota, "user_color_schemes": esquemas_visor(tokens, marca)}, ensure_ascii=False, indent=2) + "\n", hechos)
    return hechos
