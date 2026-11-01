"""Iconos y cursores de Lliphi: dos recursos de terceros que el tema global nombra y que no se generan aquí.

- **Iconos** (mejora 3 y decisiones 4.15): Papirus tal cual (carpetas azules) en el claro y el superpuesto
  `Papirus-Dark-Lliphi` (carpetas rojas; hereda de Papirus-Dark) en el oscuro. Los instala y construye
  `externas.py` en `$XDG_DATA_HOME/icons/`; los aplica `aplicar.py`.
- **Cursores**: WhiteSur-cursors (línea base del autor, decisiones 4.4); Bibata como opcional.

Es un módulo **externo**: no tiene carpeta en `generado/`; lo que entrega al tema global son sus identificadores."""
from __future__ import annotations

import json
from pathlib import Path

AJUSTES = json.loads((Path(__file__).resolve().parent / "ajustes.json").read_text(encoding="utf-8"))
ICONOS = AJUSTES["iconos"]
CURSORES = AJUSTES["cursores"]


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: el tema de iconos de la variante y el de cursores."""
    return {"kdeglobals][Icons": {"Theme": ICONOS[variante]}, "kcminputrc][Mouse": {"cursorTheme": CURSORES}}
