"""GitHub: el estilo redefine las variables de Primer, su sistema de diseño.

GitHub solo deja elegir entre sus temas (claro, oscuro, alto contraste, para daltonismo) y seguir al sistema. Cada
tema es un bloque de unas 960 variables de Primer sobre `<html>`, que GitHub marca con `data-color-mode`
(`light`, `dark` o `auto`) y `data-light-theme`/`data-dark-theme`; en `auto` elige por `prefers-color-scheme`. El
estilo hace lo mismo: Lliphi Claro con `data-color-mode="light"` o con `auto` y el sistema claro, Lliphi Oscuro con
`dark` o con `auto` y el sistema oscuro, así que sigue al modo que el usuario haya elegido en GitHub (lo mejor es
«Sincronizar con el sistema») sea cual sea el tema de GitHub debajo.

Solo se redefinen las variables funcionales (`--bgColor-*`, `--fgColor-*`, `--borderColor-*`, `--button-*`,
`--control-*`, `--diffBlob-*`, `--prettylights-syntax-*`, `--codeMirror-syntax-*`, `--ansi-*`, `--fontStack-*`…):
las demás de Primer están escritas como `var(...)` de estas y las siguen solas. Las etiquetas de colores que elige
cada repositorio (`--label-*`, `--data-*`) se dejan como las pinta GitHub.

- El acento (azul en el claro, rojo en el oscuro) va en los enlaces, el foco, la selección, la pestaña elegida y el
  botón principal, que en GitHub es verde.
- Los fondos tenues del «acento» de Primer (avisos informativos, cabeceras de los trozos de un diff) van en el azul de
  información (`estado.info`): en el oscuro el acento es rojo y se leería como un borrado.
- Los rellenos con texto blanco (insignias «Open», «Merged», «Closed», contadores, casillas marcadas) toman los rellenos
  de la `Paleta`; los textos de estado, los estados de la variante; los diffs, los estados con alfa.
- El código, con la tabla de sintaxis de los editores; los registros de Actions, con los ANSI de la terminal.
- El gráfico de contribuciones, en el verde de éxito de la variante con alfa: actividad, no acento."""
from __future__ import annotations

NOMBRE = "GitHub"
DOMINIOS = ("github.com", "gist.github.com")
DESCRIPCION = "Lliphi Claro y Lliphi Oscuro en GitHub (variables de Primer), según el modo de GitHub y el del sistema."
AMBITOS = {"claro": [("(prefers-color-scheme: light)", '[data-color-mode="auto"]'), (None, '[data-color-mode="light"]')],
           "oscuro": [("(prefers-color-scheme: dark)", '[data-color-mode="auto"]'), (None, '[data-color-mode="dark"]')]}
FONDO = "--bgColor-default"

# (texto, fondo) que deben llegar a 4,5:1
CONTRASTE = [("--fgColor-default", "--bgColor-default"), ("--fgColor-default", "--bgColor-muted"),
             ("--fgColor-default", "--bgColor-inset"), ("--fgColor-default", "--overlay-bgColor"),
             ("--fgColor-muted", "--bgColor-default"), ("--fgColor-muted", "--bgColor-muted"), ("--fgColor-muted", "--bgColor-inset"),
             ("--fgColor-accent", "--bgColor-default"), ("--fgColor-accent", "--bgColor-muted"),
             ("--fgColor-success", "--bgColor-default"), ("--fgColor-danger", "--bgColor-default"),
             ("--fgColor-attention", "--bgColor-default"), ("--fgColor-severe", "--bgColor-default"),
             ("--fgColor-done", "--bgColor-default"), ("--fgColor-sponsors", "--bgColor-default"),
             ("--fgColor-default", "--control-bgColor-rest"), ("--fgColor-default", "--control-bgColor-hover"),
             ("--fgColor-default", "--control-bgColor-active"),
             ("--fgColor-onEmphasis", "--bgColor-emphasis"), ("--fgColor-onEmphasis", "--bgColor-accent-emphasis"),
             ("--fgColor-onEmphasis", "--bgColor-success-emphasis"), ("--fgColor-onEmphasis", "--bgColor-danger-emphasis"),
             ("--fgColor-onEmphasis", "--bgColor-attention-emphasis"), ("--fgColor-onEmphasis", "--bgColor-severe-emphasis"),
             ("--fgColor-onEmphasis", "--bgColor-done-emphasis"), ("--fgColor-onEmphasis", "--bgColor-sponsors-emphasis"),
             ("--fgColor-onEmphasis", "--bgColor-neutral-emphasis"), ("--fgColor-onInverse", "--bgColor-inverse"),
             ("--button-primary-fgColor-rest", "--button-primary-bgColor-rest"),
             ("--button-primary-fgColor-rest", "--button-primary-bgColor-hover"),
             ("--button-primary-fgColor-rest", "--button-primary-bgColor-active"),
             ("--tooltip-fgColor", "--tooltip-bgColor"), ("--header-fgColor-default", "--header-bgColor"),
             ("--header-fgColor-logo", "--header-bgColor"),
             ("--fgColor-default", "--diffBlob-additionNum-bgColor"), ("--fgColor-default", "--diffBlob-additionWord-bgColor"),
             ("--fgColor-default", "--diffBlob-deletionNum-bgColor"), ("--fgColor-default", "--diffBlob-deletionWord-bgColor"),
             ("--fgColor-default", "--bgColor-success-muted"), ("--fgColor-default", "--bgColor-danger-muted"),
             ("--fgColor-default", "--selection-bgColor")]
# la sintaxis se lee sobre el fondo de la vista de código y sobre el de los bloques de Markdown
CONTRASTE += [(f"--prettylights-syntax-{p}", fondo) for p in ("comment", "constant", "entity", "entityTag", "keyword",
              "string", "stringRegexp", "variable", "markup-heading", "markup-list", "metaDiffRange")
              for fondo in ("--bgColor-default", "--bgColor-muted")]

# papel de Primer → papel de la tabla de sintaxis de los editores
PRETTYLIGHTS = {"comment": "comentario", "constant": "constante", "constantOtherReferenceLink": "enlace",
                "entity": "funcion", "entityTag": "etiqueta", "keyword": "palabra-clave", "storageModifierImport": "variable",
                "string": "cadena", "stringRegexp": "regex", "variable": "tipo", "markup-heading": "titulo",
                "markup-bold": "variable", "markup-italic": "variable", "markup-list": "numero",
                "markup-inserted-text": "insertado", "markup-deleted-text": "borrado", "markup-changed-text": "cambiado",
                "markup-ignored-text": "variable", "metaDiffRange": "atributo", "bracketHighlighterAngle": "puntuacion",
                "bracketHighlighterUnmatched": "invalido"}
CODEMIRROR = {"comment": "comentario", "constant": "constante", "entity": "funcion", "keyword": "palabra-clave",
              "storage": "palabra-clave", "string": "cadena", "support": "tipo", "variable": "variable"}
# color ANSI de Primer → color de la terminal (registros de Actions)
ANSI = {"black": "color0", "blackBright": "color8", "red": "color1", "redBright": "color9", "green": "color2",
        "greenBright": "color10", "yellow": "color3", "yellowBright": "color11", "blue": "color4", "blueBright": "color12",
        "magenta": "color5", "magentaBright": "color13", "cyan": "color6", "cyanBright": "color14", "white": "color7",
        "whiteBright": "color15", "gray": "color8"}
ANSI_ANTIGUO = {"black": "black", "black-bright": "blackBright", "red": "red", "red-bright": "redBright", "green": "green",
                "green-bright": "greenBright", "yellow": "yellow", "yellow-bright": "yellowBright", "blue": "blue",
                "blue-bright": "blueBright", "magenta": "magenta", "magenta-bright": "magentaBright", "cyan": "cyan",
                "cyan-bright": "cyanBright", "white": "white", "white-bright": "whiteBright", "gray": "gray"}
# alfas de los fondos translúcidos (sobre el fondo de la página)
MUTED, BORDE_MUTED, DIFF_NUM, DIFF_PALABRA = "26", "66", "4d", "66"
CONTRIBUCIONES = ("4d", "80", "b3", "")


def variables(p) -> dict[str, str]:
    s, x, r = p.s, p.x, p.relleno
    # estado → (color del texto en la variante, relleno con texto blanco)
    estados = {"accent": (s["enlace"], r["acento"]), "success": (s["estado.exito"], r["exito"]),
               "attention": (s["estado.advertencia"], r["advertencia"]), "severe": (s["estado.advertencia"], r["advertencia"]),
               "danger": (s["estado.error"], r["error"]), "done": (p.t["color5"], r["morado"]),
               "sponsors": (p.t["color13"], r["rosa"])}
    # el fondo translúcido de cada estado: el color base del estado en la variante; el de «accent» (avisos informativos,
    # cabeceras de los trozos de un diff, filas resaltadas) es el azul de información, no el acento: en el oscuro el
    # acento es rojo y se confundiría con un borrado o un error
    base = {"accent": s["estado.info"], "success": s["estado.exito"], "attention": s["estado.advertencia"],
            "severe": s["estado.advertencia"], "danger": s["estado.error"], "done": p.t["color5"], "sponsors": p.t["color13"]}
    v = {
        # lienzos
        "--bgColor-default": s["fondo.vista"], "--bgColor-muted": s["fondo.vista-alterno"], "--bgColor-inset": s["fondo.ventana"],
        "--bgColor-emphasis": s["fondo.tooltip"] if p.variante == "claro" else s["borde.separador"],
        "--bgColor-inverse": s["texto.normal"], "--fgColor-onInverse": s["fondo.vista"], "--bgColor-disabled": s["fondo.ventana-alterno"],
        "--bgColor-neutral-muted": p.alfa("texto.inactivo", "33"), "--bgColor-neutral-emphasis": r["neutro"],
        "--overlay-bgColor": s["fondo.vista"] if p.variante == "claro" else s["fondo.ventana"],
        "--overlay-backdrop-bgColor": p.alfa("fondo.complementario", "66"),
        "--page-header-bgColor": s["fondo.vista"], "--dashboard-bgColor": s["fondo.ventana"], "--card-bgColor": s["fondo.vista-alterno"],
        # textos
        "--fgColor-default": s["texto.normal"], "--fgColor-muted": s["texto.secundario"], "--fgColor-neutral": s["texto.secundario"],
        "--fgColor-disabled": s["texto.inactivo"], "--fgColor-onEmphasis": s["texto.sobre-acento"],
        "--fgColor-link": s["enlace"],
        # bordes
        "--borderColor-default": s["borde.separador"], "--borderColor-muted": s["borde.sutil"],
        "--borderColor-emphasis": s["texto.inactivo"], "--borderColor-disabled": s["borde.sutil"],
        "--borderColor-translucent": p.alfa("borde.separador", "80"),
        # cabecera
        "--header-bgColor": s["fondo.ventana"], "--header-fgColor-default": s["texto.secundario"],
        "--header-fgColor-logo": s["texto.normal"], "--header-borderColor-divider": s["borde.separador"],
        "--headerSearch-bgColor": s["fondo.vista"], "--headerSearch-borderColor": s["borde.separador"],
        # controles y botones: el principal en el acento, los demás en los grises de la ventana
        "--control-bgColor-rest": s["fondo.ventana"], "--control-bgColor-hover": s["fondo.ventana-alterno"],
        "--control-bgColor-active": s["fondo.boton"], "--control-transparent-bgColor-hover": s["fondo.ventana-alterno"],
        "--control-transparent-bgColor-active": s["fondo.boton"], "--control-transparent-bgColor-selected": s["fondo.ventana-alterno"],
        "--control-borderColor-selected": s["texto.normal"], "--control-checked-bgColor-hover": r["acento-pasar"],
        "--control-checked-bgColor-active": r["acento-pasar"], "--controlKnob-bgColor-rest": s["fondo.vista"],
        "--controlTrack-bgColor-rest": s["fondo.ventana-alterno"], "--controlTrack-bgColor-hover": s["fondo.boton"],
        "--controlTrack-bgColor-active": s["borde.separador"],
        "--button-primary-bgColor-rest": s["acento.base"], "--button-primary-bgColor-hover": r["acento-pasar"],
        "--button-primary-bgColor-active": r["acento-pasar"], "--button-primary-bgColor-disabled": p.alfa("acento.base", "80"),
        "--button-primary-borderColor-disabled": p.alfa("acento.base", "80"), "--button-primary-fgColor-rest": s["texto.sobre-acento"],
        "--button-primary-iconColor-rest": s["texto.sobre-acento"],
        "--button-danger-fgColor-rest": s["estado.error"], "--button-danger-bgColor-hover": r["error"],
        "--button-outline-fgColor-rest": s["enlace"], "--button-outline-fgColor-hover": s["enlace"],
        "--button-outline-bgColor-active": s["acento.base"], "--button-inactive-bgColor": s["fondo.ventana-alterno"],
        "--button-inactive-fgColor": s["texto.inactivo"], "--button-star-iconColor": s["estado.advertencia"],
        "--buttonCounter-default-bgColor-rest": s["fondo.boton"],
        # foco, selección y navegación
        "--focus-outline-color": s["foco"], "--selection-bgColor": p.alfa("seleccion.fondo", "4d"),
        "--underlineNav-borderColor-active": s["acento.base"], "--sideNav-bgColor-selected": s["fondo.ventana-alterno"],
        "--menu-bgColor-active": s["fondo.ventana-alterno"], "--selectMenu-bgColor-active": p.alfa("acento.base", "33"),
        "--tooltip-bgColor": s["fondo.tooltip"], "--tooltip-fgColor": s["texto.tooltip"],
        "--highlight-neutral-bgColor": p.alfa("estado.advertencia", "66"),
        "--counter-bgColor-muted": p.alfa("texto.inactivo", "33"), "--counter-bgColor-emphasis": r["neutro"],
        "--timelineBadge-bgColor": s["fondo.ventana-alterno"], "--avatar-borderColor": s["borde.sutil"],
        "--skeletonLoader-bgColor": s["fondo.ventana"],
        # diffs: los estados con alfa sobre el fondo; la cabecera de cada trozo, el acento con alfa
        "--diffBlob-additionNum-bgColor": s["estado.exito"] + DIFF_NUM, "--diffBlob-additionWord-bgColor": s["estado.exito"] + DIFF_PALABRA,
        "--diffBlob-deletionNum-bgColor": s["estado.error"] + DIFF_NUM, "--diffBlob-deletionWord-bgColor": s["estado.error"] + DIFF_PALABRA,
        "--diffBlob-hunkNum-bgColor-rest": p.alfa("estado.info", "33"), "--diffBlob-hunkLine-bgColor": p.alfa("estado.info", "1f"),
        "--codeMirror-selection-bgColor": p.alfa("seleccion.fondo", "4d"),
    }
    for estado, (texto, relleno) in estados.items():
        v[f"--fgColor-{estado}"] = texto
        v[f"--bgColor-{estado}-muted"] = base[estado] + MUTED
        v[f"--bgColor-{estado}-emphasis"] = relleno
        v[f"--borderColor-{estado}-muted"] = base[estado] + BORDE_MUTED
        v[f"--borderColor-{estado}-emphasis"] = relleno
    # código: la tabla de los editores
    v |= {f"--prettylights-syntax-{papel}": x[lliphi] for papel, lliphi in PRETTYLIGHTS.items()}
    v |= {"--prettylights-syntax-markup-inserted-bg": s["estado.exito"] + MUTED, "--prettylights-syntax-markup-deleted-bg": s["estado.error"] + MUTED,
          "--prettylights-syntax-markup-changed-bg": s["estado.advertencia"] + MUTED, "--prettylights-syntax-markup-ignored-bg": s["fondo.boton"],
          "--prettylights-syntax-carriageReturn-bg": r["error"], "--prettylights-syntax-carriageReturn-text": s["texto.sobre-acento"],
          "--prettylights-syntax-sublimeLinterGutterMark": s["borde.separador"]}
    v |= {f"--codeMirror-syntax-fgColor-{papel}": x[lliphi] for papel, lliphi in CODEMIRROR.items()}
    # terminal: los registros de Actions (y los nombres antiguos de los mismos colores)
    v |= {f"--ansi-{nombre}": p.t[color] for nombre, color in ANSI.items()}
    v |= {f"--color-ansi-{antiguo}": p.t[ANSI[nombre]] for antiguo, nombre in ANSI_ANTIGUO.items()}
    # gráfico de contribuciones: el verde de éxito, de menos a más
    v["--contribution-default-bgColor-0"] = s["fondo.vista-alterno"]
    v |= {f"--contribution-default-bgColor-{i}": s["estado.exito"] + aa for i, aa in enumerate(CONTRIBUCIONES, 1)}
    v["--contribution-default-borderColor-0"] = s["borde.sutil"]
    return v


def reglas(p) -> dict[str, dict[str, str]]:
    return {}


def comunes(fuentes: dict[str, str]) -> dict[str, dict[str, str]]:
    """Inter en la interfaz y JetBrains Mono en el código: Primer las toma de sus `--fontStack-*`."""
    return {":root": {"--fontStack-sansSerif": fuentes["interfaz"], "--fontStack-sansSerifDisplay": fuentes["interfaz"],
                      "--fontStack-system": fuentes["interfaz"], "--fontStack-monospace": fuentes["monoespaciada"]}}
