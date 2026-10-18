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


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    """Línea base del autor (2026-10-18): los esquemas de WhiteSur tal cual, renombrados. El esquema generado desde los
    tokens (`texto_esquema`) se conserva como `<Id>-tokens.colors` para la mejora siguiente (acento rojo)."""
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        id_ = marca["id_esquema"][variante]
        base = (BASE / ORIGEN[variante]).read_text(encoding="utf-8")
        base = re.sub(r"^ColorScheme=.*$", f"ColorScheme={id_}", base, flags=re.M)
        base = re.sub(r"^Name=.*$", f"Name={marca['nombre_esquema'][variante]}", base, flags=re.M)
        base = re.sub(r"^Name\[.*$\n?", "", base, flags=re.M)
        escribir(destino / "color-schemes" / f"{id_}.colors", "# GENERADO por herramientas/generar.py desde fuentes/base/WhiteSur-kde (GPL-3.0); no editar\n" + base, hechos)
        escribir(destino / "color-schemes" / f"{id_}-tokens.colors", texto_esquema(tokens, marca, variante).replace(f"ColorScheme={id_}", f"ColorScheme={id_}-tokens").replace(f"Name={marca['nombre_esquema'][variante]}", f"Name={marca['nombre_esquema'][variante]} (tokens)"), hechos)
    return hechos
