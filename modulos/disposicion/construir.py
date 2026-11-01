"""Disposición del escritorio de Lliphi: paneles, widgets y fondo de cada escritorio (script de disposición de Plasma)
y los selectores de ventanas y de escritorios de KWin.

Es un **componente** del tema global: Plasma ejecuta `contents/layouts/org.kde.plasma.desktop-layout.js` del paquete
`Plasma/LookAndFeel` solo si el usuario marca «Disposición del escritorio» al aplicar el tema (o con
`plasma-apply-lookandfeel --resetLayout`), así que el script se escribe dentro del paquete del tema global
(`integrar`). La fuente es `escritorio.js`, JavaScript de verdad (la API de scripting de Plasma: `Panel`,
`addWidget`, `desktopsForActivity`, `userDataPath`) con tres marcas que se sustituyen al construir: `@NOMBRE@` (el
nombre del tema), `@FONDO@` (el id del paquete de fondo de `complementos/fondos`) y `@PANELES@` (los paneles y sus
widgets de `ajustes.json`, como literal de JavaScript; los edita Lliphi Studio)."""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import escribir

FUENTE = Path(__file__).resolve().parent / "escritorio.js"
AJUSTES = Path(__file__).resolve().parent / "ajustes.json"
UBICACIONES = ("top", "bottom", "left", "right")
OCULTAR = ("none", "autohide", "dodgewindows", "windowsgobelow")   # los que entiende el scripting de Plasma 6.6
CABECERA = "// GENERADO por herramientas/generar.py desde tokens/; no editar.\n"
DESTINO = Path("contents") / "layouts" / "org.kde.plasma.desktop-layout.js"


def paneles(ajustes: dict | None = None) -> list[dict]:
    """Los paneles de `ajustes.json`, comprobados (un valor que Plasma no entiende se ignoraría en silencio)."""
    lista = (ajustes or json.loads(AJUSTES.read_text(encoding="utf-8")))["paneles"]
    for p in lista:
        if p["ubicacion"] not in UBICACIONES or p["ocultar"] not in OCULTAR:
            raise ValueError(f"disposicion/ajustes.json: panel {p.get('variable')}: ubicacion u ocultar no válidos")
        if not p.get("widgets"):
            raise ValueError(f"disposicion/ajustes.json: panel {p.get('variable')} sin widgets")
    return lista


def script(marca: dict, ajustes: dict | None = None) -> str:
    js = FUENTE.read_text(encoding="utf-8")
    literal = json.dumps([{k: v for k, v in p.items() if k != "variable"} for p in paneles(ajustes)], ensure_ascii=False, indent=4)
    return CABECERA + js.replace("@NOMBRE@", marca["nombre"]).replace("@FONDO@", marca["id_fondo"]).replace("@PANELES@", literal)


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: los selectores de KWin de Breeze."""
    return {"kwinrc][WindowSwitcher": {"LayoutName": "org.kde.breeze.desktop"},
            "kwinrc][DesktopSwitcher": {"LayoutName": "org.kde.breeze.desktop"}}


def integrar(tokens: dict, marca: dict, variante: str, paquete: Path, hechos: list[Path]) -> None:
    escribir(paquete / DESTINO, script(marca), hechos)
