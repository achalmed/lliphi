#!/usr/bin/env python3
"""Paleta y tokens semánticos del tema: la fuente de verdad del color.

Define cada color en OKLCH (luminosidad perceptual), deriva los tokens semánticos de las dos
variantes (claro y oscuro), mide el contraste WCAG 2.2 de cada par que importa (1.4.3 texto
≥ 4.5:1; 1.4.11 componentes y foco ≥ 3:1) y escribe `tokens/tokens.json` en el formato
Design Tokens 2025.10 (color en `oklch` con `hex` de respaldo).

Uso:  .venv/bin/python herramientas/paleta.py            # informe en pantalla; sale 1 si un par falla
      .venv/bin/python herramientas/paleta.py --aplicar  # además escribe tokens/tokens.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from coloraide import Color

RAIZ = Path(__file__).resolve().parent.parent
TOKENS = RAIZ / "tokens" / "tokens.json"

# ---------------------------------------------------------------------------
# 1. Primitivas: una familia de neutros por variante y un acento por variante (rojo oscuro, azul claro).
#    Día: neutros cálidos (matiz 80, papel). Noche: neutros fríos (matiz 255, pizarra).
#    El acento es un verde azulado sereno (matiz 195) con dos luminosidades.
# ---------------------------------------------------------------------------

def oklch(l: float, c: float, h: float) -> Color:
    return Color("oklch", [l, c, h]).fit("srgb")


# Neutros casi negros (Nothing) y grises suaves (WhiteSur claro), con un matiz frío apenas perceptible.
# Acento principal: el rojo de Nothing, llevado a la luminosidad que cumple 4.5:1 con texto claro.
# Otros acentos (azul de WhiteSur, verde azulado) se generan con --acento; el esquema sigue además
# el acento del sistema de Plasma 6, así que el usuario puede cambiarlo sin tocar el tema.
MATIZ_NEUTRO = 270
ACENTOS = {
    #            claro: base, suave, texto          oscuro: base, suave, texto
    "rojo":       ((0.545, 0.185, 25), (0.62, 0.17, 25), (0.50, 0.185, 25),
                   (0.555, 0.185, 25), (0.68, 0.17, 25), (0.78, 0.13, 25)),
    "azul":       ((0.50, 0.17, 262), (0.60, 0.15, 262), (0.46, 0.17, 262),
                   (0.56, 0.17, 262), (0.70, 0.13, 262), (0.80, 0.10, 262)),
    # el azul exacto de WhiteSur (#315bef, 5,4:1 con blanco), su texto (#2a4fd0) y un suave (#4777f0) apenas más
    # oscuro que el #4f7fef de WhiteSur para que el hover cumpla 3:1 sobre los botones claros
    "azul-whitesur": ((0.538, 0.227, 266.26), (0.60, 0.19, 265), (0.487, 0.203, 266.26),
                      (0.56, 0.17, 262), (0.70, 0.13, 262), (0.80, 0.10, 262)),
    "verde-azul": ((0.50, 0.085, 195), (0.575, 0.09, 195), (0.44, 0.095, 195),
                   (0.545, 0.10, 195), (0.68, 0.095, 195), (0.76, 0.09, 195)),
}
# Decisión del autor (2026-10-19, decisiones 4.12): un acento por variante, cada uno de su tema de partida:
# el rojo de Nothing en el oscuro y el azul de WhiteSur en el claro.
ACENTO = {"claro": "azul-whitesur", "oscuro": "rojo"}


def primitivas(acento: dict[str, str] | str = ACENTO) -> dict[str, dict[str, Color]]:
    if isinstance(acento, str):
        acento = {"claro": acento, "oscuro": acento}
    a = ACENTOS[acento["claro"]][:3] + ACENTOS[acento["oscuro"]][3:]
    h = MATIZ_NEUTRO
    return {
        "claro": {
            "neutro-0": oklch(0.990, 0.002, h),   # vista
            "neutro-1": oklch(0.965, 0.003, h),   # vista alterna
            "neutro-2": oklch(0.945, 0.004, h),   # ventana
            "neutro-3": oklch(0.910, 0.005, h),   # ventana alterna, botón
            "neutro-4": oklch(0.850, 0.006, h),   # separadores, bordes
            "neutro-5": oklch(0.515, 0.008, h),   # texto inactivo
            "neutro-6": oklch(0.420, 0.010, h),   # texto secundario
            "neutro-7": oklch(0.240, 0.010, h),   # texto
            "neutro-8": oklch(0.260, 0.008, h),   # tooltip (inverso)
            "acento": oklch(*a[0]), "acento-suave": oklch(*a[1]), "acento-texto": oklch(*a[2]),
            "negativo": oklch(0.520, 0.170, 25),
            "neutral":  oklch(0.520, 0.120, 70),
            "positivo": oklch(0.500, 0.130, 150),
            "info":     oklch(0.520, 0.120, 250),
        },
        "oscuro": {
            "neutro-0": oklch(0.175, 0.004, h),   # vista (más profunda)
            "neutro-1": oklch(0.205, 0.004, h),   # vista alterna
            "neutro-2": oklch(0.225, 0.004, h),   # ventana (≈ el #1b1b1d de Nothing)
            "neutro-3": oklch(0.260, 0.005, h),   # ventana alterna
            "neutro-3b": oklch(0.305, 0.005, h),  # botón
            "neutro-4": oklch(0.365, 0.006, h),   # separadores, bordes
            "neutro-5": oklch(0.680, 0.006, h),   # texto inactivo
            "neutro-6": oklch(0.800, 0.005, h),   # texto secundario
            "neutro-7": oklch(0.940, 0.003, h),   # texto
            "neutro-8": oklch(0.320, 0.005, h),   # tooltip
            "acento": oklch(*a[3]), "acento-suave": oklch(*a[4]), "acento-texto": oklch(*a[5]),
            "negativo": oklch(0.740, 0.150, 25),
            "neutral":  oklch(0.800, 0.120, 75),
            "positivo": oklch(0.760, 0.130, 150),
            "info":     oklch(0.760, 0.100, 250),
        },
    }


PRIMITIVAS = primitivas()

BLANCO = Color("srgb", [0.99, 0.99, 0.99])

# Paleta ANSI de 16 colores para terminales (Konsole y después otras): matices fijos con significado
# (0 negro, 1 rojo, 2 verde, 3 amarillo, 4 azul, 5 magenta, 6 cian, 7 blanco) y luminosidades por variante
# que dan ≥ 4.5:1 sobre el fondo de vista; las «intensas» (8–15) suben de luminosidad, nunca de ruido.
ANSI_MATIZ = {"rojo": 25, "verde": 150, "amarillo": 85, "azul": 262, "magenta": 330, "cian": 200}


def terminal(variante: str) -> dict[str, Color]:
    p = PRIMITIVAS[variante]
    h = MATIZ_NEUTRO
    if variante == "claro":
        normal, intensa, croma = 0.50, 0.42, 0.14
        negro, negro_i = oklch(0.30, 0.008, h), oklch(0.45, 0.008, h)
        blanco, blanco_i = oklch(0.80, 0.004, h), oklch(0.93, 0.002, h)
    else:
        normal, intensa, croma = 0.74, 0.82, 0.13
        negro, negro_i = oklch(0.32, 0.006, h), oklch(0.50, 0.006, h)
        blanco, blanco_i = oklch(0.86, 0.004, h), oklch(0.96, 0.002, h)
    t = {"fondo": p["neutro-0"], "texto": p["neutro-7"], "texto-tenue": p["neutro-5"], "texto-intenso": p["neutro-7"],
         "color0": negro, "color8": negro_i, "color7": blanco, "color15": blanco_i}
    for i, nombre in enumerate(("rojo", "verde", "amarillo", "azul", "magenta", "cian"), start=1):
        t[f"color{i}"] = oklch(normal, croma, ANSI_MATIZ[nombre])
        t[f"color{i + 8}"] = oklch(intensa, croma, ANSI_MATIZ[nombre])
    return t


# ---------------------------------------------------------------------------
# 2. Tokens semánticos: los roles que consumen los generadores (esquema de Plasma,
#    estilo de Plasma, Konsole, sitio…). Mismo nombre en las dos variantes.
# ---------------------------------------------------------------------------

def semanticos(variante: str) -> dict[str, Color]:
    p = PRIMITIVAS[variante]
    boton = p["neutro-3"] if variante == "claro" else p["neutro-3b"]
    return {
        # superficies
        "fondo.ventana": p["neutro-2"],
        "fondo.ventana-alterno": p["neutro-3"],
        "fondo.vista": p["neutro-0"],
        "fondo.vista-alterno": p["neutro-1"],
        "fondo.boton": boton,
        "fondo.encabezado": p["neutro-2"] if variante == "claro" else p["neutro-0"],
        "fondo.tooltip": p["neutro-8"],
        "fondo.complementario": PRIMITIVAS["oscuro"]["neutro-0"],   # bloqueo y cierre: siempre oscuro
        # texto
        "texto.normal": p["neutro-7"],
        "texto.secundario": p["neutro-6"],
        "texto.inactivo": p["neutro-5"],
        "texto.tooltip": PRIMITIVAS["claro"]["neutro-0"] if variante == "claro" else p["neutro-7"],
        "texto.complementario": PRIMITIVAS["oscuro"]["neutro-7"],
        "texto.sobre-acento": BLANCO,
        # bordes
        "borde.separador": p["neutro-4"],
        "borde.sutil": p["neutro-3"] if variante == "claro" else p["neutro-3b"],
        # acento y estados interactivos
        "acento.base": p["acento"],
        "acento.suave": p["acento-suave"],
        "acento.texto": p["acento-texto"],
        "seleccion.fondo": p["acento"],
        "seleccion.texto": BLANCO,
        # el anillo de foco es el acento de mayor contraste de cada variante: oscuro en el claro, claro en el oscuro
        "foco": p["acento"] if variante == "claro" else p["acento-suave"],
        "hover": p["acento-suave"],
        "enlace": p["acento-texto"],
        "visitado": p["neutro-6"],
        # semánticos
        "estado.error": p["negativo"],
        "estado.advertencia": p["neutral"],
        "estado.exito": p["positivo"],
        "estado.info": p["info"],
    }


# ---------------------------------------------------------------------------
# 3. Pares de contraste. (texto, fondo, mínimo, criterio)
# ---------------------------------------------------------------------------

PARES = [
    ("texto.normal", "fondo.ventana", 4.5, "1.4.3"),
    ("texto.normal", "fondo.vista", 4.5, "1.4.3"),
    ("texto.normal", "fondo.boton", 4.5, "1.4.3"),
    ("texto.normal", "fondo.encabezado", 4.5, "1.4.3"),
    ("texto.secundario", "fondo.ventana", 4.5, "1.4.3"),
    ("texto.inactivo", "fondo.ventana", 4.5, "1.4.3"),
    ("texto.inactivo", "fondo.vista", 4.5, "1.4.3"),
    ("texto.tooltip", "fondo.tooltip", 4.5, "1.4.3"),
    ("texto.complementario", "fondo.complementario", 4.5, "1.4.3"),
    ("seleccion.texto", "seleccion.fondo", 4.5, "1.4.3"),
    ("enlace", "fondo.ventana", 4.5, "1.4.3"),
    ("enlace", "fondo.vista", 4.5, "1.4.3"),
    ("estado.error", "fondo.ventana", 4.5, "1.4.3"),
    ("estado.advertencia", "fondo.ventana", 4.5, "1.4.3"),
    ("estado.exito", "fondo.ventana", 4.5, "1.4.3"),
    ("estado.info", "fondo.ventana", 4.5, "1.4.3"),
    ("estado.error", "fondo.vista", 4.5, "1.4.3"),
    ("foco", "fondo.ventana", 3.0, "1.4.11"),
    ("foco", "fondo.vista", 3.0, "1.4.11"),
    ("foco", "fondo.boton", 3.0, "1.4.11"),
    ("hover", "fondo.ventana", 3.0, "1.4.11"),
    ("hover", "fondo.boton", 3.0, "1.4.11"),
    ("acento.base", "fondo.ventana", 3.0, "1.4.11"),
    ("borde.separador", "fondo.ventana", 1.2, "jerarquía (informativo)"),
    ("fondo.vista", "fondo.ventana", 1.05, "jerarquía (informativo)"),
    ("fondo.boton", "fondo.ventana", 1.05, "jerarquía (informativo)"),
]


def contraste(a: Color, b: Color) -> float:
    return a.contrast(b, method="wcag21")


def hexa(c: Color) -> str:
    return c.convert("srgb").to_string(hex=True)


def rgb(c: Color) -> str:
    s = c.convert("srgb")
    return ",".join(str(round(v * 255)) for v in s.coords())


def informe() -> bool:
    ok = True
    for variante in ("claro", "oscuro"):
        t = semanticos(variante)
        print(f"\n== {variante}")
        for nombre, c in t.items():
            print(f"  {nombre:24s} {hexa(c)}  {rgb(c):>12s}  {c.to_string(precision=3)}")
        print(f"\n  {'par':46s} {'ratio':>6s}  mínimo  criterio")
        for fg, bg, minimo, criterio in PARES:
            r = contraste(t[fg], t[bg])
            cumple = r >= minimo
            ok &= cumple or criterio.startswith("jerarquía")
            marca = "ok " if cumple else "FALLA"
            print(f"  {marca} {fg + ' / ' + bg:42s} {r:6.2f}  {minimo:>5}   {criterio}")
        term = terminal(variante)
        # el negro ANSI sobre fondo oscuro y el blanco ANSI sobre fondo claro son del mismo polo que el fondo:
        # no son texto corriente y se miden solo a título informativo
        mismo_polo = {"color0", "color8"} if variante == "oscuro" else {"color7", "color15"}
        for k, c in term.items():
            if k.startswith("color") or k == "texto":
                r = contraste(c, term["fondo"])
                informativo = k in mismo_polo
                cumple = r >= 4.5 or informativo
                ok &= cumple
                print(f"  {'ok ' if cumple else 'FALLA'} {'terminal.' + k + ' / terminal.fondo':42s} {r:6.2f}    4.5   {'informativo (mismo polo)' if informativo else '1.4.3'}")
    return ok


def token_color(c: Color, descripcion: str = "") -> dict:
    o = c.convert("oklch")
    d = {
        "$type": "color",
        "$value": {
            "colorSpace": "oklch",
            "components": [round(o["l"], 4), round(o["c"], 4), round(o["h"], 2) if o["h"] == o["h"] else 0],
            "alpha": 1,
            "hex": hexa(c),
        },
    }
    if descripcion:
        d["$description"] = descripcion
    return d


def escribir_tokens() -> None:
    doc = {
        "$description": "Fuente de verdad del color del tema. Generado por herramientas/paleta.py; no editar a mano.",
        "acento": ACENTO,
        "primitivas": {
            v: {k: token_color(c) for k, c in p.items()} for v, p in PRIMITIVAS.items()
        },
        "semanticos": {},
    }
    for variante in ("claro", "oscuro"):
        grupo: dict = {}
        for nombre, c in semanticos(variante).items():
            partes = nombre.split(".")
            d = grupo
            for parte in partes[:-1]:
                d = d.setdefault(parte, {})
            d[partes[-1]] = token_color(c)
        doc["semanticos"][variante] = grupo
    doc["terminal"] = {v: {k: token_color(c) for k, c in terminal(v).items()} for v in ("claro", "oscuro")}
    doc["espaciado"] = {"$type": "dimension", **{f"e{n}": {"$value": {"value": n, "unit": "px"}} for n in (4, 8, 12, 16, 24, 32)}}
    doc["radio"] = {"$type": "dimension", "control": {"$value": {"value": 6, "unit": "px"}}, "menu": {"$value": {"value": 10, "unit": "px"}},
                    "ventana": {"$value": {"value": 12, "unit": "px"}}, "panel-flotante": {"$value": {"value": 14, "unit": "px"}}}
    # vidrio: opacidades de los fondos translúcidos (Plasma los usa solo con desenfoque), contraste tras el vidrio y textura
    doc["efectos"] = {"$type": "number",
                      "opacidad-panel": {"$value": 0.64, "$description": "panel y dock en translucent/: 0.58 oscuro; el claro usa la misma SVG con su fondo"},
                      "opacidad-dialogo": {"$value": 0.85, "$description": "lanzador, menús del shell, notificaciones, tooltips"},
                      "contraste": {"$value": 0.35}, "intensidad": {"$value": 1.0}, "saturacion": {"$value": 1.15},
                      "textura": {"$value": 0.07, "$description": "opacidad de la retícula de puntos del panel"},
                      "opacidad-menus-qt": {"$value": 80, "$description": "MenuOpacity de Breeze (menús de las aplicaciones)"},
                      "opacidad-konsole": {"$value": 0.86}}
    doc["tipografia"] = {"interfaz": {"$type": "fontFamily", "$value": ["Inter", "Noto Sans", "sans-serif"]},
                         "monoespaciada": {"$type": "fontFamily", "$value": ["JetBrainsMono Nerd Font", "JetBrains Mono", "monospace"]},
                         "tamano-base": {"$type": "dimension", "$value": {"value": 10, "unit": "pt"}}}
    TOKENS.parent.mkdir(exist_ok=True)
    TOKENS.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nescrito {TOKENS.relative_to(RAIZ)}")


if __name__ == "__main__":
    if "--acento" in sys.argv:   # el mismo acento en las dos variantes (para probar otros)
        ACENTO = sys.argv[sys.argv.index("--acento") + 1]
        PRIMITIVAS = primitivas(ACENTO)
    bien = informe()
    if "--aplicar" in sys.argv:
        escribir_tokens()
    print("\nresultado:", "todos los pares cumplen" if bien else "HAY PARES QUE FALLAN")
    sys.exit(0 if bien else 1)
