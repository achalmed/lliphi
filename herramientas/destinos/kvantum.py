"""Tema de Kvantum de Lliphi, DERIVADO del de WhiteSur-kde (GPL-3.0): los widgets de las aplicaciones Qt con el
refinamiento de WhiteSur (menús y tooltips translúcidos, controles redondeados, barras finas) en los colores de Lliphi.

Se toma `Kvantum/WhiteSur/WhiteSurDark.{kvconfig,svg}` y `WhiteSur.{kvconfig,svg}`, se escriben las claves de color del
`.kvconfig` desde los tokens y se sustituyen los hex fijos del `.svg`. Lo derivado es GPL-3.0-or-later.
Se instala en `$XDG_CONFIG_HOME/Kvantum/<id>/` y se activa con `[General] theme=<id>` en `Kvantum/kvantum.kvconfig`
(`herramientas/instalar.py`), con `widgetStyle=kvantum-dark` / `kvantum` en el tema global.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import RAIZ, escribir, semanticos

BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "Kvantum" / "WhiteSur"
ORIGEN = {"oscuro": "WhiteSurDark", "claro": "WhiteSur"}

CLAVES = {  # clave del kvconfig → token
    "window.color": "fondo.ventana", "base.color": "fondo.vista", "alt.base.color": "fondo.vista-alterno",
    "button.color": "fondo.boton", "light.color": "fondo.ventana-alterno", "mid.color": "borde.separador",
    "dark.color": "fondo.vista", "highlight.color": "seleccion.fondo", "inactive.highlight.color": "acento.suave",
    "text.color": "texto.normal", "window.text.color": "texto.normal", "button.text.color": "texto.normal",
    "disabled.text.color": "texto.inactivo", "tooltip.base.color": "fondo.tooltip", "tooltip.text.color": "texto.tooltip",
    "highlight.text.color": "seleccion.texto", "link.color": "enlace", "visited.link.color": "visitado",
    "progress.indicator.text.color": "seleccion.texto",
}
HEX = {  # hex fijo del svg de WhiteSur → token (los demás se dejan)
    "oscuro": {"#315bef": "acento.base", "#5294e2": "acento.suave", "#a0b4f8": "acento.suave", "#242424": "fondo.vista",
               "#2d2d2d": "fondo.vista-alterno", "#656565": "fondo.boton", "#333333": "fondo.tooltip", "#dedede": "texto.normal",
               "#dfdfdf": "texto.normal", "#9d9d9d": "texto.inactivo", "#4f4f4f": "borde.separador", "#696969": "borde.separador",
               "#1b1b1b": "fondo.ventana", "#1a1a1a": "fondo.ventana"},
    # el acento de WhiteSur.svg (claro) es #0860f2 (47 usos: foco, selección, deslizadores), con #0e4bb4/#0852ce/#1352c4 como
    # tonos pulsados o de borde y #77aff1 como tono claro (mejora 2, decisiones 4.6); #315bef solo aparece una vez
    "claro": {"#0860f2": "acento.base", "#0e4bb4": "acento.texto", "#0852ce": "acento.texto", "#1352c4": "acento.texto",
              "#77aff1": "acento.suave",
              "#315bef": "acento.base", "#5294e2": "acento.suave", "#a0b4f8": "acento.suave", "#4285f4": "acento.base",
              "#333333": "texto.normal", "#666666": "texto.inactivo", "#f5f5f5": "fondo.ventana", "#ffffff": "fondo.vista",
              "#e5e5e5": "fondo.boton", "#d9d9d9": "borde.separador"},
}


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        id_ = marca["id_esquema"][variante]
        kv = (BASE / f"{ORIGEN[variante]}.kvconfig").read_text(encoding="utf-8")
        for clave, token in CLAVES.items():
            kv = re.sub(rf"^{re.escape(clave)}=.*$", f"{clave}={t[token]}", kv, flags=re.M)
        kv = kv.replace("[%General]", "[%General]\ncomment=Lliphi, derivado de WhiteSur-kde (GPL-3.0)", 1)
        svg = (BASE / f"{ORIGEN[variante]}.svg").read_text(encoding="utf-8", errors="ignore")
        mapa = {h: t[tok] for h, tok in HEX[variante].items()}
        svg = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), svg)
        escribir(destino / "kvantum" / id_ / f"{id_}.kvconfig", "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/WhiteSur-kde; no editar\n" + kv, hechos)
        escribir(destino / "kvantum" / id_ / f"{id_}.svg", svg, hechos)
    return hechos
