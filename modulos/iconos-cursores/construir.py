"""Iconos y cursores de Lliphi: dos recursos de terceros que el tema global nombra y que no se generan aquí.

- **Iconos** (decisiones 4.22, decisión del autor): Colloid Grey, `Colloid-Grey-Light` en el claro y
  `Colloid-Grey-Dark` en el oscuro. Si no están, la reserva es la de antes (mejora 3 y decisiones 4.15): Papirus tal
  cual en el claro y el superpuesto `Papirus-Dark-Lliphi` (carpetas rojas) en el oscuro, que `externas.py` instala en
  `$XDG_DATA_HOME/icons/`; los aplica `aplicar.py`.
- **Bandeja** (decisiones 4.35): el tema global nombra un superpuesto de cada tema de iconos, `<tema>-Lliphi`, que
  `externas.py` construye desde el tema instalado: los iconos simbólicos de estado, aplicaciones y dispositivos con una
  versión de 22 px que lleva su dibujo en 16 px centrado, como los iconos de 22 del propio tema. Colloid dibuja sus
  simbólicos llenando un lienzo de 16; en la bandeja (22 px) se veían más grandes que los demás. El superpuesto solo se
  usa al pedir exactamente 22 px: en menús y botones (16 px) siguen los de la base.
- **Cursores**: WhiteSur-cursors (línea base del autor, decisiones 4.4); Bibata como opcional.

Es un módulo **externo**: no tiene carpeta en `generado/`; lo que entrega al tema global son sus identificadores."""
from __future__ import annotations

import json
from pathlib import Path

AJUSTES = json.loads((Path(__file__).resolve().parent / "ajustes.json").read_text(encoding="utf-8"))
ICONOS = AJUSTES["iconos"]
RESERVA = AJUSTES.get("reserva", {})
CURSORES = AJUSTES["cursores"]
BANDEJA = AJUSTES.get("bandeja", {})


def tema(variante: str) -> str:
    """El tema de iconos que nombra el tema global: el superpuesto de la bandeja del de la variante, si está activo."""
    base = ICONOS[variante]
    return f"{base}{BANDEJA['sufijo']}" if BANDEJA.get("activo") else base


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: el tema de iconos de la variante y el de cursores."""
    return {"kdeglobals][Icons": {"Theme": tema(variante)}, "kcminputrc][Mouse": {"cursorTheme": CURSORES}}
