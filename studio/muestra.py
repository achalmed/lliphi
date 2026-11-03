#!/usr/bin/python3
"""studio/muestra.py — una COPIA ligera del proyecto Lliphi y un HOME falso para las pruebas y las capturas de Lliphi
Studio: nunca el repo real ni la configuración del escritorio (`docs/rediseno.md` S9; sigue en la 3.0, `docs/reingenieria.md`).

La copia lleva lo que leen y escriben las órdenes (tokens, global, modulos, complementos, herramientas, generado,
fuentes y docs, más VERSION, REUSE.toml, pyproject.toml, README.md y CHANGELOG.md, que lee `generar.py verificar`), enlaza `muestras/` y el `.venv` del proyecto
(solo se leen) y de `sitio/` solo `generado/` (lo que `generar.py` escribe y `verificar` compara). El entorno devuelto apunta HOME, XDG_* y LLIPHI_DIR a la copia: ninguna ruta de
la máquina en pantalla y ninguna instalación en la sesión de KDE real.

`generado/` y `sitio/generado/` pesan unos 70 MB. Una copia **de solo lectura** (`solo_lectura=True`: ver, simular,
capturar, instalar en el HOME falso, que lee de `generado/` y escribe en la casa) los **enlaza** en vez de copiarlos
(2026-11-03); la que vaya a generar de verdad los copia (`generar.py --aplicar` reescribe esos archivos en su sitio, y
a través de un enlace reescribiría los del repo). La marca `.solo-lectura` en la carpeta de la muestra lo recuerda, y
las pruebas comprueban al terminar que el `generado/` del repo no cambió.

    from muestra import crear
    m = crear(Path(carpeta))                     # m.lliphi (la copia), m.casa (el HOME falso), m.entorno
    m = crear(Path(carpeta), solo_lectura=True)  # lo mismo, sin copiar generado/
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
CARPETAS = ("tokens", "global", "modulos", "complementos", "herramientas", "generado", "fuentes", "docs")
GENERADOS = ("generado", "sitio/generado")      # lo que generar.py escribe: se enlaza en una copia de solo lectura
ARCHIVOS = ("VERSION", "REUSE.toml", "pyproject.toml", "README.md", "CHANGELOG.md", "requirements.txt")


@dataclass
class Muestra:
    raiz: Path
    lliphi: Path
    casa: Path
    entorno: dict = field(default_factory=dict)
    solo_lectura: bool = False


def copiar_proyecto(destino: Path, origen: Path = REPO, solo_lectura: bool = False) -> Path:
    ignorar = shutil.ignore_patterns("__pycache__", ".pytest_cache", "_site", ".quarto", "*.pyc")
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS:
        if (origen / nombre).is_file():
            shutil.copy2(origen / nombre, destino / nombre)
    (destino / "sitio").mkdir(exist_ok=True)
    for carpeta in CARPETAS + ("sitio/generado",):                   # sitio/generado: lo que generar.py escribe en el sitio
        if not (origen / carpeta).is_dir():
            continue
        if solo_lectura and carpeta in GENERADOS:
            if not (destino / carpeta).exists():
                (destino / carpeta).symlink_to(origen / carpeta)
            continue
        shutil.copytree(origen / carpeta, destino / carpeta, ignore=ignorar, symlinks=True, dirs_exist_ok=True)
    for enlace in ("muestras", ".venv"):
        if (origen / enlace).exists() and not (destino / enlace).exists():
            (destino / enlace).symlink_to(origen / enlace)
    return destino


def crear(raiz: Path, origen: Path = REPO, solo_lectura: bool = False) -> Muestra:
    raiz = Path(raiz)
    lliphi = copiar_proyecto(raiz / "lliphi", origen, solo_lectura)
    if solo_lectura:
        (raiz / ".solo-lectura").write_text("generado/ y sitio/generado/ son enlaces al repo: nada de generar --aplicar aquí\n",
                                            encoding="utf-8")
    casa = raiz / "casa"
    for sub in (".config", ".cache", ".local/share", ".local/state"):
        (casa / sub).mkdir(parents=True, exist_ok=True)
    entorno = {"HOME": str(casa), "XDG_CONFIG_HOME": str(casa / ".config"), "XDG_CACHE_HOME": str(casa / ".cache"), "XDG_DATA_HOME": str(casa / ".local" / "share"),
               "XDG_STATE_HOME": str(casa / ".local" / "state"), "LLIPHI_DIR": str(lliphi), "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
    return Muestra(raiz=raiz, lliphi=lliphi, casa=casa, entorno=entorno, solo_lectura=solo_lectura)


if __name__ == "__main__":
    import sys
    m = crear(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "muestra-lliphi")
    print(m.lliphi)
