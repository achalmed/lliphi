"""Temas de editores, desde los semánticos (interfaz) y el grupo `terminal` (sintaxis y terminal integrada):

- VS Code: una extensión mínima `vscode/<id>/` (`package.json` que contribuye dos temas, `themes/*-color-theme.json`
  con `colors` y `tokenColors`, `README.md`). Se instala copiando la carpeta a `~/.vscode/extensions/`.
- Zed: `zed/<id>.json` con las dos variantes en un solo archivo (`themes[]`, esquema v0.2.0), para `~/.config/zed/themes/`.

La sintaxis deriva de los ANSI de cada variante con una tabla única (`sintaxis`): palabras clave en rojo (color1),
cadenas en verde (color2), números y constantes en amarillo (color3), funciones en azul (color4), tipos en cian
(color6), atributos y símbolos en magenta (color5), comentarios en el texto inactivo y operadores y puntuación en
el texto secundario. Los dos editores leen la misma tabla, de modo que un archivo se ve igual en ambos.

Donde un resalte se superpone al texto (selección, coincidencias, línea actual) se usa el color del maestro con un
canal alfa (`#rrggbbaa`): el color base sigue siendo un token; la prueba de hexes lo comprueba sin el alfa."""
from __future__ import annotations

import json
from pathlib import Path

from . import VERSION, escribir, hexa, semanticos

ANSI_VSCODE = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")
ANSI_ZED = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")


def paleta(tokens: dict, variante: str) -> tuple[dict[str, str], dict[str, str]]:
    """(semánticos → hex, terminal → hex) de una variante."""
    return semanticos(tokens, variante), {k: hexa(v) for k, v in tokens["terminal"][variante].items()}


def sintaxis(s: dict[str, str], t: dict[str, str]) -> dict[str, str]:
    """Papel sintáctico → hex. Una sola tabla para los dos editores."""
    return {"palabra-clave": t["color1"], "cadena": t["color2"], "numero": t["color3"], "constante": t["color3"],
            "funcion": t["color4"], "tipo": t["color6"], "atributo": t["color5"], "simbolo": t["color5"],
            "etiqueta": t["color1"], "escape": t["color6"], "regex": t["color6"],
            "comentario": s["texto.inactivo"], "operador": s["texto.secundario"], "puntuacion": s["texto.secundario"],
            "variable": s["texto.normal"], "propiedad": s["texto.normal"], "parametro": s["texto.normal"],
            "invalido": s["estado.error"], "enlace": s["enlace"], "titulo": t["color1"],
            "insertado": s["estado.exito"], "borrado": s["estado.error"], "cambiado": s["estado.advertencia"]}


def alfa(hex6: str, aa: str) -> str:
    return hex6 + aa


# ---------------------------------------------------------------- VS Code

def colores_vscode(s: dict[str, str], t: dict[str, str]) -> dict[str, str]:
    c = {
        "focusBorder": s["foco"], "foreground": s["texto.normal"], "disabledForeground": s["texto.inactivo"],
        "descriptionForeground": s["texto.secundario"], "errorForeground": s["estado.error"], "icon.foreground": s["texto.secundario"],
        "selection.background": alfa(s["seleccion.fondo"], "66"), "widget.border": s["borde.separador"],
        "textLink.foreground": s["enlace"], "textLink.activeForeground": s["acento.suave"], "textPreformat.foreground": s["texto.normal"],
        "textBlockQuote.background": s["fondo.ventana"], "textBlockQuote.border": s["acento.base"], "textCodeBlock.background": s["fondo.ventana"],
        "button.background": s["acento.base"], "button.foreground": s["texto.sobre-acento"], "button.hoverBackground": s["acento.suave"],
        "button.secondaryBackground": s["fondo.boton"], "button.secondaryForeground": s["texto.normal"], "button.secondaryHoverBackground": s["fondo.ventana-alterno"],
        "badge.background": s["acento.base"], "badge.foreground": s["texto.sobre-acento"], "progressBar.background": s["acento.base"],
        "input.background": s["fondo.vista"], "input.foreground": s["texto.normal"], "input.border": s["borde.separador"],
        "input.placeholderForeground": s["texto.inactivo"], "inputOption.activeBorder": s["foco"],
        "inputOption.activeBackground": alfa(s["seleccion.fondo"], "33"), "inputOption.activeForeground": s["texto.normal"],
        "inputValidation.errorBackground": s["fondo.ventana"], "inputValidation.errorBorder": s["estado.error"],
        "inputValidation.warningBackground": s["fondo.ventana"], "inputValidation.warningBorder": s["estado.advertencia"],
        "inputValidation.infoBackground": s["fondo.ventana"], "inputValidation.infoBorder": s["estado.info"],
        "dropdown.background": s["fondo.vista"], "dropdown.foreground": s["texto.normal"], "dropdown.border": s["borde.separador"], "dropdown.listBackground": s["fondo.ventana"],
        "checkbox.background": s["fondo.vista"], "checkbox.border": s["borde.separador"], "checkbox.foreground": s["texto.normal"],
        "scrollbarSlider.background": alfa(s["texto.inactivo"], "40"), "scrollbarSlider.hoverBackground": alfa(s["texto.inactivo"], "66"),
        "scrollbarSlider.activeBackground": alfa(s["texto.inactivo"], "88"), "scrollbar.shadow": alfa(s["fondo.complementario"], "33"),
        # editor
        "editor.background": s["fondo.vista"], "editor.foreground": s["texto.normal"],
        "editorLineNumber.foreground": s["texto.inactivo"], "editorLineNumber.activeForeground": s["texto.normal"],
        "editorCursor.foreground": s["acento.base"], "editorCursor.background": s["texto.sobre-acento"],
        "editor.selectionBackground": alfa(s["seleccion.fondo"], "55"), "editor.inactiveSelectionBackground": alfa(s["seleccion.fondo"], "2a"),
        "editor.selectionHighlightBackground": alfa(s["acento.suave"], "33"), "editor.selectionHighlightBorder": alfa(s["acento.suave"], "66"),
        "editor.wordHighlightBackground": alfa(s["texto.inactivo"], "33"), "editor.wordHighlightStrongBackground": alfa(s["acento.suave"], "33"),
        "editor.findMatchBackground": alfa(t["color3"], "66"), "editor.findMatchHighlightBackground": alfa(t["color3"], "33"),
        "editor.findMatchBorder": t["color3"], "editor.findRangeHighlightBackground": alfa(s["fondo.ventana-alterno"], "66"),
        "editor.hoverHighlightBackground": alfa(s["acento.suave"], "22"), "editor.rangeHighlightBackground": alfa(s["fondo.ventana-alterno"], "66"),
        "editor.lineHighlightBackground": s["fondo.vista-alterno"], "editor.lineHighlightBorder": s["fondo.vista-alterno"],
        "editor.foldBackground": alfa(s["fondo.ventana-alterno"], "66"),
        "editorLink.activeForeground": s["enlace"], "editorWhitespace.foreground": s["borde.separador"],
        "editorIndentGuide.background1": s["borde.sutil"], "editorIndentGuide.activeBackground1": s["borde.separador"],
        "editorRuler.foreground": s["borde.sutil"], "editorCodeLens.foreground": s["texto.inactivo"],
        "editorBracketMatch.background": alfa(s["acento.suave"], "33"), "editorBracketMatch.border": s["acento.suave"],
        "editorBracketHighlight.foreground1": t["color4"], "editorBracketHighlight.foreground2": t["color3"], "editorBracketHighlight.foreground3": t["color5"],
        "editorBracketHighlight.foreground4": t["color6"], "editorBracketHighlight.foreground5": t["color2"], "editorBracketHighlight.foreground6": t["color1"],
        "editorBracketHighlight.unexpectedBracket.foreground": s["estado.error"],
        "editorGutter.background": s["fondo.vista"], "editorGutter.modifiedBackground": s["estado.advertencia"],
        "editorGutter.addedBackground": s["estado.exito"], "editorGutter.deletedBackground": s["estado.error"],
        "editorGutter.foldingControlForeground": s["texto.secundario"],
        "editorOverviewRuler.border": s["borde.sutil"], "editorOverviewRuler.findMatchForeground": alfa(t["color3"], "88"),
        "editorOverviewRuler.modifiedForeground": s["estado.advertencia"], "editorOverviewRuler.addedForeground": s["estado.exito"],
        "editorOverviewRuler.deletedForeground": s["estado.error"], "editorOverviewRuler.errorForeground": s["estado.error"],
        "editorOverviewRuler.warningForeground": s["estado.advertencia"], "editorOverviewRuler.infoForeground": s["estado.info"],
        "editorError.foreground": s["estado.error"], "editorWarning.foreground": s["estado.advertencia"], "editorInfo.foreground": s["estado.info"],
        "editorHint.foreground": s["texto.secundario"], "problemsErrorIcon.foreground": s["estado.error"],
        "problemsWarningIcon.foreground": s["estado.advertencia"], "problemsInfoIcon.foreground": s["estado.info"],
        "editorInlayHint.background": s["fondo.ventana-alterno"], "editorInlayHint.foreground": s["texto.secundario"],
        "editorWidget.background": s["fondo.ventana"], "editorWidget.border": s["borde.separador"], "editorWidget.foreground": s["texto.normal"],
        "editorSuggestWidget.background": s["fondo.ventana"], "editorSuggestWidget.border": s["borde.separador"],
        "editorSuggestWidget.selectedBackground": s["seleccion.fondo"], "editorSuggestWidget.selectedForeground": s["seleccion.texto"],
        "editorSuggestWidget.highlightForeground": s["acento.texto"], "editorSuggestWidget.focusHighlightForeground": s["seleccion.texto"],
        "editorHoverWidget.background": s["fondo.ventana"], "editorHoverWidget.border": s["borde.separador"],
        "editorGroup.border": s["borde.separador"], "editorGroupHeader.tabsBackground": s["fondo.ventana"], "editorGroupHeader.tabsBorder": s["borde.sutil"],
        "editorGroup.dropBackground": alfa(s["seleccion.fondo"], "33"), "editorPane.background": s["fondo.ventana"],
        # pestañas, barras y paneles
        "tab.activeBackground": s["fondo.vista"], "tab.activeForeground": s["texto.normal"], "tab.inactiveBackground": s["fondo.ventana"],
        "tab.inactiveForeground": s["texto.secundario"], "tab.border": s["borde.sutil"], "tab.activeBorderTop": s["acento.base"],
        "tab.hoverBackground": s["fondo.vista-alterno"], "tab.unfocusedActiveBorderTop": s["borde.separador"],
        "tab.unfocusedActiveForeground": s["texto.secundario"], "tab.unfocusedInactiveForeground": s["texto.inactivo"],
        "tab.lastPinnedBorder": s["borde.separador"],
        "breadcrumb.foreground": s["texto.secundario"], "breadcrumb.focusForeground": s["texto.normal"], "breadcrumb.activeSelectionForeground": s["texto.normal"],
        "breadcrumb.background": s["fondo.vista"], "breadcrumbPicker.background": s["fondo.ventana"],
        "sideBar.background": s["fondo.ventana"], "sideBar.foreground": s["texto.normal"], "sideBar.border": s["borde.separador"],
        "sideBarTitle.foreground": s["texto.secundario"], "sideBarSectionHeader.background": s["fondo.ventana"],
        "sideBarSectionHeader.foreground": s["texto.normal"], "sideBarSectionHeader.border": s["borde.sutil"],
        "list.activeSelectionBackground": s["seleccion.fondo"], "list.activeSelectionForeground": s["seleccion.texto"],
        "list.activeSelectionIconForeground": s["seleccion.texto"], "list.inactiveSelectionBackground": s["fondo.ventana-alterno"],
        "list.inactiveSelectionForeground": s["texto.normal"], "list.hoverBackground": s["fondo.ventana-alterno"], "list.hoverForeground": s["texto.normal"],
        "list.focusOutline": s["foco"], "list.focusBackground": s["fondo.ventana-alterno"], "list.highlightForeground": s["acento.texto"],
        "list.focusHighlightForeground": s["seleccion.texto"], "list.errorForeground": s["estado.error"], "list.warningForeground": s["estado.advertencia"],
        "list.deemphasizedForeground": s["texto.inactivo"], "list.dropBackground": alfa(s["seleccion.fondo"], "33"),
        "listFilterWidget.background": s["fondo.ventana"], "listFilterWidget.outline": s["foco"], "listFilterWidget.noMatchesOutline": s["estado.error"],
        "tree.indentGuidesStroke": s["borde.separador"], "tree.inactiveIndentGuidesStroke": s["borde.sutil"],
        "activityBar.background": s["fondo.encabezado"], "activityBar.foreground": s["texto.normal"], "activityBar.inactiveForeground": s["texto.inactivo"],
        "activityBar.border": s["borde.separador"], "activityBar.activeBorder": s["acento.base"], "activityBar.activeBackground": s["fondo.ventana-alterno"],
        "activityBarBadge.background": s["acento.base"], "activityBarBadge.foreground": s["texto.sobre-acento"],
        "activityBarTop.foreground": s["texto.normal"], "activityBarTop.activeBorder": s["acento.base"], "activityBarTop.inactiveForeground": s["texto.inactivo"],
        "statusBar.background": s["fondo.encabezado"], "statusBar.foreground": s["texto.secundario"], "statusBar.border": s["borde.separador"],
        "statusBar.debuggingBackground": s["acento.base"], "statusBar.debuggingForeground": s["texto.sobre-acento"],
        "statusBar.noFolderBackground": s["fondo.encabezado"], "statusBar.noFolderForeground": s["texto.secundario"],
        "statusBar.focusBorder": s["foco"], "statusBarItem.hoverBackground": s["fondo.ventana-alterno"], "statusBarItem.activeBackground": s["fondo.boton"],
        "statusBarItem.remoteBackground": s["acento.base"], "statusBarItem.remoteForeground": s["texto.sobre-acento"],
        "statusBarItem.prominentBackground": s["fondo.boton"], "statusBarItem.prominentForeground": s["texto.normal"],
        "statusBarItem.errorBackground": s["estado.error"], "statusBarItem.errorForeground": s["texto.sobre-acento"],
        "statusBarItem.warningBackground": s["estado.advertencia"], "statusBarItem.warningForeground": s["texto.sobre-acento"],
        "titleBar.activeBackground": s["fondo.encabezado"], "titleBar.activeForeground": s["texto.normal"],
        "titleBar.inactiveBackground": s["fondo.ventana"], "titleBar.inactiveForeground": s["texto.inactivo"], "titleBar.border": s["borde.separador"],
        "menu.background": s["fondo.ventana"], "menu.foreground": s["texto.normal"], "menu.selectionBackground": s["seleccion.fondo"],
        "menu.selectionForeground": s["seleccion.texto"], "menu.separatorBackground": s["borde.separador"], "menu.border": s["borde.separador"],
        "menubar.selectionBackground": s["fondo.ventana-alterno"], "menubar.selectionForeground": s["texto.normal"],
        "commandCenter.background": s["fondo.ventana"], "commandCenter.foreground": s["texto.secundario"], "commandCenter.border": s["borde.separador"],
        "commandCenter.activeBackground": s["fondo.ventana-alterno"], "commandCenter.activeForeground": s["texto.normal"],
        "panel.background": s["fondo.ventana"], "panel.border": s["borde.separador"], "panelTitle.activeBorder": s["acento.base"],
        "panelTitle.activeForeground": s["texto.normal"], "panelTitle.inactiveForeground": s["texto.secundario"], "panelInput.border": s["borde.separador"],
        "panelSectionHeader.background": s["fondo.ventana"], "panelSection.border": s["borde.separador"],
        # terminal integrada: el grupo `terminal`
        "terminal.background": t["fondo"], "terminal.foreground": t["texto"], "terminal.border": s["borde.separador"],
        "terminal.selectionBackground": alfa(s["seleccion.fondo"], "55"), "terminal.inactiveSelectionBackground": alfa(s["seleccion.fondo"], "2a"),
        "terminalCursor.foreground": s["acento.base"], "terminalCursor.background": s["texto.sobre-acento"],
        "terminal.findMatchBackground": alfa(t["color3"], "66"), "terminal.findMatchHighlightBackground": alfa(t["color3"], "33"),
        "terminal.tab.activeBorder": s["acento.base"],
        **{f"terminal.ansi{n}": t[f"color{i}"] for i, n in enumerate(ANSI_VSCODE)},
        **{f"terminal.ansiBright{n}": t[f"color{i + 8}"] for i, n in enumerate(ANSI_VSCODE)},
        # avisos, selector, vistas previas, diff, git
        "notifications.background": s["fondo.ventana"], "notifications.foreground": s["texto.normal"], "notifications.border": s["borde.separador"],
        "notificationCenterHeader.background": s["fondo.encabezado"], "notificationCenterHeader.foreground": s["texto.normal"],
        "notificationLink.foreground": s["enlace"], "notificationsErrorIcon.foreground": s["estado.error"],
        "notificationsWarningIcon.foreground": s["estado.advertencia"], "notificationsInfoIcon.foreground": s["estado.info"],
        "pickerGroup.border": s["borde.separador"], "pickerGroup.foreground": s["acento.texto"],
        "quickInput.background": s["fondo.ventana"], "quickInput.foreground": s["texto.normal"],
        "quickInputList.focusBackground": s["seleccion.fondo"], "quickInputList.focusForeground": s["seleccion.texto"], "quickInputList.focusIconForeground": s["seleccion.texto"],
        "quickInputTitle.background": s["fondo.ventana-alterno"],
        "peekView.border": s["acento.base"], "peekViewEditor.background": s["fondo.vista-alterno"], "peekViewEditor.matchHighlightBackground": alfa(t["color3"], "66"),
        "peekViewResult.background": s["fondo.ventana"], "peekViewResult.fileForeground": s["texto.normal"], "peekViewResult.lineForeground": s["texto.secundario"],
        "peekViewResult.matchHighlightBackground": alfa(t["color3"], "66"), "peekViewResult.selectionBackground": s["seleccion.fondo"],
        "peekViewResult.selectionForeground": s["seleccion.texto"], "peekViewTitle.background": s["fondo.ventana"],
        "peekViewTitleLabel.foreground": s["texto.normal"], "peekViewTitleDescription.foreground": s["texto.secundario"],
        "diffEditor.insertedTextBackground": alfa(s["estado.exito"], "26"), "diffEditor.removedTextBackground": alfa(s["estado.error"], "26"),
        "diffEditor.insertedLineBackground": alfa(s["estado.exito"], "1a"), "diffEditor.removedLineBackground": alfa(s["estado.error"], "1a"),
        "diffEditor.diagonalFill": s["borde.sutil"], "diffEditor.border": s["borde.separador"],
        "merge.currentHeaderBackground": alfa(s["estado.exito"], "66"), "merge.currentContentBackground": alfa(s["estado.exito"], "26"),
        "merge.incomingHeaderBackground": alfa(s["estado.info"], "66"), "merge.incomingContentBackground": alfa(s["estado.info"], "26"),
        "gitDecoration.modifiedResourceForeground": s["estado.advertencia"], "gitDecoration.addedResourceForeground": s["estado.exito"],
        "gitDecoration.deletedResourceForeground": s["estado.error"], "gitDecoration.untrackedResourceForeground": s["estado.exito"],
        "gitDecoration.ignoredResourceForeground": s["texto.inactivo"], "gitDecoration.conflictingResourceForeground": s["acento.texto"],
        "gitDecoration.renamedResourceForeground": s["estado.info"], "gitDecoration.stageModifiedResourceForeground": s["estado.advertencia"],
        "gitDecoration.stageDeletedResourceForeground": s["estado.error"], "gitDecoration.submoduleResourceForeground": s["estado.info"],
        "minimap.selectionHighlight": s["seleccion.fondo"], "minimap.findMatchHighlight": t["color3"], "minimap.errorHighlight": s["estado.error"],
        "minimap.warningHighlight": s["estado.advertencia"], "minimapGutter.addedBackground": s["estado.exito"],
        "minimapGutter.modifiedBackground": s["estado.advertencia"], "minimapGutter.deletedBackground": s["estado.error"],
        "debugToolBar.background": s["fondo.ventana"], "debugToolBar.border": s["borde.separador"], "debugIcon.breakpointForeground": s["acento.base"],
        "debugConsole.errorForeground": s["estado.error"], "debugConsole.warningForeground": s["estado.advertencia"], "debugConsole.infoForeground": s["estado.info"],
        "settings.headerForeground": s["texto.normal"], "settings.modifiedItemIndicator": s["acento.base"], "settings.focusedRowBackground": s["fondo.ventana-alterno"],
        "settings.rowHoverBackground": s["fondo.ventana-alterno"], "settings.focusedRowBorder": s["foco"],
        "keybindingLabel.background": s["fondo.boton"], "keybindingLabel.border": s["borde.separador"], "keybindingLabel.bottomBorder": s["borde.separador"],
        "keybindingLabel.foreground": s["texto.normal"], "toolbar.hoverBackground": s["fondo.ventana-alterno"], "toolbar.activeBackground": s["fondo.boton"],
        "walkThrough.embeddedEditorBackground": s["fondo.vista"], "welcomePage.background": s["fondo.ventana"],
        "welcomePage.tileBackground": s["fondo.vista"], "welcomePage.tileHoverBackground": s["fondo.vista-alterno"], "welcomePage.progress.foreground": s["acento.base"],
        "extensionButton.prominentBackground": s["acento.base"], "extensionButton.prominentForeground": s["texto.sobre-acento"], "extensionButton.prominentHoverBackground": s["acento.suave"],
        "extensionBadge.remoteBackground": s["acento.base"], "extensionBadge.remoteForeground": s["texto.sobre-acento"], "extensionIcon.starForeground": t["color3"],
        "charts.red": t["color1"], "charts.green": t["color2"], "charts.yellow": t["color3"], "charts.blue": t["color4"],
        "charts.purple": t["color5"], "charts.orange": t["color3"], "charts.foreground": s["texto.normal"], "charts.lines": s["borde.separador"],
        "symbolIcon.functionForeground": t["color4"], "symbolIcon.methodForeground": t["color4"], "symbolIcon.classForeground": t["color6"],
        "symbolIcon.interfaceForeground": t["color6"], "symbolIcon.variableForeground": s["texto.normal"], "symbolIcon.constantForeground": t["color3"],
        "symbolIcon.stringForeground": t["color2"], "symbolIcon.numberForeground": t["color3"], "symbolIcon.keywordForeground": t["color1"],
        "symbolIcon.propertyForeground": s["texto.normal"], "symbolIcon.enumeratorMemberForeground": t["color5"],
    }
    return c


def token_colors(x: dict[str, str]) -> list[dict]:
    """`tokenColors` de TextMate: nombre, ámbitos y ajustes; un papel por entrada, para que se lea como la tabla."""
    def e(nombre: str, ambitos: list[str], color: str, estilo: str | None = None) -> dict:
        ajustes = {"foreground": color}
        if estilo is not None:
            ajustes["fontStyle"] = estilo
        return {"name": nombre, "scope": ambitos, "settings": ajustes}
    return [
        e("Comentarios", ["comment", "punctuation.definition.comment", "string.comment"], x["comentario"], "italic"),
        e("Palabras clave y almacenamiento", ["keyword", "keyword.control", "keyword.other", "storage", "storage.type", "storage.modifier",
                                               "keyword.operator.new", "keyword.operator.expression", "keyword.operator.logical.python"], x["palabra-clave"]),
        e("Operadores", ["keyword.operator", "keyword.operator.assignment", "keyword.operator.arithmetic", "keyword.operator.comparison"], x["operador"]),
        e("Puntuación", ["punctuation", "punctuation.separator", "punctuation.terminator", "punctuation.definition.parameters",
                         "meta.brace", "punctuation.section"], x["puntuacion"]),
        e("Cadenas", ["string", "string.quoted", "string.template", "punctuation.definition.string", "string.unquoted"], x["cadena"]),
        e("Escapes y expresiones regulares", ["constant.character.escape", "string.regexp", "constant.other.placeholder"], x["escape"]),
        e("Números y constantes", ["constant.numeric", "constant.language", "constant.character", "constant.other",
                                   "keyword.other.unit", "support.constant"], x["numero"]),
        e("Funciones y métodos", ["entity.name.function", "support.function", "meta.function-call entity.name.function",
                                  "entity.name.function.member", "variable.function", "meta.require", "support.function.any-method"], x["funcion"]),
        e("Tipos, clases e interfaces", ["entity.name.type", "entity.name.class", "entity.name.namespace", "entity.other.inherited-class",
                                         "support.type", "support.class", "entity.name.struct", "entity.name.enum", "entity.name.interface"], x["tipo"]),
        e("Variables y propiedades", ["variable", "variable.other", "variable.other.property", "variable.other.object", "meta.object-literal.key",
                                      "support.variable", "variable.language"], x["variable"]),
        e("Parámetros", ["variable.parameter", "meta.parameter"], x["parametro"], "italic"),
        e("Etiquetas (HTML, XML, JSX)", ["entity.name.tag", "punctuation.definition.tag", "meta.tag.sgml", "entity.name.tag.css"], x["etiqueta"]),
        e("Atributos, decoradores y símbolos", ["entity.other.attribute-name", "meta.decorator", "entity.name.function.decorator",
                                                 "constant.other.symbol", "entity.other.attribute-name.id", "entity.other.attribute-name.class"], x["atributo"]),
        e("Propiedades CSS y claves", ["support.type.property-name", "meta.property-name", "support.type.property-name.json",
                                       "string.key", "entity.name.tag.yaml"], x["propiedad"]),
        e("Markdown: títulos", ["markup.heading", "entity.name.section", "markup.heading entity.name"], x["titulo"], "bold"),
        e("Markdown: negrita", ["markup.bold"], x["variable"], "bold"),
        e("Markdown: cursiva", ["markup.italic"], x["variable"], "italic"),
        e("Markdown: código", ["markup.inline.raw", "markup.raw", "markup.fenced_code.block"], x["cadena"]),
        e("Markdown: listas y citas", ["markup.list punctuation.definition.list.begin", "markup.quote", "beginning.punctuation.definition.list"], x["operador"]),
        e("Enlaces", ["markup.underline.link", "string.other.link", "constant.other.reference.link"], x["enlace"], "underline"),
        e("Diferencias: insertado", ["markup.inserted", "meta.diff.header.to-file", "punctuation.definition.inserted"], x["insertado"]),
        e("Diferencias: borrado", ["markup.deleted", "meta.diff.header.from-file", "punctuation.definition.deleted"], x["borrado"]),
        e("Diferencias: cambiado", ["markup.changed", "punctuation.definition.changed"], x["cambiado"]),
        e("Inválido", ["invalid", "invalid.illegal", "invalid.deprecated"], x["invalido"], "underline"),
    ]


def semantic_token_colors(x: dict[str, str]) -> dict[str, str]:
    return {"keyword": x["palabra-clave"], "string": x["cadena"], "number": x["numero"], "regexp": x["regex"],
            "function": x["funcion"], "method": x["funcion"], "class": x["tipo"], "interface": x["tipo"], "struct": x["tipo"],
            "type": x["tipo"], "typeParameter": x["tipo"], "namespace": x["tipo"], "enum": x["tipo"], "enumMember": x["simbolo"],
            "decorator": x["atributo"], "macro": x["atributo"], "variable": x["variable"], "property": x["propiedad"],
            "parameter": x["parametro"], "comment": x["comentario"], "operator": x["operador"]}


def tema_vscode(tokens: dict, marca: dict, variante: str) -> dict:
    s, t = paleta(tokens, variante)
    x = sintaxis(s, t)
    return {"$schema": "vscode://schemas/color-theme", "name": marca["nombre_esquema"][variante],
            "type": "light" if variante == "claro" else "dark", "semanticHighlighting": True,
            "colors": colores_vscode(s, t), "tokenColors": token_colors(x), "semanticTokenColors": semantic_token_colors(x)}


def package_json(marca: dict) -> dict:
    return {"name": marca["id"], "displayName": marca["nombre"], "description": marca["descripcion"], "version": VERSION,
            "publisher": marca["id"], "license": marca["licencia_activos"], "author": {"name": marca["autor"]},
            "homepage": marca["sitio_tema"], "repository": {"type": "git", "url": marca["repositorio"]},
            "engines": {"vscode": "^1.80.0"}, "categories": ["Themes"], "keywords": ["theme", "kde", "plasma", marca["id"]],
            "contributes": {"themes": [
                {"label": marca["nombre_esquema"]["oscuro"], "uiTheme": "vs-dark", "path": f"./themes/{marca['id']}-oscuro-color-theme.json"},
                {"label": marca["nombre_esquema"]["claro"], "uiTheme": "vs", "path": f"./themes/{marca['id']}-claro-color-theme.json"}]}}


# ---------------------------------------------------------------- Zed

def estilo_zed(s: dict[str, str], t: dict[str, str]) -> dict:
    x = sintaxis(s, t)
    estado = {"conflict": s["acento.texto"], "created": s["estado.exito"], "deleted": s["estado.error"], "error": s["estado.error"],
              "hidden": s["texto.inactivo"], "hint": s["texto.secundario"], "ignored": s["texto.inactivo"], "info": s["estado.info"],
              "modified": s["estado.advertencia"], "predictive": s["texto.inactivo"], "renamed": s["estado.info"],
              "success": s["estado.exito"], "unreachable": s["texto.inactivo"], "warning": s["estado.advertencia"]}
    e: dict = {
        "border": s["borde.separador"], "border.variant": s["borde.sutil"], "border.focused": s["foco"], "border.selected": s["acento.base"],
        "border.transparent": alfa(s["borde.separador"], "00"), "border.disabled": s["borde.sutil"],
        "elevated_surface.background": s["fondo.ventana"], "surface.background": s["fondo.ventana"], "background": s["fondo.ventana"],
        "element.background": s["fondo.boton"], "element.hover": s["fondo.ventana-alterno"], "element.active": s["fondo.boton"],
        "element.selected": alfa(s["seleccion.fondo"], "33"), "element.disabled": s["fondo.ventana"],
        "drop_target.background": alfa(s["seleccion.fondo"], "33"),
        "ghost_element.background": alfa(s["fondo.ventana"], "00"), "ghost_element.hover": s["fondo.ventana-alterno"],
        "ghost_element.active": s["fondo.boton"], "ghost_element.selected": alfa(s["seleccion.fondo"], "33"), "ghost_element.disabled": alfa(s["fondo.ventana"], "00"),
        "text": s["texto.normal"], "text.muted": s["texto.secundario"], "text.placeholder": s["texto.inactivo"],
        "text.disabled": s["texto.inactivo"], "text.accent": s["acento.texto"],
        "icon": s["texto.normal"], "icon.muted": s["texto.secundario"], "icon.disabled": s["texto.inactivo"],
        "icon.placeholder": s["texto.inactivo"], "icon.accent": s["acento.texto"],
        "status_bar.background": s["fondo.encabezado"], "title_bar.background": s["fondo.encabezado"], "title_bar.inactive_background": s["fondo.ventana"],
        "toolbar.background": s["fondo.vista"], "tab_bar.background": s["fondo.ventana"],
        "tab.inactive_background": s["fondo.ventana"], "tab.active_background": s["fondo.vista"],
        "search.match_background": alfa(t["color3"], "66"),
        "panel.background": s["fondo.ventana"], "panel.focused_border": s["foco"], "panel.indent_guide": s["borde.sutil"],
        "panel.indent_guide_hover": s["borde.separador"], "panel.indent_guide_active": s["borde.separador"],
        "pane.focused_border": s["foco"], "pane_group.border": s["borde.separador"],
        "scrollbar.thumb.background": alfa(s["texto.inactivo"], "40"), "scrollbar.thumb.hover_background": alfa(s["texto.inactivo"], "66"),
        "scrollbar.thumb.border": alfa(s["texto.inactivo"], "00"), "scrollbar.track.background": alfa(s["fondo.vista"], "00"), "scrollbar.track.border": s["borde.sutil"],
        "editor.foreground": s["texto.normal"], "editor.background": s["fondo.vista"], "editor.gutter.background": s["fondo.vista"],
        "editor.subheader.background": s["fondo.ventana"], "editor.active_line.background": s["fondo.vista-alterno"],
        "editor.highlighted_line.background": alfa(s["acento.suave"], "22"), "editor.line_number": s["texto.inactivo"],
        "editor.active_line_number": s["texto.normal"], "editor.hover_line_number": s["texto.secundario"], "editor.invisible": s["borde.separador"],
        "editor.wrap_guide": s["borde.sutil"], "editor.active_wrap_guide": s["borde.separador"],
        "editor.indent_guide": s["borde.sutil"], "editor.indent_guide_active": s["borde.separador"],
        "editor.document_highlight.read_background": alfa(s["texto.inactivo"], "33"),
        "editor.document_highlight.write_background": alfa(s["acento.suave"], "33"),
        "editor.document_highlight.bracket_background": alfa(s["acento.suave"], "33"),
        "terminal.background": t["fondo"], "terminal.foreground": t["texto"], "terminal.bright_foreground": t["texto-intenso"],
        "terminal.dim_foreground": t["texto-tenue"],
        **{f"terminal.ansi.{n}": t[f"color{i}"] for i, n in enumerate(ANSI_ZED)},
        **{f"terminal.ansi.bright_{n}": t[f"color{i + 8}"] for i, n in enumerate(ANSI_ZED)},
        **{f"terminal.ansi.dim_{n}": t[f"color{i}"] for i, n in enumerate(ANSI_ZED)},
        "link_text.hover": s["acento.suave"],
        "version_control.added": s["estado.exito"], "version_control.modified": s["estado.advertencia"], "version_control.deleted": s["estado.error"],
        "version_control.conflict_marker.ours": alfa(s["estado.exito"], "33"), "version_control.conflict_marker.theirs": alfa(s["estado.info"], "33"),
    }
    for k, v in estado.items():
        e[k] = v
        e[f"{k}.background"] = alfa(v, "1a")
        e[f"{k}.border"] = alfa(v, "66")
    e["players"] = [{"cursor": s["acento.base"], "background": s["acento.base"], "selection": alfa(s["seleccion.fondo"], "55")},
                    {"cursor": t["color4"], "background": t["color4"], "selection": alfa(t["color4"], "3d")},
                    {"cursor": t["color2"], "background": t["color2"], "selection": alfa(t["color2"], "3d")},
                    {"cursor": t["color3"], "background": t["color3"], "selection": alfa(t["color3"], "3d")},
                    {"cursor": t["color5"], "background": t["color5"], "selection": alfa(t["color5"], "3d")},
                    {"cursor": t["color6"], "background": t["color6"], "selection": alfa(t["color6"], "3d")}]
    def c(color: str, **extra) -> dict:
        return {"color": color, **extra}
    e["syntax"] = {
        "attribute": c(x["atributo"]), "boolean": c(x["constante"]), "comment": c(x["comentario"], font_style="italic"),
        "comment.doc": c(x["comentario"], font_style="italic"), "constant": c(x["constante"]), "constructor": c(x["tipo"]),
        "embedded": c(x["variable"]), "emphasis": c(x["variable"], font_style="italic"), "emphasis.strong": c(x["variable"], font_weight=700),
        "enum": c(x["tipo"]), "function": c(x["funcion"]), "function.method": c(x["funcion"]), "hint": c(x["comentario"]),
        "keyword": c(x["palabra-clave"]), "label": c(x["atributo"]), "link_text": c(x["enlace"], font_style="italic"),
        "link_uri": c(x["enlace"]), "number": c(x["numero"]), "operator": c(x["operador"]), "predictive": c(x["comentario"]),
        "preproc": c(x["palabra-clave"]), "primary": c(x["variable"]), "property": c(x["propiedad"]),
        "punctuation": c(x["puntuacion"]), "punctuation.bracket": c(x["puntuacion"]), "punctuation.delimiter": c(x["puntuacion"]),
        "punctuation.list_marker": c(x["operador"]), "punctuation.special": c(x["escape"]),
        "string": c(x["cadena"]), "string.escape": c(x["escape"]), "string.regex": c(x["regex"]), "string.special": c(x["escape"]),
        "string.special.symbol": c(x["simbolo"]), "tag": c(x["etiqueta"]), "text.literal": c(x["cadena"]),
        "title": c(x["titulo"], font_weight=700), "type": c(x["tipo"]), "variable": c(x["variable"]),
        "variable.special": c(x["palabra-clave"]), "variant": c(x["simbolo"]),
    }
    return e


def tema_zed(tokens: dict, marca: dict) -> dict:
    return {"$schema": "https://zed.dev/schema/themes/v0.2.0.json", "name": marca["nombre"], "author": marca["autor"],
            "themes": [{"name": marca["nombre_esquema"][v], "appearance": "light" if v == "claro" else "dark",
                        "style": estilo_zed(*paleta(tokens, v))} for v in ("oscuro", "claro")]}


# ---------------------------------------------------------------- salida

def _json(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, indent=2) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    ext = destino / "editores" / "vscode" / marca["id"]
    escribir(ext / "package.json", _json(package_json(marca)), hechos)
    for v in ("claro", "oscuro"):
        escribir(ext / "themes" / f"{marca['id']}-{v}-color-theme.json", _json(tema_vscode(tokens, marca, v)), hechos)
    escribir(ext / "README.md", f"""# {marca['nombre']} para VS Code

{marca['descripcion']}

Dos temas, **{marca['nombre_esquema']['oscuro']}** y **{marca['nombre_esquema']['claro']}**, generados desde los tokens
de {marca['nombre']} (los mismos del escritorio Plasma y de las terminales): la interfaz sigue el esquema de color,
la sintaxis los dieciséis ANSI y la terminal integrada el esquema de Konsole.

Generado por `herramientas/generar.py`; no editar. Sitio: {marca['sitio_tema']} · Código: {marca['repositorio']}
""", hechos)
    escribir(destino / "editores" / "zed" / f"{marca['id']}.json", _json(tema_zed(tokens, marca)), hechos)
    return hechos
