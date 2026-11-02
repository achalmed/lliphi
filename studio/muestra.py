#!/usr/bin/python3
"""studio/muestra.py — una COPIA ligera del proyecto Lliphi y un HOME falso para las pruebas y las capturas de Lliphi
Studio: nunca el repo real ni la configuración del escritorio (`docs/rediseno.md` S9).

La copia lleva lo que leen y escriben las órdenes (tokens, global, modulos, complementos, herramientas, generado,
fuentes y docs, más VERSION, REUSE.toml, pyproject.toml y README.md), enlaza `muestras/` y el `.venv` del proyecto
(solo se leen) y deja `sitio/` vacío. El entorno devuelto apunta HOME, XDG_* y LLIPHI_DIR a la copia: ninguna ruta de
la máquina en pantalla y ninguna instalación en la sesión de KDE real.

    from muestra import crear
    m = crear(Path(carpeta))      # m.lliphi (la copia), m.casa (el HOME falso), m.entorno
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
CARPETAS = ("tokens", "global", "modulos", "complementos", "herramientas", "generado", "fuentes", "docs")
ARCHIVOS = ("VERSION", "REUSE.toml", "pyproject.toml", "README.md", "requirements.txt")


@dataclass
class Muestra:
    raiz: Path
    lliphi: Path
    casa: Path
    entorno: dict = field(default_factory=dict)


def copiar_proyecto(destino: Path, origen: Path = REPO) -> Path:
    ignorar = shutil.ignore_patterns("__pycache__", ".pytest_cache", "_site", ".quarto", "*.pyc")
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS:
        if (origen / nombre).is_file():
            shutil.copy2(origen / nombre, destino / nombre)
    for carpeta in CARPETAS:
        if (origen / carpeta).is_dir():
            shutil.copytree(origen / carpeta, destino / carpeta, ignore=ignorar, symlinks=True, dirs_exist_ok=True)
    (destino / "sitio").mkdir(exist_ok=True)
    for enlace in ("muestras", ".venv"):
        if (origen / enlace).exists() and not (destino / enlace).exists():
            (destino / enlace).symlink_to(origen / enlace)
    return destino


def crear(raiz: Path, origen: Path = REPO) -> Muestra:
    raiz = Path(raiz)
    lliphi = copiar_proyecto(raiz / "lliphi", origen)
    casa = raiz / "casa"
    for sub in (".config", ".cache", ".local/share", ".local/state"):
        (casa / sub).mkdir(parents=True, exist_ok=True)
    entorno = {"HOME": str(casa), "XDG_CONFIG_HOME": str(casa / ".config"), "XDG_CACHE_HOME": str(casa / ".cache"), "XDG_DATA_HOME": str(casa / ".local" / "share"),
               "XDG_STATE_HOME": str(casa / ".local" / "state"), "LLIPHI_DIR": str(lliphi), "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    return Muestra(raiz=raiz, lliphi=lliphi, casa=casa, entorno=entorno)


if __name__ == "__main__":
    import sys
    m = crear(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "muestra-lliphi")
    print(m.lliphi)
