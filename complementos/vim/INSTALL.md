## Instalar

```bash
python3 herramientas/instalar.py --modulos vim --aplicar
```

Copia el esquema a `~/.local/share/nvim/site/colors/lliphi.vim`.

**Neovim** lo encuentra ahí. En `~/.config/nvim/init.lua`:

```lua
vim.cmd.colorscheme("lliphi")
```

(o `colorscheme lliphi` en `init.vim`). Neovim ≥ 0.10 activa solo los colores verdaderos y deduce `background` del fondo
de la terminal.

**Vim** busca los esquemas en `~/.vim/colors/`. Enlaza el instalado (así se actualiza con él) y actívalo en `~/.vimrc`:

```bash
mkdir -p ~/.vim/colors
ln -s ~/.local/share/nvim/site/colors/lliphi.vim ~/.vim/colors/lliphi.vim
```

```vim
set termguicolors
colorscheme lliphi
```

No fijes `background` en la configuración: así Vim y Neovim lo toman de Konsole y abren en la variante de Plasma. En
una sesión que ya estaba abierta cuando cambiaste de variante, `:set background=light` (o `dark`) la cambia.

## Actualizar

Vuelve a instalar; en un editor abierto, `:colorscheme lliphi`.

## Desinstalar

`python3 herramientas/instalar.py desinstalar --aplicar` (retira lo de todos los módulos) o borra
`~/.local/share/nvim/site/colors/lliphi.vim` y el enlace de `~/.vim/colors/`, y quita `colorscheme lliphi` de tu
configuración.
