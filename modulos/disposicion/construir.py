"""Disposición del escritorio de Lliphi: paneles, widgets y fondo de cada escritorio (script de disposición de Plasma)
y los selectores de ventanas y de escritorios de KWin.

Es un **componente** del tema global: Plasma ejecuta `contents/layouts/org.kde.plasma.desktop-layout.js` del paquete
`Plasma/LookAndFeel` solo si el usuario marca «Disposición del escritorio» al aplicar el tema (o con
`plasma-apply-lookandfeel --resetLayout`), así que el script se escribe dentro del paquete del tema global
(`integrar`). La fuente es `escritorio.js`, JavaScript de verdad (la API de scripting de Plasma: `Panel`,
`addWidget`, `desktopsForActivity`, `userDataPath`) con dos marcas que se sustituyen al construir: `@NOMBRE@` (el
nombre del tema) y `@FONDO@` (el id del paquete de fondo de `complementos/fondos`)."""
from __future__ import annotations

from pathlib import Path

from nucleo import escribir

FUENTE = Path(__file__).resolve().parent / "escritorio.js"
CABECERA = "// GENERADO por herramientas/generar.py desde tokens/; no editar.\n"
DESTINO = Path("contents") / "layouts" / "org.kde.plasma.desktop-layout.js"


def script(marca: dict) -> str:
    js = FUENTE.read_text(encoding="utf-8")
    return CABECERA + js.replace("@NOMBRE@", marca["nombre"]).replace("@FONDO@", marca["id_fondo"])


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: los selectores de KWin de Breeze."""
    return {"kwinrc][WindowSwitcher": {"LayoutName": "org.kde.breeze.desktop"},
            "kwinrc][DesktopSwitcher": {"LayoutName": "org.kde.breeze.desktop"}}


def integrar(tokens: dict, marca: dict, variante: str, paquete: Path, hechos: list[Path]) -> None:
    escribir(paquete / DESTINO, script(marca), hechos)
