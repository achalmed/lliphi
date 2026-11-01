"""Decoración de ventanas de Lliphi, DERIVADA del tema Aurorae «Nothing» (jomada, Seducción Linux, GPL-3.0-or-later;
`fuentes/base/Nothing-aurorae`), por decisión del autor (2026-10-18): los botones circulares con glifo al pasar el
ratón y el marco sobrio de Nothing. La variante oscura es Nothing tal cual (más una barra de 18 px); la clara se recolorea
con los tokens porque Nothing no tiene variante clara.

Plus de Lliphi sobre Nothing (mejora 4, decisiones 4.8), sin tocar formas ni tamaños de los botones:
- el anillo cian del botón de minimizar (`#9cdde4`) toma el gris del anillo de maximizar (`#bdbab8`): el trío queda en
  rojo y dos neutros, la paleta de Lliphi;
- el título usa los grises de los tokens (`texto.normal`, `texto.inactivo`) en vez del lavanda de Nothing, sin sombra;
  la fuente es la de títulos del sistema (Inter Medium, la fija el instalador).

En el claro (decisiones 4.33), el rojo de cerrar pasa al acento azul y el centro de minimizar y maximizar, casi blanco en
Nothing, al gris de texto inactivo: sobre el título claro no se veían.

Nothing no trae botón de menú de aplicación (`appmenu.svg`) y Aurorae dibujaba en su lugar el icono de la aplicación,
repetido junto al del menú de ventana. Lliphi lo dibuja (`appmenu_svg`, decisiones 4.33): tres líneas redondeadas de
largo decreciente en el color del título, con un círculo tenue al pasar y al pulsar, en el tamaño de los círculos de
Nothing.

Variantes: `lliphi` (oscuro) y `lliphi-claro`. La posición de los botones la fija el instalador en `kwinrc`
(`ButtonsOnRight=IAX`). Lo derivado es GPL-3.0-or-later (REUSE.toml)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from nucleo import RAIZ, VERSION, autores, escribir, semanticos

BASE = RAIZ / "fuentes" / "base" / "Nothing-aurorae"

AJUSTES = Path(__file__).resolve().parent / "ajustes.json"


def ajustes() -> dict:
    """Los ajustes de la decoración (`ajustes.json`): las claves del rc, los colores del título, la posición de los
    botones y los mapas de recoloreo. En el oscuro, Nothing tal cual (decisión del autor: «la decoración me gusta más de
    Nothing así como está»): los plus van en `neutro` y en el rc. En el claro, cerrar va en el acento azul (decisiones 4.33; antes, 4.12, seguía rojo)."""
    return json.loads(AJUSTES.read_text(encoding="utf-8"))


def _poner(rc: str, clave: str, valor: str) -> str:
    rc, n = re.subn(rf"^{re.escape(clave)}=.*$", f"{clave}={valor}", rc, flags=re.M)
    if not n:
        raise ValueError(f"decoracion/ajustes.json: la clave {clave} no está en el rc de la base")
    return rc


def rgb(hex_: str) -> str:
    h = hex_.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def appmenu_svg(t: dict[str, str]) -> str:
    """El botón de menú de aplicación: un estado por grupo (`active-center`, `hover-center`, `pressed-center`,
    `inactive-center`, `deactivated-center`) de 20 × 20, el diámetro de los círculos de Nothing; un rectángulo invisible
    fija los límites que Aurorae escala al tamaño del botón."""
    def estado(i: int, id_: str, color: str, fondo: float, opacidad: float = 1.0) -> str:
        x = i * 25
        circulo = f'<circle cx="{x + 10}" cy="10" r="10" style="fill:{color};opacity:{fondo}"/>' if fondo else ""
        lineas = "".join(f'<line x1="{x + 5}" y1="{y}" x2="{x + 5 + largo}" y2="{y}"/>'
                         for y, largo in ((6, 10), (10, 7.5), (14, 5)))
        return (f'<g id="{id_}" style="opacity:{opacidad}"><rect x="{x}" y="0" width="20" height="20" style="fill:{color};opacity:0"/>'
                f'{circulo}<g style="stroke:{color};stroke-width:2;stroke-linecap:round;fill:none">{lineas}</g></g>')
    estados = [("active-center", t["texto.normal"], 0), ("hover-center", t["texto.normal"], 0.14),
               ("pressed-center", t["texto.normal"], 0.24), ("inactive-center", t["texto.inactivo"], 0),
               ("deactivated-center", t["texto.inactivo"], 0, 0.5)]
    return ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="125" height="20" viewBox="0 0 125 20">'
            + "".join(estado(i, *e) for i, e in enumerate(estados)) + "</svg>\n")


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    aj = ajustes()
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        mapa = {**aj["neutro"], **{h: t[tok] for h, tok in aj["recoloreo"][variante].items()}}
        id_ = marca["id"] if variante == "oscuro" else f"{marca['id']}-claro"
        base = destino / id_
        for svg in sorted(BASE.glob("*.svg")):
            texto = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), svg.read_text(encoding="utf-8", errors="ignore"))
            escribir(base / svg.name, texto, hechos)
        escribir(base / "appmenu.svg", appmenu_svg(t), hechos)   # Nothing no lo trae (decisiones 4.33)
        rc = (BASE / "Nothingrc").read_text(encoding="utf-8")
        # título en los grises de Lliphi y sin sombra, en las dos variantes (mejora 4); barra algo más alta
        for clave, token in aj["titulo"].items():
            rc = _poner(rc, clave, rgb(t[token]))
        for clave, valor in aj["rc"].items():
            rc = _poner(rc, clave, valor)
        escribir(base / f"{id_}rc", "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/Nothing-aurorae; no editar\n" + rc, hechos)
        nombre = marca["nombre_esquema"][variante]
        escribir(base / "metadata.json", json.dumps({
            "KPackageStructure": "KWin/Aurorae",
            "KPlugin": {"Authors": autores(marca) + [{"Name": "jomada (Nothing, base GPL-3.0-or-later)", "Email": ""}],
                        "Category": "Plasma 6 Window Decorations", "ServiceTypes": ["KWin/Aurorae"], "EnabledByDefault": True,
                        "Name": nombre, "Description": f"Decoración de {marca['nombre']}, derivada de Nothing", "Id": id_,
                        "Version": VERSION, "License": "GPL-3.0-or-later", "X-KDE-PluginInfo-blur": False, "X-KPackage-Dependencies": []},
        }, ensure_ascii=False, indent=4) + "\n", hechos)
        escribir(base / "metadata.desktop", "\n".join([
            "[Desktop Entry]", f"Name={nombre}", f"Comment=Decoración de {marca['nombre']}, derivada de Nothing", "Type=Service",
            "X-KDE-ServiceTypes=KWin/Aurorae", f"X-KDE-PluginInfo-Name={id_}", f"X-KDE-PluginInfo-Version={VERSION}",
            f"X-KDE-PluginInfo-Author={marca['autor']}", "X-KDE-PluginInfo-License=GPL-3.0-or-later", "X-KDE-PluginInfo-EnabledByDefault=true", ""]), hechos)
    return hechos


def id_tema(marca: dict, variante: str) -> str:
    return marca["id"] if variante == "oscuro" else f"{marca['id']}-claro"


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: la decoración Aurorae (motor SVG V2 de Plasma 6.6: el KCM
    escribe `org.kde.kwin.aurorae.v2`) con los botones a la izquierda, sin menú."""
    botones = ajustes()["botones"]
    return {"kwinrc][org.kde.kdecoration2": {"library": "org.kde.kwin.aurorae.v2", "theme": f"__aurorae__svg__{id_tema(marca, variante)}",
                                             "ButtonsOnLeft": botones["izquierda"], "ButtonsOnRight": botones["derecha"]}}
