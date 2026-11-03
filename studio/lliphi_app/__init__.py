"""studio/lliphi_app/__init__.py — Lliphi Studio, la ventana opcional de Lliphi (QML + Kirigami sobre gui-comun 3.0).

La ventana es cliente del proyecto: lee los `modulo.json`, los tokens, `generado/` y el manifiesto de instalación, y
corre las órdenes de Lliphi (`generar.py`, `instalar.py`, `sesion.py`, `paleta.py`) con la salida en el panel inferior.
Es un centro de configuración por áreas; generar, instalar y desinstalar van en seis pasos visibles
(`docs/reingenieria.md`). Lo de terminal funciona sin ella.

Necesita el PySide6 del sistema (el que carga Kirigami) y `gui_comun`, que llega como paquete de pip o por
`GUI_COMUN_DIR` (la carpeta del repo gui-comun): nunca se busca subiendo carpetas, porque el repo es autónomo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Lliphi Studio"
APP_VERSION = "3.0.0"
ORG_NAME = "achalma"
VARIABLE_GUI_COMUN = "GUI_COMUN_DIR"
INSTALAR = 'python3 -m pip install --user "gui-comun @ git+https://github.com/achalmed/gui-comun.git@v4.0.0"   # o GUI_COMUN_DIR=<repo gui-comun>'


def hay_gui_comun() -> bool:
    """¿Está `gui_comun`? Instalado, o en la carpeta que diga `GUI_COMUN_DIR` (se añade al final del `sys.path`)."""
    try:
        import gui_comun  # noqa: F401
        return True
    except ImportError:
        pass
    carpeta = os.environ.get(VARIABLE_GUI_COMUN, "").strip()
    if carpeta and (Path(carpeta) / "gui_comun").is_dir():
        sys.path.append(carpeta)
        return True
    return False


def faltan() -> list[str]:
    """Lo que falta para abrir la ventana (vacío si está todo)."""
    import importlib.util
    salida = []
    if importlib.util.find_spec("PySide6") is None and importlib.util.find_spec("PyQt6") is None:
        salida.append("PySide6 (python3-pyside6.* del sistema)")
    if not hay_gui_comun():
        salida.append("gui_comun")
    else:
        import gui_comun
        try:
            if tuple(int(x) for x in gui_comun.__version__.split(".")[:2]) < (3, 1):
                salida.append(f"gui_comun 3.1 o superior (hay {gui_comun.__version__})")
        except (AttributeError, ValueError):
            salida.append("gui_comun 3.1 o superior")
    return salida
