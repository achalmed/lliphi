#!/usr/bin/env python3
"""Lliphi: el fondo y Konsole siguen a la variante. GENERADO por herramientas/generar.py desde complementos/fondo-variante; no editar.

Al cambiar el tema global (o el esquema de color) entre Lliphi Claro y Lliphi Oscuro, Plasma no cambia el fondo;
y si el fondo es un paquete con imagen clara y oscura, elige por los colores del estilo de Plasma, que no siempre son
los de la variante. Este programa mira el esquema de color (`[General] ColorScheme` de kdeglobals) y pone en
cada escritorio, del mismo paquete de fondo de Lliphi que ya tenga (`org.lliphi.*`), la imagen de la variante:
`contents/images/` en el claro y `contents/images_dark/` en el oscuro. Si el esquema o el fondo no son de Lliphi,
no toca nada.

Konsole tampoco sigue a la variante: si el perfil por defecto (`konsolerc` → DefaultProfile) usa un esquema de
Lliphi, se le pone el de la variante (ventanas nuevas) y se cambia en las sesiones abiertas con ese esquema, con la
secuencia de Konsole `ESC ] 50 ; ColorScheme=… BEL` escrita en su terminal (la de `konsoleprofile`); un perfil con
otro esquema no se toca.

Los programas que no cambian solos de variante (RStudio, Octave, Spyder) instalan cada uno el suyo en
`variante.d/`, junto a este: en cada cambio se ejecuta `variante.d/<programa>.py <variante> --aplicar` (sin
`--aplicar` al simular), y cada uno decide si le toca (decisiones 5.43).

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
KONSOLE = {"claro": "Lliphi Claro", "oscuro": "Lliphi Oscuro"}
DATA = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
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


def perfil_konsole() -> Path | None:
    """El perfil por defecto de Konsole, si es un archivo del usuario."""
    rc = CONFIG / "konsolerc"
    if not rc.exists():
        return None
    m = re.search(r"^DefaultProfile=(.+)$", rc.read_text(encoding="utf-8", errors="ignore"), re.M)
    perfil = DATA / "konsole" / m.group(1).strip() if m else None
    return perfil if perfil and perfil.exists() else None


def esquema_del_perfil(perfil: Path) -> str | None:
    grupo = None
    for linea in perfil.read_text(encoding="utf-8", errors="ignore").splitlines():
        if linea.startswith("["):
            grupo = linea.strip()
        elif grupo == "[Appearance]" and linea.startswith("ColorScheme="):
            return linea.split("=", 1)[1].strip()
    return None


def fijar_esquema(perfil: Path, esquema: str) -> None:
    """Cambia solo `ColorScheme=` de [Appearance]; en el archivo real, para no romper un enlace de dotfiles."""
    real, grupo, salida = perfil.resolve(), None, []
    for linea in real.read_text(encoding="utf-8").splitlines():
        if linea.startswith("["):
            grupo = linea.strip()
        elif grupo == "[Appearance]" and linea.startswith("ColorScheme="):
            linea = f"ColorScheme={esquema}"
        salida.append(linea)
    real.write_text("\n".join(salida) + "\n", encoding="utf-8")


def terminales_abiertas() -> list[str]:
    """Las terminales (/dev/pts/N) de las sesiones de Konsole abiertas, por su proceso."""
    qdbus = herramienta("qdbus6")
    if not qdbus:
        return []
    salida = []
    servicios = subprocess.run([qdbus], capture_output=True, text=True, timeout=10).stdout.split()
    for servicio in (s for s in servicios if s.startswith("org.kde.konsole-")):
        rutas = subprocess.run([qdbus, servicio], capture_output=True, text=True, timeout=10).stdout.split()
        for ruta in (r for r in rutas if re.fullmatch(r"/Sessions/\d+", r)):
            pid = subprocess.run([qdbus, servicio, ruta, "org.kde.konsole.Session.processId"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
            try:
                tty = os.readlink(f"/proc/{int(pid)}/fd/0")
            except (ValueError, OSError):
                continue
            if tty.startswith("/dev/pts/") and tty not in salida:
                salida.append(tty)
    return salida


def konsole(var: str, escribir: bool) -> None:
    perfil = perfil_konsole()
    actual = esquema_del_perfil(perfil) if perfil else None
    if actual not in KONSOLE.values():
        return                                       # sin perfil propio, o con un esquema que no es de Lliphi
    if actual == KONSOLE[var]:
        return
    print(f"{'' if escribir else 'SIM '}Konsole: {perfil.name} {actual} → {KONSOLE[var]}")
    if not escribir:
        return
    fijar_esquema(perfil, KONSOLE[var])
    for tty in terminales_abiertas():
        try:
            with open(tty, "w", encoding="utf-8") as t:
                t.write(f"\033]50;ColorScheme={KONSOLE[var]}\007")
        except OSError:
            pass


def una_vez(escribir: bool) -> None:
    lista = cambios()
    for i, vieja, nueva in lista:
        print(f"{'escritorio' if escribir else 'SIM escritorio'} {i}: {Path(urlparse(vieja).path).name} → {nueva}")
    if escribir and lista:
        aplicar(lista)
    if not lista:
        print("nada que cambiar en el fondo (ya es el de la variante, o no es de Lliphi)")
    var = variante()
    if var:
        konsole(var, escribir)
        programas(var, escribir)


def programas(var: str, escribir: bool) -> None:
    """Los programas de `variante.d/` (decisiones 5.43): cada uno cambia el suyo, si es de Lliphi."""
    carpeta = Path(__file__).resolve().parent / "variante.d"
    for programa in sorted(carpeta.glob("*.py")) if carpeta.is_dir() else []:
        try:
            r = subprocess.run([sys.executable, str(programa), var, *(["--aplicar"] if escribir else [])],
                               capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as e:
            print(f"{programa.name}: {e}", file=sys.stderr)
            continue
        for linea in (r.stdout + r.stderr).splitlines():
            print(linea)


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
