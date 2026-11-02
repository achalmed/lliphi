"""Xournal++ con Lliphi (decisiones 5.20).

Xournal++ es una aplicación GTK 3: su interfaz sigue al complemento gtk (Breeze con los colores de los tokens) y su
modo oscuro, con `themeVariant=useSystem`, a la preferencia oscura de GTK; la caja de herramientas flotante, que su
propia hoja pinta en blanco, la colorea también el complemento gtk. Lo que es de Xournal++ y no de GTK sale de aquí:

- `palettes/<nombre>.gpl`: la paleta de bolígrafos (formato «GIMP Palette»), en el orden de los botones de color de la
  barra de herramientas (`COLOR(0)`…`COLOR(10)`; los demás, en el selector). Se instala en
  `~/.config/xournalpp/palettes/`, la carpeta de paletas del usuario, y se elige en Preferencias → Paleta.
- `settings-<id>.xml`: las propiedades de color de `settings.xml` (alrededor de las páginas, selección, el recoloreado
  del modo oscuro y la ruta de la paleta) como fragmento para copiar a mano; `aplicar.py` las escribe con Xournal++
  cerrado.

Los colores los declara `ajustes.json` como `[variante, token]`; «terminal-claro» y «terminal-oscuro» son el grupo
`terminal` de los tokens (los ANSI de Lliphi, los mismos de las paletas de LibreOffice). Xournal++ guarda los colores
como entero ARGB sin signo (0xAARRGGBB, en decimal).
"""
from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import quoteattr

from nucleo import escribir, hexa, semanticos

AJUSTES = Path(__file__).resolve().parent / "ajustes.json"
RUTA_PALETA = "~/.config/xournalpp/palettes"          # solo para el texto del fragmento; aplicar.py usa CONFIG


def ajustes() -> dict:
    return json.loads(AJUSTES.read_text(encoding="utf-8"))


def color(tokens: dict, grupo: str, clave: str) -> str:
    if grupo.startswith("terminal-"):
        return hexa(tokens["terminal"][grupo.split("-", 1)[1]][clave])
    return semanticos(tokens, grupo)[clave]


def argb(hex6: str) -> int:
    """`#rrggbb` → entero ARGB opaco, como lo guarda Xournal++."""
    return 0xFF000000 | int(hex6.lstrip("#"), 16)


def boligrafos(tokens: dict) -> list[tuple[str, str]]:
    return [(nombre, color(tokens, g, c)) for nombre, g, c in ajustes()["boligrafos"]]


def propiedades(tokens: dict, ruta_paleta: str) -> dict[str, str]:
    """Propiedad de settings.xml → valor (texto), en el orden en que se escriben."""
    a = ajustes()
    salida = {k: str(argb(color(tokens, g, c))) for k, (g, c) in {**a["interfaz"], **a["recolor"]}.items()}
    salida["colorPalette"] = ruta_paleta
    return salida


def texto_gpl(tokens: dict, marca: dict) -> str:
    lineas = ["GIMP Palette", f"Name: {marca['nombre']}", "# GENERADO por herramientas/generar.py desde tokens/; no editar"]
    for nombre, h in boligrafos(tokens):
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
        lineas.append(f"{r:3d} {g:3d} {b:3d}\t{nombre}")
    return "\n".join(lineas) + "\n"


def texto_fragmento(tokens: dict, marca: dict) -> str:
    lineas = ["<!-- GENERADO por herramientas/generar.py desde tokens/ (complementos/xournalpp); no editar -->",
              f"<!-- Colores de {marca['nombre']} para Xournal++: con Xournal++ cerrado, sustituye estas propiedades en",
              "     ~/.config/xournalpp/settings.xml (o deja que lo haga instalar.py --aplicar-tema). Los colores son ARGB en decimal;",
              "     en colorPalette, escribe la ruta completa de la paleta (sin ~). -->"]
    for k, v in propiedades(tokens, f"{RUTA_PALETA}/{marca['nombre']}.gpl").items():
        lineas.append(f"<property name={quoteattr(k)} value={quoteattr(v)}/>")
    return "\n".join(lineas) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / "palettes" / f"{marca['nombre']}.gpl", texto_gpl(tokens, marca), hechos)
    escribir(destino / f"settings-{marca['id']}.xml", texto_fragmento(tokens, marca), hechos)
    return hechos
