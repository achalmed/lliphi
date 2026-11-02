"""Aplicación: pone ya la imagen de la variante en los escritorios con un fondo de Lliphi y arranca la vigilancia en la
sesión (el archivo de inicio automático la arranca en las siguientes). Konsole lo cambia la propia vigilancia."""
from __future__ import annotations

import os
import shutil
import subprocess


def misma_sesion() -> bool:
    """El systemd de usuario es el de esta sesión (mismo HOME y misma pantalla). En la sesión de prueba anidada no lo
    es: la vigilancia arrancada por él correría en el escritorio real."""
    if not shutil.which("systemd-run"):
        return False
    r = subprocess.run(["systemctl", "--user", "show-environment"], capture_output=True, text=True)
    if r.returncode != 0:
        return False
    entorno = dict(linea.split("=", 1) for linea in r.stdout.splitlines() if "=" in linea)
    return all(entorno.get(k) == os.environ.get(k) for k in ("HOME", "WAYLAND_DISPLAY", "DISPLAY"))


def aplicar(ctx) -> int:
    programa = ctx.DATA / ctx.marca["id"] / "seguir-variante.py"
    if "fondo-variante" not in ctx.modulos or not programa.exists():
        return 0
    # una vigilancia que ya corría tiene el programa anterior en memoria: se para y se arranca la recién instalada
    unidad = f"{ctx.marca['id']}-fondo-variante"
    subprocess.run(["systemctl", "--user", "stop", unidad], capture_output=True)
    ya = subprocess.run(["pkill", "-f", f"{programa} --vigilar"], capture_output=True).returncode == 0
    # en una unidad propia del systemd de usuario: arrancada desde un programa (una terminal, un asistente), seguiría en
    # su grupo de procesos y se pararía al cerrarlo (decisiones 5.45)
    if not (misma_sesion() and subprocess.run(
            ["systemd-run", "--user", "--collect", f"--unit={unidad}", f"--description={ctx.marca['nombre']}: el fondo, "
             "Konsole y GTK siguen a la variante", "python3", str(programa), "--vigilar"], capture_output=True).returncode == 0):
        subprocess.Popen(["python3", str(programa), "--vigilar"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    ctx.decir("el fondo y Konsole siguen a la variante: vigilancia " + ("reiniciada" if ya else "arrancada"))
    return 0
