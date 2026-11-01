"""Aplicación: pone ya la imagen de la variante en los escritorios con un fondo de Lliphi y arranca la vigilancia en la
sesión (el archivo de inicio automático la arranca en las siguientes). Konsole lo cambia la propia vigilancia."""
from __future__ import annotations

import subprocess


def aplicar(ctx) -> int:
    programa = ctx.DATA / ctx.marca["id"] / "seguir-variante.py"
    if "fondo-variante" not in ctx.modulos or not programa.exists():
        return 0
    # una vigilancia que ya corría tiene el programa anterior en memoria: se para y se arranca la recién instalada
    ya = subprocess.run(["pkill", "-f", f"{programa} --vigilar"], capture_output=True).returncode == 0
    subprocess.Popen(["python3", str(programa), "--vigilar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    ctx.decir("el fondo y Konsole siguen a la variante: vigilancia " + ("reiniciada" if ya else "arrancada"))
    return 0
