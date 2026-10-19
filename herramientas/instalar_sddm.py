#!/usr/bin/env python3
"""Instala el inicio de sesión (SDDM) de Lliphi; mejora 7, decisiones 4.11. Es la única pieza que necesita root.

Qué hace con `--aplicar` (en un solo `pkexec`, que pide la contraseña en el diálogo de Plasma):
- copia `generado/sddm/lliphi/` a `/usr/share/sddm/themes/lliphi/`;
- escribe `/etc/sddm.conf.d/99-lliphi.conf` con `[Theme] Current=lliphi` y `Font=Inter…`. SDDM lee `sddm.conf.d/` en orden
  alfabético y el último gana, así que `20-kubuntu.conf` no se toca.
No sobrescribe nada que no sea suyo: si ya existe uno de los dos destinos y no lo instaló Lliphi, se detiene.
Deja `UNDO.sh` en `$XDG_STATE_HOME/lliphi/respaldos/<fecha>_sddm/`: borra lo instalado (también con pkexec) y SDDM
vuelve al tema de Kubuntu en el próximo inicio.

Uso:  python3 herramientas/instalar_sddm.py            # simula
      python3 herramientas/instalar_sddm.py --aplicar  # instala (pide la contraseña)
Vista previa sin root:  sddm-greeter-qt6 --test-mode --theme generado/sddm/lliphi
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "generado" / "sddm" / "lliphi"
TEMA = Path("/usr/share/sddm/themes/lliphi")
CONF = Path("/etc/sddm.conf.d/99-lliphi.conf")
MARCA_CONF = "# Lliphi: tema de inicio de sesión (herramientas/instalar_sddm.py)"
CONTENIDO = f"{MARCA_CONF}\n[Theme]\nCurrent=lliphi\nFont=Inter,10,-1,5,400,0,0,0,0,0\n"
STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "lliphi"


def ajeno() -> list[str]:
    """Destinos ocupados por algo que no instaló Lliphi."""
    malos = []
    if TEMA.exists():
        meta = TEMA / "metadata.desktop"
        if not meta.exists() or "Name=Lliphi" not in meta.read_text(encoding="utf-8", errors="ignore"):
            malos.append(str(TEMA))
    if CONF.exists() and MARCA_CONF not in CONF.read_text(encoding="utf-8", errors="ignore"):
        malos.append(str(CONF))
    return malos


def main() -> int:
    aplicar = "--aplicar" in sys.argv
    if not (ORIGEN / "Main.qml").exists():
        print("falta generado/sddm/lliphi (ejecuta herramientas/generar.py --aplicar)"); return 1
    malos = ajeno()
    if malos:
        print("estos destinos existen y no son de Lliphi; no se tocan:\n  " + "\n  ".join(malos)); return 3
    print(f"{'Instalando' if aplicar else 'SIMULACIÓN:'} inicio de sesión de Lliphi")
    print(f"  {'copiar' if aplicar else 'SIM copiar'} {ORIGEN} → {TEMA}")
    print(f"  {'escribir' if aplicar else 'SIM escribir'} {CONF} (Current=lliphi, Font=Inter)")
    if not aplicar:
        print("nada escrito; añade --aplicar (pedirá la contraseña con pkexec)."); return 0
    if not shutil.which("pkexec"):
        print("falta pkexec"); return 2
    with tempfile.TemporaryDirectory() as tmp:
        conf_tmp = Path(tmp) / "99-lliphi.conf"
        conf_tmp.write_text(CONTENIDO, encoding="utf-8")
        orden = " && ".join([
            f"rm -rf {shlex.quote(str(TEMA))}",
            f"cp -r {shlex.quote(str(ORIGEN))} {shlex.quote(str(TEMA))}",
            f"chmod -R a+rX {shlex.quote(str(TEMA))}",
            f"mkdir -p {shlex.quote(str(CONF.parent))}",
            f"install -m 644 {shlex.quote(str(conf_tmp))} {shlex.quote(str(CONF))}"])
        r = subprocess.run(["pkexec", "/bin/sh", "-c", orden])
    if r.returncode:
        print(f"pkexec terminó con {r.returncode}: no se instaló nada (¿contraseña cancelada?)"); return 1
    carpeta = STATE / "respaldos" / f"{datetime.now():%Y-%m-%d_%H%M%S}_sddm"
    carpeta.mkdir(parents=True, exist_ok=True)
    undo = carpeta / "UNDO.sh"
    undo.write_text("#!/usr/bin/env bash\n# UNDO del inicio de sesión de Lliphi: SDDM vuelve al tema anterior (Kubuntu) en el próximo inicio\n"
                    f"pkexec /bin/sh -c {shlex.quote(f'rm -rf {TEMA} {CONF}')} && echo 'retirados {TEMA} y {CONF}'\n", encoding="utf-8")
    undo.chmod(0o755)
    print(f"  instalado. Se verá en el próximo inicio de sesión.\n  reversión: {undo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
