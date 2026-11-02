"""Temas de RStudio (decisiones 5.40): «<nombre> Claro» y «<nombre> Oscuro» como `.rstheme`, el CSS sobre Ace que RStudio
registra desde `~/.config/rstudio/themes/` (o con `rstudioapi::addTheme`), y el programa con que la vigilancia de
`fondo-variante` cambia `editor_theme` al pasar de una variante a otra.

Formato (comprobado el 2026-11-01 en los 34 temas de RStudio 2026.05.1, `resources/app/resources/themes/`): dos
comentarios de cabecera, `rs-theme-name` y `rs-theme-is-dark` (TRUE o FALSE; con TRUE RStudio pone oscura la interfaz
entera: paneles, pestañas, barras y menús se derivan del fondo del editor), y reglas CSS sobre las clases de Ace
(`.ace_keyword`, `.ace_string`…), las de RStudio (`.ace_foreign_line` para los bloques de código de R Markdown,
`.ace_console_error`, `.ace_paren_color_0..6` de los paréntesis de colores, las guías de sangría de colores) y las de la
consola y la terminal: `.terminal` y `.xtermColor0..255` / `.xtermBgColor0..255`, con las que RStudio pinta los
colores ANSI de la consola de R y de la terminal integrada.

La sintaxis sale de la misma tabla que los demás editores (`editores.sintaxis`); la consola y la terminal, de los
dieciséis colores de Konsole (`konsole.ansi`, decisiones 4.30). Los colores 16 a 255 de xterm (el cubo 6×6×6 y la
rampa de grises) no son de Lliphi: se calculan con la fórmula estándar de xterm, como en los temas de RStudio, para que
los paquetes que usan 256 colores (cli, tibble) se vean igual que en una terminal. Ningún color se escribe aquí."""
from __future__ import annotations

from pathlib import Path

from nucleo import escribir, registro

sintaxis = registro.codigo("editores").sintaxis   # la tabla única de sintaxis de los editores
paleta = registro.codigo("editores").paleta
ansi = registro.codigo("konsole").ansi             # la terminal: los ANSI de Konsole (decisiones 4.30)

FUENTE_VARIANTE = Path(__file__).resolve().parent / "variante.py"
PROGRAMA_VARIANTE = "variante-rstudio.py"
# orden de los paréntesis y de las guías de sangría de colores (siete, como los de RStudio)
ARCOIRIS = ("color4", "color3", "color5", "color6", "color2", "color1", "color13")


def xterm256() -> dict[int, str]:
    """Los colores 16–255 de xterm: el cubo 6×6×6 (niveles 0, 95, 135, 175, 215, 255) y la rampa de grises 8 + 10·n."""
    niveles = (0, 95, 135, 175, 215, 255)
    c = {16 + 36 * r + 6 * g + b: "#%02x%02x%02x" % (niveles[r], niveles[g], niveles[b])
         for r in range(6) for g in range(6) for b in range(6)}
    c.update({232 + i: "#%02x%02x%02x" % ((8 + 10 * i,) * 3) for i in range(24)})
    return c


def reglas(tokens: dict, variante: str) -> list[tuple[str, dict[str, str]]]:
    """(selector, {propiedad: valor}) del tema de una variante, en orden."""
    s, t = paleta(tokens, variante)
    x, k = sintaxis(s, t), ansi(tokens, variante)
    oscuro = variante == "oscuro"
    r: list[tuple[str, dict[str, str]]] = [
        # editor
        (".ace_editor, .ace_editor_theme .profvis-flamegraph, .ace_editor_theme", {"background-color": s["fondo.vista"], "color": s["texto.normal"]}),
        (".ace_gutter", {"background": s["fondo.vista"], "color": s["texto.inactivo"]}),
        (".ace_gutter-active-line", {"background-color": s["fondo.vista-alterno"], "color": s["texto.normal"]}),
        (".ace_print-margin", {"width": "1px", "background": s["borde.sutil"]}),
        (".ace_cursor", {"color": s["acento.base"]}),
        (".ace_marker-layer .ace_selection", {"background": s["seleccion.fondo"] + "55"}),
        (".ace_selection.ace_start", {"box-shadow": f"0 0 3px 0px {s['fondo.vista']}", "border-radius": "2px"}),
        (".ace_marker-layer .ace_step", {"background": t["color3"] + "44"}),
        (".ace_marker-layer .ace_bracket", {"margin": "-1px 0 0 -1px", "border": f"1px solid {s['acento.suave']}"}),
        (".ace_marker-layer .ace_active-line", {"background": s["fondo.vista-alterno"]}),
        (".ace_marker-layer .ace_selected-word", {"border": f"1px solid {s['acento.suave']}"}),
        (".ace_invisible", {"color": s["borde.separador"]}),
        (".ace_indent-guide", {"background": f"linear-gradient(to left, {s['borde.sutil']} 1px, transparent 1px, transparent)"}),
        (".ace_fold", {"background-color": x["funcion"], "border-color": s["texto.normal"]}),
        # sintaxis: la tabla de los editores
        (".ace_keyword, .ace_meta, .ace_storage, .ace_storage.ace_type", {"color": x["palabra-clave"]}),
        (".ace_keyword.ace_operator, .ace_punctuation, .ace_paren", {"color": x["operador"]}),
        (".ace_constant.ace_numeric, .ace_keyword.ace_other.ace_unit", {"color": x["numero"]}),
        (".ace_constant.ace_language, .ace_constant.ace_character, .ace_support.ace_constant, .ace_constant.ace_other", {"color": x["constante"]}),
        (".ace_constant.ace_character.ace_escape", {"color": x["escape"]}),
        (".ace_string", {"color": x["cadena"]}),
        (".ace_string.ace_regexp", {"color": x["regex"]}),
        (".ace_comment", {"color": x["comentario"], "font-style": "italic"}),
        (".ace_entity.ace_name.ace_function, .ace_support.ace_function", {"color": x["funcion"]}),
        (".ace_support.ace_class, .ace_support.ace_type, .ace_entity.ace_name.ace_type", {"color": x["tipo"]}),
        (".ace_variable", {"color": x["variable"]}),
        (".ace_variable.ace_parameter", {"color": x["parametro"], "font-style": "italic"}),
        (".ace_entity.ace_other.ace_attribute-name", {"color": x["atributo"]}),
        (".ace_entity.ace_name.ace_tag, .ace_meta.ace_tag", {"color": x["etiqueta"]}),
        (".ace_heading, .ace_markup.ace_heading", {"color": x["titulo"], "font-weight": "bold"}),
        (".ace_markup.ace_underline", {"color": x["enlace"]}),
        (".ace_invalid", {"color": s["texto.sobre-acento"], "background-color": x["invalido"]}),
        (".ace_invalid.ace_deprecated", {"color": s["texto.sobre-acento"], "background-color": x["cambiado"]}),
        (".nocolor.ace_editor .ace_line span", {"color": x["palabra-clave"] + " !important"}),
        # RStudio: paréntesis, bloques de R Markdown, depuración, búsqueda, consola
        (".ace_bracket", {"margin": "0 !important", "border": "0 !important", "background-color": s["acento.suave"] + "55"}),
        (".ace_marker-layer .ace_foreign_line", {"position": "absolute", "z-index": "-1", "background-color": s["fondo.vista-alterno"]}),
        (".ace_node-selector", {"background-color": s["acento.base"]}),
        (".ace_comment-highlight", {"color": s["fondo.vista"], "background-color": t["color3"]}),
        (".ace_marker-layer .ace_active_debug_line", {"position": "absolute", "z-index": "-1", "background-color": t["color3"] + "44"}),
        (".ace_marker-layer .ace_find_line", {"position": "absolute", "z-index": "-1", "background-color": s["fondo.ventana-alterno"]}),
        (".ace_console_error", {"background-color": s["fondo.vista-alterno"]}),
        (".ace_editor_theme a" if not oscuro else ".editor_dark.ace_editor_theme a", {"color": s["enlace"] + " !important"}),
        # terminal integrada: los ANSI de Konsole
        (".terminal", {"background-color": k["fondo"], "color": k["texto"], "font-feature-settings": '"liga" 0', "position": "relative",
                       "user-select": "none", "-ms-user-select": "none", "-webkit-user-select": "none"}),
        (".terminal.xterm-cursor-style-block.focus:not(.xterm-cursor-blink-on) .terminal-cursor", {"background-color": s["acento.base"], "color": s["texto.sobre-acento"]}),
        (".terminal.focus.xterm-cursor-style-bar:not(.xterm-cursor-blink-on) .terminal-cursor::before,\n"
         ".terminal.focus.xterm-cursor-style-underline:not(.xterm-cursor-blink-on) .terminal-cursor::before",
         {"content": "''", "position": "absolute", "background-color": s["acento.base"]}),
        (".terminal:not(.focus) .terminal-cursor", {"outline": f"1px solid {s['acento.base']}", "outline-offset": "-1px"}),
        (".terminal .xterm-selection div", {"position": "absolute", "background-color": s["seleccion.fondo"] + "55"}),
        (".terminal .xterm-viewport", {"background-color": k["fondo"], "overflow-y": "scroll"}),
        (".xtermInvertColor", {"color": k["fondo"]}), (".xtermInvertBgColor", {"background-color": k["texto"]}),
        (".xtermBold", {"font-weight": "bold"}), (".xtermBlur", {"filter": "brightness(75%)"}),
        (".xtermUnderline", {"text-decoration": "underline"}), (".xtermBlink", {"text-decoration": "blink"}),
        (".xtermHidden", {"visibility": "hidden"}), (".xtermItalic", {"font-style": "italic"}),
        (".xtermStrike", {"text-decoration": "line-through"}),
    ]
    colores = {i: k[f"color{i}"] for i in range(16)} | xterm256()
    for i, c in colores.items():
        r += [(f".xtermColor{i}", {"color": c + " !important"}), (f".xtermBgColor{i}", {"background-color": c})]
    # capas de Ace, como en los temas de RStudio
    r += [(".ace_layer", {"z-index": "3"}), (".ace_layer.ace_print-margin-layer", {"z-index": "2"}),
          (".ace_layer.ace_marker-layer", {"z-index": "1"})]
    # autocompletado: el menú de la interfaz
    for prefijo in ("", ".rstudio-themes-dark-menus "):
        r += [(f"{prefijo}.ace_editor.ace_autocomplete", {"background": s["fondo.ventana"], "border": f"solid 1px {s['borde.separador']} !important",
                                                          "color": s["texto.normal"]}),
              (f"{prefijo}.ace_editor.ace_autocomplete .ace_marker-layer .ace_active-line,\n"
               f"{prefijo}.ace_editor.ace_autocomplete .ace_marker-layer .ace_line-hover",
               {"background": s["seleccion.fondo"] + "44", "border": "none"}),
              (f"{prefijo}.ace_editor.ace_autocomplete .ace_completion-highlight", {"color": s["acento.texto"]})]
    # paréntesis y guías de sangría de colores: siete ANSI de Konsole
    for i, c in enumerate(ARCOIRIS):
        r.append((f".ace_paren_color_{i}, .editor_dark .ace_paren_color_{i}", {"color": k[c]}))
    for i, c in enumerate(ARCOIRIS):
        r.append((f".rstudio_rainbow_indent_guides .ace_line .ace_indent-guide:nth-child(7n+{i + 1})",
                  {"background": f"linear-gradient(to left, {k[c]}bb 1px, transparent 1px, transparent)"}))
    for i, c in enumerate(ARCOIRIS):
        r.append((f".rstudio_rainbow_indent_fills .ace_line .ace_indent-guide:nth-child(7n+{i + 1})",
                  {"background": f"linear-gradient(to left, {k[c]}bb 1px, {k[c]}33 1px, {k[c]}33)"}))
    return r


def texto_rstheme(tokens: dict, marca: dict, variante: str) -> str:
    lineas = [f"/* rs-theme-name: {marca['nombre_esquema'][variante]} */",
              f"/* rs-theme-is-dark: {'TRUE' if variante == 'oscuro' else 'FALSE'} */",
              "/* GENERADO por herramientas/generar.py desde tokens/; no editar */"]
    for selector, props in reglas(tokens, variante):
        lineas.append(selector + " {")
        lineas += [f"  {p}: {v};" for p, v in props.items()]
        lineas.append("}")
    return "\n".join(lineas) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for v in ("claro", "oscuro"):
        escribir(destino / f"{marca['nombre_esquema'][v]}.rstheme", texto_rstheme(tokens, marca, v), hechos)
    texto = (FUENTE_VARIANTE.read_text(encoding="utf-8").replace("@NOMBRE@", marca["nombre"])
             .replace("@CLARO@", marca["nombre_esquema"]["claro"]).replace("@OSCURO@", marca["nombre_esquema"]["oscuro"]))
    escribir(destino / PROGRAMA_VARIANTE, texto, hechos)
    (destino / PROGRAMA_VARIANTE).chmod(0o755)
    return hechos
