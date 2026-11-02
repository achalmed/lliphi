"""Tema del editor de TeXstudio (4.x) desde los tokens: los formatos de resaltado de las dos variantes en un perfil
`<id>.txsprofile` (INI de QSettings con `[formats]` para el claro y `[formatsDark]` para el oscuro).

TeXstudio guarda sus formatos en `texstudio.ini`, en `[formats]` o en `[formatsDark]` según su «modo oscuro», que
deduce de la paleta de la aplicación (texto casi blanco: oscuro) y vuelve a deducir cuando la paleta cambia
(`Texstudio::paletteChanged`): con las dos secciones llenas, **TeXstudio sigue solo a la variante de Plasma** (decisiones
5.6). Cada formato es un grupo `data/<id>` con `foreground`, `background`, `linescolor`, `bold`, `italic`,
`underline`, `waveUnderline` y `priority` (`QFormatScheme::save(QSettings&)`); un formato leído sustituye entero al de
omisión, así que se escriben todos los de `defaultFormats.qxf` de TeXstudio 4.9 salvo los marcadores, y la prioridad de
los que la llevan.

El fondo del editor no es un formato: TeXstudio pinta con el `Base` de la paleta, que con el estilo Kvantum del tema
global es el `base.color` de Kvantum (`kvantum.paleta_qt`, `fondo.vista`). Sobre él se componen, opacos, los resaltes (línea actual, selección, búsqueda,
diferencias), porque TeXstudio guarda los colores sin alfa. La sintaxis es la tabla única de los editores, leída como
la lee LaTeX Workshop en VS Code: las órdenes (`\\section`) en el azul de las funciones, `\\begin` y `\\end` en el rojo
de las palabras clave, los entornos en el cian de los tipos, lo matemático en amarillo y cian, los títulos en el rojo de
los títulos."""
from __future__ import annotations

from pathlib import Path

from nucleo import CABECERA_INI, escribir, registro

editores = registro.codigo("editores")
paleta_qt = registro.codigo("kvantum").paleta_qt

SECCION = {"claro": "formats", "oscuro": "formatsDark"}
# prioridad de los formatos que la declaran en defaultFormats.qxf (los demás, la de QFormat)
PRIORIDAD = {"magicComment": 0, "commentTodo": 0, "math-keyword": 0, "align-ampersand": 5, "math-text": 2}
ESTILOS = ("bold", "italic", "overline", "underline", "strikeout", "waveUnderline")


def formatos(tokens: dict, marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Formato de TeXstudio → sus campos (colores en `#rrggbb`, estilos en `true`)."""
    s, t = editores.paleta(tokens, variante)
    x, qt = editores.sintaxis(s, t), paleta_qt(tokens, variante)
    fondo = qt["base.color"]
    sobre = lambda color, aa: editores.sobre(color, fondo, aa)  # noqa: E731

    def fg(color: str, *estilos: str) -> dict[str, str]:
        return {"foreground": x.get(color, color), **{e: "true" for e in estilos}}

    def bg(color: str, *estilos: str) -> dict[str, str]:
        return {"background": color, **{e: "true" for e in estilos}}

    def ondulado(color: str) -> dict[str, str]:
        return {"waveUnderline": "true", "linescolor": color}

    f = {
        "background": {"linescolor": s["borde.separador"]},
        "line:error": bg(sobre(s["estado.error"], "33")), "line:warning": bg(sobre(s["estado.advertencia"], "33")),
        "line:badbox": bg(sobre(s["estado.info"], "33")),
        # comentarios
        "comment": fg("comentario", "italic"), "magicComment": fg("atributo"), "commentTodo": fg(s["estado.advertencia"], "bold"),
        # órdenes y entornos
        "keyword": fg("funcion"), "extra-keyword": fg("palabra-clave"), "environment": fg("tipo"),
        "structure": fg("titulo", "bold"), "escapeseq": fg("escape"), "numbers": fg("numero"),
        "align-ampersand": fg("atributo", "bold"), "verbatim": fg("cadena"), "text": fg("variable"),
        "link": fg("enlace", "underline"),
        # matemática
        "math-keyword": fg("numero"), "math-delimiter": fg("numero"), "math-text": fg("tipo"),
        # referencias, citas y paquetes: presentes en magenta; los que faltan, en el color de error y ondulados
        "referencePresent": fg("simbolo"), "referenceMissing": {**fg(s["estado.error"]), **ondulado(s["estado.error"])},
        "referenceMultiple": {**fg(s["estado.advertencia"]), **ondulado(s["estado.advertencia"])},
        "citationPresent": fg("simbolo"), "citationMissing": {**fg(s["estado.error"]), **ondulado(s["estado.error"])},
        "packagePresent": fg("simbolo"), "packageMissing": {**fg(s["estado.error"]), **ondulado(s["estado.error"])},
        # Sweave, Pweave, picture
        "sweave-block": fg("variable"), "sweave-delimiter": fg("atributo", "bold"),
        "pweave-block": fg("variable"), "pweave-delimiter": fg("atributo", "bold"),
        "picture": fg("tipo"), "picture-keyword": fg("funcion"),
        # resaltes sobre el texto
        "current": bg(qt["alt.base.color"]), "selection": bg(sobre(s["seleccion.fondo"], "55")),
        "search": {**bg(sobre(t["color3"], "66")), "foreground": s["texto.normal"]},
        "replacement": bg(sobre(s["estado.advertencia"], "33")), "previewSelection": bg(sobre(s["acento.suave"], "26")),
        "braceMatch": bg(sobre(s["acento.suave"], "40"), "bold"),
        "braceMismatch": {**bg(sobre(s["estado.error"], "66"), "bold"), "foreground": s["texto.normal"]},
        "preedit": bg(sobre(s["acento.suave"], "33")),
        "diffDelete": bg(sobre(s["estado.error"], "33")), "diffAdd": bg(sobre(s["estado.exito"], "33")),
        "diffReplace": bg(sobre(s["estado.advertencia"], "33")),
        # ortografía y gramática
        "spellingMistake": ondulado(s["estado.error"]), "badWord": {"linescolor": s["estado.error"]},
        "wordRepetition": ondulado(s["estado.advertencia"]), "wordRepetitionLongRange": ondulado(s["estado.advertencia"]),
        "grammarMistake": ondulado(s["estado.info"]), "latexSyntaxMistake": bg(sobre(s["estado.error"], "33")),
        "grammarMistakeSpecial1": bg(sobre(t["color2"], "33")), "grammarMistakeSpecial2": bg(sobre(t["color6"], "33")),
        "grammarMistakeSpecial3": bg(sobre(t["color4"], "33")), "grammarMistakeSpecial4": bg(sobre(t["color3"], "33")),
        "temporaryCodeCompletion": fg("comentario", "italic"),
        # docstrip (.dtx), Lua, Asymptote y los guiones de TeXstudio
        "dtx:guard": fg("atributo"), "dtx:macro": fg("funcion", "bold"), "dtx:verbatim": fg("cadena"),
        "dtx:specialchar": fg("escape"), "dtx:commands": fg("funcion", "bold"),
        "lua:keyword": fg("palabra-clave"), "lua:comment": fg("comentario", "italic"),
        "asymptote:block": fg("variable"), "asymptote:keyword": fg("palabra-clave"), "asymptote:type": fg("tipo"),
        "asymptote:numbers": fg("numero"), "asymptote:string": fg("cadena"), "asymptote:comment": fg("comentario", "italic"),
        "qtscript:comment": fg("comentario", "italic"), "qtscript:string": fg("cadena"), "qtscript:number": fg("numero"),
        "qtscript:keyword": fg("palabra-clave"), "qtscript:txs-variable": fg("simbolo"), "qtscript:txs-function": {"italic": "true"},
        "txs-test": fg(s["estado.info"], "bold"), "txs-test-summary": {"bold": "true"}, "txs-test-pass": fg(s["estado.exito"]),
        "txs-test-fail": fg(s["estado.error"]), "txs-test-warn": fg(s["estado.advertencia"]), "txs-test-qdebug": fg("constante"),
    }
    # llaves por nivel: el orden de los corchetes de VS Code (editorBracketHighlight.foreground1…6), y vuelta a empezar
    for i, c in enumerate(("color4", "color3", "color5", "color6", "color2", "color1", "color4", "color3")):
        f[f"braceLevel{i}"] = {"foreground": t[c]}
    for clave, campos in f.items():
        for e in ESTILOS:
            campos.setdefault(e, "false")
        if clave in PRIORIDAD:
            campos["priority"] = str(PRIORIDAD[clave])
    return f


def clave_ini(clave: str) -> str:
    """Una clave como la escribe QSettings en INI: `/` → `\\`, y todo lo que no sea letra, dígito, `_`, `-` o `.`, como
    `%XX` (así `line:error` es `line%3Aerror`)."""
    salida = []
    for c in clave:
        if c == "/":
            salida.append("\\")
        elif c.isascii() and (c.isalnum() or c in "_-."):
            salida.append(c)
        else:
            salida.append("".join(f"%{b:02X}" for b in c.encode()))
    return "".join(salida)


def seccion(tokens: dict, marca: dict, variante: str) -> list[str]:
    """Las líneas de `[formats]` o `[formatsDark]` (con la cabecera)."""
    lineas = [f"[{SECCION[variante]}]"]
    for id_, campos in sorted(formatos(tokens, marca, variante).items()):
        lineas += [f"{clave_ini(f'data/{id_}/{k}')}={v}" for k, v in sorted(campos.items())]
    return lineas + ["version=1.0", ""]


def texto_perfil(tokens: dict, marca: dict) -> str:
    return "\n".join([CABECERA_INI.rstrip("\n"), f"; {marca['nombre']} para TeXstudio: Opciones → Cargar perfil… "
                      "(solo cambia el resaltado del editor)", ""]
                     + seccion(tokens, marca, "claro") + seccion(tokens, marca, "oscuro"))


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / f"{marca['id']}.txsprofile", texto_perfil(tokens, marca), hechos)
    return hechos
