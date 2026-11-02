# Vim y Neovim (`vim`)

El esquema de colores **`lliphi`** para Vim (≥ 9) y Neovim (≥ 0.9): un solo `colors/lliphi.vim` que leen los dos, con
**Lliphi Claro** cuando `background=light` y **Lliphi Oscuro** cuando `background=dark`.

- **El fondo y el texto** son los de Konsole (`konsole.ansi`): el editor se funde con la terminal en que corre. La
  terminal integrada (`:terminal`) lleva los dieciséis ANSI de Konsole.
- **La sintaxis** es la tabla única de los editores (palabras clave en rojo, cadenas en verde, números en amarillo,
  funciones en azul, tipos en cian, atributos en magenta, comentarios en cursiva en el texto inactivo).
- **La interfaz** (menús emergentes, barras de estado y de pestañas, selección, búsqueda, diferencias, ortografía) sale
  de los semánticos, con los resaltes compuestos sobre el fondo, porque Vim no mezcla alfa.
- **En Neovim**, además, los grupos de Tree-sitter, los de los tokens semánticos del LSP (con el reparto de VS Code) y
  los de diagnósticos.
- **Sin colores verdaderos** (`notermguicolors`), cada grupo toma el más cercano de los dieciséis colores de Konsole.
- **Sigue a la variante al arrancar**: Vim y Neovim deducen `background` del fondo de la terminal (Konsole responde a
  la pregunta OSC 11), y un cambio de `background` vuelve a cargar el esquema (decisiones 5.6).
- `let g:lliphi_transparente = 1` antes de `colorscheme lliphi` deja sin fondo el texto, para ver la transparencia de
  Konsole.

Es un **complemento** (fuera del tema global). Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: Vim script (`:highlight`, `g:terminal_ansi_colors`; en Neovim, grupos `@…` y `g:terminal_color_N` bajo
  `has('nvim')`, porque Vim no admite `@` en un nombre de grupo).
- El instalador lo pone en `$XDG_DATA_HOME/nvim/site/colors/`, que Neovim lee sin configurar nada. Vim no lee carpetas
  XDG cuando existe `~/.vimrc` o `~/.vim`: ver `INSTALL.md`.
- Lo generado: `generado/vim/colors/lliphi.vim`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos vim --aplicar
```

Prueba: `test_vim_esquema` (y, si están instalados, carga el esquema en Vim y en Neovim sin errores).
