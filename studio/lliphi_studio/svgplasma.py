"""Los SVG de Plasma y de Aurorae, sin Qt: qué elementos tiene un archivo, qué marcos de nueve piezas forma, cómo se
sustituye la hoja `current-color-scheme` por los colores de un esquema (lo que hace Plasma al dibujarlos) y el `rc` de
una decoración Aurorae.

Un marco de Plasma (y la decoración de Aurorae) es un prefijo con nueve elementos: `<p>-topleft`, `<p>-top`,
`<p>-topright`, `<p>-left`, `<p>-center`, `<p>-right`, `<p>-bottomleft`, `<p>-bottom` y `<p>-bottomright` (sin prefijo,
`topleft`…). Las esquinas se dibujan a su tamaño; los bordes y el centro se estiran.
"""
from __future__ import annotations

import configparser
import gzip
import re
from pathlib import Path

PIEZAS = ("topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright")
# clases de la hoja de Plasma → (grupo del esquema, clave)
CLASES = {
    "Text": ("Colors:Window", "ForegroundNormal"), "Background": ("Colors:Window", "BackgroundNormal"),
    "Highlight": ("Colors:Selection", "BackgroundNormal"), "HighlightedText": ("Colors:Selection", "ForegroundNormal"),
    "ViewText": ("Colors:View", "ForegroundNormal"), "ViewBackground": ("Colors:View", "BackgroundNormal"),
    "ViewHover": ("Colors:View", "DecorationHover"), "ViewFocus": ("Colors:View", "DecorationFocus"),
    "ButtonText": ("Colors:Button", "ForegroundNormal"), "ButtonBackground": ("Colors:Button", "BackgroundNormal"),
    "ButtonHover": ("Colors:Button", "DecorationHover"), "ButtonFocus": ("Colors:Button", "DecorationFocus"),
    "NegativeText": ("Colors:Window", "ForegroundNegative"), "PositiveText": ("Colors:Window", "ForegroundPositive"),
    "NeutralText": ("Colors:Window", "ForegroundNeutral"),
    "ComplementaryText": ("Colors:Complementary", "ForegroundNormal"),
    "ComplementaryBackground": ("Colors:Complementary", "BackgroundNormal"),
    "ComplementaryHover": ("Colors:Complementary", "DecorationHover"),
    "ComplementaryFocus": ("Colors:Complementary", "DecorationFocus"),
    "HeaderText": ("Colors:Header", "ForegroundNormal"), "HeaderBackground": ("Colors:Header", "BackgroundNormal"),
    "Tooltip": ("Colors:Tooltip", "BackgroundNormal"), "TooltipText": ("Colors:Tooltip", "ForegroundNormal"),
}
ESTRUCTURA = re.compile(r"^(linearGradient|radialGradient|stop|defs|svg|filter|feGaussianBlur|metadata|base|grid|guide|"
                        r"layer|namedview|clipPath|current-color-scheme|true|false)\d*", re.I)


def leer(ruta: Path) -> str:
    datos = ruta.read_bytes()
    return (gzip.decompress(datos) if ruta.suffix == ".svgz" else datos).decode("utf-8", errors="replace")


def archivos(carpeta: Path) -> dict[str, list[Path]]:
    """Los SVG de un estilo de Plasma, por subcarpeta (`widgets`, `dialogs`, `solid/widgets`…)."""
    salida: dict[str, list[Path]] = {}
    for p in sorted(carpeta.rglob("*")):
        if p.suffix in (".svg", ".svgz"):
            salida.setdefault(str(p.parent.relative_to(carpeta)), []).append(p)
    return salida


def elementos(texto: str) -> list[str]:
    """Los ids con nombre de un SVG de Plasma (sin degradados, filtros ni restos de Inkscape como `path1234`)."""
    vistos, salida = set(), []
    for i in re.findall(r'\bid="([^"]+)"', texto):
        if i in vistos or ESTRUCTURA.match(i) or re.fullmatch(r"(path|rect|g|use|text|tspan|circle|ellipse)[-\d]*", i):
            continue
        vistos.add(i)
        salida.append(i)
    return salida


def marcos(ids: list[str]) -> list[str]:
    """Los prefijos que forman un marco completo de nueve piezas ("" = sin prefijo)."""
    conjunto = set(ids)
    prefijos = {i[: -len("center")].rstrip("-") for i in ids if i.endswith("center")}
    return sorted(p for p in prefijos if all((f"{p}-{x}" if p else x) in conjunto for x in PIEZAS))


def pieza(prefijo: str, nombre: str) -> str:
    return f"{prefijo}-{nombre}" if prefijo else nombre


def sueltos(ids: list[str]) -> list[str]:
    """Los elementos que no son pieza de ningún marco ni pistas (`hint-…`): iconos, flechas, marcas."""
    en_marcos = {pieza(p, x) for p in marcos(ids) for x in PIEZAS}
    return [i for i in ids if i not in en_marcos and "hint-" not in i]


def esquema(ruta_colors: Path) -> dict[str, str]:
    """Los colores de un esquema de KDE (`.colors`) que usan las clases de la hoja de Plasma, en hex."""
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    cfg.read(ruta_colors, encoding="utf-8")
    salida = {}
    for clase, (grupo, clave) in CLASES.items():
        if cfg.has_option(grupo, clave):
            r, g, b = (int(x) for x in cfg.get(grupo, clave).split(",")[:3])
            salida[clase] = f"#{r:02x}{g:02x}{b:02x}"
    return salida


def con_esquema(texto: str, colores: dict[str, str]) -> str:
    """El SVG con la hoja `current-color-scheme` reescrita con los colores del esquema (como hace Plasma)."""
    css = "\n".join(f".ColorScheme-{c} {{ color:{h}; stop-color:{h}; }}" for c, h in colores.items())
    nuevo, n = re.subn(r'(<style[^>]*id="current-color-scheme"[^>]*>)(.*?)(</style>)',
                       lambda m: m.group(1) + css + m.group(3), texto, flags=re.S)
    return nuevo


def colores_usados(texto: str) -> list[str]:
    return sorted({h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", texto)})


# ------------------------------------------------------------------ Aurorae

BOTONES = {"X": ("close", "cerrar"), "I": ("minimize", "minimizar"), "A": ("maximize", "maximizar"),
           "S": ("alldesktops", "en todos los escritorios"), "F": ("keepabove", "mantener encima"),
           "B": ("keepbelow", "mantener debajo"), "M": ("menu", "menú de la ventana"), "H": ("help", "ayuda"),
           "N": ("appmenu", "menú de la aplicación"), "_": ("", "separador")}
ESTADOS_BOTON = ("active", "hover", "pressed", "inactive", "deactivated")


def leer_rc(ruta: Path) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser(interpolation=None, strict=False, inline_comment_prefixes=None)
    cfg.optionxform = str
    texto = "\n".join(l for l in ruta.read_text(encoding="utf-8").splitlines() if not l.startswith("#"))
    cfg.read_string(texto)
    return cfg


def rc_plano(cfg: configparser.ConfigParser) -> dict[str, tuple[str, str]]:
    """{clave: (grupo, valor)} de [General] y [Layout] (las claves del rc no se repiten entre grupos)."""
    return {k: (g, v.strip()) for g in ("General", "Layout") if cfg.has_section(g) for k, v in cfg.items(g)}


def rgb_a_hex(valor: str) -> str:
    partes = [int(x) for x in valor.split(",")[:3]]
    return "#{:02x}{:02x}{:02x}".format(*partes)
