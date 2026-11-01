"""Tema de Kvantum de Lliphi, DERIVADO del de WhiteSur-kde (GPL-3.0): los widgets de las aplicaciones Qt con el
refinamiento de WhiteSur (menús y tooltips translúcidos, controles redondeados, barras finas) en los colores de Lliphi.

Se toma `Kvantum/WhiteSur/WhiteSurDark.{kvconfig,svg}` y `WhiteSur.{kvconfig,svg}`, se escriben las claves de color del
`.kvconfig` desde los tokens y se sustituyen los hex fijos del `.svg`. Lo derivado es GPL-3.0-or-later.
`ajustes.json` dice, por variante, si las ventanas son translúcidas (WhiteSur) o sólidas (`WhiteSur-opaque`), y con qué
token se pinta la barra de herramientas: en el oscuro, translúcidas (la vista de Dolphin y la terminal integrada dejan
ver el fondo) y la barra, opaca en el color de la ventana, que es el del título de la decoración (decisiones 4.18).
Un solo tema, `Lliphi` (el nombre de la marca), con las dos variantes en su carpeta, como hace WhiteSur:
`Lliphi/Lliphi.{kvconfig,svg}` es el claro y `Lliphi/LliphiDark.{kvconfig,svg}` el oscuro. Kvantum elige solo: con el
estilo `kvantum` usa `Lliphi` y con `kvantum-dark` busca `LliphiDark`; el tema global declara uno u otro, así que cambiar
de variante en Preferencias del sistema cambia también Kvantum (antes eran dos temas, `LliphiClaro` y `LliphiOscuro`, y
el de Kvantum solo lo cambiaba el instalador: aplicar el claro desde Preferencias dejaba el Kvantum oscuro; decisiones
4.19). Se instala en `$XDG_CONFIG_HOME/Kvantum/Lliphi/` y se activa una vez con `[General] theme=Lliphi` en
`Kvantum/kvantum.kvconfig`.
"""
from __future__ import annotations

import colorsys
import json
import re
from pathlib import Path

from nucleo import RAIZ, escribir, semanticos

BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "Kvantum" / "WhiteSur"
ORIGEN = {"oscuro": "WhiteSurDark", "claro": "WhiteSur"}
SUFIJO = {"claro": "", "oscuro": "Dark"}   # Kvantum busca <tema>Dark con el estilo kvantum-dark
AJUSTES = Path(__file__).resolve().parent / "ajustes.json"

CLAVES = {  # clave del kvconfig → token
    "window.color": "fondo.ventana", "base.color": "fondo.vista", "alt.base.color": "fondo.vista-alterno",
    "button.color": "fondo.boton", "light.color": "fondo.ventana-alterno", "mid.color": "borde.separador",
    "dark.color": "fondo.vista", "highlight.color": "seleccion.fondo", "inactive.highlight.color": "acento.suave",
    "text.color": "texto.normal", "window.text.color": "texto.normal", "button.text.color": "texto.normal",
    "disabled.text.color": "texto.inactivo", "tooltip.base.color": "fondo.tooltip", "tooltip.text.color": "texto.tooltip",
    "highlight.text.color": "seleccion.texto", "link.color": "enlace", "visited.link.color": "visitado",
    "progress.indicator.text.color": "seleccion.texto",
}
HEX = {  # hex fijo del svg de WhiteSur → token (los demás se dejan)
    "oscuro": {"#315bef": "acento.base", "#5294e2": "acento.suave", "#a0b4f8": "acento.suave", "#242424": "fondo.vista",
               "#2d2d2d": "fondo.vista-alterno", "#656565": "fondo.boton", "#333333": "fondo.tooltip", "#dedede": "texto.normal",
               "#dfdfdf": "texto.normal", "#9d9d9d": "texto.inactivo", "#4f4f4f": "borde.separador", "#696969": "borde.separador",
               "#1b1b1b": "fondo.ventana", "#1a1a1a": "fondo.ventana"},
    # el acento de WhiteSur.svg (claro) es #0860f2 (47 usos: foco, selección, deslizadores), con #0e4bb4/#0852ce/#1352c4 como
    # tonos pulsados o de borde y #77aff1 como tono claro (mejora 2, decisiones 4.6); #315bef solo aparece una vez
    "claro": {"#0860f2": "acento.base", "#0e4bb4": "acento.texto", "#0852ce": "acento.texto", "#1352c4": "acento.texto",
              "#77aff1": "acento.suave",
              "#315bef": "acento.base", "#5294e2": "acento.suave", "#a0b4f8": "acento.suave", "#4285f4": "acento.base",
              "#333333": "texto.normal", "#666666": "texto.inactivo", "#f5f5f5": "fondo.ventana", "#ffffff": "fondo.vista",
              "#e5e5e5": "fondo.boton", "#d9d9d9": "borde.separador"},
}


def barra(svg: str, color: str) -> str:
    """La barra de herramientas (`toolbar-normal*`, activa e inactiva) en un color: el gris propio de WhiteSur
    (#363636 y #2d2d2d la inactiva en el oscuro; #ffffff y #f5f5f5 en el claro) la separaba del título de la decoración. Solo el relleno opaco de sus piezas: la línea
    oscura de abajo (negro al 65 %) se queda como divisoria con el contenido."""
    def pieza(m: re.Match) -> str:
        return re.sub(r"fill:#(363636|2d2d2d|ffffff|f5f5f5)\b", f"fill:{color}", m.group(0), flags=re.I)
    return re.sub(r'<[^<>]*\bid="toolbar-normal[^"]*"[^<>]*>', pieza, svg)


def azules_al_acento(svg: str, t: dict[str, str]) -> str:
    """Todo azul de WhiteSur que quede (no es ya un color de Lliphi) pasa al acento de la variante, por su luz: hasta la
    del acento, a `acento.base`; más claro, a `acento.suave`. Así no queda ningún azul de la base en el oscuro, donde el
    acento es rojo (los botones pulsados o por omisión salían azules: decisiones 4.21)."""
    propios = {h.lower() for h in t.values()}
    luz_base = colorsys.rgb_to_hls(*(int(t["acento.base"][i:i + 2], 16) / 255 for i in (1, 3, 5)))[1]

    def cambiar(m: re.Match) -> str:
        h = m.group(0).lower()
        if h in propios:
            return m.group(0)
        tono, luz, sat = colorsys.rgb_to_hls(*(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)))
        if sat < 0.3 or not 0.5 < tono < 0.75 or luz > 0.9:
            return m.group(0)
        return t["acento.base"] if luz <= luz_base + 0.03 else t["acento.suave"]
    return re.sub(r"#[0-9a-fA-F]{6}\b", cambiar, svg)


def menu_abierto(svg: str, color: str) -> str:
    """El elemento abierto de la barra de menús (`menubaritem-pressed*`, `menubaritem-toggled*`) en un color: WhiteSur
    oscuro lo pinta con su tono claro (#5294e2, el de pasar el ratón), distinto del elemento elegido dentro del menú."""
    def pieza(m: re.Match) -> str:
        return re.sub(r"fill:#5294e2\b", f"fill:{color}", m.group(0), flags=re.I)
    return re.sub(r'<[^<>]*\bid="menubaritem-(?:pressed|toggled)[^"]*"[^<>]*>', pieza, svg)


def inactivo_pleno(svg: str) -> str:
    """El deslizador y la barra de progreso de una ventana inactiva (`slider-toggled-inactive*`,
    `progress-pattern-normal-inactive*`) con el acento entero: WhiteSur oscuro los pinta con `opacity:0.5` y el rojo
    quedaba apagado, mientras el claro los deja enteros (decisiones 4.31). Lo deshabilitado sigue a media opacidad."""
    def pieza(m: re.Match) -> str:
        return re.sub(r";?(?<![-\w])opacity:0?\.5\b", "", m.group(0))
    return re.sub(r'<[^<>]*\bid="(?:slider-toggled|progress-pattern-normal)-inactive[^"]*"[^<>]*>', pieza, svg)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    aj = json.loads(AJUSTES.read_text(encoding="utf-8"))
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        tema = tema_de(marca)
        archivo = f"{tema}{SUFIJO[variante]}"
        kv = (BASE / f"{ORIGEN[variante]}.kvconfig").read_text(encoding="utf-8")
        for clave, token in CLAVES.items():
            kv = re.sub(rf"^{re.escape(clave)}=.*$", f"{clave}={t[token]}", kv, flags=re.M)
        kv = kv.replace("[%General]", "[%General]\ncomment=Lliphi, derivado de WhiteSur-kde (GPL-3.0)", 1)
        if not aj["ventanas_translucidas"][variante]:
            kv = re.sub(r"^translucent_windows=.*$", "translucent_windows=false", kv, flags=re.M)
        svg = (BASE / f"{ORIGEN[variante]}.svg").read_text(encoding="utf-8", errors="ignore")
        mapa = {h: t[tok] for h, tok in HEX[variante].items()}
        if aj["barra_de_herramientas"][variante]:   # antes del mapa general: #2d2d2d también lo usan otros controles
            svg = barra(svg, t[aj["barra_de_herramientas"][variante]])
        if aj["menu_abierto"][variante]:            # antes del mapa general: #5294e2 es también el tono de pasar
            svg = menu_abierto(svg, t[aj["menu_abierto"][variante]])
        svg = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), svg)
        if aj.get("azules_al_acento"):
            svg = azules_al_acento(svg, t)
        if aj.get("inactivo_pleno", {}).get(variante):
            svg = inactivo_pleno(svg)
        escribir(destino / tema / f"{archivo}.kvconfig", "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/WhiteSur-kde; no editar\n" + kv, hechos)
        escribir(destino / tema / f"{archivo}.svg", svg, hechos)
    return hechos


def tema_de(marca: dict) -> str:
    """El nombre del tema de Kvantum: el de la marca (sin espacios, como pide Kvantum)."""
    return marca["nombre"].replace(" ", "")


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: Kvantum como estilo de las aplicaciones."""
    return {"kdeglobals][KDE": {"widgetStyle": "kvantum" if variante == "claro" else "kvantum-dark"}}
