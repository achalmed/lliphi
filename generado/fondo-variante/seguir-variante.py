#!/usr/bin/env python3
"""Lliphi: el fondo sigue a la variante. GENERADO por herramientas/generar.py desde complementos/fondo-variante; no editar.

Al cambiar el tema global (o el esquema de color) entre Lliphi Claro y Lliphi Oscuro, Plasma no cambia el fondo;
y si el fondo es un paquete con imagen clara y oscura, elige por los colores del estilo de Plasma, que en el claro
declara su panel oscuro. Este programa mira el esquema de color (`[General] ColorScheme` de kdeglobals) y pone en
cada escritorio, del mismo paquete de fondo de Lliphi que ya tenga (`org.lliphi.*`), la imagen de la variante:
`contents/images/` en el claro y `contents/images_dark/` en el oscuro. Si el esquema o el fondo no son de Lliphi,
no toca nada.

Uso:  seguir-variante.py              # simula: dice qué cambiaría
      seguir-variante.py --aplicar    # lo cambia una vez
      seguir-variante.py --vigilar    # lo cambia ahora y cada vez que KDE avisa de un cambio de colores (sesión)
Solo biblioteca estándar; usa kreadconfig6, qdbus6 y dbus-monitor.
"""
from __future__ import annotations

import os
import re
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

DOMINIO = "org.lliphi"
VARIANTES = {"LliphiClaro": "claro", "LliphiOscuro": "oscuro"}
CARPETA = {"claro": "images", "oscuro": "images_dark"}
DATA = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
LEER = """var d = desktops(); var r = [];
for (var i = 0; i < d.length; i++) { d[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
  r.push(i + "\\t" + d[i].wallpaperPlugin + "\\t" + d[i].readConfig("Image")); }
print(r.join("\\n"));"""


def herramienta(nombre: str) -> str | None:
    return shutil.which(nombre, path="/usr/bin:/usr/local/bin:/bin") or shutil.which(nombre)


def variante() -> str | None:
    r = subprocess.run([herramienta("kreadconfig6") or "kreadconfig6", "--file", "kdeglobals", "--group", "General",
                        "--key", "ColorScheme"], capture_output=True, text=True)
    return VARIANTES.get(r.stdout.strip())


def guion(js: str) -> str:
    r = subprocess.run([herramienta("qdbus6") or "qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                        "org.kde.PlasmaShell.evaluateScript", js], capture_output=True, text=True, timeout=20)
    return r.stdout


def imagen_para(url: str, var: str) -> str | None:
    """La imagen de la variante del mismo paquete de fondo de Lliphi, o None si el fondo no es de Lliphi."""
    ruta = Path(unquote(urlparse(url).path)) if url.startswith("file:") else Path(url)
    try:
        rel = ruta.relative_to(DATA / "wallpapers")
    except ValueError:
        return None
    paquete = rel.parts[0] if rel.parts else ""
    if not paquete.startswith(DOMINIO + "."):
        return None
    carpeta = DATA / "wallpapers" / paquete / "contents" / CARPETA[var]
    if not carpeta.is_dir():
        return None
    candidatas = sorted((p for p in carpeta.iterdir() if re.fullmatch(r"\d+x\d+\.(png|jpe?g)", p.name)),
                        key=lambda p: int(p.stem.split("x")[0]) * int(p.stem.split("x")[1]))
    if not candidatas:
        return None
    misma = carpeta / ruta.name
    elegida = misma if misma in candidatas else candidatas[-1]   # el mismo tamaño si lo hay; si no, el mayor
    return elegida.as_uri()


def cambios() -> list[tuple[int, str, str]]:
    var = variante()
    if var is None:
        return []
    salida = []
    for linea in guion(LEER).splitlines():
        partes = linea.split("\t")
        if len(partes) != 3 or partes[1] != "org.kde.image":
            continue
        nueva = imagen_para(partes[2], var)
        if nueva and nueva != partes[2]:
            salida.append((int(partes[0]), partes[2], nueva))
    return salida


def aplicar(lista: list[tuple[int, str, str]]) -> None:
    js = "var d = desktops();\n" + "".join(
        f'd[{i}].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]; d[{i}].writeConfig("Image", "{nueva}");\n'
        for i, _vieja, nueva in lista)
    guion(js)


def una_vez(escribir: bool) -> None:
    lista = cambios()
    for i, vieja, nueva in lista:
        print(f"{'escritorio' if escribir else 'SIM escritorio'} {i}: {Path(urlparse(vieja).path).name} → {nueva}")
    if escribir and lista:
        aplicar(lista)
    if not lista:
        print("nada que cambiar (el fondo ya es el de la variante, o no es de Lliphi)")


def vigilar() -> int:
    una_vez(True)
    monitor = herramienta("dbus-monitor")
    if not monitor:
        print("falta dbus-monitor", file=sys.stderr)
        return 2
    proc = subprocess.Popen([monitor, "--session", "type='signal',interface='org.kde.KGlobalSettings',member='notifyChange'"],
                            stdout=subprocess.PIPE, text=True)
    pendiente = 0.0
    while proc.poll() is None:
        listo, _, _ = select.select([proc.stdout], [], [], 1.0)
        if listo:
            if "notifyChange" in proc.stdout.readline():
                pendiente = time.monotonic() + 1.5   # el cambio de tema avisa varias veces: se espera a que acabe
        elif pendiente and time.monotonic() >= pendiente:
            pendiente = 0.0
            try:
                una_vez(True)
            except (OSError, subprocess.SubprocessError) as e:
                print(f"no se pudo cambiar el fondo: {e}", file=sys.stderr)
    return proc.returncode or 0


if __name__ == "__main__":
    if "--vigilar" in sys.argv:
        sys.exit(vigilar())
    una_vez("--aplicar" in sys.argv)
