"""Aplicación en Calibre (decisiones 5.22): funde las paletas de Lliphi en `gui.json` y los dos esquemas del visor en
`viewer-webengine.json` (`session_data` → `user_color_schemes`), con Calibre y el visor cerrados, porque los reescriben
al salir. Solo esas claves: lo demás de los dos archivos, y los esquemas propios del usuario, quedan como estaban. La
biblioteca (`metadata.db`, en la carpeta de la biblioteca) no se abre ni se toca. Los dos archivos se respaldan antes."""
from __future__ import annotations

import json
import os
from pathlib import Path


def carpeta(config: Path) -> Path:
    """La carpeta de configuración de Calibre: `CALIBRE_CONFIG_DIRECTORY` si está, si no `<config>/calibre`."""
    return Path(os.environ["CALIBRE_CONFIG_DIRECTORY"]) if os.environ.get("CALIBRE_CONFIG_DIRECTORY") else config / "calibre"


def fundir_gui(datos: dict, propias: dict) -> dict:
    """Pone las claves de Lliphi; en los diccionarios de paletas, añade o sustituye solo la de Lliphi."""
    salida = dict(datos)
    for clave, valor in propias.items():
        if clave.endswith("_palettes"):
            salida[clave] = {**(datos.get(clave) or {}), **valor}
        else:
            salida[clave] = valor
    return salida


def fundir_visor(datos: dict, esquemas: dict) -> dict:
    salida = dict(datos)
    sesion = dict(datos.get("session_data") or {})
    sesion["user_color_schemes"] = {**(sesion.get("user_color_schemes") or {}), **esquemas}
    salida["session_data"] = sesion
    return salida


def _leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def _escribir(ruta: Path, datos: dict) -> None:
    real = ruta.resolve() if ruta.exists() else ruta
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def respaldos(ctx) -> list:
    c = carpeta(ctx.CONFIG)
    return [(c / f, "reponer", f"{f} de Calibre") for f in ("gui.json", "viewer-webengine.json")
            if (c / f).exists() and c.is_relative_to(ctx.CONFIG)]


def aplicar(ctx) -> int:
    if "calibre" not in ctx.modulos:
        return 0
    c = carpeta(ctx.CONFIG)
    if not c.is_dir():
        ctx.decir("Calibre: sin carpeta de configuración (ábrelo una vez); no se toca nada")
        return 0
    if not c.is_relative_to(ctx.CONFIG):     # el respaldo solo cubre lo que cuelga de XDG_CONFIG_HOME
        ctx.decir(f"Calibre: su configuración está fuera de {ctx.CONFIG} (CALIBRE_CONFIG_DIRECTORY); aplícalo a mano (INSTALL.md)")
        return 0
    if ctx.hay("pgrep") and any(ctx.ejecutar(["pgrep", "-x", p]).returncode == 0 for p in ("calibre", "ebook-viewer")):
        ctx.decir("Calibre o su visor están abiertos: ciérralos y vuelve a aplicar (los reescriben al salir)")
        return 0
    construir = ctx.codigo("calibre")
    _escribir(c / "gui.json", fundir_gui(_leer(c / "gui.json"), construir.preferencias_gui(ctx.tokens, ctx.marca)))
    _escribir(c / "viewer-webengine.json", fundir_visor(_leer(c / "viewer-webengine.json"), construir.esquemas_visor(ctx.tokens, ctx.marca)))
    ctx.decir(f"Calibre: paletas {ctx.marca['nombre_esquema']['claro']} y {ctx.marca['nombre_esquema']['oscuro']} (siguen al "
              "escritorio) y sus dos esquemas en el visor; la biblioteca no se toca")
    return 0
