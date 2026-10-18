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
# 1. Primitivas: una familia de neutros por variante y un acento común.
#    Día: neutros cálidos (matiz 80, papel). Noche: neutros fríos (matiz 255, pizarra).
#    El acento es un verde azulado sereno (matiz 195) con dos luminosidades.
# ---------------------------------------------------------------------------

def oklch(l: float, c: float, h: float) -> Color:
    return Color("oklch", [l, c, h]).fit("srgb")


MATIZ = {"claro": 80, "oscuro": 255}
ACENTO_H = 195

PRIMITIVAS = {
    "claro": {
        "neutro-0": oklch(0.990, 0.003, 80),   # vista (papel claro)
        "neutro-1": oklch(0.965, 0.005, 80),   # vista alterna
        "neutro-2": oklch(0.950, 0.006, 80),   # ventana
        "neutro-3": oklch(0.920, 0.007, 80),   # ventana alterna, botón
        "neutro-4": oklch(0.860, 0.008, 80),   # separadores, bordes
        "neutro-5": oklch(0.530, 0.010, 80),   # texto inactivo
        "neutro-6": oklch(0.420, 0.012, 80),   # texto secundario
        "neutro-7": oklch(0.250, 0.012, 80),   # texto
        "neutro-8": oklch(0.280, 0.010, 80),   # tooltip (inverso)
        "acento":   oklch(0.500, 0.095, ACENTO_H),
        "acento-suave": oklch(0.575, 0.090, ACENTO_H),
        "acento-texto": oklch(0.440, 0.095, ACENTO_H),
        "negativo": oklch(0.520, 0.170, 25),
        "neutral":  oklch(0.520, 0.120, 70),
        "positivo": oklch(0.500, 0.130, 150),
        "info":     oklch(0.520, 0.120, 250),
    },
    "oscuro": {
        "neutro-0": oklch(0.190, 0.012, 255),  # vista (más profunda que la ventana)
        "neutro-1": oklch(0.220, 0.012, 255),  # vista alterna
        "neutro-2": oklch(0.245, 0.013, 255),  # ventana
        "neutro-3": oklch(0.275, 0.013, 255),  # ventana alterna
        "neutro-3b": oklch(0.320, 0.014, 255), # botón
        "neutro-4": oklch(0.380, 0.014, 255),  # separadores, bordes
        "neutro-5": oklch(0.680, 0.012, 255),  # texto inactivo
        "neutro-6": oklch(0.800, 0.010, 255),  # texto secundario
        "neutro-7": oklch(0.935, 0.006, 255),  # texto
        "neutro-8": oklch(0.340, 0.014, 255),  # tooltip
        "acento":   oklch(0.545, 0.100, ACENTO_H),
        "acento-suave": oklch(0.680, 0.095, ACENTO_H),
        "acento-texto": oklch(0.760, 0.090, ACENTO_H),
        "negativo": oklch(0.740, 0.150, 25),
        "neutral":  oklch(0.800, 0.120, 75),
        "positivo": oklch(0.760, 0.130, 150),
        "info":     oklch(0.760, 0.100, 250),
    },
}

BLANCO = Color("srgb", [0.99, 0.99, 0.99])


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
        "fondo.encabezado": p["neutro-2"] if variante == "claro" else p["neutro-1"],
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
    doc["espaciado"] = {"$type": "dimension", **{f"e{n}": {"$value": {"value": n, "unit": "px"}} for n in (4, 8, 12, 16, 24, 32)}}
    doc["radio"] = {"$type": "dimension", "control": {"$value": {"value": 4, "unit": "px"}}, "menu": {"$value": {"value": 6, "unit": "px"}},
                    "ventana": {"$value": {"value": 8, "unit": "px"}}, "panel-flotante": {"$value": {"value": 10, "unit": "px"}}}
    doc["tipografia"] = {"interfaz": {"$type": "fontFamily", "$value": ["Inter", "Noto Sans", "sans-serif"]},
                         "monoespaciada": {"$type": "fontFamily", "$value": ["IBM Plex Mono", "Hack", "monospace"]},
                         "tamano-base": {"$type": "dimension", "$value": {"value": 10, "unit": "pt"}}}
    TOKENS.parent.mkdir(exist_ok=True)
    TOKENS.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nescrito {TOKENS.relative_to(RAIZ)}")


if __name__ == "__main__":
    bien = informe()
    if "--aplicar" in sys.argv:
        escribir_tokens()
    print("\nresultado:", "todos los pares cumplen" if bien else "HAY PARES QUE FALLAN")
    sys.exit(0 if bien else 1)
