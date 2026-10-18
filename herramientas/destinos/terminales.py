"""Esquemas para terminales ajenas a KDE, uno por variante, desde el grupo `terminal` de los tokens:

- Alacritty (≥ 0.13): `alacritty/<id>-<variante>.toml` con la tabla `[colors]` (`primary`, `cursor`, `selection`,
  `normal`, `bright`, `search`, `hints`); se importa desde `alacritty.toml` con `general.import`.
- Kitty: `kitty/<id>-<variante>.conf` con `foreground`, `background`, `selection_*`, `cursor*`, `url_color`, los
  colores de bordes y pestañas y `color0..15`; se carga con `include` o como tema de `kitten themes`.

Los dieciséis ANSI, el fondo y los textos salen de `terminal.<variante>`; la selección, el cursor y los enlaces,
que Konsole no define, salen de los semánticos de la misma variante (`seleccion.*`, `acento.base`, `enlace`),
de modo que las tres terminales coinciden con el esquema de Plasma. Ningún color se escribe aquí."""
from __future__ import annotations

from pathlib import Path

from . import escribir, hexa, semanticos

NOMBRES_ANSI = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
CABECERA = "# GENERADO por herramientas/generar.py desde tokens/; no editar\n"


def colores(tokens: dict, variante: str) -> dict[str, str]:
    """Nombre → hex de todo lo que necesita una terminal en una variante."""
    t = {k: hexa(v) for k, v in tokens["terminal"][variante].items()}
    s = semanticos(tokens, variante)
    t.update({"seleccion-fondo": s["seleccion.fondo"], "seleccion-texto": s["seleccion.texto"],
              "cursor": s["acento.base"], "cursor-texto": s["texto.sobre-acento"], "enlace": s["enlace"],
              "borde": s["borde.separador"], "pestana-fondo": s["fondo.ventana"], "pestana-texto": s["texto.secundario"]})
    return t


def texto_alacritty(tokens: dict, marca: dict, variante: str) -> str:
    t = colores(tokens, variante)
    q = lambda k: f'"{t[k]}"'  # noqa: E731
    lineas = [CABECERA + f"# {marca['nombre_esquema'][variante]}: en alacritty.toml añade  [general]  import = [\"~/.config/alacritty/themes/{marca['id']}-{variante}.toml\"]", "",
              "[colors.primary]", f"background = {q('fondo')}", f"foreground = {q('texto')}",
              f"dim_foreground = {q('texto-tenue')}", f"bright_foreground = {q('texto-intenso')}", "",
              "[colors.cursor]", f"text = {q('cursor-texto')}", f"cursor = {q('cursor')}", "",
              "[colors.vi_mode_cursor]", f"text = {q('cursor-texto')}", f"cursor = {q('cursor')}", "",
              "[colors.selection]", f"text = {q('seleccion-texto')}", f"background = {q('seleccion-fondo')}", "",
              "[colors.search.matches]", f"foreground = {q('fondo')}", f"background = {q('color3')}", "",
              "[colors.search.focused_match]", f"foreground = {q('seleccion-texto')}", f"background = {q('seleccion-fondo')}", "",
              "[colors.hints.start]", f"foreground = {q('fondo')}", f"background = {q('color3')}", "",
              "[colors.hints.end]", f"foreground = {q('fondo')}", f"background = {q('color11')}", "",
              "[colors.footer_bar]", f"foreground = {q('pestana-texto')}", f"background = {q('pestana-fondo')}", "",
              "[colors.line_indicator]", "foreground = \"None\"", "background = \"None\"", ""]
    for bloque, base in (("normal", 0), ("bright", 8)):
        lineas.append(f"[colors.{bloque}]")
        lineas += [f"{n} = {q(f'color{base + i}')}" for i, n in enumerate(NOMBRES_ANSI)]
        lineas.append("")
    return "\n".join(lineas)


def texto_kitty(tokens: dict, marca: dict, variante: str) -> str:
    t = colores(tokens, variante)
    lineas = [CABECERA + f"# {marca['nombre_esquema'][variante]}: en kitty.conf añade  include themes/{marca['id']}-{variante}.conf",
              "", "## name: " + marca["nombre_esquema"][variante], "## author: " + marca["autor"],
              f"## license: {marca['licencia_activos']}", f"## blurb: {marca['descripcion']}", "",
              f"foreground {t['texto']}", f"background {t['fondo']}",
              f"selection_foreground {t['seleccion-texto']}", f"selection_background {t['seleccion-fondo']}", "",
              f"cursor {t['cursor']}", f"cursor_text_color {t['cursor-texto']}", "",
              f"url_color {t['enlace']}", "",
              f"active_border_color {t['cursor']}", f"inactive_border_color {t['borde']}", f"bell_border_color {t['color3']}", "",
              f"active_tab_foreground {t['texto']}", f"active_tab_background {t['fondo']}",
              f"inactive_tab_foreground {t['pestana-texto']}", f"inactive_tab_background {t['pestana-fondo']}",
              f"tab_bar_background {t['pestana-fondo']}", "",
              f"mark1_foreground {t['fondo']}", f"mark1_background {t['color4']}",
              f"mark2_foreground {t['fondo']}", f"mark2_background {t['color3']}",
              f"mark3_foreground {t['fondo']}", f"mark3_background {t['color2']}", ""]
    for i in range(16):
        lineas.append(f"color{i} {t[f'color{i}']}")
        if i in (7, 15):
            lineas.append("")
    return "\n".join(lineas)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        nombre = f"{marca['id']}-{variante}"
        escribir(destino / "terminales" / "alacritty" / f"{nombre}.toml", texto_alacritty(tokens, marca, variante), hechos)
        escribir(destino / "terminales" / "kitty" / f"{nombre}.conf", texto_kitty(tokens, marca, variante), hechos)
    return hechos
