"""Aplicación en Spyder (decisiones 5.42): el programa instalado (`variante.d/spyder.py`, que es
`generado/spyder/spyder-lliphi.py`) escribe los esquemas de Lliphi en `spyder.ini`, pone la interfaz en automático y
elige el esquema de la variante; lo demás del archivo no se toca. El archivo se respalda antes de instalar. Con Spyder
abierto, o si nunca se abrió, no se escribe nada (lo dice)."""
from __future__ import annotations

import sys


def respaldos(ctx) -> list:
    return [(ctx.CONFIG / "spyder-py3" / "config" / "spyder.ini", "reponer", "preferencias de Spyder")]


def aplicar(ctx) -> int:
    programa = ctx.DATA / ctx.marca["id"] / "variante.d" / "spyder.py"
    if "spyder" not in ctx.modulos or not programa.exists():
        return 0
    r = ctx.ejecutar([sys.executable, str(programa), ctx.variante, "--esquemas", "--aplicar"])
    for linea in (r.stdout + r.stderr).splitlines():
        ctx.decir(linea)
    return r.returncode
