"""Temas del editor de Kate (y de KWrite, KDevelop y todo lo que use KTextEditor) desde los tokens: dos archivos de
KSyntaxHighlighting (`<id>-claro.theme`, `<id>-oscuro.theme`, JSON con `metadata`, `text-styles` y `editor-colors`)
para `$XDG_DATA_HOME/org.kde.syntax-highlighting/themes/`.

La sintaxis es la tabla única de los editores (`registro.codigo("editores").sintaxis`): un archivo se ve igual en Kate,
VS Code, Positron y Zed. Lo que cambia es el fondo: Kate, con «Seleccionar automáticamente el tema de color» (su
`Auto Color Theme Selection`, activo por omisión), elige el tema cuyo `BackgroundColor` es el `Base` de la paleta de
la aplicación y, entre ellos, el de `TextSelection` igual a su `Highlight` (`Repository::themeForPalette` de
KSyntaxHighlighting 6). Con el estilo Kvantum que aplica el tema global, esa paleta es la de Kvantum
(`kvantum.paleta_qt`: `base.color` es `fondo.vista`, `highlight.color` es `seleccion.fondo`), no la del esquema
`.colors`; el fondo y la selección del tema son exactamente esos, y al pasar de Lliphi Claro a Lliphi Oscuro Kate
cambia solo de tema, también en las ventanas abiertas (decisiones 5.4).

Como la selección es el acento opaco (el de Plasma), el texto seleccionado de todos los estilos es `seleccion.texto`.
Los resaltes sobre el texto (línea actual, búsqueda, plegado, plantillas) son el color del maestro con su alfa ya
compuesto sobre el fondo (`editores.sobre`), porque KSyntaxHighlighting no mezcla el alfa con el fondo."""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import VERSION, escribir, registro

editores = registro.codigo("editores")
paleta_qt = registro.codigo("kvantum").paleta_qt


def revision() -> int:
    """La `revision` de los metadatos sube con la versión de Lliphi (Kate prefiere el tema de revisión mayor)."""
    a, b, c = (int(x) for x in VERSION.split("-")[0].split(".")[:3])
    return a * 10000 + b * 100 + c


def tema(tokens: dict, marca: dict, variante: str) -> dict:
    s, t = editores.paleta(tokens, variante)
    x, qt = editores.sintaxis(s, t), paleta_qt(tokens, variante)
    fondo, sel = qt["base.color"], qt["highlight.color"]
    sobre = lambda color, aa: editores.sobre(color, fondo, aa)  # noqa: E731

    def e(papel: str, **estilo) -> dict:
        return {"text-color": x[papel] if papel in x else papel, "selected-text-color": s["seleccion.texto"], **estilo}

    estilos = {
        "Normal": e("variable", bold=False, italic=False, underline=False, **{"strike-through": False}),
        "Keyword": e("palabra-clave"), "ControlFlow": e("palabra-clave"), "Import": e("palabra-clave"),
        "Preprocessor": e("palabra-clave"), "Function": e("funcion"), "BuiltIn": e("funcion"),
        "Variable": e("variable"), "Operator": e("operador"), "Extension": e("tipo"), "DataType": e("tipo"),
        "Attribute": e("atributo"), "Annotation": e("atributo"), "CommentVar": e("atributo"), "Others": e("simbolo"),
        "Char": e("cadena"), "String": e("cadena"), "VerbatimString": e("cadena"),
        "SpecialChar": e("escape"), "SpecialString": e("regex"),
        "DecVal": e("numero"), "BaseN": e("numero"), "Float": e("numero"), "Constant": e("constante"),
        "Comment": e("comentario", italic=True), "Documentation": e("comentario", italic=True),
        "RegionMarker": e("comentario", **{"background-color": sobre(s["acento.suave"], "1a")}),
        "Information": e(s["estado.info"]), "Warning": e(s["estado.advertencia"]),
        "Alert": e(s["estado.error"], bold=True, **{"background-color": sobre(s["estado.error"], "26")}),
        "Error": e("invalido", underline=True),
    }
    colores = {
        "BackgroundColor": fondo, "TextSelection": sel, "CurrentLine": qt["alt.base.color"],
        "IconBorder": fondo, "LineNumbers": s["texto.inactivo"], "CurrentLineNumber": s["texto.normal"],
        "Separator": s["borde.separador"], "IndentationLine": s["borde.separador"], "TabMarker": s["borde.separador"],
        "WordWrapMarker": s["borde.separador"], "CodeFolding": sobre(s["acento.suave"], "33"),
        "BracketMatching": sobre(s["acento.suave"], "40"), "SearchHighlight": sobre(t["color3"], "66"),
        "ReplaceHighlight": sobre(t["color2"], "66"), "SpellChecking": s["estado.error"],
        "ModifiedLines": s["estado.advertencia"], "SavedLines": s["estado.exito"],
        "MarkBookmark": s["estado.info"], "MarkBreakpointActive": s["acento.base"],
        "MarkBreakpointReached": s["estado.advertencia"], "MarkBreakpointDisabled": s["texto.inactivo"],
        "MarkExecution": s["texto.secundario"], "MarkWarning": s["estado.advertencia"], "MarkError": s["estado.error"],
        "TemplateBackground": qt["alt.base.color"], "TemplatePlaceholder": sobre(s["estado.exito"], "33"),
        "TemplateFocusedPlaceholder": sobre(s["estado.exito"], "55"),
        "TemplateReadOnlyPlaceholder": sobre(s["estado.error"], "33"),
    }
    return {"metadata": {"name": marca["nombre_esquema"][variante], "revision": revision(),
                         "license": marca["licencia_codigo"], "copyright": [marca["autor"]]},
            "text-styles": estilos, "editor-colors": colores}


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for v in ("claro", "oscuro"):
        escribir(destino / f"{marca['id']}-{v}.theme",
                 json.dumps(tema(tokens, marca, v), ensure_ascii=False, indent=4) + "\n", hechos)
    return hechos
