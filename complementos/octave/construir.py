"""Colores de la interfaz gráfica de GNU Octave (decisiones 5.41): el editor, la ventana de órdenes, el editor de
variables y el espacio de trabajo, en los dos «modos de color» que Octave guarda a la vez: Lliphi Claro en el primero y
Lliphi Oscuro en el segundo («Second color mode (light/dark)» de Preferencias), de modo que pasar de una variante a otra
es cambiar cuatro interruptores.

Formato (comprobado el 2026-11-01 en el código de la rama `stable` de Octave, `libgui/src/gui-preferences-*.cc` y
`gui-settings.cc`, y con Octave 11.1.0 en un HOME de prueba): los ajustes están en `$XDG_CONFIG_HOME/octave/octave-gui.ini`
(QSettings en formato ini; ya no `qt-settings`). Cada color tiene una clave del primer modo y otra con el sufijo `_2`
del segundo (`terminal/color_f` y `terminal/color_f_2`…), y el modo en uso lo dicen `editor/color_mode`,
`terminal/color_mode`, `variable_editor/color_mode` y `workspaceview/color_mode` (0 o 1). Los colores se escriben como
los escribe Octave, un `QColor` serializado (`@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff…)`). Los del editor son los de cada
lexer de QScintilla en los grupos `[Scintilla]` (primer modo) y `[Scintilla_2]` (segundo): `<Lenguaje>\\style<N>\\color`
y `\\paper` (entero 0xRRGGBB), `\\eolfill` y `\\font` (familia, tamaño, negrita, cursiva, subrayado), y `defaultcolor`,
`defaultpaper` y `defaultfont`; se escriben todos los estilos válidos de cada lexer (QScintilla 2.14.1), porque uno que
falte vuelve al blanco de QScintilla. Los lexers son los de Octave y Matlab (los `.m`), Bash y Diff; los demás (C++,
Java, Perl, Batch) los calcula Octave en el segundo modo invirtiendo la luz de los suyos.

La ventana de órdenes solo tiene cuatro colores (texto, fondo, selección y cursor): el fondo y el texto son los de
Konsole (`konsole.ansi`); Octave no admite los dieciséis ANSI. La sintaxis sale de la tabla de los editores
(`editores.sintaxis`). La interfaz (menús, paneles, barras) no se toca: Octave 11 es Qt 6 y sigue el esquema de color de
Plasma. Ningún color se escribe aquí.

Se generan `lliphi.ini`, el fragmento legible (los dos modos, sin los interruptores), y `octave-lliphi.py`, el programa
que lo fusiona en `octave-gui.ini` conservando lo demás y que cambia de modo al cambiar la variante."""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import escribir, registro

sintaxis = registro.codigo("editores").sintaxis
paleta = registro.codigo("editores").paleta
ansi = registro.codigo("konsole").ansi

FUENTE_PROGRAMA = Path(__file__).resolve().parent / "variante.py"
PROGRAMA = "octave-lliphi.py"
MODO = {"claro": 0, "oscuro": 1}
SUFIJO = {"claro": "", "oscuro": "_2"}
GRUPO_LEXER = {"claro": "Scintilla", "oscuro": "Scintilla_2"}
INTERRUPTORES = ("editor/color_mode", "terminal/color_mode", "variable_editor/color_mode", "workspaceview/color_mode")

# estilo de QScintilla → papel de la tabla de sintaxis (todos los estilos con descripción en QScintilla 2.14.1)
MATLAB = {0: "variable", 1: "comentario", 2: "atributo", 3: "numero", 4: "palabra-clave", 5: "cadena", 6: "operador",
          7: "variable", 8: "cadena"}
LEXERS = {
    "Octave": MATLAB,
    "Matlab": MATLAB,
    "Bash": {0: "variable", 1: "invalido", 2: "comentario", 3: "numero", 4: "palabra-clave", 5: "cadena", 6: "cadena",
             7: "operador", 8: "variable", 9: "atributo", 10: "atributo", 11: "escape", 12: "etiqueta", 13: "cadena"},
    "Diff": {0: "variable", 1: "comentario", 2: "palabra-clave", 3: "funcion", 4: "simbolo", 5: "borrado", 6: "insertado",
             7: "cambiado", 8: "insertado", 9: "borrado", 10: "insertado", 11: "borrado"},
}
CURSIVA = {"comentario"}


def qcolor(hex6: str) -> str:
    """Un color como lo guarda QSettings: `@Variant(…)` con el `QColor` serializado por QDataStream (versión Qt 4.0:
    tipo 67, espec. RGB, alfa, rojo, verde y azul en 16 bits, relleno) y escapado como en `iniEscapedString` de Qt."""
    r, g, b = (int(hex6[i:i + 2], 16) for i in (1, 3, 5))
    datos = b"\0\0\0\x43\x01" + b"".join((v * 257).to_bytes(2, "big") for v in (255, r, g, b)) + b"\0\0"
    texto, sigue_hex, comillas = "@Variant(", False, False
    especiales = {0x07: "\\a", 0x08: "\\b", 0x0c: "\\f", 0x0a: "\\n", 0x0d: "\\r", 0x09: "\\t", 0x0b: "\\v"}
    for c in datos:
        ch = chr(c)
        comillas |= ch in ";,="
        if sigue_hex and ch in "0123456789abcdefABCDEF":
            texto += "\\x%x" % c
            continue
        sigue_hex = False
        if c == 0:
            texto, sigue_hex = texto + "\\0", True
        elif c in especiales:
            texto += especiales[c]
        elif ch in '"\\':
            texto += "\\" + ch
        elif c <= 0x1f or c >= 0x7f:
            texto, sigue_hex = texto + "\\x%x" % c, True
        else:
            texto += ch
    texto += ")"
    return f'"{texto}"' if comillas else texto


def entero(hex6: str) -> str:
    return str(int(hex6.lstrip("#"), 16))


def colores(tokens: dict, variante: str) -> dict[str, str]:
    """Clave de QSettings (`grupo/clave`, sin el sufijo del modo) → hex, de la interfaz de Octave."""
    s, _ = paleta(tokens, variante)
    k = ansi(tokens, variante)
    return {
        "terminal/color_f": k["texto"], "terminal/color_b": k["fondo"], "terminal/color_s": s["seleccion.fondo"],
        "terminal/color_c": s["acento.base"],
        "variable_editor/color_f": s["texto.normal"], "variable_editor/color_b": s["fondo.vista"],
        "variable_editor/color_s": s["seleccion.texto"], "variable_editor/color_h": s["seleccion.fondo"],
        "variable_editor/color_a": s["fondo.vista-alterno"],
        "workspaceview/color_a": s["fondo.vista-alterno"], "workspaceview/color_g": s["fondo.ventana-alterno"],
        "workspaceview/color_p": s["fondo.boton"],
        "editor/highlightCurrentLineColor": s["fondo.vista-alterno"],
    }


def estilos(tokens: dict, variante: str) -> dict[str, dict[int, str]]:
    """Lenguaje → estilo → hex del texto, de cada lexer."""
    s, t = paleta(tokens, variante)
    x = sintaxis(s, t)
    return {lengua: {n: x[papel] for n, papel in tabla.items()} for lengua, tabla in LEXERS.items()}


def fragmento(tokens: dict, variante: str) -> dict[str, dict[str, str]]:
    """Sección del ini → clave → valor ya escrito como lo escribe QSettings, de una variante (su modo). Las fuentes
    llevan la familia como marca `@FUENTE@`: la elige el programa al aplicar, entre las instaladas."""
    s, _ = paleta(tokens, variante)
    tam = int(tokens["tipografia"]["tamano-base"]["$value"]["value"])
    salida: dict[str, dict[str, str]] = {}
    for clave, h in colores(tokens, variante).items():
        grupo, nombre = clave.split("/")
        salida.setdefault(grupo, {})[nombre + SUFIJO[variante]] = qcolor(h)
    lexer = salida.setdefault(GRUPO_LEXER[variante], {})
    for lengua, tabla in estilos(tokens, variante).items():
        papeles = LEXERS[lengua]
        for n, h in tabla.items():
            base = f"{lengua}\\style{n}\\"
            lexer[base + "color"] = entero(h)
            lexer[base + "paper"] = entero(s["fondo.vista"])
            lexer[base + "eolfill"] = "false"
            lexer[base + "font"] = f"@FUENTE@, {tam}, 0, {int(papeles[n] in CURSIVA)}, 0"
        lexer[f"{lengua}\\defaultcolor"] = entero(s["texto.normal"])
        lexer[f"{lengua}\\defaultpaper"] = entero(s["fondo.vista"])
        lexer[f"{lengua}\\defaultfont"] = f"@FUENTE@, {tam}, 0, 0, 0"
    return salida


def texto_ini(tokens: dict, marca: dict) -> str:
    lineas = [f"; GENERADO por herramientas/generar.py desde tokens/; no editar",
              f"; {marca['nombre_esquema']['claro']} (primer modo de color) y {marca['nombre_esquema']['oscuro']} (segundo, sufijo _2)",
              "; para $XDG_CONFIG_HOME/octave/octave-gui.ini; lo fusiona octave-lliphi.py (INSTALL.md). @FUENTE@ es la",
              "; familia monoespaciada que elige al aplicar."]
    juntos: dict[str, dict[str, str]] = {}
    for v in ("claro", "oscuro"):
        for grupo, claves in fragmento(tokens, v).items():
            juntos.setdefault(grupo, {}).update(claves)
    for grupo in sorted(juntos):
        lineas += ["", f"[{grupo}]", *(f"{k}={v}" for k, v in sorted(juntos[grupo].items()))]
    return "\n".join(lineas) + "\n"


def texto_programa(tokens: dict, marca: dict) -> str:
    datos = {v: fragmento(tokens, v) for v in ("claro", "oscuro")}
    huella = {v: datos[v]["terminal"]["color_b" + SUFIJO[v]] for v in ("claro", "oscuro")}
    fuentes = list(tokens["tipografia"]["monoespaciada"]["$value"])
    return (FUENTE_PROGRAMA.read_text(encoding="utf-8").replace("@NOMBRE@", marca["nombre"])
            .replace("@CLARO@", marca["nombre_esquema"]["claro"]).replace("@OSCURO@", marca["nombre_esquema"]["oscuro"])
            .replace('"@FRAGMENTO@"', json.dumps(datos, ensure_ascii=False, indent=1, sort_keys=True))
            .replace('"@HUELLA@"', json.dumps(huella, ensure_ascii=False))
            .replace('"@FUENTES@"', json.dumps(fuentes, ensure_ascii=False))
            .replace('"@INTERRUPTORES@"', json.dumps(list(INTERRUPTORES))))


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / f"{marca['id']}.ini", texto_ini(tokens, marca), hechos)
    escribir(destino / PROGRAMA, texto_programa(tokens, marca), hechos)
    (destino / PROGRAMA).chmod(0o755)
    return hechos
