"""Esquemas de color de Plasma (`.colors`), uno por variante.

Formato de KColorScheme: grupos `[Colors:View|Window|Button|Selection|Tooltip|Complementary|Header]`
(+ `[Colors:Header][Inactive]`) con doce claves `R,G,B`, más `[ColorEffects:*]`, `[General]`, `[KDE]` y
`[WM]` (Calibre 10530, 10525; `/usr/share/color-schemes/BreezeDark.colors`)."""
from __future__ import annotations

from pathlib import Path

import re

from . import CABECERA_INI, RAIZ, aplanar, escribir, rgb


def grupos(t: dict[str, str]) -> dict[str, dict[str, str]]:
    estados = {"ForegroundNegative": t["estado.error"], "ForegroundNeutral": t["estado.advertencia"],
               "ForegroundPositive": t["estado.exito"]}
    base = {"ForegroundNormal": t["texto.normal"], "ForegroundInactive": t["texto.inactivo"],
            "ForegroundActive": t["acento.texto"], "ForegroundLink": t["enlace"], "ForegroundVisited": t["visitado"],
            "DecorationFocus": t["foco"], "DecorationHover": t["hover"], **estados}
    sobre_acento = {k: t["seleccion.texto"] for k in ("ForegroundNormal", "ForegroundInactive", "ForegroundActive",
                                                      "ForegroundLink", "ForegroundVisited")}
    inverso = {"ForegroundActive": t["acento.suave"], "ForegroundLink": t["acento.suave"],
               "DecorationFocus": t["acento.suave"], "DecorationHover": t["acento.suave"], **estados}
    return {
        "Colors:Window": {"BackgroundNormal": t["fondo.ventana"], "BackgroundAlternate": t["fondo.ventana-alterno"], **base},
        "Colors:View": {"BackgroundNormal": t["fondo.vista"], "BackgroundAlternate": t["fondo.vista-alterno"], **base},
        "Colors:Button": {"BackgroundNormal": t["fondo.boton"], "BackgroundAlternate": t["fondo.ventana"], **base},
        "Colors:Selection": {"BackgroundNormal": t["seleccion.fondo"], "BackgroundAlternate": t["acento.suave"],
                             **sobre_acento, "DecorationFocus": t["foco"], "DecorationHover": t["hover"], **estados},
        "Colors:Tooltip": {"BackgroundNormal": t["fondo.tooltip"], "BackgroundAlternate": t["fondo.tooltip"],
                           "ForegroundNormal": t["texto.tooltip"], "ForegroundInactive": t["texto.tooltip"],
                           "ForegroundVisited": t["texto.tooltip"], **inverso},
        "Colors:Complementary": {"BackgroundNormal": t["fondo.complementario"], "BackgroundAlternate": t["fondo.complementario"],
                                 "ForegroundNormal": t["texto.complementario"], "ForegroundInactive": t["texto.complementario"],
                                 "ForegroundVisited": t["texto.complementario"], **inverso},
        "Colors:Header": {"BackgroundNormal": t["fondo.encabezado"], "BackgroundAlternate": t["fondo.ventana-alterno"], **base},
        "Colors:Header][Inactive": {"BackgroundNormal": t["fondo.ventana"], "BackgroundAlternate": t["fondo.ventana-alterno"],
                                    **base, "ForegroundNormal": t["texto.inactivo"]},
    }


def texto_esquema(tokens: dict, marca: dict, variante: str, con_efectos: bool = True) -> str:
    t = {k: rgb(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}
    g = grupos(t)
    lineas = [CABECERA_INI]
    if con_efectos:
        lineas += ["[ColorEffects:Disabled]", "Color=56,56,56", "ColorAmount=0", "ColorEffect=0", "ContrastAmount=0.65",
                   "ContrastEffect=1", "IntensityAmount=0.1", "IntensityEffect=2", "",
                   "[ColorEffects:Inactive]", "ChangeSelectionColor=true", "Color=112,111,110", "ColorAmount=0.025",
                   "ColorEffect=2", "ContrastAmount=0.1", "ContrastEffect=2", "Enable=false", "IntensityAmount=0",
                   "IntensityEffect=0", ""]
    for nombre in ("Colors:Button", "Colors:Complementary", "Colors:Header", "Colors:Header][Inactive",
                   "Colors:Selection", "Colors:Tooltip", "Colors:View", "Colors:Window"):
        lineas.append(f"[{nombre}]")
        lineas += [f"{k}={v}" for k, v in sorted(g[nombre].items())]
        lineas.append("")
    lineas += ["[General]", f"ColorScheme={marca['id_esquema'][variante]}", f"Name={marca['nombre_esquema'][variante]}",
               "shadeSortColumn=true", "", "[KDE]", "contrast=4", ""]
    lineas += ["[WM]", f"activeBackground={t['fondo.encabezado']}", f"activeBlend={t['fondo.encabezado']}",
               f"activeForeground={t['texto.normal']}", f"inactiveBackground={t['fondo.ventana']}",
               f"inactiveBlend={t['fondo.ventana']}", f"inactiveForeground={t['texto.inactivo']}", ""]
    return "\n".join(lineas)


BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "color-schemes"
ORIGEN = {"oscuro": "WhiteSurDark.colors", "claro": "WhiteSur.colors"}

# Mejora 1 sobre la línea base (docs/linea-base.md §2.1): el acento azul de WhiteSur se sustituye por el rojo de los
# tokens y todo lo demás se copia byte a byte. Estos son los azules que WhiteSur-kde usa como acento en sus dos esquemas
# (base 49,91,239; claro 79/74,124-127,239; sobre selección 127-135,152-163,239; hover 83,143,255 y 30,146,255;
# ForegroundActive 61,174,230-233; enlace de Breeze 41,128,185). Un valor que no esté aquí no se toca.
AZULES_WHITESUR = frozenset({"49,91,239", "79,127,239", "74,124,239", "130,156,239", "135,163,239", "128,152,239",
                             "127,160,239", "83,143,255", "30,146,255", "61,174,230", "61,174,233", "41,128,185"})
# clave → token semántico que cumple la misma función; en Colors:Selection el texto va «sobre acento»
TOKEN_POR_CLAVE = {"DecorationFocus": "foco", "DecorationHover": "hover", "ForegroundLink": "enlace",
                   "ForegroundActive": "acento.texto", "ForegroundVisited": "acento.suave"}
TOKEN_EN_SELECCION = {"BackgroundNormal": "seleccion.fondo", "BackgroundAlternate": "acento.suave",
                      "ForegroundInactive": "seleccion.texto", "ForegroundVisited": "seleccion.texto",
                      "ForegroundLink": "seleccion.texto", "DecorationHover": "hover", "DecorationFocus": "foco"}
_LINEA = re.compile(r"^(\w+)=(\d{1,3},\d{1,3},\d{1,3})((?:,\d{1,3})?)$")


def token_de(grupo: str, clave: str, valor: str) -> str | None:
    """Nombre del token que sustituye a `clave=valor` en `grupo`, o None si el valor se copia tal cual.
    Se sustituye si el valor es un azul de WhiteSur, y además `ForegroundLink` en la selección (amarillo en WhiteSur)."""
    if grupo == "Colors:Selection":
        if clave in TOKEN_EN_SELECCION and (valor in AZULES_WHITESUR or clave == "ForegroundLink"):
            return TOKEN_EN_SELECCION[clave]
        return None
    if clave in TOKEN_POR_CLAVE and valor in AZULES_WHITESUR:
        return TOKEN_POR_CLAVE[clave]
    return None


def con_acento(base: str, t: dict[str, str]) -> str:
    """El texto de un esquema de WhiteSur con sus azules sustituidos por los tokens (`t`: token semántico → R,G,B);
    se conserva el alfa (`R,G,B,A`) cuando lo hay."""
    salida, grupo = [], ""
    for linea in base.splitlines():
        if linea.startswith("[") and linea.endswith("]"):
            grupo = linea[1:-1]
        elif grupo.startswith("Colors:") and (m := _LINEA.match(linea)):
            clave, valor, alfa = m.groups()
            if (nombre := token_de(grupo, clave, valor)) is not None:
                linea = f"{clave}={t[nombre]}{alfa}"
        salida.append(linea)
    return "\n".join(salida) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    """Línea base del autor (2026-10-18, decisiones 4.4) más la mejora 1 (4.5): los esquemas de WhiteSur renombrados y
    con solo el acento (foco, hover, enlace, selección) tomado de los tokens. El esquema generado por entero desde los
    tokens (`texto_esquema`) se conserva como `<Id>-tokens.colors`."""
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        id_ = marca["id_esquema"][variante]
        t = {k: rgb(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}
        base = (BASE / ORIGEN[variante]).read_text(encoding="utf-8")
        base = re.sub(r"^ColorScheme=.*$", f"ColorScheme={id_}", base, flags=re.M)
        base = re.sub(r"^Name=.*$", f"Name={marca['nombre_esquema'][variante]}", base, flags=re.M)
        base = re.sub(r"^Name\[.*$\n?", "", base, flags=re.M)
        escribir(destino / "color-schemes" / f"{id_}.colors",
                 "# GENERADO por herramientas/generar.py desde fuentes/base/WhiteSur-kde (GPL-3.0) con el acento de tokens/; no editar\n"
                 + con_acento(base, t), hechos)
        escribir(destino / "color-schemes" / f"{id_}-tokens.colors", texto_esquema(tokens, marca, variante).replace(f"ColorScheme={id_}", f"ColorScheme={id_}-tokens").replace(f"Name={marca['nombre_esquema'][variante]}", f"Name={marca['nombre_esquema'][variante]} (tokens)"), hechos)
    return hechos
