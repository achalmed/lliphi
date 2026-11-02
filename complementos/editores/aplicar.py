"""Instalación de la extensión en la familia de VS Code (decisiones 5.9): con la orden de cada editor que haya en el
PATH, `<editor> --install-extension generado/editores/vscode/<id>.vsix --force`, que la registra en su
`extensions.json`. Copiar la carpeta a `~/.<editor>/extensions/` ya no sirve: el editor no la encuentra en su registro,
la anota en `.obsolete` como desinstalada y no la carga (visto en Positron 2026.06).

`tras_instalar()` corre después de copiar los archivos (también al simular, para decir qué haría) y devuelve las
líneas de `UNDO.sh` que la desinstalan; `al_desinstalar()` la desinstala con `instalar.py desinstalar`. Si el usuario
fijó la carpeta de extensiones de un editor (`VSCODE_EXTENSIONS`, `POSITRON_EXTENSIONS`, `VSCODIUM_EXTENSIONS`), se
le pasa como `--extensions-dir`."""
from __future__ import annotations

import os
import shlex
import shutil
from pathlib import Path

GENERADO = Path(__file__).resolve().parents[2] / "generado" / "editores"
# orden en el PATH, nombre, variable con la carpeta de extensiones
EDITORES = (("code", "VS Code", "VSCODE_EXTENSIONS"), ("positron", "Positron", "POSITRON_EXTENSIONS"),
            ("codium", "VSCodium", "VSCODIUM_EXTENSIONS"))


def presentes() -> list[tuple[str, str, str]]:
    """(ruta de la orden, nombre, variable) de los editores instalados."""
    return [(ruta, nombre, var) for orden, nombre, var in EDITORES if (ruta := shutil.which(orden))]


def orden(ruta: str, var: str, *args: str) -> list[str]:
    carpeta = os.environ.get(var)
    return [ruta, *args, *(["--extensions-dir", carpeta] if carpeta else [])]


def tras_instalar(ctx, aplicar: bool) -> list[str]:
    if "editores" not in ctx.modulos:
        return []
    id_ = ctx.marca["id"]
    vsix = GENERADO / "vscode" / f"{id_}.vsix"
    editores = presentes()
    if not editores:
        ctx.decir(f"ningún editor de la familia de VS Code en el PATH (code, positron, codium): instala {vsix.name} desde el "
                  "editor (Extensiones → … → Instalar desde VSIX)")
        return []
    deshacer = []
    for ruta, nombre, var in editores:
        instalar = orden(ruta, var, "--install-extension", str(vsix), "--force")
        if not aplicar:
            ctx.decir(f"SIM {nombre}: {shlex.join(instalar)}")
        else:
            r = ctx.ejecutar(instalar)
            ctx.decir(f"{nombre}: extensión {id_}.{id_} " + ("instalada y registrada" if r.returncode == 0
                      else f"NO instalada ({(r.stderr or r.stdout).strip()[:160]})"))
        deshacer.append(f"{shlex.join(orden(ruta, var, '--uninstall-extension', f'{id_}.{id_}'))} >/dev/null 2>&1 "
                        f'&& echo "retirada la extensión de {nombre}" || true')
    return deshacer


def al_desinstalar(ctx, aplicar: bool) -> None:
    id_ = ctx.marca["id"]
    for ruta, nombre, var in presentes():
        desinstalar = orden(ruta, var, "--uninstall-extension", f"{id_}.{id_}")
        if aplicar:
            r = ctx.ejecutar(desinstalar)
            ctx.decir(f"{nombre}: extensión {'retirada' if r.returncode == 0 else 'no estaba instalada'}")
        else:
            ctx.decir(f"SIM {nombre}: {shlex.join(desinstalar)}")
