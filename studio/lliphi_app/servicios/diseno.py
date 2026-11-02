"""studio/lliphi_app/servicios/diseno.py — el sistema de diseño de Lliphi visto con su color real, sin Qt (reingeniería
2026-11-02, `docs/reingenieria.md` §3.1): de `tokens/tokens.json`, la única fuente, por variante (claro y oscuro):

- `muestras`: cada token de color con su hex y su OKLCH (L, C, H), por grupo: neutros, acento, estados, terminal;
- `relaciones`: la escala de neutros ordenada por luminosidad, el acento con sus variantes y los estados, con el paso
  de L entre vecinos (lo que hace que una escala se lea como escala);
- `contrastes`: los pares que importan (texto sobre fondo, acento sobre fondo, selección, estados, bordes) con su razón
  WCAG 2.x y su veredicto: AAA ≥ 7, AA ≥ 4,5, AA grande ≥ 3 (texto) o «no textual» ≥ 3 (bordes y foco), falla;
- `maqueta`: los colores semánticos que pinta la vista previa de una ventana (QML los usa como datos, no como estilo).

La conversión y el contraste son los de `servicios/color.py` (Björn Ottosson y WCAG 2.x).
"""
from __future__ import annotations

from lliphi_app.servicios import color, proyecto

VARIANTES = ("claro", "oscuro")
# (frente, fondo, qué es, tipo): «texto» pide 4,5 (AA); «grafico» pide 3 (WCAG 1.4.11, componentes no textuales);
# «decorativo» no tiene requisito (un separador no es un componente: se muestra la razón, sin veredicto de falla)
PARES = (
    ("texto.normal", "fondo.ventana", "Texto sobre la ventana", "texto"),
    ("texto.normal", "fondo.vista", "Texto sobre las vistas (listas, editores)", "texto"),
    ("texto.secundario", "fondo.ventana", "Texto secundario sobre la ventana", "texto"),
    ("texto.inactivo", "fondo.ventana", "Texto inactivo sobre la ventana", "texto"),
    ("texto.normal", "fondo.boton", "Texto sobre un botón", "texto"),
    ("seleccion.texto", "seleccion.fondo", "Texto seleccionado", "texto"),
    ("texto.sobre-acento", "acento.base", "Texto sobre el acento", "texto"),
    ("acento.texto", "fondo.vista", "Acento como texto (enlaces, rótulos)", "texto"),
    ("enlace", "fondo.vista", "Enlace", "texto"),
    ("estado.error", "fondo.vista", "Error", "texto"),
    ("estado.advertencia", "fondo.vista", "Advertencia", "texto"),
    ("estado.exito", "fondo.vista", "Éxito", "texto"),
    ("estado.info", "fondo.vista", "Información", "texto"),
    ("texto.tooltip", "fondo.tooltip", "Texto de un tooltip", "texto"),
    ("foco", "fondo.vista", "Anillo de foco", "grafico"),
    ("acento.base", "fondo.ventana", "Acento sobre la ventana (casillas, barras)", "grafico"),
    ("borde.separador", "fondo.ventana", "Separador", "decorativo"),
)
MAQUETA = ("fondo.ventana", "fondo.ventana-alterno", "fondo.vista", "fondo.vista-alterno", "fondo.boton", "fondo.encabezado",
           "fondo.tooltip", "texto.normal", "texto.secundario", "texto.inactivo", "texto.tooltip", "texto.sobre-acento", "borde.separador",
           "borde.sutil", "acento.base", "acento.suave", "acento.texto", "seleccion.fondo", "seleccion.texto", "foco", "enlace",
           "estado.error", "estado.advertencia", "estado.exito", "estado.info")


def _hojas(nodo: dict, prefijo: str = "") -> dict[str, dict]:
    """{ruta.del.token: {hex, oklch: [L, C, H]}} de un árbol de tokens de color."""
    salida: dict[str, dict] = {}
    for k, v in (nodo or {}).items():
        if k.startswith("$") or not isinstance(v, dict):
            continue
        if "$value" in v:
            valor = v["$value"]
            if isinstance(valor, dict) and str(valor.get("hex", "")).startswith("#"):
                comp = valor.get("components") if valor.get("colorSpace") == "oklch" else None
                salida[prefijo + k] = {"hex": valor["hex"].lower(), "oklch": list(comp) if isinstance(comp, list) and len(comp) == 3 else None}
        else:
            salida.update(_hojas(v, prefijo + k + "."))
    return salida


def _muestra(nombre: str, d: dict) -> dict:
    l, c, h = d["oklch"] if d["oklch"] else (None, None, None)
    return {"nombre": nombre, "hex": d["hex"], "l": l if l is not None else -1, "c": c if c is not None else -1, "h": h if h is not None else -1,
            "oklch": f"oklch({l:.3f} {c:.3f} {h:.0f})" if l is not None else "",
            "texto": "#000000" if color.contraste(d["hex"], "#000000") >= color.contraste(d["hex"], "#ffffff") else "#ffffff"}


def veredicto(razon: float, tipo: str) -> tuple[str, str]:
    """(veredicto, nivel semántico) de una razón de contraste WCAG 2.x."""
    if tipo == "decorativo":
        return "Decorativo (sin requisito)", ""
    if tipo == "grafico":
        return ("No textual ≥ 3", "positivo") if razon >= 3 else ("Falla (< 3)", "negativo")
    if razon >= 7:
        return "AAA", "positivo"
    if razon >= 4.5:
        return "AA", "positivo"
    if razon >= 3:
        return "AA grande", "neutro"
    return "Falla", "negativo"


def variante(tokens: dict, nombre: str) -> dict:
    prim = _hojas((tokens.get("primitivas") or {}).get(nombre))
    sem = _hojas((tokens.get("semanticos") or {}).get(nombre))
    term = _hojas((tokens.get("terminal") or {}).get(nombre))
    neutros = sorted((k for k in prim if k.startswith("neutro")), key=lambda k: prim[k]["oklch"][0] if prim[k]["oklch"] else 0)
    acentos = [k for k in prim if k.startswith("acento")]
    estados = [k for k in prim if k in ("negativo", "neutral", "positivo", "info")]

    def escala(claves: list[str], fuente: dict) -> list[dict]:
        salida, previa = [], None
        for k in claves:
            m = _muestra(k, fuente[k])
            m["paso"] = round(m["l"] - previa, 3) if previa is not None and m["l"] >= 0 else 0
            previa = m["l"] if m["l"] >= 0 else previa
            salida.append(m)
        return salida

    contrastes = []
    for frente, fondo, que, tipo in PARES:
        if frente in sem and fondo in sem:
            razon = color.contraste(sem[frente]["hex"], sem[fondo]["hex"])
            texto, nivel = veredicto(razon, tipo)
            contrastes.append({"frente": frente, "fondo": fondo, "que": que, "tipo": tipo, "razon": round(razon, 2),
                               "textoRazon": f"{razon:.2f}:1", "veredicto": texto, "nivel": nivel,
                               "hexFrente": sem[frente]["hex"], "hexFondo": sem[fondo]["hex"]})
    ansi = [_muestra(f"color{i}", term[f"color{i}"]) for i in range(16) if f"color{i}" in term]
    return {
        "variante": nombre, "titulo": proyecto.marca().get("nombre_esquema", {}).get(nombre, f"Lliphi {nombre}"),
        "acento": (tokens.get("acento") or {}).get(nombre, ""),
        "neutros": escala(neutros, prim), "acentos": [_muestra(k, prim[k]) for k in acentos], "estados": [_muestra(k, prim[k]) for k in estados],
        "semanticos": [_muestra(k, v) for k, v in sem.items()], "ansi": ansi,
        "terminal": {k: v["hex"] for k, v in term.items() if not k.startswith("color")},
        "contrastes": contrastes, "fallan": sum(c["nivel"] == "negativo" for c in contrastes),
        "maqueta": {k.replace(".", "_").replace("-", "_"): sem[k]["hex"] for k in MAQUETA if k in sem},
    }


def sistema(tokens: dict | None = None) -> dict:
    """Las dos variantes y la tipografía, listas para la página del sistema de diseño."""
    tokens = tokens if tokens is not None else proyecto.tokens()
    tipo = tokens.get("tipografia") or {}
    familias = {k: (v.get("$value") or []) for k, v in tipo.items() if isinstance(v, dict) and isinstance(v.get("$value"), list)}
    tamano = (tipo.get("tamano-base") or {}).get("$value") or {}
    return {"variantes": [variante(tokens, v) for v in VARIANTES],
            "tipografia": {"familias": familias, "tamano": f"{tamano.get('value', '')} {tamano.get('unit', '')}".strip()},
            "radios": {k: v.get("$value") for k, v in (tokens.get("radio") or {}).items() if isinstance(v, dict)},
            "espaciado": {k: v.get("$value") for k, v in (tokens.get("espaciado") or {}).items() if isinstance(v, dict)}}
