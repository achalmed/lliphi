"""Aplicación: pone ya la imagen de la variante en los escritorios con un fondo de Lliphi y arranca la vigilancia en la
sesión (el archivo de inicio automático la arranca en las siguientes)."""
from __future__ import annotations

import subprocess


def aplicar(ctx) -> int:
    programa = ctx.DATA / ctx.marca["id"] / "seguir-variante.py"
    if "fondo-variante" not in ctx.modulos or not programa.exists():
        return 0
    ya = subprocess.run(["pgrep", "-f", f"{programa} --vigilar"], capture_output=True).returncode == 0
    if not ya:
        subprocess.Popen(["python3", str(programa), "--vigilar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    ctx.decir("el fondo sigue a la variante" + (" (ya vigilaba)" if ya else ": vigilancia arrancada"))
    return 0
