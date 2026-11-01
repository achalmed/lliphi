#!/usr/bin/env python3
"""Instala, aplica, actualiza, comprueba y desinstala el tema en el usuario actual, con simulación, respaldo y reversión.

Solo escribe en `$XDG_DATA_HOME` (`~/.local/share`), `$XDG_CONFIG_HOME` (`~/.config`) y, para la extensión de los
editores, en `~/.vscode/extensions/` y en Positron y VSCodium si existen; nunca en `/usr` (salvo `sddm`, con pkexec).
Qué instala cada módulo lo dice su `modulo.json`; el núcleo está en `herramientas/nucleo/instalacion.py`
(docs/arquitectura.md). Antes de tocar nada respalda la configuración que cambia Plasma al aplicar un tema, con su
SHA-256 verificada, en `$XDG_STATE_HOME/<id>/respaldos/<fecha>/` y deja allí un `UNDO.sh` que restaura byte a byte y
desinstala. Lo instalado queda anotado en `$XDG_STATE_HOME/<id>/instalado.json`.

Uso:
  python3 herramientas/instalar.py                       simula la instalación (no escribe nada)
  python3 herramientas/instalar.py --aplicar             instala los módulos
  python3 herramientas/instalar.py --aplicar --aplicar-tema oscuro|claro   además aplica el tema global en la sesión
  python3 herramientas/instalar.py --modulos esquema,konsole --aplicar
  python3 herramientas/instalar.py --dependencias --aplicar   además instala lo de terceros (como `dependencias`)
  python3 herramientas/instalar.py dependencias [--aplicar] [--opcionales]   Papirus, cursores y tipografías, sin root
  python3 herramientas/instalar.py comprobar             lo instalado está completo, es de esta versión y KDE lo reconoce
  python3 herramientas/instalar.py estado                qué hay instalado y si se modificó
  python3 herramientas/instalar.py desinstalar [--aplicar]
  python3 herramientas/instalar.py sddm [--aplicar]      inicio de sesión SDDM (pkexec; complementos/sddm)
Solo biblioteca estándar; Python ≥ 3.10. Sale 0 bien, 1 error de uso, 2 falta una dependencia, 3 conflicto,
4 la comprobación encontró faltas.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nucleo import instalacion, registro  # noqa: E402


def main() -> int:
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__); return 0
    aplicar = "--aplicar" in args
    seleccion = registro.ids()
    if "--modulos" in args:
        seleccion = args[args.index("--modulos") + 1].split(",")
        desconocidos = [m for m in seleccion if m not in registro.ids()]
        if desconocidos:
            print("módulos desconocidos:", ", ".join(desconocidos), "\nmódulos:", ", ".join(registro.ids())); return 1
    aplicar_tema = args[args.index("--aplicar-tema") + 1] if "--aplicar-tema" in args else None
    if aplicar_tema and aplicar_tema not in ("claro", "oscuro"):
        print("--aplicar-tema claro|oscuro"); return 1
    if "dependencias" in args or "--dependencias" in args:
        r = instalacion.dependencias(aplicar, "--opcionales" in args)
        if r or "dependencias" in args:
            return r
    if "sddm" in args:
        return registro.codigo("sddm", "instalar_sddm").main(aplicar)
    if "desinstalar" in args:
        return instalacion.desinstalar(aplicar)
    if "estado" in args:
        return instalacion.estado()
    if "comprobar" in args:
        return instalacion.comprobar()
    return instalacion.instalar(seleccion, aplicar, aplicar_tema)


if __name__ == "__main__":
    sys.exit(main())
