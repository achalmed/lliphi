"""Aplicación en GNU Octave (decisiones 5.41): el programa instalado (`variante.d/octave.py`, que es
`generado/octave/octave-lliphi.py`) fusiona los colores de Lliphi en `octave-gui.ini` y elige el modo de color de la
variante; lo demás del archivo no se toca. El archivo se respalda antes de instalar. Si Octave nunca se abrió, no se crea
nada (lo dice)."""
from __future__ import annotations

import sys


def respaldos(ctx) -> list:
    return [(ctx.CONFIG / "octave" / "octave-gui.ini", "reponer", "preferencias de Octave")]


def aplicar(ctx) -> int:
    programa = ctx.DATA / ctx.marca["id"] / "variante.d" / "octave.py"
    if "octave" not in ctx.modulos or not programa.exists():
        return 0
    r = ctx.ejecutar([sys.executable, str(programa), ctx.variante, "--colores", "--aplicar"])
    for linea in (r.stdout + r.stderr).splitlines():
        ctx.decir(linea)
    return r.returncode
