"""Decoración de ventanas Aurorae (KWin; Plasma ≥ 6.6, motor SVG «V2», `kwin-style-aurorae`) derivada de dos temas
GPL-3.0-or-later que viven en `fuentes/aurorae/base/` (ver `ORIGEN.md`): el marco, los radios, las sombras y la
disposición de **WhiteSur-dark** (vinceliuice) y los botones circulares con glifo al pasar el ratón de **Nothing**
(jomada). Decisión del autor (2026-10-18): no se dibuja desde cero; se parte de ese código y se reescriben SOLO los
colores (con los hex de `tokens/tokens.json`), el rojo del botón de cerrar (acento), el gris del resto de botones (sin
semáforo) y los valores del rc que cambian (barra de 30 px, botones a la derecha). Por derivar de GPL, lo generado en
`generado/aurorae/` es GPL-3.0-or-later (REUSE.toml).

Formato que lee el motor V2 (Calibre 10523 y `aurorae/v2/decorationtheme.cpp` 6.6.6): `decoration.svg` con los
FrameSvg `decoration-*`, `decoration-inactive-*`, `mask-*` (región de desenfoque) y los `hint-*-margin`; un SVG por
botón con `<estado>-center` (`active`, `hover`, `pressed`, `deactivated`, `inactive`…; Nothing trae los cinco
primeros y el motor usa `active`/`inactive` como respaldo del resto); `<id>rc` con `[General]` y `[Layout]`; y
`metadata.desktop` (es lo que lista el proveedor de temas; `metadata.json` se añade para KPackage). Dos temas:
`<id>` (oscuro) y `<id>-claro`."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import RAIZ, VERSION, autores, escribir, semanticos

BASE = RAIZ / "fuentes" / "aurorae" / "base"
BOTONES = ["close", "maximize", "minimize", "restore", "alldesktops", "keepabove", "keepbelow"]   # los que trae Nothing
TITULO = {"TitleEdgeTop": 7, "TitleHeight": 16, "TitleEdgeBottom": 7}    # barra de 30 px (WhiteSur: 8+16+8)
CABECERA = "<!-- GENERADO por herramientas/generar.py desde tokens/ y fuentes/aurorae/base/ ({origen}, GPL-3.0-or-later); no editar -->\n"


def _rgb(hex_: str) -> str:
    h = hex_.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def _luminancia(hex_: str) -> float:
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mapa_marco(t: dict[str, str]) -> dict[str, str]:
    """Colores del `decoration.svg` de WhiteSur-dark → tokens. Las sombras (#000000) se conservan."""
    return {"#363636": t["fondo.encabezado"],          # barra y marco de la ventana activa
            "#2d2d2d": t["fondo.ventana"],             # ventana inactiva (= Colors:Header Inactive del esquema)
            "#1a1a1a": t["borde.separador"], "#242424": t["borde.separador"], "#585858": t["borde.separador"],   # contornos
            "#666666": t["texto.inactivo"], "#ffffff": t["texto.normal"],   # brillo interior de 1 px (a baja opacidad)
            "#6decff": t["acento.base"], "#8f8fff": t["acento.base"],       # restos sin uso en el archivo original
            "#ff00ff": t["acento.base"], "#00ff29": t["estado.exito"]}      # hints (no se pintan)


def mapa_boton(t: dict[str, str], boton: str) -> dict[str, str]:
    """Colores de los botones de Nothing → tokens: cerrar en el acento, el resto en el gris del esquema (sin semáforo)."""
    glifo = t["texto.sobre-acento"] if boton == "close" else t["texto.normal"]
    return {"#eb3131": t["acento.suave"], "#a82323": t["acento.base"], "#d46969": t["acento.suave"],   # cerrar: cuerpo y aro
            "#f4f0ed": t["fondo.boton"], "#c2bdbf": t["fondo.ventana-alterno"],                      # cuerpo de los demás
            "#bdbab8": t["texto.inactivo"], "#9cdde4": t["texto.inactivo"],                          # aros (Nothing: gris y cian)
            "#1b1b1d": glifo, "#6b6b6b": t["texto.inactivo"], "#ffffff": t["texto.normal"]}


def recolorear(svg: str, mapa: dict[str, str], t: dict[str, str], origen: str) -> str:
    """Sustituye cada `#rrggbb` del SVG por su token; lo que no está en el mapa (degradados sin uso heredados de
    Inkscape) va a `fondo.boton` si es claro y a `fondo.ventana-alterno` si es oscuro; `#000000` (sombras) se queda."""
    def sust(m: re.Match) -> str:
        h = m.group(0).lower()
        if h == "#000000":
            return h
        if h in mapa:
            return mapa[h]
        return t["fondo.boton"] if _luminancia(h) > 0.5 else t["fondo.ventana-alterno"]
    salida = re.sub(r"#[0-9a-fA-F]{6}\b", sust, svg)
    return re.sub(r"(<\?xml[^>]*\?>\n)", r"\1" + CABECERA.format(origen=origen), salida, count=1)


def rc(t: dict[str, str]) -> str:
    """`[General]` y `[Layout]` de WhiteSur-dark con lo que cambia: colores del título desde los tokens, sin sombra
    de texto, botones a la derecha (`IAX`), barra de 30 px, botones de 16 px separados 8 px, márgenes de 12 px."""
    general = {"TitleAlignment": "Center", "TitleVerticalAlignment": "Center", "Animation": 150,
               "ActiveTextColor": _rgb(t["texto.normal"]), "InactiveTextColor": _rgb(t["texto.inactivo"]),
               "UseTextShadow": "false", "LeftButtons": "", "RightButtons": "IAX", "Shadow": "true"}
    layout = {"BorderLeft": 1, "BorderRight": 1, "BorderBottom": 12, **TITULO,
              "TitleEdgeLeft": 12, "TitleEdgeRight": 12, "TitleBorderLeft": 8, "TitleBorderRight": 8,
              "ButtonWidth": 16, "ButtonHeight": 16, "ButtonSpacing": 8, "ButtonMarginTop": 0, "ExplicitButtonSpacer": 8,
              "PaddingTop": 36, "PaddingBottom": 95, "PaddingRight": 76, "PaddingLeft": 76,
              "TitleEdgeTopMaximized": TITULO["TitleEdgeTop"], "TitleEdgeBottomMaximized": TITULO["TitleEdgeBottom"],
              "TitleEdgeLeftMaximized": 12, "TitleEdgeRightMaximized": 12}
    lineas = ["# GENERADO por herramientas/generar.py desde tokens/ y fuentes/aurorae/base/whitesur-dark/WhiteSur-darkrc; no editar",
              "[General]"] + [f"{k}={v}" for k, v in general.items()]
    lineas += ["", "[Layout]"] + [f"{k}={v}" for k, v in layout.items()]
    return "\n".join(lineas) + "\n"


def id_tema(marca: dict, variante: str) -> str:
    return marca["id"] if variante == "oscuro" else f"{marca['id']}-claro"


def nombre_tema(marca: dict, variante: str) -> str:
    return marca["nombre"] if variante == "oscuro" else marca["nombre_esquema"]["claro"]


def metadata_desktop(marca: dict, variante: str) -> str:
    return "\n".join([
        "# GENERADO por herramientas/generar.py desde tokens/; no editar",
        "[Desktop Entry]", f"Name={nombre_tema(marca, variante)}",
        f"Comment={marca['nombre']} ({marca['nombre_esquema'][variante]}): marco de WhiteSur y botones de Nothing con los colores de {marca['nombre']}",
        f"X-KDE-PluginInfo-Name={id_tema(marca, variante)}", f"X-KDE-PluginInfo-Author={marca['autor']}",
        f"X-KDE-PluginInfo-Email={marca.get('correo', '')}", f"X-KDE-PluginInfo-Website={marca['sitio_tema']}",
        f"X-KDE-PluginInfo-Version={VERSION}", "X-KDE-PluginInfo-License=GPL-3.0-or-later",
        "X-KDE-PluginInfo-Category=Plasma 6 Window Decorations", "X-KDE-PluginInfo-EnabledByDefault=true", ""])


def metadata_json(marca: dict, variante: str) -> str:
    return json.dumps({
        "KPackageStructure": "KWin/Aurorae",
        "KPlugin": {"Authors": autores(marca) + [{"Name": "vinceliuice (WhiteSur)", "Email": ""}, {"Name": "jomada (Nothing)", "Email": ""}],
                    "Category": "Plasma 6 Window Decorations",
                    "Description": f"{marca['nombre']}: decoración de ventanas ({marca['nombre_esquema'][variante]}), derivada de WhiteSur y Nothing",
                    "EnabledByDefault": True, "Id": id_tema(marca, variante), "License": "GPL-3.0-or-later",
                    "Name": nombre_tema(marca, variante), "Version": VERSION, "Website": marca["sitio_tema"]},
    }, ensure_ascii=False, indent=4) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    marco = (BASE / "whitesur-dark" / "decoration.svg").read_text(encoding="utf-8")
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        base = destino / "aurorae" / id_tema(marca, variante)
        escribir(base / "decoration.svg", recolorear(marco, mapa_marco(t), t, "WhiteSur-dark de vinceliuice"), hechos)
        for b in BOTONES:
            svg = (BASE / "nothing" / f"{b}.svg").read_text(encoding="utf-8")
            escribir(base / f"{b}.svg", recolorear(svg, mapa_boton(t, b), t, "Nothing de jomada"), hechos)
        escribir(base / f"{id_tema(marca, variante)}rc", rc(t), hechos)
        escribir(base / "metadata.desktop", metadata_desktop(marca, variante), hechos)
        escribir(base / "metadata.json", metadata_json(marca, variante), hechos)
    return hechos
