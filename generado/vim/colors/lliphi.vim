" Lliphi para Vim y Neovim: Lliphi Claro con background=light,
" Lliphi Oscuro con background=dark. Lliphi 0.3.0 · https://github.com/achalmed/lliphi
" GENERADO por herramientas/generar.py desde tokens/ (complementos/vim); no editar. Licencia: MIT.
" g:lliphi_transparente = 1 deja sin fondo el texto (la transparencia de la terminal).

hi clear
if exists('syntax_on')
  syntax reset
endif
let g:colors_name = 'lliphi'

if &background ==# 'light'
  " Lliphi Claro
  hi Normal guifg=#1d1f24 guibg=#f2f3f5 gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi NormalNC guifg=#1d1f24 guibg=#f2f3f5 gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi NormalFloat guifg=#1d1f24 guibg=#e0e1e5 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi FloatBorder guifg=#ccced2 guibg=#e0e1e5 gui=NONE ctermfg=7 ctermbg=7 cterm=NONE
  hi FloatTitle guifg=#a43b38 guibg=#e0e1e5 gui=bold ctermfg=0 ctermbg=7 cterm=bold
  hi Cursor guifg=#f2f3f5 guibg=#315bef gui=NONE ctermfg=7 ctermbg=4 cterm=NONE
  hi lCursor guifg=#f2f3f5 guibg=#315bef gui=NONE ctermfg=7 ctermbg=4 cterm=NONE
  hi CursorIM guifg=#f2f3f5 guibg=#315bef gui=NONE ctermfg=7 ctermbg=4 cterm=NONE
  hi CursorLine guifg=NONE guibg=#e1e2e4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi CursorColumn guifg=NONE guibg=#e1e2e4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi ColorColumn guifg=NONE guibg=#e1e2e4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi CursorLineNr guifg=#1d1f24 guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi LineNr guifg=#66676c guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi SignColumn guifg=#66676c guibg=#f2f3f5 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi FoldColumn guifg=#66676c guibg=#f2f3f5 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Folded guifg=#66676c guibg=#e1e6f4 gui=NONE ctermfg=7 ctermbg=7 cterm=NONE
  hi Visual guifg=NONE guibg=#b2c0f3 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi VisualNOS guifg=NONE guibg=#cbd5f4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi Search guifg=#1d1f24 guibg=#c4b793 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi IncSearch guifg=#f2f3f5 guibg=#7e5e00 gui=bold ctermfg=7 ctermbg=3 cterm=bold
  hi CurSearch guifg=#f2f3f5 guibg=#7e5e00 gui=bold ctermfg=7 ctermbg=3 cterm=bold
  hi Substitute guifg=#f2f3f5 guibg=#915b00 gui=NONE ctermfg=7 ctermbg=3 cterm=NONE
  hi MatchParen guifg=NONE guibg=#c7d4f4 gui=bold ctermfg=NONE ctermbg=7 cterm=bold
  hi Pmenu guifg=#1d1f24 guibg=#e0e1e5 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi PmenuSel guifg=#fcfcfc guibg=#315bef gui=NONE ctermfg=7 ctermbg=4 cterm=NONE
  hi PmenuSbar guifg=NONE guibg=#e0e1e5 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi PmenuThumb guifg=NONE guibg=#66676c gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi PmenuKind guifg=#007176 guibg=#e0e1e5 gui=NONE ctermfg=14 ctermbg=7 cterm=NONE
  hi PmenuExtra guifg=#4b4d53 guibg=#e0e1e5 gui=NONE ctermfg=15 ctermbg=7 cterm=NONE
  hi WildMenu guifg=#fcfcfc guibg=#315bef gui=NONE ctermfg=7 ctermbg=4 cterm=NONE
  hi StatusLine guifg=#1d1f24 guibg=#e0e1e5 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi StatusLineNC guifg=#66676c guibg=#ecedef gui=NONE ctermfg=7 ctermbg=7 cterm=NONE
  hi StatusLineTerm guifg=#1d1f24 guibg=#e0e1e5 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi StatusLineTermNC guifg=#66676c guibg=#ecedef gui=NONE ctermfg=7 ctermbg=7 cterm=NONE
  hi TabLine guifg=#4b4d53 guibg=#ecedef gui=NONE ctermfg=15 ctermbg=7 cterm=NONE
  hi TabLineFill guifg=NONE guibg=#ecedef gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi TabLineSel guifg=#1d1f24 guibg=#f2f3f5 gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi ToolbarLine guifg=NONE guibg=#ecedef gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi VertSplit guifg=#ccced2 guibg=#f2f3f5 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi WinSeparator guifg=#ccced2 guibg=#f2f3f5 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi NonText guifg=#ccced2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi EndOfBuffer guifg=#ccced2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi SpecialKey guifg=#ccced2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Whitespace guifg=#ccced2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Conceal guifg=#66676c guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Directory guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
  hi Title guifg=#a43b38 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
  hi ModeMsg guifg=#1d1f24 guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi MoreMsg guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi Question guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi ErrorMsg guifg=#b63132 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
  hi WarningMsg guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi QuickFixLine guifg=NONE guibg=#d9e1f4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi DiffAdd guifg=NONE guibg=#c5dacf gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi DiffChange guifg=NONE guibg=#e4dcd0 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi DiffDelete guifg=#b63132 guibg=#e6ccce gui=NONE ctermfg=0 ctermbg=7 cterm=NONE
  hi DiffText guifg=NONE guibg=#d2c0a3 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
  hi SpellBad guifg=NONE guibg=NONE guisp=#b63132 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellCap guifg=NONE guibg=NONE guisp=#286cab gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellRare guifg=NONE guibg=NONE guisp=#8e4088 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellLocal guifg=NONE guibg=NONE guisp=#007176 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi Comment guifg=#66676c guibg=NONE gui=italic ctermfg=7 ctermbg=NONE cterm=italic
  hi Constant guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi String guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi Character guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi Number guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi Boolean guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi Float guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi Identifier guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Function guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
  hi Statement guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Conditional guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Repeat guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Label guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Keyword guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Exception guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Operator guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi PreProc guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Include guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi PreCondit guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Define guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Macro guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Type guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
  hi StorageClass guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Structure guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
  hi Typedef guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
  hi Special guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
  hi SpecialChar guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
  hi Tag guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi Delimiter guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi SpecialComment guifg=#66676c guibg=NONE gui=bold ctermfg=7 ctermbg=NONE cterm=bold
  hi Debug guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi Underlined guifg=#2a4fd0 guibg=NONE gui=underline ctermfg=12 ctermbg=NONE cterm=underline
  hi Ignore guifg=#66676c guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Error guifg=#b63132 guibg=NONE gui=bold,underline ctermfg=0 ctermbg=NONE cterm=bold,underline
  hi Todo guifg=#915b00 guibg=NONE gui=bold ctermfg=3 ctermbg=NONE cterm=bold
  hi Added guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi Changed guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi Removed guifg=#b63132 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi diffAdded guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
  hi diffRemoved guifg=#b63132 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
  hi diffChanged guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
  hi diffFile guifg=#a43b38 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
  hi diffLine guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi helpHyperTextJump guifg=#2a4fd0 guibg=NONE gui=underline ctermfg=12 ctermbg=NONE cterm=underline
  hi markdownH1 guifg=#a43b38 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
  let g:terminal_ansi_colors = ['#db1a22', '#2640d3', '#067c75', '#637703', '#315bef', '#ae20e7', '#017b87', '#607275', '#c00115', '#1b29be', '#036963', '#546502', '#2a4fd0', '#9802cd', '#006872', '#4f6164']
  if has('nvim')
    hi WinBar guifg=#1d1f24 guibg=#f2f3f5 gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
    hi WinBarNC guifg=#66676c guibg=#f2f3f5 gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi MsgArea guifg=#1d1f24 guibg=#f2f3f5 gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi MsgSeparator guifg=#ccced2 guibg=#ecedef gui=NONE ctermfg=7 ctermbg=7 cterm=NONE
    hi LspReferenceText guifg=NONE guibg=#d6d7da gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
    hi LspReferenceRead guifg=NONE guibg=#d6d7da gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
    hi LspReferenceWrite guifg=NONE guibg=#d0daf4 gui=NONE ctermfg=NONE ctermbg=7 cterm=NONE
    hi LspInlayHint guifg=#4b4d53 guibg=#e0e1e5 gui=NONE ctermfg=15 ctermbg=7 cterm=NONE
    hi LspCodeLens guifg=#66676c guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi LspSignatureActiveParameter guifg=NONE guibg=#d0daf4 gui=bold ctermfg=NONE ctermbg=7 cterm=bold
    hi DiagnosticError guifg=#b63132 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi DiagnosticWarn guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi DiagnosticInfo guifg=#286cab guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi DiagnosticHint guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi DiagnosticOk guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi DiagnosticSignError guifg=#b63132 guibg=#f2f3f5 gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi DiagnosticSignWarn guifg=#915b00 guibg=#f2f3f5 gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi DiagnosticSignInfo guifg=#286cab guibg=#f2f3f5 gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi DiagnosticSignHint guifg=#4b4d53 guibg=#f2f3f5 gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi DiagnosticSignOk guifg=#137738 guibg=#f2f3f5 gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi DiagnosticVirtualTextError guifg=#b63132 guibg=#ecdfe1 gui=NONE ctermfg=0 ctermbg=7 cterm=NONE
    hi DiagnosticVirtualTextWarn guifg=#915b00 guibg=#e8e4dc gui=NONE ctermfg=3 ctermbg=7 cterm=NONE
    hi DiagnosticVirtualTextInfo guifg=#286cab guibg=#dde5ed gui=NONE ctermfg=12 ctermbg=7 cterm=NONE
    hi DiagnosticVirtualTextHint guifg=#4b4d53 guibg=#e1e2e4 gui=NONE ctermfg=15 ctermbg=7 cterm=NONE
    hi DiagnosticVirtualTextOk guifg=#137738 guibg=#dbe6e2 gui=NONE ctermfg=10 ctermbg=7 cterm=NONE
    hi DiagnosticUnderlineError guifg=NONE guibg=NONE guisp=#b63132 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineWarn guifg=NONE guibg=NONE guisp=#915b00 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineInfo guifg=NONE guibg=NONE guisp=#286cab gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineHint guifg=NONE guibg=NONE guisp=#4b4d53 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineOk guifg=NONE guibg=NONE guisp=#137738 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnnecessary guifg=#66676c guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticDeprecated guifg=NONE guibg=NONE guisp=#66676c gui=strikethrough ctermfg=NONE ctermbg=NONE cterm=strikethrough
    hi @variable guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @variable.builtin guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @variable.parameter guifg=#1d1f24 guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @variable.member guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @property guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @constant guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @constant.builtin guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @constant.macro guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @module guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @label guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @string guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi @string.escape guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @string.regexp guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @string.special guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @string.special.symbol guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @string.special.url guifg=#2a4fd0 guibg=NONE gui=underline ctermfg=12 ctermbg=NONE cterm=underline
    hi @character guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi @character.special guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @number guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @number.float guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @boolean guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @type guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @type.builtin guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @type.definition guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @attribute guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @function.builtin guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @function.call guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @function.macro guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.method guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @function.method.call guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @constructor guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @operator guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @keyword guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @keyword.function guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @keyword.return guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @keyword.import guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @keyword.operator guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @keyword.directive guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @punctuation.delimiter guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @punctuation.bracket guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @punctuation.special guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @comment guifg=#66676c guibg=NONE gui=italic ctermfg=7 ctermbg=NONE cterm=italic
    hi @comment.documentation guifg=#66676c guibg=NONE gui=italic ctermfg=7 ctermbg=NONE cterm=italic
    hi @comment.error guifg=#b63132 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
    hi @comment.warning guifg=#915b00 guibg=NONE gui=bold ctermfg=3 ctermbg=NONE cterm=bold
    hi @comment.todo guifg=#915b00 guibg=NONE gui=bold ctermfg=3 ctermbg=NONE cterm=bold
    hi @comment.note guifg=#286cab guibg=NONE gui=bold ctermfg=12 ctermbg=NONE cterm=bold
    hi @markup.heading guifg=#a43b38 guibg=NONE gui=bold ctermfg=0 ctermbg=NONE cterm=bold
    hi @markup.strong guifg=#1d1f24 guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
    hi @markup.italic guifg=#1d1f24 guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @markup.strikethrough guifg=#1d1f24 guibg=NONE gui=strikethrough ctermfg=NONE ctermbg=NONE cterm=strikethrough
    hi @markup.underline guifg=#1d1f24 guibg=NONE gui=underline ctermfg=NONE ctermbg=NONE cterm=underline
    hi @markup.link guifg=#2a4fd0 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @markup.link.url guifg=#2a4fd0 guibg=NONE gui=underline ctermfg=12 ctermbg=NONE cterm=underline
    hi @markup.link.label guifg=#2a4fd0 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @markup.raw guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi @markup.list guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @markup.quote guifg=#66676c guibg=NONE gui=italic ctermfg=7 ctermbg=NONE cterm=italic
    hi @markup.math guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @tag guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @tag.attribute guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @tag.delimiter guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @diff.plus guifg=#137738 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi @diff.minus guifg=#b63132 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @diff.delta guifg=#915b00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @lsp.type.keyword guifg=#a43b38 guibg=NONE gui=NONE ctermfg=0 ctermbg=NONE cterm=NONE
    hi @lsp.type.string guifg=#007835 guibg=NONE gui=NONE ctermfg=10 ctermbg=NONE cterm=NONE
    hi @lsp.type.number guifg=#7e5e00 guibg=NONE gui=NONE ctermfg=3 ctermbg=NONE cterm=NONE
    hi @lsp.type.regexp guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.function guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @lsp.type.method guifg=#345fb2 guibg=NONE gui=NONE ctermfg=12 ctermbg=NONE cterm=NONE
    hi @lsp.type.class guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.interface guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.struct guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.type guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.typeParameter guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.namespace guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.enum guifg=#007176 guibg=NONE gui=NONE ctermfg=14 ctermbg=NONE cterm=NONE
    hi @lsp.type.enumMember guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.decorator guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.macro guifg=#8e4088 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.variable guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @lsp.type.property guifg=#1d1f24 guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @lsp.type.parameter guifg=#1d1f24 guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @lsp.type.comment guifg=#66676c guibg=NONE gui=italic ctermfg=7 ctermbg=NONE cterm=italic
    hi @lsp.type.operator guifg=#4b4d53 guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    let g:terminal_color_0 = '#db1a22'
    let g:terminal_color_1 = '#2640d3'
    let g:terminal_color_2 = '#067c75'
    let g:terminal_color_3 = '#637703'
    let g:terminal_color_4 = '#315bef'
    let g:terminal_color_5 = '#ae20e7'
    let g:terminal_color_6 = '#017b87'
    let g:terminal_color_7 = '#607275'
    let g:terminal_color_8 = '#c00115'
    let g:terminal_color_9 = '#1b29be'
    let g:terminal_color_10 = '#036963'
    let g:terminal_color_11 = '#546502'
    let g:terminal_color_12 = '#2a4fd0'
    let g:terminal_color_13 = '#9802cd'
    let g:terminal_color_14 = '#006872'
    let g:terminal_color_15 = '#4f6164'
  endif
else
  " Lliphi Oscuro
  hi Normal guifg=#eaebed guibg=#1b1b1d gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi NormalNC guifg=#eaebed guibg=#1b1b1d gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi NormalFloat guifg=#eaebed guibg=#232426 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi FloatBorder guifg=#3d3e42 guibg=#232426 gui=NONE ctermfg=8 ctermbg=8 cterm=NONE
  hi FloatTitle guifg=#f28881 guibg=#232426 gui=bold ctermfg=1 ctermbg=8 cterm=bold
  hi Cursor guifg=#1b1b1d guibg=#e22529 gui=NONE ctermfg=8 ctermbg=12 cterm=NONE
  hi lCursor guifg=#1b1b1d guibg=#e22529 gui=NONE ctermfg=8 ctermbg=12 cterm=NONE
  hi CursorIM guifg=#1b1b1d guibg=#e22529 gui=NONE ctermfg=8 ctermbg=12 cterm=NONE
  hi CursorLine guifg=NONE guibg=#2a2a2c gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi CursorColumn guifg=NONE guibg=#2a2a2c gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi ColorColumn guifg=NONE guibg=#2a2a2c gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi CursorLineNr guifg=#eaebed guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi LineNr guifg=#97989c guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi SignColumn guifg=#97989c guibg=#1b1b1d gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi FoldColumn guifg=#97989c guibg=#1b1b1d gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi Folded guifg=#97989c guibg=#312223 gui=NONE ctermfg=15 ctermbg=8 cterm=NONE
  hi Visual guifg=NONE guibg=#5d1e21 gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
  hi VisualNOS guifg=NONE guibg=#431d1f gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
  hi Search guifg=#eaebed guibg=#635229 gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
  hi IncSearch guifg=#1b1b1d guibg=#d0a43a gui=bold ctermfg=8 ctermbg=11 cterm=bold
  hi CurSearch guifg=#1b1b1d guibg=#d0a43a gui=bold ctermfg=8 ctermbg=11 cterm=bold
  hi Substitute guifg=#1b1b1d guibg=#ebb25f gui=NONE ctermfg=8 ctermbg=11 cterm=NONE
  hi MatchParen guifg=NONE guibg=#512d2c gui=bold ctermfg=NONE ctermbg=12 cterm=bold
  hi Pmenu guifg=#eaebed guibg=#232426 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi PmenuSel guifg=#fcfcfc guibg=#e22529 gui=NONE ctermfg=7 ctermbg=12 cterm=NONE
  hi PmenuSbar guifg=NONE guibg=#2e2f32 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi PmenuThumb guifg=NONE guibg=#97989c gui=NONE ctermfg=NONE ctermbg=15 cterm=NONE
  hi PmenuKind guifg=#00c2ca guibg=#232426 gui=NONE ctermfg=6 ctermbg=8 cterm=NONE
  hi PmenuExtra guifg=#bcbec1 guibg=#232426 gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
  hi WildMenu guifg=#fcfcfc guibg=#e22529 gui=NONE ctermfg=7 ctermbg=12 cterm=NONE
  hi StatusLine guifg=#eaebed guibg=#232426 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi StatusLineNC guifg=#97989c guibg=#1b1c1e gui=NONE ctermfg=15 ctermbg=8 cterm=NONE
  hi StatusLineTerm guifg=#eaebed guibg=#232426 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi StatusLineTermNC guifg=#97989c guibg=#1b1c1e gui=NONE ctermfg=15 ctermbg=8 cterm=NONE
  hi TabLine guifg=#bcbec1 guibg=#1b1c1e gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
  hi TabLineFill guifg=NONE guibg=#1b1c1e gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi TabLineSel guifg=#eaebed guibg=#1b1b1d gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi ToolbarLine guifg=NONE guibg=#1b1c1e gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi VertSplit guifg=#3d3e42 guibg=#1b1b1d gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi WinSeparator guifg=#3d3e42 guibg=#1b1b1d gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi NonText guifg=#3d3e42 guibg=NONE gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi EndOfBuffer guifg=#3d3e42 guibg=NONE gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi SpecialKey guifg=#3d3e42 guibg=NONE gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi Whitespace guifg=#3d3e42 guibg=NONE gui=NONE ctermfg=8 ctermbg=NONE cterm=NONE
  hi Conceal guifg=#97989c guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi Directory guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Title guifg=#f28881 guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
  hi ModeMsg guifg=#eaebed guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
  hi MoreMsg guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Question guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi ErrorMsg guifg=#fb817a guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
  hi WarningMsg guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi QuickFixLine guifg=NONE guibg=#3b2626 gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
  hi DiffAdd guifg=NONE guibg=#2c3e32 gui=NONE ctermfg=NONE ctermbg=10 cterm=NONE
  hi DiffChange guifg=NONE guibg=#3a3227 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
  hi DiffDelete guifg=#fb817a guibg=#482f30 gui=NONE ctermfg=1 ctermbg=12 cterm=NONE
  hi DiffText guifg=NONE guibg=#604d33 gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
  hi SpellBad guifg=NONE guibg=NONE guisp=#fb817a gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellCap guifg=NONE guibg=NONE guisp=#7fb6ee gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellRare guifg=NONE guibg=NONE guisp=#d98cd2 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi SpellLocal guifg=NONE guibg=NONE guisp=#00c2ca gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
  hi Comment guifg=#97989c guibg=NONE gui=italic ctermfg=15 ctermbg=NONE cterm=italic
  hi Constant guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi String guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi Character guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi Number guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi Boolean guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi Float guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi Identifier guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Function guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Statement guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Conditional guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Repeat guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Label guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Keyword guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Exception guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Operator guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi PreProc guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Include guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi PreCondit guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Define guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Macro guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Type guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
  hi StorageClass guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Structure guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
  hi Typedef guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
  hi Special guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
  hi SpecialChar guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
  hi Tag guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi Delimiter guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi SpecialComment guifg=#97989c guibg=NONE gui=bold ctermfg=15 ctermbg=NONE cterm=bold
  hi Debug guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi Underlined guifg=#ff968b guibg=NONE gui=underline ctermfg=7 ctermbg=NONE cterm=underline
  hi Ignore guifg=#97989c guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
  hi Error guifg=#fb817a guibg=NONE gui=bold,underline ctermfg=1 ctermbg=NONE cterm=bold,underline
  hi Todo guifg=#ebb25f guibg=NONE gui=bold ctermfg=11 ctermbg=NONE cterm=bold
  hi Added guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi Changed guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi Removed guifg=#fb817a guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi diffAdded guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi diffRemoved guifg=#fb817a guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
  hi diffChanged guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
  hi diffFile guifg=#f28881 guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
  hi diffLine guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
  hi helpHyperTextJump guifg=#ff968b guibg=NONE gui=underline ctermfg=7 ctermbg=NONE cterm=underline
  hi markdownH1 guifg=#f28881 guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
  let g:terminal_ansi_colors = ['#2640d3', '#fe3762', '#20aba2', '#c8ed17', '#eb3131', '#bd37f7', '#2fbfcf', '#99adb0', '#223cbf', '#e73259', '#1c948c', '#a9c413', '#dd2e2e', '#aa32e1', '#2aaab8', '#819294']
  if has('nvim')
    hi WinBar guifg=#eaebed guibg=#1b1b1d gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
    hi WinBarNC guifg=#97989c guibg=#1b1b1d gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi MsgArea guifg=#eaebed guibg=#1b1b1d gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi MsgSeparator guifg=#3d3e42 guibg=#1b1c1e gui=NONE ctermfg=8 ctermbg=8 cterm=NONE
    hi LspReferenceText guifg=NONE guibg=#343436 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
    hi LspReferenceRead guifg=NONE guibg=#343436 gui=NONE ctermfg=NONE ctermbg=8 cterm=NONE
    hi LspReferenceWrite guifg=NONE guibg=#462929 gui=NONE ctermfg=NONE ctermbg=12 cterm=NONE
    hi LspInlayHint guifg=#bcbec1 guibg=#232426 gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
    hi LspCodeLens guifg=#97989c guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi LspSignatureActiveParameter guifg=NONE guibg=#462929 gui=bold ctermfg=NONE ctermbg=12 cterm=bold
    hi DiagnosticError guifg=#fb817a guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi DiagnosticWarn guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi DiagnosticInfo guifg=#7fb6ee guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticHint guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticOk guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticSignError guifg=#fb817a guibg=#1b1b1d gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi DiagnosticSignWarn guifg=#ebb25f guibg=#1b1b1d gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi DiagnosticSignInfo guifg=#7fb6ee guibg=#1b1b1d gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticSignHint guifg=#bcbec1 guibg=#1b1b1d gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticSignOk guifg=#6fc884 guibg=#1b1b1d gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi DiagnosticVirtualTextError guifg=#fb817a guibg=#322526 gui=NONE ctermfg=1 ctermbg=8 cterm=NONE
    hi DiagnosticVirtualTextWarn guifg=#ebb25f guibg=#302a24 gui=NONE ctermfg=11 ctermbg=8 cterm=NONE
    hi DiagnosticVirtualTextInfo guifg=#7fb6ee guibg=#252b32 gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
    hi DiagnosticVirtualTextHint guifg=#bcbec1 guibg=#2b2c2e gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
    hi DiagnosticVirtualTextOk guifg=#6fc884 guibg=#242d28 gui=NONE ctermfg=7 ctermbg=8 cterm=NONE
    hi DiagnosticUnderlineError guifg=NONE guibg=NONE guisp=#fb817a gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineWarn guifg=NONE guibg=NONE guisp=#ebb25f gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineInfo guifg=NONE guibg=NONE guisp=#7fb6ee gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineHint guifg=NONE guibg=NONE guisp=#bcbec1 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnderlineOk guifg=NONE guibg=NONE guisp=#6fc884 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=undercurl
    hi DiagnosticUnnecessary guifg=#97989c guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi DiagnosticDeprecated guifg=NONE guibg=NONE guisp=#97989c gui=strikethrough ctermfg=NONE ctermbg=NONE cterm=strikethrough
    hi @variable guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @variable.builtin guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @variable.parameter guifg=#eaebed guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @variable.member guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @property guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @constant guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @constant.builtin guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @constant.macro guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @module guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @label guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @string guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @string.escape guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @string.regexp guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @string.special guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @string.special.symbol guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @string.special.url guifg=#ff968b guibg=NONE gui=underline ctermfg=7 ctermbg=NONE cterm=underline
    hi @character guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @character.special guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @number guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @number.float guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @boolean guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @type guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @type.builtin guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @type.definition guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @attribute guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.builtin guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.call guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.macro guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.method guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @function.method.call guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @constructor guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @operator guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @keyword guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @keyword.function guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @keyword.return guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @keyword.import guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @keyword.operator guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @keyword.directive guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @punctuation.delimiter guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @punctuation.bracket guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @punctuation.special guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @comment guifg=#97989c guibg=NONE gui=italic ctermfg=15 ctermbg=NONE cterm=italic
    hi @comment.documentation guifg=#97989c guibg=NONE gui=italic ctermfg=15 ctermbg=NONE cterm=italic
    hi @comment.error guifg=#fb817a guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
    hi @comment.warning guifg=#ebb25f guibg=NONE gui=bold ctermfg=11 ctermbg=NONE cterm=bold
    hi @comment.todo guifg=#ebb25f guibg=NONE gui=bold ctermfg=11 ctermbg=NONE cterm=bold
    hi @comment.note guifg=#7fb6ee guibg=NONE gui=bold ctermfg=7 ctermbg=NONE cterm=bold
    hi @markup.heading guifg=#f28881 guibg=NONE gui=bold ctermfg=1 ctermbg=NONE cterm=bold
    hi @markup.strong guifg=#eaebed guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
    hi @markup.italic guifg=#eaebed guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @markup.strikethrough guifg=#eaebed guibg=NONE gui=strikethrough ctermfg=NONE ctermbg=NONE cterm=strikethrough
    hi @markup.underline guifg=#eaebed guibg=NONE gui=underline ctermfg=NONE ctermbg=NONE cterm=underline
    hi @markup.link guifg=#ff968b guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @markup.link.url guifg=#ff968b guibg=NONE gui=underline ctermfg=7 ctermbg=NONE cterm=underline
    hi @markup.link.label guifg=#ff968b guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @markup.raw guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @markup.list guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @markup.quote guifg=#97989c guibg=NONE gui=italic ctermfg=15 ctermbg=NONE cterm=italic
    hi @markup.math guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @tag guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @tag.attribute guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @tag.delimiter guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @diff.plus guifg=#6fc884 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @diff.minus guifg=#fb817a guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @diff.delta guifg=#ebb25f guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @lsp.type.keyword guifg=#f28881 guibg=NONE gui=NONE ctermfg=1 ctermbg=NONE cterm=NONE
    hi @lsp.type.string guifg=#69c27e guibg=NONE gui=NONE ctermfg=15 ctermbg=NONE cterm=NONE
    hi @lsp.type.number guifg=#d0a43a guibg=NONE gui=NONE ctermfg=11 ctermbg=NONE cterm=NONE
    hi @lsp.type.regexp guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.function guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.method guifg=#7daafd guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.class guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.interface guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.struct guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.type guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.typeParameter guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.namespace guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.enum guifg=#00c2ca guibg=NONE gui=NONE ctermfg=6 ctermbg=NONE cterm=NONE
    hi @lsp.type.enumMember guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.decorator guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.macro guifg=#d98cd2 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    hi @lsp.type.variable guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @lsp.type.property guifg=#eaebed guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
    hi @lsp.type.parameter guifg=#eaebed guibg=NONE gui=italic ctermfg=NONE ctermbg=NONE cterm=italic
    hi @lsp.type.comment guifg=#97989c guibg=NONE gui=italic ctermfg=15 ctermbg=NONE cterm=italic
    hi @lsp.type.operator guifg=#bcbec1 guibg=NONE gui=NONE ctermfg=7 ctermbg=NONE cterm=NONE
    let g:terminal_color_0 = '#2640d3'
    let g:terminal_color_1 = '#fe3762'
    let g:terminal_color_2 = '#20aba2'
    let g:terminal_color_3 = '#c8ed17'
    let g:terminal_color_4 = '#eb3131'
    let g:terminal_color_5 = '#bd37f7'
    let g:terminal_color_6 = '#2fbfcf'
    let g:terminal_color_7 = '#99adb0'
    let g:terminal_color_8 = '#223cbf'
    let g:terminal_color_9 = '#e73259'
    let g:terminal_color_10 = '#1c948c'
    let g:terminal_color_11 = '#a9c413'
    let g:terminal_color_12 = '#dd2e2e'
    let g:terminal_color_13 = '#aa32e1'
    let g:terminal_color_14 = '#2aaab8'
    let g:terminal_color_15 = '#819294'
  endif
endif

if get(g:, 'lliphi_transparente', 0)
  hi Normal guibg=NONE ctermbg=NONE
  hi NormalNC guibg=NONE ctermbg=NONE
  hi SignColumn guibg=NONE ctermbg=NONE
  hi FoldColumn guibg=NONE ctermbg=NONE
  hi EndOfBuffer guibg=NONE ctermbg=NONE
  hi VertSplit guibg=NONE ctermbg=NONE
  hi WinSeparator guibg=NONE ctermbg=NONE
  hi TabLineSel guibg=NONE ctermbg=NONE
endif
