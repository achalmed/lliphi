#!/usr/bin/env python3
"""Lliphi en las aplicaciones GTK que se abren como administrador (decisiones 5.47): «BleachBit as Administrator» y
cualquier otra que se lance con pkexec o sudo.

Como root, su `HOME` es el de root: no leen `~/.config/gtk-3.0/` del usuario y salen con Breeze sin los colores de
Lliphi ni sus botones de ventana. pkexec les quita Wayland, así que van por X11 y toman el tema y los iconos de
xsettingsd, que es de la sesión del usuario; lo que les falta es `gtk.css` y lo que importa. Con `--aplicar` (en un
solo pkexec, que pide la contraseña) se enlazan en `~root/.config/gtk-3.0/` y `gtk-4.0/` esos archivos del usuario:
**enlaces, no copias**, para que sigan a la variante (la vigilancia de fondo-variante cambia la línea de `gtk.css`, y
KDE reescribe `colors.css` y los botones). `settings.ini` no se enlaza: el tema y los iconos llegan por xsettingsd.
No sobrescribe nada de root que no sea ya uno de estos enlaces: si hay un archivo propio, se detiene sin tocar nada.
Deja `UNDO.sh` en `$XDG_STATE_HOME/lliphi/respaldos/<fecha>_gtk-root/`: quita los enlaces (también con pkexec).

Uso:  python3 herramientas/instalar.py gtk-root            # simula
      python3 herramientas/instalar.py gtk-root --aplicar  # enlaza (pide la contraseña)
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "lliphi"
RAIZ_DE_ROOT = "$(getent passwd root | cut -d: -f6)"   # se resuelve dentro de pkexec
# lo que GTK lee de la carpeta del usuario: la hoja (que importa los colores de KDE y los de Lliphi) y los botones
ARCHIVOS = {"gtk-3.0": ["gtk.css", "colors.css", "lliphi-claro.css", "lliphi-oscuro.css", "window_decorations.css", "assets"],
            "gtk-4.0": ["gtk.css", "colors.css", "lliphi.css", "window_decorations.css", "assets"]}


def enlaces() -> list[tuple[str, Path]]:
    """(ruta relativa a `.config` de root, archivo del usuario) de lo que existe en la configuración del usuario."""
    return [(f"{d}/{a}", CONFIG / d / a) for d, nombres in ARCHIVOS.items() for a in nombres if (CONFIG / d / a).exists()]


def guion(raiz: str, pares: list[tuple[str, Path]]) -> str:
    """El programa de sh que corre como root: primero comprueba que ningún destino sea ajeno (sale 3 sin tocar
    nada); después enlaza. `raiz` es una expresión de sh (la carpeta de root, o otra en las pruebas)."""
    lineas = [f"R={raiz}", "ajeno="]
    for rel, origen in pares:
        t, o = f'"$R/.config/{rel}"', shlex.quote(str(origen))
        lineas.append(f'if [ -e {t} ] || [ -L {t} ]; then [ -L {t} ] && [ "$(readlink {t})" = {o} ] '
                      f'|| {{ echo "ajeno: $R/.config/{rel}"; ajeno=1; }}; fi')
    lineas.append('[ -z "$ajeno" ] || exit 3')
    for d in sorted({rel.split("/")[0] for rel, _ in pares}):
        lineas.append(f'mkdir -p "$R/.config/{d}"')
    lineas += [f'ln -sfn {shlex.quote(str(origen))} "$R/.config/{rel}"' for rel, origen in pares]
    return "\n".join(lineas) + "\n"


def guion_deshacer(raiz: str, pares: list[tuple[str, Path]]) -> str:
    """Quita solo los enlaces que siguen apuntando a la configuración del usuario."""
    lineas = [f"R={raiz}"]
    for rel, origen in pares:
        t = f'"$R/.config/{rel}"'
        lineas.append(f'[ -L {t} ] && [ "$(readlink {t})" = {shlex.quote(str(origen))} ] && rm {t}')
    return "\n".join(lineas) + "\ntrue\n"


def main(aplicar: bool | None = None) -> int:
    aplicar = "--aplicar" in sys.argv if aplicar is None else aplicar
    hoja = CONFIG / "gtk-3.0" / "gtk.css"
    if "lliphi-" not in (hoja.read_text(encoding="utf-8", errors="ignore") if hoja.exists() else ""):
        print("GTK de Lliphi no está aplicado (gtk.css no importa una hoja de Lliphi): instala antes el complemento gtk")
        return 1
    pares = enlaces()
    print(f"{'Enlazando' if aplicar else 'SIMULACIÓN:'} GTK de Lliphi para las aplicaciones que corren como root")
    for rel, origen in pares:
        print(f"  {'enlazar' if aplicar else 'SIM enlazar'} ~root/.config/{rel} → {origen}")
    if not aplicar:
        print("nada escrito; añade --aplicar (pedirá la contraseña con pkexec)."); return 0
    if not shutil.which("pkexec"):
        print("falta pkexec"); return 2
    r = subprocess.run(["pkexec", "/bin/sh", "-c", guion(RAIZ_DE_ROOT, pares)])
    if r.returncode == 3:
        print("root ya tiene archivos propios en esos destinos; no se tocó nada"); return 3
    if r.returncode:
        print(f"pkexec terminó con {r.returncode}: no se enlazó nada (¿contraseña cancelada?)"); return 1
    carpeta = STATE / "respaldos" / f"{datetime.now():%Y-%m-%d_%H%M%S}_gtk-root"
    carpeta.mkdir(parents=True, exist_ok=True)
    undo = carpeta / "UNDO.sh"
    undo.write_text("#!/usr/bin/env bash\n# UNDO de GTK de Lliphi para root: quita los enlaces de ~root/.config/gtk-3.0 y gtk-4.0\n"
                    f"pkexec /bin/sh -c {shlex.quote(guion_deshacer(RAIZ_DE_ROOT, pares))} && echo 'enlaces retirados'\n",
                    encoding="utf-8")
    undo.chmod(0o755)
    print(f"  enlazado. Las aplicaciones como root lo toman al abrirse de nuevo.\n  reversión: {undo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
