"""studio/lliphi_studio/__init__.py — paquete de Lliphi Studio, el centro de control visual de Lliphi.

La ventana es opcional: lo de terminal de Lliphi (`herramientas/generar.py`, `instalar.py`, `sesion.py`) funciona sin
ella y no gana ninguna dependencia. Necesita PySide6 y `gui-comun` como paquete de pip (nunca se busca en otra
carpeta: el repo es autónomo). Sin ellos, `main.py` dice cómo instalarlos y sale.
"""

INSTALAR = 'python3 -m pip install --user PySide6 "git+https://github.com/achalmed/gui-comun@v1.4.0"'


def faltan() -> list[str]:
    """Los módulos que faltan para abrir la ventana (vacío si están todos)."""
    import importlib.util
    return [m for m in ("PySide6", "gui_comun") if importlib.util.find_spec(m) is None]
