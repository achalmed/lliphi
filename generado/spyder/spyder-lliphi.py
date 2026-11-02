#!/usr/bin/env python3
"""Lliphi en Spyder. GENERADO por herramientas/generar.py desde complementos/spyder; no editar.

Escribe en `spyder.ini` los esquemas de sintaxis «Lliphi Claro» y «Lliphi Oscuro», pone la interfaz en automático (clara u
oscura según el esquema) y elige el de la variante; y, si la consola no ejecuta ya otro archivo al arrancar, le pone
`consola.py`, que da a la consola IPython los dieciséis colores de la terminal. Solo cambia esas claves; lo demás de
`spyder.ini` queda como estaba. Spyder reescribe el archivo entero mientras está abierto: con Spyder abierto no se
toca nada (lo dice).

Uso:  spyder-lliphi.py claro|oscuro                        # simula: dice qué cambiaría
      spyder-lliphi.py claro|oscuro --esquemas --aplicar   # escribe los esquemas y elige el de la variante
      spyder-lliphi.py claro|oscuro --aplicar              # solo cambia de esquema, si el elegido es de Lliphi
Sin `--esquemas` no toca un Spyder con otro esquema: así lo llama la vigilancia de fondo-variante en cada cambio de
variante. Si Spyder nunca se abrió (no hay `spyder.ini`), no crea nada. Solo biblioteca estándar.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

ESQUEMAS = {'lliphi/claro': {'name': 'Lliphi Claro',
                  'background': '#fbfcfd',
                  'currentline': '#f2f3f5',
                  'currentcell': '#ecedef',
                  'occurrence': '#ccced2',
                  'ctrlclick': '#2a4fd0',
                  'sideareas': '#fbfcfd',
                  'matched_p': '#ccced2',
                  'unmatched_p': '#b63132',
                  'normal': ('#1d1f24', False, False),
                  'keyword': ('#a43b38', False, False),
                  'magic': ('#8e4088', False, False),
                  'builtin': ('#345fb2', False, False),
                  'definition': ('#345fb2', True, False),
                  'comment': ('#66676c', False, True),
                  'string': ('#007835', False, False),
                  'number': ('#7e5e00', False, False),
                  'instance': ('#8e4088', False, True)},
 'lliphi/oscuro': {'name': 'Lliphi Oscuro',
                   'background': '#101012',
                   'currentline': '#161719',
                   'currentcell': '#1b1c1e',
                   'occurrence': '#3d3e42',
                   'ctrlclick': '#ff968b',
                   'sideareas': '#101012',
                   'matched_p': '#3d3e42',
                   'unmatched_p': '#fb817a',
                   'normal': ('#eaebed', False, False),
                   'keyword': ('#f28881', False, False),
                   'magic': ('#d98cd2', False, False),
                   'builtin': ('#7daafd', False, False),
                   'definition': ('#7daafd', True, False),
                   'comment': ('#97989c', False, True),
                   'string': ('#69c27e', False, False),
                   'number': ('#d0a43a', False, False),
                   'instance': ('#d98cd2', False, True)}}
NOMBRES = {"claro": "lliphi/claro", "oscuro": "lliphi/oscuro"}
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
DATA = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
CARPETA = CONFIG / "spyder-py3"
INI = CARPETA / "config" / "spyder.ini"
CONSOLA = DATA / "lliphi" / "spyder" / "consola.py"


def abierto() -> bool:
    """Spyder está abierto si su cerrojo (`spyder.lock`, un enlace al PID) apunta a un proceso de Spyder vivo."""
    try:
        pid = int(os.readlink(CARPETA / "spyder.lock"))
        return b"spyder" in Path(f"/proc/{pid}/cmdline").read_bytes()
    except (OSError, ValueError):
        return False


def valor(v: object) -> str:
    """Un valor como lo escribe Spyder: las tuplas `(color, negrita, cursiva)` por su repr; las cadenas, tal cual."""
    return v if isinstance(v, str) else repr(v)


def leer(texto: str) -> dict[str, dict[str, str]]:
    secciones: dict[str, dict[str, str]] = {}
    grupo = None
    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            grupo = linea.strip()[1:-1]
        elif grupo and "=" in linea:
            clave, v = linea.split("=", 1)
            secciones.setdefault(grupo, {})[clave.strip()] = v.strip()
    return secciones


def fusionar(texto: str, cambios: dict[str, dict[str, str]]) -> str:
    """El ini con `cambios` (sección → clave → valor), en el formato `clave = valor` de Spyder: reemplaza la línea de
    cada clave en su sección o la añade al final de la sección; las demás líneas quedan tal cual."""
    pendientes = {g: dict(c) for g, c in cambios.items()}
    salida: list[str] = []
    grupo = None

    def cerrar(g: str | None) -> None:
        resto = pendientes.pop(g, {}) if g else {}
        if resto:
            while salida and salida[-1] == "":
                salida.pop()
            salida.extend(f"{k} = {v}" for k, v in resto.items())
            salida.append("")

    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            cerrar(grupo)
            grupo = linea.strip()[1:-1]
        elif grupo in pendientes and "=" in linea:
            clave = linea.split("=", 1)[0].strip()
            if clave in pendientes[grupo]:
                linea = f"{clave} = {pendientes[grupo].pop(clave)}"
        salida.append(linea)
    cerrar(grupo)
    for g, resto in pendientes.items():
        if resto:
            if salida and salida[-1] != "":
                salida.append("")
            salida += [f"[{g}]", *(f"{k} = {v}" for k, v in resto.items()), ""]
    while salida and salida[-1] == "":
        salida.pop()
    return "\n".join(salida) + ("\n\n" if texto.endswith("\n\n") else "\n")


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in NOMBRES:
        print(__doc__.split("\n\n")[2], file=sys.stderr)
        return 1
    var, escribir, esquemas = argv[0], "--aplicar" in argv, "--esquemas" in argv
    if not INI.exists():
        if esquemas:
            print(f"Spyder: no hay {INI}; abre Spyder una vez y vuelve a aplicar")
        return 0
    real = INI.resolve()                          # el archivo real: un enlace de dotfiles (stow) se conserva
    texto = real.read_text(encoding="utf-8")
    actual = leer(texto)
    apariencia = actual.get("appearance", {})
    elegido = apariencia.get("selected", "").strip("'\"")
    if not esquemas and elegido not in NOMBRES.values():
        return 0                                  # otro esquema: la vigilancia no lo toca
    cambios: dict[str, dict[str, str]] = {"appearance": {"selected": NOMBRES[var]}}
    avisos = []
    if esquemas:
        try:
            nombres = list(ast.literal_eval(apariencia.get("names", "[]")))
        except (ValueError, SyntaxError):
            nombres = []
        for esquema, claves in ESQUEMAS.items():
            cambios["appearance"].update({f"{esquema}/{k}": valor(v) for k, v in claves.items()})
        cambios["appearance"]["names"] = repr(sorted(set(nombres) | set(ESQUEMAS)))
        cambios["appearance"]["ui_theme"] = "automatic"
        consola = actual.get("ipython_console", {})
        archivo = consola.get("startup/run_file", "").strip("'\"")
        if archivo in ("", str(CONSOLA)):
            cambios["ipython_console"] = {"startup/use_run_file": "True", "startup/run_file": str(CONSOLA)}
        else:
            avisos.append(f"la consola ya ejecuta {archivo} al arrancar: no se le ponen los colores ANSI (INSTALL.md)")
    nuevo = fusionar(texto, cambios)
    if nuevo == texto:
        return 0
    if abierto():
        print(f"Spyder está abierto: cierra Spyder y vuelve a aplicar (esquema {ESQUEMAS[NOMBRES[var]]['name']})")
        return 0
    nombre = ESQUEMAS[NOMBRES[var]]["name"]
    print(f"{'' if escribir else 'SIM '}Spyder: {'esquemas de Lliphi, interfaz automática y ' if esquemas else ''}esquema {nombre}; se ve al abrir Spyder")
    for aviso in avisos:
        print(f"  {aviso}")
    if escribir:
        temporal = real.with_name(real.name + ".lliphi")
        temporal.write_text(nuevo, encoding="utf-8")
        temporal.replace(real)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
