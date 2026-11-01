#!/usr/bin/env python3
"""Paleta y tokens semánticos del tema: la fuente de verdad del color.

Define cada color en OKLCH (luminosidad perceptual), deriva los tokens semánticos de las dos
variantes (claro y oscuro), mide el contraste WCAG 2.2 de cada par que importa (1.4.3 texto
≥ 4.5:1; 1.4.11 componentes y foco ≥ 3:1) y escribe `tokens/tokens.json` en el formato
Design Tokens 2025.10 (color en `oklch` con `hex` de respaldo).

Los valores (OKLCH de neutros, acentos, estados y terminal) están en `ajustes.json`, junto a este archivo: es la
fuente que edita Lliphi Studio; aquí queda cómo se combinan.

Uso:  .venv/bin/python modulos/esquema/paleta.py            # informe en pantalla; sale 1 si un par falla
      .venv/bin/python modulos/esquema/paleta.py --aplicar  # además escribe tokens/tokens.json
      .venv/bin/python modulos/esquema/paleta.py --ajustes <borrador.json> --json   # informe de un borrador, en JSON
      .venv/bin/python modulos/esquema/paleta.py --acento azul                      # el mismo acento en las dos variantes
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from coloraide import Color

RAIZ = Path(__file__).resolve().parents[2]
TOKENS = RAIZ / "tokens" / "tokens.json"
AJUSTES = Path(__file__).resolve().parent / "ajustes.json"

# ---------------------------------------------------------------------------
# 1. Primitivas: una familia de neutros por variante (casi negros de Nothing, grises suaves de WhiteSur, con un matiz
#    frío apenas perceptible) y un acento por variante (decisiones 4.12: el rojo de Nothing en el oscuro, el azul de
#    WhiteSur en el claro). Otros acentos (azul, verde azulado) se prueban con --acento; el esquema sigue además el
#    acento del sistema de Plasma 6. El azul-whitesur es el #315bef de WhiteSur (5,4:1 con blanco), su texto
#    (#2a4fd0) y un suave (#4777f0) apenas más oscuro que su #4f7fef para que el hover cumpla 3:1 sobre los botones.
# ---------------------------------------------------------------------------

def oklch(l: float, c: float, h: float) -> Color:
    return Color("oklch", [l, c, h]).fit("srgb")


def leer_ajustes(ruta: Path = AJUSTES) -> dict:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def volcar_ajustes(doc: dict) -> str:
    """El texto canónico de `ajustes.json`: sangría de dos espacios y cada terna OKLCH en una línea."""
    texto = json.dumps(doc, ensure_ascii=False, indent=2)
    return re.sub(r"\[\s*(-?[\d.]+(?:,\s*-?[\d.]+)*)\s*\]",
                  lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", texto) + "\n"


def cargar(ajustes: dict) -> None:
    """Fija los valores del módulo desde unos ajustes (los del archivo o un borrador)."""
    global AJ, MATIZ_NEUTRO, ACENTOS, ACENTO, ANSI_MATIZ, PRIMITIVAS
    AJ = ajustes
    MATIZ_NEUTRO = ajustes["matiz_neutro"]
    ACENTOS = ajustes["acentos"]
    ACENTO = dict(ajustes["acento"])
    ANSI_MATIZ = ajustes["terminal"]["matices"]
    PRIMITIVAS = primitivas()


def primitivas(acento: dict[str, str] | str | None = None) -> dict[str, dict[str, Color]]:
    acento = acento or ACENTO
    if isinstance(acento, str):
        acento = {"claro": acento, "oscuro": acento}
    salida: dict[str, dict[str, Color]] = {}
    for variante in ("claro", "oscuro"):
        a = ACENTOS[acento[variante]][variante]
        p = {k: oklch(l, c, MATIZ_NEUTRO) for k, (l, c) in AJ["neutros"][variante].items()}
        p.update({"acento": oklch(*a["base"]), "acento-suave": oklch(*a["suave"]), "acento-texto": oklch(*a["texto"])})
        p.update({k: oklch(*v) for k, v in AJ["estados"][variante].items()})
        salida[variante] = p
    return salida


BLANCO = Color("srgb", [0.99, 0.99, 0.99])

# Paleta ANSI de 16 colores para terminales (Konsole y después otras): matices fijos con significado
# (0 negro, 1 rojo, 2 verde, 3 amarillo, 4 azul, 5 magenta, 6 cian, 7 blanco) y luminosidades por variante
# que dan ≥ 4.5:1 sobre el fondo de vista; las «intensas» (8–15) suben de luminosidad, nunca de ruido.

def terminal(variante: str) -> dict[str, Color]:
    p = PRIMITIVAS[variante]
    h = MATIZ_NEUTRO
    a = AJ["terminal"][variante]
    normal, intensa, croma = a["normal"], a["intensa"], a["croma"]
    negro, negro_i = oklch(*a["negro"], h), oklch(*a["negro-intenso"], h)
    blanco, blanco_i = oklch(*a["blanco"], h), oklch(*a["blanco-intenso"], h)
    t = {"fondo": p["neutro-0"], "texto": p["neutro-7"], "texto-tenue": p["neutro-5"], "texto-intenso": p["neutro-7"],
         "color0": negro, "color8": negro_i, "color7": blanco, "color15": blanco_i}
    for i, nombre in enumerate(("rojo", "verde", "amarillo", "azul", "magenta", "cian"), start=1):
        t[f"color{i}"] = oklch(normal, croma, ANSI_MATIZ[nombre])
        t[f"color{i + 8}"] = oklch(intensa, croma, ANSI_MATIZ[nombre])
    return t


cargar(leer_ajustes())


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
        "$description": "Fuente de verdad del color del tema. Generado por modulos/esquema/paleta.py; no editar a mano.",
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


def informe_json() -> dict:
    """El informe en forma de máquina: los semánticos y la terminal de cada variante en hex y OKLCH, y cada par con
    su razón, su mínimo y si cumple (lo lee Lliphi Studio)."""
    def color(c: Color) -> dict:
        o = c.convert("oklch")
        return {"hex": hexa(c), "oklch": [round(o["l"], 4), round(o["c"], 4), round(o["h"], 2) if o["h"] == o["h"] else 0]}
    out: dict = {"acento": ACENTO, "ok": True, "variantes": {}}
    for variante in ("claro", "oscuro"):
        t = semanticos(variante)
        term = terminal(variante)
        mismo_polo = {"color0", "color8"} if variante == "oscuro" else {"color7", "color15"}
        pares = []
        for fg, bg, minimo, criterio in PARES:
            r = contraste(t[fg], t[bg])
            pares.append({"texto": fg, "fondo": bg, "razon": round(r, 2), "minimo": minimo, "criterio": criterio,
                          "cumple": r >= minimo, "informativo": criterio.startswith("jerarquía")})
        for k, c in term.items():
            if k.startswith("color") or k == "texto":
                r = contraste(c, term["fondo"])
                pares.append({"texto": f"terminal.{k}", "fondo": "terminal.fondo", "razon": round(r, 2), "minimo": 4.5,
                              "criterio": "informativo (mismo polo)" if k in mismo_polo else "1.4.3",
                              "cumple": r >= 4.5, "informativo": k in mismo_polo})
        out["ok"] &= all(p["cumple"] or p["informativo"] for p in pares)
        out["variantes"][variante] = {"primitivas": {k: color(c) for k, c in PRIMITIVAS[variante].items()},
                                      "semanticos": {k: color(c) for k, c in t.items()},
                                      "terminal": {k: color(c) for k, c in term.items()}, "pares": pares}
    return out


if __name__ == "__main__":
    if "--ajustes" in sys.argv:   # un borrador (Lliphi Studio): solo para informar, nunca se escribe con él
        if "--aplicar" in sys.argv:
            sys.exit("--ajustes es para probar un borrador; para aplicarlo, guárdalo en modulos/esquema/ajustes.json")
        cargar(leer_ajustes(Path(sys.argv[sys.argv.index("--ajustes") + 1])))
    if "--acento" in sys.argv:   # el mismo acento en las dos variantes (para probar otros)
        ACENTO = sys.argv[sys.argv.index("--acento") + 1]
        PRIMITIVAS = primitivas(ACENTO)
    if "--json" in sys.argv:
        datos = informe_json()
        print(json.dumps(datos, ensure_ascii=False))
        sys.exit(0 if datos["ok"] else 1)
    bien = informe()
    if "--aplicar" in sys.argv:
        escribir_tokens()
    print("\nresultado:", "todos los pares cumplen" if bien else "HAY PARES QUE FALLAN")
    sys.exit(0 if bien else 1)
