"""Esquema de colores `lliphi` para Vim (≥ 9) y Neovim (≥ 0.9) desde los tokens: un solo `colors/lliphi.vim` que leen
los dos, con Lliphi Claro y Lliphi Oscuro según `background`.

- **Variante.** `:colorscheme lliphi` pinta la variante de `&background`. Vim y Neovim deducen `background` del fondo
  de la terminal al arrancar (Konsole responde a la pregunta OSC 11), y al cambiar `background` vuelven a cargar el
  esquema: en Konsole con Lliphi, un Vim nuevo abre en la variante de Plasma (decisiones 5.7).
- **Colores.** Fondo y texto, los de Konsole (`konsole.ansi`), para que el editor se funda con la terminal en que corre;
  la sintaxis, la tabla única de los editores; la interfaz (menús, barras, selección, búsqueda, diferencias), de los
  semánticos, con los resaltes compuestos sobre el fondo (`editores.sobre`), porque Vim no mezcla alfa. La terminal
  integrada (`:terminal`) lleva los dieciséis ANSI de Konsole (`g:terminal_ansi_colors`, `g:terminal_color_N`).
- **Neovim.** Además, los grupos de Tree-sitter (`@keyword`, `@function.method`…), los de los tokens semánticos del LSP
  (`@lsp.type.*`, con el mismo reparto que `semanticTokenColors` de VS Code) y los de diagnósticos, dentro de
  `if has('nvim')`, porque Vim no admite `@` en un nombre de grupo.
- **Sin colores verdaderos** (`notermguicolors`), cada grupo toma de los dieciséis colores de Konsole el más cercano
  al suyo (`ctermfg`/`ctermbg`), y el fondo y el texto son los de la terminal.

`g:lliphi_transparente = 1` (antes de `:colorscheme`) deja sin fondo el texto, para ver la transparencia de Konsole."""
from __future__ import annotations

from pathlib import Path

from nucleo import VERSION, escribir, registro

editores = registro.codigo("editores")
ansi = registro.codigo("konsole").ansi

ATRIBUTOS = ("bold", "italic", "underline", "undercurl", "strikethrough", "reverse")


def _rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def cercano(color: str, k: dict[str, str]) -> int:
    """El índice (0–15) del color de Konsole más cercano a `color` (distancia RGB ponderada por la vista)."""
    c = _rgb(color)

    def d(i: int) -> float:
        o = _rgb(k[f"color{i}"])
        r = (c[0] + o[0]) / 2
        return (2 + r / 256) * (c[0] - o[0]) ** 2 + 4 * (c[1] - o[1]) ** 2 + (2 + (255 - r) / 256) * (c[2] - o[2]) ** 2
    return min(range(16), key=d)


def grupos(tokens: dict, variante: str) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """(grupos de Vim y Neovim, grupos solo de Neovim, ANSI de Konsole): grupo → {fg, bg, sp, estilo}."""
    s, t = editores.paleta(tokens, variante)
    x, k = editores.sintaxis(s, t), ansi(tokens, variante)
    fondo = k["fondo"]
    sobre = lambda color, aa: editores.sobre(color, fondo, aa)  # noqa: E731

    def g(fg: str | None = None, bg: str | None = None, *estilo: str, sp: str | None = None) -> dict:
        return {"fg": x.get(fg, fg) if fg else None, "bg": bg, "sp": sp, "estilo": estilo}

    flotante = s["fondo.ventana-alterno"]
    linea = sobre(s["texto.inactivo"], "1f")
    comun = {
        # interfaz
        "Normal": g("variable", fondo), "NormalNC": g("variable", fondo), "NormalFloat": g("variable", flotante),
        "FloatBorder": g(s["borde.separador"], flotante), "FloatTitle": g("titulo", flotante, "bold"),
        "Cursor": g(fondo, s["acento.base"]), "lCursor": g(fondo, s["acento.base"]), "CursorIM": g(fondo, s["acento.base"]),
        "CursorLine": g(None, linea), "CursorColumn": g(None, linea), "ColorColumn": g(None, linea),
        "CursorLineNr": g(s["texto.normal"], None, "bold"), "LineNr": g(s["texto.inactivo"]),
        "SignColumn": g(s["texto.inactivo"], fondo), "FoldColumn": g(s["texto.inactivo"], fondo),
        "Folded": g("comentario", sobre(s["acento.suave"], "1a")),
        "Visual": g(None, sobre(s["seleccion.fondo"], "55")), "VisualNOS": g(None, sobre(s["seleccion.fondo"], "33")),
        "Search": g(s["texto.normal"], sobre(t["color3"], "66")), "IncSearch": g(fondo, t["color3"], "bold"),
        "CurSearch": g(fondo, t["color3"], "bold"), "Substitute": g(fondo, s["estado.advertencia"]),
        "MatchParen": g(None, sobre(s["acento.suave"], "40"), "bold"),
        "Pmenu": g("variable", flotante), "PmenuSel": g(s["seleccion.texto"], s["seleccion.fondo"]),
        "PmenuSbar": g(None, s["borde.sutil"]), "PmenuThumb": g(None, s["texto.inactivo"]),
        "PmenuKind": g("tipo", flotante), "PmenuExtra": g(s["texto.secundario"], flotante),
        "WildMenu": g(s["seleccion.texto"], s["seleccion.fondo"]),
        "StatusLine": g(s["texto.normal"], s["fondo.ventana-alterno"]), "StatusLineNC": g(s["texto.inactivo"], s["fondo.ventana"]),
        "StatusLineTerm": g(s["texto.normal"], s["fondo.ventana-alterno"]), "StatusLineTermNC": g(s["texto.inactivo"], s["fondo.ventana"]),
        "TabLine": g(s["texto.secundario"], s["fondo.ventana"]), "TabLineFill": g(None, s["fondo.ventana"]),
        "TabLineSel": g(s["texto.normal"], fondo, "bold"), "ToolbarLine": g(None, s["fondo.ventana"]),
        "VertSplit": g(s["borde.separador"], fondo), "WinSeparator": g(s["borde.separador"], fondo),
        "NonText": g(s["borde.separador"]), "EndOfBuffer": g(s["borde.separador"]), "SpecialKey": g(s["borde.separador"]),
        "Whitespace": g(s["borde.separador"]), "Conceal": g(s["texto.inactivo"]), "Directory": g("funcion"),
        "Title": g("titulo", None, "bold"), "ModeMsg": g(s["texto.normal"], None, "bold"), "MoreMsg": g(s["estado.exito"]),
        "Question": g(s["estado.exito"]), "ErrorMsg": g(s["estado.error"], None, "bold"), "WarningMsg": g(s["estado.advertencia"]),
        "QuickFixLine": g(None, sobre(s["acento.suave"], "26")),
        "DiffAdd": g(None, sobre(s["estado.exito"], "33")), "DiffChange": g(None, sobre(s["estado.advertencia"], "26")),
        "DiffDelete": g(s["estado.error"], sobre(s["estado.error"], "33")), "DiffText": g(None, sobre(s["estado.advertencia"], "55")),
        "SpellBad": g(None, None, "undercurl", sp=s["estado.error"]), "SpellCap": g(None, None, "undercurl", sp=s["estado.info"]),
        "SpellRare": g(None, None, "undercurl", sp=x["atributo"]), "SpellLocal": g(None, None, "undercurl", sp=x["tipo"]),
        # sintaxis
        "Comment": g("comentario", None, "italic"), "Constant": g("constante"), "String": g("cadena"), "Character": g("cadena"),
        "Number": g("numero"), "Boolean": g("constante"), "Float": g("numero"), "Identifier": g("variable"),
        "Function": g("funcion"), "Statement": g("palabra-clave"), "Conditional": g("palabra-clave"),
        "Repeat": g("palabra-clave"), "Label": g("palabra-clave"), "Keyword": g("palabra-clave"),
        "Exception": g("palabra-clave"), "Operator": g("operador"), "PreProc": g("palabra-clave"),
        "Include": g("palabra-clave"), "PreCondit": g("palabra-clave"), "Define": g("atributo"), "Macro": g("atributo"),
        "Type": g("tipo"), "StorageClass": g("palabra-clave"), "Structure": g("tipo"), "Typedef": g("tipo"),
        "Special": g("escape"), "SpecialChar": g("escape"), "Tag": g("etiqueta"), "Delimiter": g("puntuacion"),
        "SpecialComment": g("comentario", None, "bold"), "Debug": g(s["estado.advertencia"]),
        "Underlined": g("enlace", None, "underline"), "Ignore": g(s["texto.inactivo"]),
        "Error": g("invalido", None, "bold", "underline"), "Todo": g(s["estado.advertencia"], None, "bold"),
        "Added": g("insertado"), "Changed": g("cambiado"), "Removed": g("borrado"),
        "diffAdded": g("insertado"), "diffRemoved": g("borrado"), "diffChanged": g("cambiado"),
        "diffFile": g("titulo", None, "bold"), "diffLine": g("atributo"),
        "helpHyperTextJump": g("enlace", None, "underline"), "markdownH1": g("titulo", None, "bold"),
    }
    estados = {"Error": s["estado.error"], "Warn": s["estado.advertencia"], "Info": s["estado.info"],
               "Hint": s["texto.secundario"], "Ok": s["estado.exito"]}
    nvim = {
        "WinBar": g(s["texto.normal"], fondo, "bold"), "WinBarNC": g(s["texto.inactivo"], fondo),
        "MsgArea": g("variable", fondo), "MsgSeparator": g(s["borde.separador"], s["fondo.ventana"]),
        "LspReferenceText": g(None, sobre(s["texto.inactivo"], "33")), "LspReferenceRead": g(None, sobre(s["texto.inactivo"], "33")),
        "LspReferenceWrite": g(None, sobre(s["acento.suave"], "33")), "LspInlayHint": g(s["texto.secundario"], flotante),
        "LspCodeLens": g(s["texto.inactivo"]), "LspSignatureActiveParameter": g(None, sobre(s["acento.suave"], "33"), "bold"),
        **{f"Diagnostic{n}": g(c) for n, c in estados.items()},
        **{f"DiagnosticSign{n}": g(c, fondo) for n, c in estados.items()},
        **{f"DiagnosticVirtualText{n}": g(c, sobre(c, "1a")) for n, c in estados.items()},
        **{f"DiagnosticUnderline{n}": g(None, None, "undercurl", sp=c) for n, c in estados.items()},
        "DiagnosticUnnecessary": g(s["texto.inactivo"]), "DiagnosticDeprecated": g(None, None, "strikethrough", sp=s["texto.inactivo"]),
        # Tree-sitter (nombres de Neovim 0.10)
        "@variable": g("variable"), "@variable.builtin": g("palabra-clave"), "@variable.parameter": g("parametro", None, "italic"),
        "@variable.member": g("propiedad"), "@property": g("propiedad"), "@constant": g("constante"),
        "@constant.builtin": g("constante"), "@constant.macro": g("atributo"), "@module": g("tipo"), "@label": g("atributo"),
        "@string": g("cadena"), "@string.escape": g("escape"), "@string.regexp": g("regex"), "@string.special": g("escape"),
        "@string.special.symbol": g("simbolo"), "@string.special.url": g("enlace", None, "underline"),
        "@character": g("cadena"), "@character.special": g("escape"), "@number": g("numero"), "@number.float": g("numero"),
        "@boolean": g("constante"), "@type": g("tipo"), "@type.builtin": g("tipo"), "@type.definition": g("tipo"),
        "@attribute": g("atributo"), "@function": g("funcion"), "@function.builtin": g("funcion"),
        "@function.call": g("funcion"), "@function.macro": g("atributo"), "@function.method": g("funcion"),
        "@function.method.call": g("funcion"), "@constructor": g("tipo"), "@operator": g("operador"),
        "@keyword": g("palabra-clave"), "@keyword.function": g("palabra-clave"), "@keyword.return": g("palabra-clave"),
        "@keyword.import": g("palabra-clave"), "@keyword.operator": g("palabra-clave"), "@keyword.directive": g("palabra-clave"),
        "@punctuation.delimiter": g("puntuacion"), "@punctuation.bracket": g("puntuacion"), "@punctuation.special": g("escape"),
        "@comment": g("comentario", None, "italic"), "@comment.documentation": g("comentario", None, "italic"),
        "@comment.error": g(s["estado.error"], None, "bold"), "@comment.warning": g(s["estado.advertencia"], None, "bold"),
        "@comment.todo": g(s["estado.advertencia"], None, "bold"), "@comment.note": g(s["estado.info"], None, "bold"),
        "@markup.heading": g("titulo", None, "bold"), "@markup.strong": g("variable", None, "bold"),
        "@markup.italic": g("variable", None, "italic"), "@markup.strikethrough": g("variable", None, "strikethrough"),
        "@markup.underline": g("variable", None, "underline"), "@markup.link": g("enlace"),
        "@markup.link.url": g("enlace", None, "underline"), "@markup.link.label": g("enlace"), "@markup.raw": g("cadena"),
        "@markup.list": g("operador"), "@markup.quote": g("comentario", None, "italic"), "@markup.math": g("tipo"),
        "@tag": g("etiqueta"), "@tag.attribute": g("atributo"), "@tag.delimiter": g("puntuacion"),
        "@diff.plus": g("insertado"), "@diff.minus": g("borrado"), "@diff.delta": g("cambiado"),
    }
    # tokens semánticos del LSP: el reparto de `semanticTokenColors` de VS Code
    for tipo, color in editores.semantic_token_colors(x).items():
        nvim[f"@lsp.type.{tipo}"] = g(color, None, *(("italic",) if tipo in ("parameter", "comment") else ()))
    return comun, nvim, k


def linea_hi(grupo: str, d: dict, k: dict[str, str], texto: str) -> str:
    estilo = ",".join(e for e in ATRIBUTOS if e in d["estilo"]) or "NONE"
    partes = [f"hi {grupo}", f"guifg={d['fg'] or 'NONE'}", f"guibg={d['bg'] or 'NONE'}"]
    if d["sp"]:
        partes.append(f"guisp={d['sp']}")
    # sin colores verdaderos: el texto y el fondo, los de la terminal; lo demás, el ANSI de Konsole más cercano
    fg = "NONE" if not d["fg"] or d["fg"] == texto else str(cercano(d["fg"], k))
    bg = "NONE" if not d["bg"] or d["bg"] == k["fondo"] else str(cercano(d["bg"], k))
    partes += [f"gui={estilo}", f"ctermfg={fg}", f"ctermbg={bg}", f"cterm={estilo}"]
    return " ".join(partes)


def bloque(tokens: dict, marca: dict, variante: str) -> list[str]:
    comun, nvim, k = grupos(tokens, variante)
    texto = comun["Normal"]["fg"]
    lineas = [f'  " {marca["nombre_esquema"][variante]}'] + [f"  {linea_hi(n, d, k, texto)}" for n, d in comun.items()]
    lineas += ["  let g:terminal_ansi_colors = [" + ", ".join(f"'{k[f'color{i}']}'" for i in range(16)) + "]",
               "  if has('nvim')"]
    lineas += [f"    {linea_hi(n, d, k, texto)}" for n, d in nvim.items()]
    lineas += [f"    let g:terminal_color_{i} = '{k[f'color{i}']}'" for i in range(16)]
    return lineas + ["  endif"]


def texto_vim(tokens: dict, marca: dict) -> str:
    return "\n".join([
        f'" {marca["nombre"]} para Vim y Neovim: {marca["nombre_esquema"]["claro"]} con background=light,',
        f'" {marca["nombre_esquema"]["oscuro"]} con background=dark. {marca["nombre"]} {VERSION} · {marca["repositorio"]}',
        f'" GENERADO por herramientas/generar.py desde tokens/ (complementos/vim); no editar. Licencia: {marca["licencia_codigo"]}.',
        '" g:lliphi_transparente = 1 deja sin fondo el texto (la transparencia de la terminal).',
        "", "hi clear", "if exists('syntax_on')", "  syntax reset", "endif", f"let g:colors_name = '{marca['id']}'", "",
        "if &background ==# 'light'", *bloque(tokens, marca, "claro"), "else", *bloque(tokens, marca, "oscuro"), "endif", "",
        f"if get(g:, '{marca['id']}_transparente', 0)",
        *[f"  hi {n} guibg=NONE ctermbg=NONE" for n in ("Normal", "NormalNC", "SignColumn", "FoldColumn", "EndOfBuffer",
                                                         "VertSplit", "WinSeparator", "TabLineSel")],
        "endif", ""])


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / "colors" / f"{marca['id']}.vim", texto_vim(tokens, marca), hechos)
    return hechos
