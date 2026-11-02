#!/usr/bin/env python3
"""@NOMBRE@ en GNU Octave. GENERADO por herramientas/generar.py desde complementos/octave; no editar.

Octave guarda dos «modos de color» a la vez (Preferencias → «Second color mode (light/dark)»): este programa pone
«@CLARO@» en el primero y «@OSCURO@» en el segundo, en el editor, la ventana de órdenes, el editor de variables y el
espacio de trabajo, y elige el modo de la variante. Edita solo esas claves de `octave-gui.ini`: lo demás (ventanas,
atajos, archivos recientes) queda como estaba. Octave lee los colores al arrancar: el cambio se ve al abrirlo de nuevo.

Uso:  octave-lliphi.py claro|oscuro                     # simula: dice qué cambiaría
      octave-lliphi.py claro|oscuro --colores --aplicar # escribe los colores de @NOMBRE@ y elige el modo
      octave-lliphi.py claro|oscuro --aplicar           # solo cambia de modo, si los colores ya son de @NOMBRE@
Sin `--colores` no toca un Octave con otros colores: así lo llama la vigilancia de fondo-variante en cada cambio de
variante. Si Octave nunca se abrió (no hay `octave-gui.ini`), no crea nada. Solo biblioteca estándar.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

FRAGMENTO = "@FRAGMENTO@"
HUELLA = "@HUELLA@"                  # terminal/color_b de cada modo: si coinciden, los colores son de @NOMBRE@
FUENTES = "@FUENTES@"
INTERRUPTORES = "@INTERRUPTORES@"
MODO = {"claro": "0", "oscuro": "1"}
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
INI = CONFIG / "octave" / "octave-gui.ini"


def leer(texto: str) -> dict[str, dict[str, str]]:
    secciones: dict[str, dict[str, str]] = {}
    grupo = "General"
    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            grupo = linea.strip()[1:-1]
        elif "=" in linea and not linea.startswith(";"):
            clave, valor = linea.split("=", 1)
            secciones.setdefault(grupo, {})[clave] = valor
    return secciones


def fusionar(texto: str, cambios: dict[str, dict[str, str]], si_falta: set[str] = frozenset()) -> str:
    """El ini con `cambios` (sección → clave → valor): reemplaza la línea de cada clave en su sección o la añade al
    final de la sección (o en una sección nueva); las demás líneas quedan tal cual. Las claves cuyo nombre acaba en
    algo de `si_falta` solo se escriben si no estaban (las fuentes que eligió el usuario se conservan)."""
    pendientes = {g: dict(c) for g, c in cambios.items()}
    salida: list[str] = []
    grupo = "General"

    def cerrar(g: str) -> None:
        resto = pendientes.pop(g, {})
        if resto:
            while salida and salida[-1] == "":
                salida.pop()
            salida.extend(f"{k}={v}" for k, v in resto.items())
            salida.append("")

    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            cerrar(grupo)
            grupo = linea.strip()[1:-1]
        elif "=" in linea and grupo in pendientes:
            clave = linea.split("=", 1)[0]
            if clave in pendientes[grupo]:
                valor = pendientes[grupo].pop(clave)
                if not any(clave.endswith(f) for f in si_falta):
                    linea = f"{clave}={valor}"
        salida.append(linea)
    cerrar(grupo)
    for g in list(pendientes):
        if pendientes[g]:
            if salida and salida[-1] != "":
                salida.append("")
            salida += [f"[{g}]", *(f"{k}={v}" for k, v in pendientes.pop(g).items()), ""]
    while salida and salida[-1] == "":
        salida.pop()
    return "\n".join(salida) + ("\n\n" if texto.endswith("\n\n") else "\n")


def fuente() -> str:
    """La primera familia monoespaciada de @NOMBRE@ que esté instalada (fc-list), o la monoespaciada del sistema."""
    fc = shutil.which("fc-list")
    for familia in FUENTES:
        if familia == "monospace" or not fc:
            break
        if subprocess.run([fc, f":family={familia}"], capture_output=True, text=True).stdout.strip():
            return familia
    return "Monospace"


def interruptores(var: str) -> dict[str, dict[str, str]]:
    cambios: dict[str, dict[str, str]] = {}
    for clave in INTERRUPTORES:
        grupo, nombre = clave.split("/")
        cambios.setdefault(grupo, {})[nombre] = MODO[var]
    return cambios


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in MODO:
        print(__doc__.split("\n\n")[2], file=sys.stderr)
        return 1
    var, escribir, colores = argv[0], "--aplicar" in argv, "--colores" in argv
    if not INI.exists():
        if colores:
            print(f"Octave: no hay {INI}; abre Octave una vez (su asistente lo crea) y vuelve a aplicar")
        return 0
    real = INI.resolve()                         # el archivo real: un enlace de dotfiles (stow) se conserva
    texto = real.read_text(encoding="utf-8")
    actual = leer(texto)
    terminal = actual.get("terminal", {})
    propios = terminal.get("color_b") == HUELLA["claro"] and terminal.get("color_b_2") == HUELLA["oscuro"]
    if not colores and not propios:
        return 0                                  # otros colores: la vigilancia no los toca
    cambios = interruptores(var)
    if colores:
        familia = fuente()
        for v in ("claro", "oscuro"):
            for grupo, claves in FRAGMENTO[v].items():
                cambios.setdefault(grupo, {}).update({k: x.replace("@FUENTE@", familia) for k, x in claves.items()})
    nuevo = fusionar(texto, cambios, si_falta={"\\font", "\\defaultfont"})
    if nuevo == texto:
        return 0
    modo = "segundo" if MODO[var] == "1" else "primer"
    que = "colores de @NOMBRE@ y " if colores and not propios else ""
    print(f"{'' if escribir else 'SIM '}Octave: {que}{modo} modo de color ({'@OSCURO@' if var == 'oscuro' else '@CLARO@'}); se ve al abrir Octave")
    if escribir:
        temporal = real.with_name(real.name + ".lliphi")
        temporal.write_text(nuevo, encoding="utf-8")
        temporal.replace(real)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
