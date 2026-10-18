#!/usr/bin/env python3
"""Genera los esquemas de color de Plasma (`.colors`) desde `tokens/tokens.json`.

Un esquema por variante (claro y oscuro). El formato es el de KColorScheme: grupos
`[Colors:View|Window|Button|Selection|Tooltip|Complementary|Header]` (+ `[Colors:Header][Inactive]`)
con doce claves `R,G,B`, más `[ColorEffects:*]`, `[General]`, `[KDE]` y `[WM]` (fuentes: Calibre 10530,
10525; `/usr/share/color-schemes/BreezeDark.colors`).

Uso:  .venv/bin/python herramientas/generar_esquema.py            # simula: muestra qué escribiría
      .venv/bin/python herramientas/generar_esquema.py --aplicar  # escribe generado/color-schemes/<Id><Variante>.colors
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOKENS = RAIZ / "tokens" / "tokens.json"
MARCA = RAIZ / "tokens" / "marca.json"
SALIDA = RAIZ / "generado" / "color-schemes"

CABECERA = "# GENERADO por herramientas/generar_esquema.py desde tokens/tokens.json; no editar\n"


def cargar() -> tuple[dict, dict]:
    return json.loads(TOKENS.read_text(encoding="utf-8")), json.loads(MARCA.read_text(encoding="utf-8"))


def rgb(token: dict) -> str:
    h = token["$value"]["hex"].lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def aplanar(grupo: dict, prefijo: str = "") -> dict[str, dict]:
    plano = {}
    for k, v in grupo.items():
        if isinstance(v, dict) and "$value" in v:
            plano[prefijo + k] = v
        elif isinstance(v, dict):
            plano.update(aplanar(v, prefijo + k + "."))
    return plano


def grupos(t: dict[str, str], variante: str) -> dict[str, dict[str, str]]:
    """t: token semántico → 'R,G,B'. Devuelve cada grupo del esquema con sus doce claves."""
    estados = {
        "ForegroundNegative": t["estado.error"], "ForegroundNeutral": t["estado.advertencia"],
        "ForegroundPositive": t["estado.exito"],
    }
    base = {
        "ForegroundNormal": t["texto.normal"], "ForegroundInactive": t["texto.inactivo"],
        "ForegroundActive": t["acento.texto"], "ForegroundLink": t["enlace"], "ForegroundVisited": t["visitado"],
        "DecorationFocus": t["foco"], "DecorationHover": t["hover"], **estados,
    }
    sobre_acento = {k: t["seleccion.texto"] for k in ("ForegroundNormal", "ForegroundInactive", "ForegroundActive",
                                                      "ForegroundLink", "ForegroundVisited")}
    return {
        "Colors:Window": {"BackgroundNormal": t["fondo.ventana"], "BackgroundAlternate": t["fondo.ventana-alterno"], **base},
        "Colors:View": {"BackgroundNormal": t["fondo.vista"], "BackgroundAlternate": t["fondo.vista-alterno"], **base},
        "Colors:Button": {"BackgroundNormal": t["fondo.boton"], "BackgroundAlternate": t["fondo.ventana"], **base},
        "Colors:Selection": {"BackgroundNormal": t["seleccion.fondo"], "BackgroundAlternate": t["acento.suave"],
                             **sobre_acento, "DecorationFocus": t["foco"], "DecorationHover": t["hover"], **estados},
        "Colors:Tooltip": {"BackgroundNormal": t["fondo.tooltip"], "BackgroundAlternate": t["fondo.tooltip"],
                           "ForegroundNormal": t["texto.tooltip"], "ForegroundInactive": t["texto.tooltip"],
                           "ForegroundActive": t["acento.suave"], "ForegroundLink": t["acento.suave"],
                           "ForegroundVisited": t["texto.tooltip"], "DecorationFocus": t["acento.suave"],
                           "DecorationHover": t["acento.suave"], **estados},
        "Colors:Complementary": {"BackgroundNormal": t["fondo.complementario"], "BackgroundAlternate": t["fondo.complementario"],
                                 "ForegroundNormal": t["texto.complementario"], "ForegroundInactive": t["texto.complementario"],
                                 "ForegroundActive": t["acento.suave"], "ForegroundLink": t["acento.suave"],
                                 "ForegroundVisited": t["texto.complementario"], "DecorationFocus": t["acento.suave"],
                                 "DecorationHover": t["acento.suave"], **estados},
        "Colors:Header": {"BackgroundNormal": t["fondo.encabezado"], "BackgroundAlternate": t["fondo.ventana-alterno"], **base},
        "Colors:Header][Inactive": {"BackgroundNormal": t["fondo.ventana"], "BackgroundAlternate": t["fondo.ventana-alterno"],
                                    **base, "ForegroundNormal": t["texto.inactivo"]},
    }


def esquema(tokens: dict, marca: dict, variante: str) -> tuple[str, str]:
    plano = {k: rgb(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}
    g = grupos(plano, variante)
    id_ = marca["id_esquema"][variante]
    nombre = marca["nombre_esquema"][variante]
    lineas = [CABECERA]
    lineas += ["[ColorEffects:Disabled]", "Color=56,56,56", "ColorAmount=0", "ColorEffect=0", "ContrastAmount=0.65",
               "ContrastEffect=1", "IntensityAmount=0.1", "IntensityEffect=2", ""]
    lineas += ["[ColorEffects:Inactive]", "ChangeSelectionColor=true", "Color=112,111,110", "ColorAmount=0.025",
               "ColorEffect=2", "ContrastAmount=0.1", "ContrastEffect=2", "Enable=false", "IntensityAmount=0",
               "IntensityEffect=0", ""]
    for nombre_grupo in ("Colors:Button", "Colors:Complementary", "Colors:Header", "Colors:Header][Inactive",
                         "Colors:Selection", "Colors:Tooltip", "Colors:View", "Colors:Window"):
        lineas.append(f"[{nombre_grupo}]")
        lineas += [f"{k}={v}" for k, v in sorted(g[nombre_grupo].items())]
        lineas.append("")
    lineas += ["[General]", f"ColorScheme={id_}", f"Name={nombre}", "shadeSortColumn=true", "", "[KDE]", "contrast=4", ""]
    lineas += ["[WM]", f"activeBackground={plano['fondo.encabezado']}", f"activeBlend={plano['fondo.encabezado']}",
               f"activeForeground={plano['texto.normal']}", f"inactiveBackground={plano['fondo.ventana']}",
               f"inactiveBlend={plano['fondo.ventana']}", f"inactiveForeground={plano['texto.inactivo']}", ""]
    return id_, "\n".join(lineas)


def main() -> int:
    aplicar = "--aplicar" in sys.argv
    tokens, marca = cargar()
    for variante in ("claro", "oscuro"):
        id_, texto = esquema(tokens, marca, variante)
        destino = SALIDA / f"{id_}.colors"
        if aplicar:
            SALIDA.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")
            print(f"escrito {destino.relative_to(RAIZ)} ({len(texto.splitlines())} líneas)")
        else:
            print(f"SIM {destino.relative_to(RAIZ)} ({len(texto.splitlines())} líneas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
